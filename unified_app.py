#!/usr/bin/env python3
"""
Unified PDF Processing and Automation Application
Combines PDF filling, highlighting, and RPA automation into one interface.
"""

import io
import zipfile
import re
import threading
import time
import logging
import tempfile
import json
from pathlib import Path
from flask import Flask, render_template, request, send_file, flash, redirect, url_for, jsonify
from datetime import datetime

# Import modules from existing apps
try:
    import sys
    import os
    sys.path.append(os.path.join('apps', 'pdf-filler', 'app'))
    from processor import process_zip, fill_pdf
    sys.path.append(os.path.join('apps', 'rpa'))
    from automation import SeleniumAutomation
except ImportError as e:
    # Fallback imports if modules aren't available
    print(f"Warning: Some modules not available, some features may be limited: {e}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "unified-secret-key"

# Common words/phrases that might need highlighting
COMMON_HIGHLIGHTS = [
    # Signature-related fields - focused on exact matches
    "Signature of Claimant", "Claimant Signature", "Claimant's Signature",
    "Signature of Notary", "Notary Public Signature", "Notary Signature",
    "Notary Public", "Notary", "Notarized", "Notarization",
    "Witness Signature", "Witness", "Witnessed",
    "Authorized Signature", "Authorized Signer", "Authorized Representative",
    "Legal Signature", "Legal Representative", "Legal Guardian",
    "Power of Attorney", "POA", "Attorney Signature"
]

# Global variable to track automation status
automation_status = {
    'running': False,
    'completed': False,
    'error': None,
    'start_time': None,
    'end_time': None,
    'current_step': None,
    'search_text': None
}

def highlight_pdf(pdf_bytes, highlight_words):
    """Highlight specified words in a PDF by finding their positions and drawing yellow rectangles"""
    try:
        # Try to import PyMuPDF (fitz) for better text highlighting
        try:
            import fitz  # PyMuPDF
            use_fitz = True
        except ImportError:
            use_fitz = False
            print("PyMuPDF not available, using fallback method")
        
        if use_fitz:
            # Use PyMuPDF for better text highlighting
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Search for each word on the page with exact matching
                for word in highlight_words:
                    # First try exact case-sensitive search
                    text_instances = page.search_for(word, flags=0)  # No flags = case sensitive
                    
                    # If no exact matches found, try case-insensitive
                    if not text_instances:
                        text_instances = page.search_for(word, flags=fitz.TEXTFLAGS_IGNORECASE)
                    
                    # Highlight each instance found
                    for inst in text_instances:
                        # Create a highlight annotation
                        highlight = page.add_highlight_annot(inst)
                        highlight.set_colors(stroke=[1, 1, 0])  # Yellow
                        highlight.set_opacity(0.4)  # More visible
                        highlight.update()
                        
                        print(f"Highlighted '{word}' on page {page_num + 1}")
            
            # Save the highlighted PDF
            output_stream = io.BytesIO()
            doc.save(output_stream, garbage=4, deflate=True)
            doc.close()
            output_stream.seek(0)
            return output_stream.getvalue()
        
        else:
            # Fallback method using PyPDF2
            import PyPDF2
            from PyPDF2 import PdfReader, PdfWriter
            
            pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
            pdf_writer = PdfWriter()
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                
                # Extract text from the page
                text = page.extract_text()
                
                # For each word to highlight, create a simple text-based annotation
                for word in highlight_words:
                    # Check for exact matches first (case sensitive)
                    if word in text:
                        print(f"Found exact match for '{word}' on page {page_num + 1}")
                        # Create a simple highlight annotation
                        highlight_annotation = {
                            '/Type': '/Annot',
                            '/Subtype': '/Highlight',
                            '/Rect': [50, 750 - (page_num * 20), 200, 770 - (page_num * 20)],
                            '/F': 4,
                            '/C': [1, 1, 0],  # Yellow
                            '/T': 'Highlight',
                            '/Contents': f'Found: {word}'
                        }
                        
                        if '/Annots' not in page:
                            page['/Annots'] = []
                        page['/Annots'].append(highlight_annotation)
                    # Also check case-insensitive
                    elif word.lower() in text.lower():
                        print(f"Found case-insensitive match for '{word}' on page {page_num + 1}")
                        # Create a simple highlight annotation
                        highlight_annotation = {
                            '/Type': '/Annot',
                            '/Subtype': '/Highlight',
                            '/Rect': [50, 750 - (page_num * 20), 200, 770 - (page_num * 20)],
                            '/F': 4,
                            '/C': [1, 1, 0],  # Yellow
                            '/T': 'Highlight',
                            '/Contents': f'Found: {word}'
                        }
                        
                        if '/Annots' not in page:
                            page['/Annots'] = []
                        page['/Annots'].append(highlight_annotation)
                
                pdf_writer.add_page(page)
            
            output_stream = io.BytesIO()
            pdf_writer.write(output_stream)
            output_stream.seek(0)
            return output_stream.getvalue()
            
    except Exception as e:
        print(f"Error highlighting PDF: {e}")
        # Return original PDF if highlighting fails
        return pdf_bytes

def process_highlight_zip(zip_bytes, highlight_words):
    """Process a ZIP file and highlight specified words in all PDFs"""
    output_zip = io.BytesIO()
    
    with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as input_zip:
        with zipfile.ZipFile(output_zip, 'w') as output_zip_file:
            for file_info in input_zip.filelist:
                if file_info.filename.lower().endswith('.pdf'):
                    # Read the PDF
                    pdf_bytes = input_zip.read(file_info.filename)
                    
                    # Highlight the PDF
                    highlighted_pdf = highlight_pdf(pdf_bytes, highlight_words)
                    
                    # Add to output ZIP
                    output_zip_file.writestr(f"highlighted_{file_info.filename}", highlighted_pdf)
                else:
                    # Copy non-PDF files as-is
                    file_bytes = input_zip.read(file_info.filename)
                    output_zip_file.writestr(file_info.filename, file_bytes)
    
    return output_zip.getvalue()

def run_automation_in_background(highlight_text=None, name_text=None, signature_options=None, data_file_path=None):
    """
    Background function to run Selenium automation.
    This runs in a separate thread so Flask remains responsive.
    """
    global automation_status
    
    try:
        logger.info(f"Starting automation in background with highlight text: '{highlight_text}', name text: '{name_text}', signature options: '{signature_options}', data file: '{data_file_path}'")
        automation_status['running'] = True
        automation_status['start_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        automation_status['error'] = None
        automation_status['current_step'] = 'Initializing...'
        automation_status['highlight_text'] = highlight_text
        automation_status['name_text'] = name_text
        automation_status['signature_options'] = signature_options
        
        # Create and run automation
        try:
            automation = SeleniumAutomation()
            automation.run(highlight_text, name_text, signature_options, data_file_path)
            
            # Update status on completion
            automation_status['running'] = False
            automation_status['completed'] = True
            automation_status['end_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
            automation_status['current_step'] = 'Automation completed successfully'
            logger.info("Dynamic navigation automation completed successfully")
        except Exception as e:
            raise e
        
    except Exception as e:
        # Update status on error
        automation_status['running'] = False
        automation_status['error'] = str(e)
        automation_status['end_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        automation_status['current_step'] = f'Error: {str(e)}'
        logger.error(f"Dynamic navigation automation failed: {e}")

# Routes for the unified application

@app.route('/')
def index():
    """Main page with all functionality tabs"""
    return render_template('unified_index.html', 
                         common_highlights=COMMON_HIGHLIGHTS,
                         automation_status=automation_status)

# PDF Filler Routes
@app.route('/fill_pdf', methods=['POST'])
def fill_pdf_route():
    """Handle PDF filling requests"""
    try:
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()
        ein = request.form.get('ein', '').strip()
        dob = request.form.get('dob', '').strip()
        
        # Get signature options
        signature_options = {}
        for key in request.form:
            if key.startswith('signature_'):
                signature_options[key] = request.form[key]
        
        # Validate required fields
        if not name:
            flash("Name is required for PDF filling.")
            return redirect(url_for('index'))
        
        # Get uploaded file
        f = request.files.get('zipfile')
        if not f or not f.filename.lower().endswith('.zip'):
            flash("Please upload a ZIP file containing PDFs.")
            return redirect(url_for('index'))
        
        # Prepare values dictionary
        values = {
            'name': name,
            'email': email,
            'address': address,
            'phone': phone,
            'ein': ein,
            'dob': dob
        }
        
        # Add signature options
        values.update(signature_options)
        
        # Process the ZIP file
        zip_bytes = f.read()
        try:
            processed_zip = process_zip(zip_bytes, values)
        except Exception as e:
            flash(f"Error processing PDFs: {str(e)}")
            return redirect(url_for('index'))
        
        # Return the processed ZIP file
        return send_file(
            io.BytesIO(processed_zip),
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'filled_documents_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
        )
        
    except Exception as e:
        flash(f"An error occurred: {str(e)}")
        return redirect(url_for('index'))

# PDF Highlighter Routes
@app.route('/highlight_pdf', methods=['POST'])
def highlight_pdf_route():
    """Handle PDF highlighting requests"""
    try:
        # Get selected highlight words
        selected_words = request.form.getlist("highlight_words")
        custom_words = request.form.get("custom_words", "").strip()
        
        # Combine selected and custom words
        all_highlight_words = selected_words.copy()
        if custom_words:
            # Split custom words by comma or newline
            custom_list = re.split(r'[,;\n]', custom_words)
            all_highlight_words.extend([word.strip() for word in custom_list if word.strip()])
        
        if not all_highlight_words:
            flash("Please select at least one word to highlight.")
            return redirect(url_for('index'))
        
        # Get uploaded file
        f = request.files.get("zipfile")
        if not f or not f.filename.lower().endswith(".zip"):
            flash("Please upload a ZIP file containing PDFs.")
            return redirect(url_for('index'))
        
        # Process the ZIP file
        zip_bytes = f.read()
        try:
            highlighted_zip = process_highlight_zip(zip_bytes, all_highlight_words)
        except Exception as e:
            flash(f"Error highlighting PDFs: {str(e)}")
            return redirect(url_for('index'))
        
        # Return the highlighted ZIP file
        return send_file(
            io.BytesIO(highlighted_zip),
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'highlighted_documents_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
        )
        
    except Exception as e:
        flash(f"An error occurred: {str(e)}")
        return redirect(url_for('index'))

# RPA Automation Routes
@app.route('/start_automation', methods=['POST'])
def start_automation():
    """API endpoint to start the automation process."""
    global automation_status
    
    try:
        # Handle form data with file upload
        highlight_text = request.form.get('highlight_text', '').strip()
        name_text = request.form.get('name_text', '').strip()
        signature_options_str = request.form.get('signature_options', '{}')
        
        # Parse signature options
        try:
            signature_options = json.loads(signature_options_str)
        except json.JSONDecodeError:
            signature_options = {}
        
        # Handle file upload
        data_file = request.files.get('data_file')
        if not data_file:
            return jsonify({
                'success': False,
                'message': 'Data file is required'
            })
        

            
        logger.info(f"Received automation request with highlight text: '{highlight_text}', name text: '{name_text}', signature options: '{signature_options}', data file: '{data_file.filename}'")
        
    except Exception as e:
        logger.error(f"Error parsing request data: {e}")
        return jsonify({
            'success': False,
            'message': 'Invalid request data'
        })
    
    # Save uploaded file to temporary location
    import tempfile
    import os
    
    # Create uploads directory if it doesn't exist
    uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    
    # Save file with unique name
    file_extension = os.path.splitext(data_file.filename)[1]
    temp_filename = f"data_file_{int(time.time())}{file_extension}"
    file_path = os.path.join(uploads_dir, temp_filename)
    data_file.save(file_path)
    
    # Reset status for new run
    automation_status = {
        'running': False,
        'completed': False,
        'error': None,
        'start_time': None,
        'end_time': None,
        'current_step': None,
        'data_file': data_file.filename,
        'highlight_text': None,
        'name_text': None,
        'signature_options': None
    }
    
    # Start automation in background thread
    automation_thread = threading.Thread(target=run_automation_in_background, args=(highlight_text, name_text, signature_options, file_path))
    automation_thread.daemon = True  # Thread will stop when main app stops
    automation_thread.start()
    
    logger.info(f"Automation thread started with highlight text: '{highlight_text}', name text: '{name_text}', data file: '{data_file.filename}'")
    
    return jsonify({
        'success': True,
        'message': 'Automation started successfully'
    })

@app.route('/automation_status')
def get_automation_status():
    """API endpoint to get current automation status."""
    return jsonify(automation_status)

@app.route('/reset_automation')
def reset_automation_status():
    """API endpoint to reset automation status."""
    global automation_status
    automation_status = {
        'running': False,
        'completed': False,
        'error': None,
        'start_time': None,
        'end_time': None,
        'current_step': None,
        'data_file': None,
        'highlight_text': None,
        'name_text': None,
        'signature_options': None
    }
    return jsonify({'success': True, 'message': 'Status reset'})

if __name__ == '__main__':
    # Configuration for public access
    HOST = '0.0.0.0'  # Bind to all interfaces for public access
    PORT = 5001       # Port to listen on
    
    logger.info(f"Starting Unified Flask server on {HOST}:{PORT}")
    logger.info("Server will be accessible from any network interface")
    logger.info("For testing: http://localhost:5001 or http://[your-ip]:5001")
    
    # Start Flask development server
    app.run(
        host=HOST,
        port=PORT,
        debug=False,  # Disable debug mode to prevent auto-reload during automation
        threaded=True  # Enable threading for multiple requests
    )
