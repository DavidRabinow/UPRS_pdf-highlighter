#!/usr/bin/env python3
"""
Flask Web Application for PDF Highlighting
Serves a web interface to trigger PDF highlighting processes.
"""

from flask import Flask, render_template, jsonify, request
import os
import json
import threading
import time
import logging
from automation import SeleniumAutomation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Global variable to track automation status
automation_status = {
    'running': False,
    'completed': False,
    'error': None,
    'start_time': None,
    'end_time': None,
    'current_step': None,
    'highlight_text': None,
    'name_text': None,
    'signature_options': None
}

def run_automation_in_background(highlight_text=None, name_text=None, signature_options=None, uploaded_filepath=None):
    """
    Background function to run PDF highlighting automation.
    This runs in a separate thread so Flask remains responsive.
    
    Args:
        highlight_text (str): Optional custom text for ChatGPT highlighting
        name_text (str): Optional name to fill in PDF forms
        signature_options (dict): Optional signature options from checkboxes
        uploaded_filepath (str): Path to the uploaded PDF file
    """
    global automation_status
    
    try:
        logger.info(f"Starting highlighting automation with file: '{uploaded_filepath}', highlight text: '{highlight_text}', name text: '{name_text}', signature options: '{signature_options}'")
        automation_status['running'] = True
        automation_status['start_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        automation_status['error'] = None
        automation_status['current_step'] = 'Initializing highlighting...'
        automation_status['highlight_text'] = highlight_text
        automation_status['name_text'] = name_text
        automation_status['signature_options'] = signature_options
        automation_status['uploaded_file'] = uploaded_filepath
        
        # Create and run automation
        automation = SeleniumAutomation()
        automation.run_highlighting(highlight_text, name_text, signature_options, uploaded_filepath)
        
        # Update status on completion
        automation_status['running'] = False
        automation_status['completed'] = True
        automation_status['end_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        automation_status['current_step'] = 'Highlighting completed successfully'
        logger.info("PDF highlighting automation completed successfully")
        
    except Exception as e:
        # Update status on error
        automation_status['running'] = False
        automation_status['error'] = str(e)
        automation_status['end_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        automation_status['current_step'] = f'Error: {str(e)}'
        logger.error(f"PDF highlighting automation failed: {e}")

@app.route('/')
def index():
    """
    Main page with the Start Highlighting button and highlight text input.
    """
    return render_template('index.html', status=automation_status)

@app.route('/start_automation', methods=['POST'])
def start_automation():
    """
    API endpoint to start the highlighting process.
    Receives highlight text and PDF file from frontend and returns immediately while automation runs in background.
    """
    global automation_status
    
    # Check if automation is already running
    if automation_status['running']:
        return jsonify({
            'success': False,
            'message': 'Highlighting is already running'
        })
    
    # Get parameters from request (FormData)
    try:
        highlight_text = request.form.get('highlight_text', '').strip()
        name_text = request.form.get('name_text', '').strip()
        signature_options_json = request.form.get('signature_options', '{}')
        signature_options = json.loads(signature_options_json)
        
        # Handle file upload
        if 'pdf_file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'PDF file is required'
            })
        
        pdf_file = request.files['pdf_file']
        if pdf_file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected'
            })
        
        if not pdf_file.filename.lower().endswith('.pdf') and not pdf_file.filename.lower().endswith('.zip'):
            return jsonify({
                'success': False,
                'message': 'Please upload a valid PDF or ZIP file'
            })
        
        # Create uploads directory if it doesn't exist
        uploads_dir = 'uploads'
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
        
        # Save the uploaded file
        filename = f"uploaded_{int(time.time())}_{pdf_file.filename}"
        filepath = os.path.join(uploads_dir, filename)
        pdf_file.save(filepath)
        

            
        logger.info(f"Received highlighting request with file: '{filename}', highlight text: '{highlight_text}', name text: '{name_text}', signature options: '{signature_options}'")
        
    except Exception as e:
        logger.error(f"Error parsing request data: {e}")
        return jsonify({
            'success': False,
            'message': 'Invalid request data'
        })
    
    # Reset status for new run
    automation_status = {
        'running': False,
        'completed': False,
        'error': None,
        'start_time': None,
        'end_time': None,
        'current_step': None,
        'highlight_text': None,
        'name_text': None,
        'signature_options': None,
        'uploaded_file': None
    }
    
    # Start automation in background thread
    automation_thread = threading.Thread(target=run_automation_in_background, args=(highlight_text, name_text, signature_options, filepath))
    automation_thread.daemon = True  # Thread will stop when main app stops
    automation_thread.start()
    
    logger.info(f"Highlighting thread started with file: '{filename}', highlight text: '{highlight_text}', name text: '{name_text}'")
    
    return jsonify({
        'success': True,
        'message': f'Highlighting started successfully with file: "{filename}" and text: "{highlight_text}"'
    })

@app.route('/status')
def get_status():
    """
    API endpoint to get current automation status.
    Used by frontend to poll for updates.
    """
    return jsonify(automation_status)

@app.route('/reset')
def reset_status():
    """
    API endpoint to reset automation status.
    Useful for testing multiple runs.
    """
    global automation_status
    automation_status = {
        'running': False,
        'completed': False,
        'error': None,
        'start_time': None,
        'end_time': None,
        'current_step': None,
        'highlight_text': None,
        'name_text': None,
        'signature_options': None,
        'uploaded_file': None
    }
    return jsonify({'success': True, 'message': 'Status reset'})

if __name__ == '__main__':
    # Configuration for public access
    HOST = '0.0.0.0'  # Bind to all interfaces for public access
    PORT = 5002       # Port to listen on (changed from 5001 to 5002)
    
    logger.info(f"Starting Flask server on {HOST}:{PORT}")
    logger.info("Server will be accessible from any network interface")
    logger.info("For testing: http://localhost:5002 or http://[your-ip]:5002")
    
    # Start Flask development server
    app.run(
        host=HOST,
        port=PORT,
        debug=True,  # Enable debug mode for development
        threaded=True  # Enable threading for multiple requests
    ) 