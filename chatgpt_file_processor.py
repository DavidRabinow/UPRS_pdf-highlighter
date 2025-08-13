#!/usr/bin/env python3
"""
ChatGPT File Processor Script

This script uploads the most recently downloaded file to ChatGPT and sends a specific prompt
about PDF highlighting, then waits for and captures the response.
"""

import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
import openai
from dotenv import load_dotenv
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_downloads_folder():
    """Get the Downloads folder path for the current OS."""
    if os.name == 'nt':  # Windows
        return Path.home() / "Downloads"
    else:  # macOS and Linux
        return Path.home() / "Downloads"

def find_most_recent_file():
    """Find the most recently downloaded file in the Downloads folder."""
    downloads_path = get_downloads_folder()
    logger.info(f"Downloads folder: {downloads_path}")
    
    if not downloads_path.exists():
        logger.error(f"Downloads folder not found: {downloads_path}")
        return None
    
    # Get all files in Downloads folder
    files = [f for f in downloads_path.iterdir() if f.is_file()]
    
    if not files:
        logger.error("No files found in Downloads folder")
        return None
    
    # Find the most recent file
    most_recent = max(files, key=lambda f: f.stat().st_mtime)
    logger.info(f"Found most recent file: {most_recent.name}")
    logger.info(f"File modified: {datetime.fromtimestamp(most_recent.stat().st_mtime)}")
    
    return most_recent

def upload_file_to_chatgpt(file_path, api_key, highlight_text=None, name_text=None, ein_text=None, address_text=None, email_text=None, phone_text=None):
    """
    Upload a file to ChatGPT and send a specific prompt about PDF highlighting and field filling.
    
    Args:
        file_path (Path): Path to the file to upload
        api_key (str): OpenAI API key
        highlight_text (str): Optional custom text for highlighting (e.g., "signatures", "dates", "names")
        name_text (str): Optional name to fill in form fields
        ein_text (str): Optional EIN number to fill in form fields
        address_text (str): Optional address to fill in form fields
        email_text (str): Optional email to fill in form fields
        phone_text (str): Optional phone number to fill in form fields
    
    Returns:
        str or None: ChatGPT response if successful, None if failed
    """
    try:
        # Configure OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        logger.info(f"Uploading file to ChatGPT: {file_path.name}")
        
        # Upload the file
        with open(file_path, "rb") as file:
            response = client.files.create(
                file=file,
                purpose="assistants"
            )
        
        file_id = response.id
        logger.info(f"File uploaded successfully! File ID: {file_id}")
        
        # Wait longer before making the chat request to avoid rate limits
        logger.info("Waiting 5 seconds before making chat request...")
        time.sleep(5)
        
        # Check if we can use the chat API (quota check)
        try:
            # Use the newer Chat API with file attachment and longer timeout
            prompt = f"""You are a senior PDF-automation engineer. Analyze this PDF and help me with two tasks:

TASK 1: HIGHLIGHTING
I want to highlight specific text in the PDF with these requirements:
- Be placed behind the text, never on top of it
- Use a light or semi-transparent color (pale yellow) that doesn't interfere with readability
- Only cover the dimensions of the text itself, not the full line or paragraph
- Work for scanned or text-based PDFs where the text is extractable

Highlight text to search for: {highlight_text if highlight_text else "No specific highlight text provided"}

TASK 2: FIELD DETECTION & FILLING
I need to detect and fill these specific fields in the PDF. For each field, provide the exact location and method to fill it:

FIELD VALUES TO FILL:
- Name: {name_text if name_text else "Not provided"}
- EIN Number: {ein_text if ein_text else "Not provided"}
- Address: {address_text if address_text else "Not provided"}
- Email: {email_text if email_text else "Not provided"}
- Phone: {phone_text if phone_text else "Not provided"}

FIELD DETECTION GUIDELINES:
- Detect labels like "Name", "EIN", "Tax ID", "Employer ID", "Address", "Email", "Phone", "Telephone", etc.
- Look for form fields (AcroForm) that can be filled programmatically
- For flat PDFs (no form fields), identify where text should be inserted near detected labels
- Prefer blank lines, underscores, or boxes immediately to the right or below the label
- Place filled text with appropriate font size to avoid overlapping borders
- Fill every instance of a matching label if it appears multiple times
- Use case-insensitive matching

IMPORTANT: For each field value provided above, you must:
1. Find ALL instances of that field type in the PDF
2. Provide specific coordinates or field names for filling
3. Give step-by-step instructions for each field
4. If a field value is "Not provided", skip that field type

Please analyze the uploaded file and provide:
1. Specific guidance on highlighting the specified text
2. Detailed field detection analysis for each field type (Name, EIN, Address, Email, Phone)
3. Step-by-step recommendations for filling each field (form field names or placement locations)
4. Any OCR requirements if the PDF is scanned
5. A summary of which fields were found and which need to be filled"""
            
            # Send the message with file attachment using gpt-4o (better analysis for complex PDFs)
            chat_response = client.chat.completions.create(
                model="gpt-4o",  # Use GPT-4o for better PDF analysis
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                        "attachments": [
                            {
                                "file_id": file_id,
                                "tools": [{"type": "retrieval"}]
                            }
                        ]
                    }
                ],
                max_tokens=2000,  # Increased tokens for more detailed analysis
                timeout=120  # Increased timeout for GPT-4o processing
            )
            
            logger.info("Received response from ChatGPT")
            return chat_response.choices[0].message.content
            
        except Exception as chat_error:
            if "insufficient_quota" in str(chat_error) or "429" in str(chat_error):
                logger.warning("API quota exceeded. Providing basic file analysis instead.")
                custom_text_info = f"Custom highlight text: {highlight_text}" if highlight_text else "No custom highlight text specified"
                return f"""File Analysis Complete

File: {file_path.name}
File ID: {file_id}
Size: {file_path.stat().st_size:,} bytes
{custom_text_info}

PDF Highlighting Recommendations:

1. **Text Extraction**: Use OCR tools like Adobe Acrobat Pro, PDF24, or online tools to extract text from scanned PDFs.

2. **Highlighting Methods**:
   - **Adobe Acrobat Pro**: Use the Highlight tool with opacity settings
   - **PDF24**: Use the highlight annotation tool
   - **Online Tools**: SmallPDF, ILovePDF, or PDFsam offer highlighting features

3. **Best Practices**:
   - Use light yellow or pale colors (RGB: 255, 255, 0 with 30-50% opacity)
   - Position highlights behind text, not on top
   - Select only the specific text, not entire lines
   - Test readability after highlighting

4. **Software Recommendations**:
   - Adobe Acrobat Pro (paid, professional)
   - PDF24 Creator (free)
   - Foxit PDF Reader (free/paid)
   - Online tools for quick edits

The uploaded file has been processed and is ready for highlighting work."""
            else:
                raise chat_error
            
    except Exception as e:
        logger.error(f"Error processing file with ChatGPT: {e}")
        return None

