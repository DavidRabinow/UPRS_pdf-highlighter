#!/usr/bin/env python3
"""
Flask Web Application for Selenium Automation
Serves a web interface to trigger browser automation processes.
"""

from flask import Flask, render_template, jsonify, request
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
    'search_text': None
}

def run_automation_in_background(search_text, company_name=None, start_point="none", start_page=None, highlight_text=None):
    """
    Background function to run Selenium automation.
    This runs in a separate thread so Flask remains responsive.
    
    Args:
        search_text (str): The URL to navigate to (e.g., Monday.com board URL)
        company_name (str): Optional company name to begin with
        start_point (str): Starting point - "none" or "company"
        highlight_text (str): Optional custom text for ChatGPT highlighting
    """
    global automation_status
    
    try:
        logger.info(f"Starting dynamic navigation automation in background with URL: '{search_text}', company: '{company_name}', start point: '{start_point}'")
        automation_status['running'] = True
        automation_status['start_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        automation_status['error'] = None
        automation_status['current_step'] = 'Initializing...'
        automation_status['search_text'] = search_text
        automation_status['company_name'] = company_name
        automation_status['start_point'] = start_point
        automation_status['start_page'] = start_page
        automation_status['highlight_text'] = highlight_text
        
        # Create and run automation with URL and additional parameters
        automation = SeleniumAutomation()
        automation.run(search_text, company_name, start_point, start_page, highlight_text)
        
        # Update status on completion
        automation_status['running'] = False
        automation_status['completed'] = True
        automation_status['end_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        automation_status['current_step'] = 'Automation completed successfully'
        logger.info("Dynamic navigation automation completed successfully")
        
    except Exception as e:
        # Update status on error
        automation_status['running'] = False
        automation_status['error'] = str(e)
        automation_status['end_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        automation_status['current_step'] = f'Error: {str(e)}'
        logger.error(f"Dynamic navigation automation failed: {e}")

@app.route('/')
def index():
    """
    Main page with the Start Automation button and URL input.
    """
    return render_template('index.html', status=automation_status)

@app.route('/start_automation', methods=['POST'])
def start_automation():
    """
    API endpoint to start the automation process.
    Receives URL from frontend and returns immediately while automation runs in background.
    """
    global automation_status
    
    # Check if automation is already running
    if automation_status['running']:
        return jsonify({
            'success': False,
            'message': 'Automation is already running'
        })
    
    # Get parameters from request
    try:
        data = request.get_json()
        search_text = data.get('search_text', '').strip()
        company_name = data.get('company_name', '').strip()
        start_point = data.get('start_point', 'none')
        start_page = data.get('start_page', None)
        highlight_text = data.get('highlight_text', '').strip()
        if start_page is not None:
            try:
                start_page = int(start_page)
                if start_page < 1:
                    raise ValueError
            except Exception:
                return jsonify({
                    'success': False,
                    'message': 'Start page must be a positive integer.'
                })
        else:
            start_page = None
        
        if not search_text:
            return jsonify({
                'success': False,
                'message': 'URL is required'
            })
        
        # Validate that search_text looks like a URL
        if not (search_text.startswith('http://') or search_text.startswith('https://')):
            return jsonify({
                'success': False,
                'message': 'Please enter a valid URL starting with http:// or https://'
            })
        
        # Validate start point
        if start_point not in ['none', 'company']:
            return jsonify({
                'success': False,
                'message': 'Invalid start point. Must be "none" or "company"'
            })
        
        # Validate company name if start point is company
        if start_point == 'company' and not company_name:
            return jsonify({
                'success': False,
                'message': 'Company name is required when start point is "company"'
            })
            
        logger.info(f"Received dynamic navigation request with URL: '{search_text}', company: '{company_name}', start point: '{start_point}', start page: '{start_page}'")
        
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
        'search_text': None,
        'company_name': None,
        'start_point': None,
        'start_page': None,
        'highlight_text': None
    }
    
    # Start automation in background thread with all parameters
    automation_thread = threading.Thread(target=run_automation_in_background, args=(search_text, company_name, start_point, start_page, highlight_text))
    automation_thread.daemon = True  # Thread will stop when main app stops
    automation_thread.start()
    
    logger.info(f"Dynamic navigation thread started with URL: '{search_text}', company: '{company_name}', start point: '{start_point}', highlight text: '{highlight_text}'")
    
    return jsonify({
        'success': True,
        'message': f'Dynamic navigation started successfully with URL: "{search_text}", company: "{company_name}", start point: "{start_point}"'
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
        'search_text': None,
        'company_name': None,
        'start_point': None
    }
    return jsonify({'success': True, 'message': 'Status reset'})

if __name__ == '__main__':
    # Configuration for public access
    HOST = '0.0.0.0'  # Bind to all interfaces for public access
    PORT = 5001       # Port to listen on (changed from 5000 to avoid AirPlay conflict)
    
    logger.info(f"Starting Flask server on {HOST}:{PORT}")
    logger.info("Server will be accessible from any network interface")
    logger.info("For testing: http://localhost:5001 or http://[your-ip]:5001")
    
    # Start Flask development server
    app.run(
        host=HOST,
        port=PORT,
        debug=True,  # Enable debug mode for development
        threaded=True  # Enable threading for multiple requests
    ) 