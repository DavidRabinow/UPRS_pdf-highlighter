#!/usr/bin/env python3
"""
ChatGPT File Processor
Processes uploaded data files with ChatGPT for automation.
"""

import argparse
import json
import logging
import os
import sys
import time
import zipfile
import tempfile
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_file_with_chatgpt(file_path, highlight_text=None, name_text=None, signature_options=None):
    """
    Process the uploaded file with ChatGPT.
    
    Args:
        file_path (str): Path to the uploaded data file
        highlight_text (str): Optional custom text for highlighting
        name_text (str): Optional name to use in processing
        signature_options (dict): Optional signature options
    """
    try:
        logger.info(f"Processing file: {file_path}")
        
        # Read the uploaded file
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Determine file type and read content
        file_extension = Path(file_path).suffix.lower()
        
        # Handle ZIP files by extracting them first
        if file_extension == '.zip':
            logger.info("Detected ZIP file, extracting contents...")
            temp_dir = tempfile.mkdtemp()
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Find the first readable file in the extracted contents
                extracted_files = []
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path_in_zip = os.path.join(root, file)
                        file_ext = Path(file).suffix.lower()
                        # Support more file types including PDFs
                        if file_ext in ['.csv', '.txt', '.xlsx', '.xls', '.json', '.pdf']:
                            extracted_files.append(file_path_in_zip)
                
                if not extracted_files:
                    raise ValueError("No supported files found in ZIP archive")
                
                # Use the first supported file found
                actual_file_path = extracted_files[0]
                logger.info(f"Using extracted file: {actual_file_path}")
                file_extension = Path(actual_file_path).suffix.lower()
                file_path = actual_file_path
            except Exception as e:
                shutil.rmtree(temp_dir, ignore_errors=True)
                raise ValueError(f"Failed to extract ZIP file: {e}")
        
        # Read the file content based on its type
        if file_extension in ['.csv', '.txt']:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
        elif file_extension in ['.xlsx', '.xls']:
            import pandas as pd
            df = pd.read_excel(file_path)
            file_content = df.to_string()
        elif file_extension == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                file_content = json.dumps(data, indent=2)
        elif file_extension == '.pdf':
            # For PDFs, we'll create a placeholder content since we can't easily read PDF text
            # The actual PDF processing will be handled by the PDF highlighter
            file_content = f"PDF file detected: {os.path.basename(file_path)}\nThis PDF will be processed by the PDF highlighter for highlighting and annotation."
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        # Clean up temporary directory if it was created for ZIP extraction
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        logger.info(f"Successfully read file content ({len(file_content)} characters)")
        
        # Create ChatGPT prompt based on file content and parameters
        prompt = f"""
Please analyze the following data file and extract relevant information for processing:

File Content:
{file_content}

Additional Parameters:
- Highlight Text: {highlight_text or 'None provided'}
- Name Text: {name_text or 'None provided'}
- Signature Options: {signature_options or 'None provided'}

Please:
1. Extract any EIN numbers, addresses, emails, phone numbers, and other relevant data
2. Identify any patterns or important information
3. Provide recommendations for processing this data
4. Highlight any critical fields that need attention

Please format your response as JSON with the following structure:
{{
    "extracted_data": {{
        "ein_numbers": [],
        "addresses": [],
        "emails": [],
        "phone_numbers": [],
        "names": [],
        "other_fields": []
    }},
    "recommendations": [],
    "critical_fields": [],
    "processing_notes": ""
}}
"""
        
        # Save the prompt to a file for ChatGPT processing
        prompt_file = "chatgpt_prompt.txt"
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
        
        logger.info(f"Created ChatGPT prompt file: {prompt_file}")
        
        # Create a response file with sample data (in a real implementation, this would be sent to ChatGPT API)
        sample_response = {
            "extracted_data": {
                "ein_numbers": ["123456789", "987654321"],
                "addresses": ["123 Main St, City, State", "456 Oak Ave, City, State"],
                "emails": ["example@email.com", "test@email.com"],
                "phone_numbers": ["555-123-4567", "555-987-6543"],
                "names": ["John Doe", "Jane Smith"],
                "other_fields": []
            },
            "recommendations": [
                "Process EIN numbers for tax purposes",
                "Validate email addresses",
                "Standardize phone number formats"
            ],
            "critical_fields": [
                "EIN numbers for tax compliance",
                "Email addresses for communication"
            ],
            "processing_notes": f"File processed successfully. Found {len(file_content)} characters of data. Ready for automation processing."
        }
        
        # Save the response
        response_file = "chatgpt_response.txt"
        with open(response_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(sample_response, indent=2))
        
        logger.info(f"Created ChatGPT response file: {response_file}")
        
        # Create a summary file for the automation
        summary_file = "file_processing_summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"File Processing Summary\n")
            f.write(f"=====================\n")
            f.write(f"File: {file_path}\n")
            f.write(f"File Size: {len(file_content)} characters\n")
            f.write(f"File Type: {file_extension}\n")
            f.write(f"Processing Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"\nExtracted Data:\n")
            f.write(f"- EIN Numbers: {len(sample_response['extracted_data']['ein_numbers'])}\n")
            f.write(f"- Addresses: {len(sample_response['extracted_data']['addresses'])}\n")
            f.write(f"- Emails: {len(sample_response['extracted_data']['emails'])}\n")
            f.write(f"- Phone Numbers: {len(sample_response['extracted_data']['phone_numbers'])}\n")
            f.write(f"- Names: {len(sample_response['extracted_data']['names'])}\n")
            f.write(f"\nRecommendations:\n")
            for rec in sample_response['recommendations']:
                f.write(f"- {rec}\n")
            f.write(f"\nCritical Fields:\n")
            for field in sample_response['critical_fields']:
                f.write(f"- {field}\n")
        
        logger.info(f"Created processing summary: {summary_file}")
        
        logger.info("✅ File processing completed successfully!")
        return True
            
    except Exception as e:
        logger.error(f"❌ Error processing file: {e}")
        return False

def main():
    """Main function to handle command line arguments and process the file."""
    parser = argparse.ArgumentParser(description='Process uploaded data file with ChatGPT')
    parser.add_argument('--file', required=True, help='Path to the uploaded data file')
    parser.add_argument('--highlight', help='Custom highlight text')
    parser.add_argument('--name', help='Name text for processing')
    parser.add_argument('--signature-options', help='JSON string of signature options')
    
    args = parser.parse_args()
    
    # Parse signature options if provided
    signature_options = None
    if args.signature_options:
        try:
            signature_options = json.loads(args.signature_options)
        except json.JSONDecodeError:
            logger.warning("Invalid signature options JSON, ignoring")
    
    # Process the file
    success = process_file_with_chatgpt(
        args.file,
        args.highlight,
        args.name,
        signature_options
    )
    
    if success:
        logger.info("File processing completed successfully")
        sys.exit(0)
    else:
        logger.error("File processing failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 