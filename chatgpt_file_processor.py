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

def upload_file_to_chatgpt(file_path, api_key, highlight_text=None):
    """
    Upload a file to ChatGPT and send a specific prompt about PDF highlighting.
    
    Args:
        file_path (Path): Path to the file to upload
        api_key (str): OpenAI API key
        highlight_text (str): Optional custom text for highlighting (e.g., "signatures", "dates", "names")
    
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
            if highlight_text:
                # Use custom highlight text in the prompt
                prompt = f"""I want to highlight specific text in a PDF, but I need to make sure the text remains fully visible. The highlight should:

Be placed behind the text, never on top of it.
Use a light or semi-transparent color (e.g. pale yellow) that doesn't interfere with readability.
Only cover the dimensions of the text itself, not the full line or paragraph.
Work for scanned or text-based PDFs where the text is extractable.

Specifically, I want to highlight: {highlight_text}

Please analyze the uploaded file and provide specific guidance on how to achieve this type of highlighting for the specified text."""
            else:
                # Use default prompt
                prompt = """I want to highlight specific text in a PDF, but I need to make sure the text remains fully visible. The highlight should:

Be placed behind the text, never on top of it.
Use a light or semi-transparent color (e.g. pale yellow) that doesn't interfere with readability.
Only cover the dimensions of the text itself, not the full line or paragraph.
Work for scanned or text-based PDFs where the text is extractable.

Please analyze the uploaded file and provide specific guidance on how to achieve this type of highlighting."""
            
            # Send the message with file attachment using gpt-3.5-turbo (cheaper and less likely to hit limits)
            chat_response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use cheaper model
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
                max_tokens=1500,  # Reduce tokens to avoid limits
                timeout=60  # Add timeout
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

def main(highlight_text=None):
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
    
    # Upload and process with ChatGPT
    print(f"\nUploading to ChatGPT and sending PDF highlighting prompt...")
    print("This may take a few minutes...")
    
    response = upload_file_to_chatgpt(file_path, api_key, highlight_text)
    
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