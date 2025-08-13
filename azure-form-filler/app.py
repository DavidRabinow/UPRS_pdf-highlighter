"""
Azure-Powered Batch Form Filler API
Flask application for processing PDF forms with Azure Document Intelligence
"""

import os
import tempfile
import zipfile
import json
from functools import wraps
from flask import Flask, request, jsonify, send_file
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from azure_processor import process_zip_with_azure

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH_MB', 200)) * 1024 * 1024
API_SHARED_SECRET = os.getenv('API_SHARED_SECRET', 'change-me')

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if not api_key or api_key != API_SHARED_SECRET:
            return jsonify({'error': 'Unauthorized - Invalid or missing API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'error': f'File too large. Maximum size is {app.config["MAX_CONTENT_LENGTH"] // (1024*1024)}MB'}), 413

@app.errorhandler(400)
def bad_request(e):
    """Handle bad request error"""
    return jsonify({'error': 'Bad request - Invalid input data'}), 400

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'azure-form-filler'})

@app.route('/process', methods=['POST'])
@require_api_key
def process_files():
    """
    Process uploaded files with Azure Document Intelligence
    
    Accepts:
    - zip_file: ZIP file containing documents to process
    - file: Single PDF file to process
    - fill_map: JSON string mapping field labels to values
    - highlight_terms: JSON string array of terms to highlight
    
    Returns:
    - ZIP file containing processed documents
    """
    try:
        # Validate required fields
        if 'fill_map' not in request.form:
            return jsonify({'error': 'Missing required field: fill_map'}), 400
        
        if 'highlight_terms' not in request.form:
            return jsonify({'error': 'Missing required field: highlight_terms'}), 400
        
        # Parse JSON parameters
        try:
            fill_map = json.loads(request.form['fill_map'])
            highlight_terms = json.loads(request.form['highlight_terms'])
        except json.JSONDecodeError as e:
            return jsonify({'error': f'Invalid JSON in form data: {str(e)}'}), 400
        
        # Validate file upload
        if 'zip_file' in request.files:
            uploaded_file = request.files['zip_file']
            if uploaded_file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            file_type = 'zip'
        elif 'file' in request.files:
            uploaded_file = request.files['file']
            if uploaded_file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            file_type = 'single'
        else:
            return jsonify({'error': 'No file uploaded. Use zip_file or file parameter'}), 400
        
        # Create temporary directories
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = os.path.join(temp_dir, 'input')
            output_dir = os.path.join(temp_dir, 'output')
            os.makedirs(input_dir)
            os.makedirs(output_dir)
            
            # Save uploaded file
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(temp_dir, filename)
            uploaded_file.save(file_path)
            
            # Process based on file type
            if file_type == 'zip':
                # Extract ZIP to input directory
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(input_dir)
                input_zip_path = file_path
            else:
                # For single file, create a temporary ZIP
                input_zip_path = os.path.join(temp_dir, 'single_file.zip')
                with zipfile.ZipFile(input_zip_path, 'w') as zip_ref:
                    zip_ref.write(file_path, filename)
            
            # Process with Azure
            output_zip_path = process_zip_with_azure(
                input_zip_path, 
                fill_map, 
                highlight_terms,
                input_dir=input_dir,
                output_dir=output_dir
            )
            
            # Return processed ZIP
            return send_file(
                output_zip_path,
                mimetype='application/zip',
                as_attachment=True,
                download_name='processed.zip'
            )
    
    except Exception as e:
        app.logger.error(f"Error processing files: {str(e)}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