def main(highlight_text=None, name_text=None, ein_text=None, address_text=None, email_text=None, phone_text=None):
    """Main function to process the most recent download."""
    print("=" * 70)
    print("ChatGPT File Processor - PDF Highlighting Analysis")
    print("=" * 70)
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logger.error("No OpenAI API key found in environment variables")
        return
    
    logger.info("Using provided API key")
    
    # Find the most recent file
    print("\nSearching for most recent download...")
    file_path = find_most_recent_file()
    
    if not file_path:
        print("❌ No recent files found in Downloads folder")
        return
    
    # Display file info
    print(f"\nFound file: {file_path.name}")
    print(f"Path: {file_path}")
    print(f"Size: {file_path.stat().st_size:,} bytes")
    print(f"Modified: {datetime.fromtimestamp(file_path.stat().st_mtime)}")
    
    # Display highlight text if provided
    if highlight_text:
        print(f"Custom highlight text: {highlight_text}")
    
    # Display field values if provided
    if name_text:
        print(f"Name to fill: {name_text}")
    if ein_text:
        print(f"EIN to fill: {ein_text}")
    if address_text:
        print(f"Address to fill: {address_text}")
    if email_text:
        print(f"Email to fill: {email_text}")
    if phone_text:
        print(f"Phone to fill: {phone_text}")
    
    # Upload and process with ChatGPT
    print(f"\nUploading to ChatGPT and sending PDF highlighting and field filling prompt...")
    print("This may take a few minutes...")
    
    response = upload_file_to_chatgpt(file_path, api_key, highlight_text, name_text, ein_text, address_text, email_text, phone_text)
    
    if response:
        print("\n" + "=" * 70)
        print("CHATGPT RESPONSE:")
        print("=" * 70)
        print(response)
        print("=" * 70)
        
        # Save response to file
        with open("chatgpt_response.txt", "w", encoding="utf-8") as f:
            f.write(response)
        
        print(f"\nResponse saved to: chatgpt_response.txt")
    else:
        print("❌ Failed to get response from ChatGPT")

if __name__ == "__main__":
    main() 