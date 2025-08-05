#!/usr/bin/env python3
"""
Upload Most Recent Download to OpenAI API

This script locates the most recently downloaded file in the user's Downloads folder
and uploads it to the OpenAI API using the openai Python SDK.
"""

import os
import time
from pathlib import Path
from datetime import datetime
import openai
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_downloads_folder():
    """
    Get the Downloads folder path for the current operating system.
    
    Returns:
        Path: Path to the Downloads folder
    """
    if os.name == 'nt':  # Windows
        downloads_path = Path.home() / "Downloads"
    else:  # macOS and Linux
        downloads_path = Path.home() / "Downloads"
    
    return downloads_path

def find_most_recent_file(downloads_path, max_age_minutes=10):
    """
    Find the most recently downloaded file in the Downloads folder.
    
    Args:
        downloads_path (Path): Path to Downloads folder
        max_age_minutes (int): Maximum age of files to consider (in minutes)
    
    Returns:
        Path or None: Path to the most recent file, or None if not found
    """
    if not downloads_path.exists():
        logger.error(f"Downloads folder not found: {downloads_path}")
        return None
    
    # Calculate cutoff time (files older than this won't be considered)
    cutoff_time = time.time() - (max_age_minutes * 60)
    
    most_recent_file = None
    most_recent_time = 0
    
    try:
        # Iterate through all files in Downloads folder
        for file_path in downloads_path.iterdir():
            if file_path.is_file():
                # Get file modification time
                file_time = file_path.stat().st_mtime
                
                # Only consider files created/modified recently
                if file_time > cutoff_time and file_time > most_recent_time:
                    most_recent_file = file_path
                    most_recent_time = file_time
        
        if most_recent_file:
            logger.info(f"Found most recent file: {most_recent_file.name}")
            logger.info(f"File modified: {datetime.fromtimestamp(most_recent_time)}")
            return most_recent_file
        else:
            logger.warning(f"No recent files found in Downloads folder (checked last {max_age_minutes} minutes)")
            return None
            
    except Exception as e:
        logger.error(f"Error searching Downloads folder: {e}")
        return None

def upload_to_openai(file_path, api_key):
    """
    Upload a file to the OpenAI API.
    
    Args:
        file_path (Path): Path to the file to upload
        api_key (str): OpenAI API key
    
    Returns:
        str or None: OpenAI file ID if successful, None if failed
    """
    try:
        # Configure OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        logger.info(f"Uploading file to OpenAI: {file_path.name}")
        
        # Upload the file
        with open(file_path, "rb") as file:
            response = client.files.create(
                file=file,
                purpose="assistants"
            )
        
        logger.info(f"File uploaded successfully!")
        logger.info(f"OpenAI File ID: {response.id}")
        logger.info(f"File name: {response.filename}")
        logger.info(f"File size: {response.bytes} bytes")
        
        return response.id
        
    except Exception as e:
        logger.error(f"Error uploading file to OpenAI: {e}")
        return None

def main():
    """
    Main function to locate and upload the most recent download.
    """
    print("=" * 60)
    print("Upload Most Recent Download to OpenAI API")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment or use the provided one
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        # Use the provided API key as fallback
        api_key = "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"
        logger.info("Using provided API key")
    else:
        logger.info("Using API key from .env file")
    
    # Get Downloads folder
    downloads_path = get_downloads_folder()
    logger.info(f"Downloads folder: {downloads_path}")
    
    # Find most recent file
    print("\n🔍 Searching for most recent download...")
    most_recent_file = find_most_recent_file(downloads_path, max_age_minutes=10)
    
    if not most_recent_file:
        print("❌ No recent files found in Downloads folder")
        print("   Make sure you have downloaded a file in the last 10 minutes")
        return
    
    # Display file information
    print(f"\n📁 Found file: {most_recent_file.name}")
    print(f"📂 Path: {most_recent_file}")
    print(f"📏 Size: {most_recent_file.stat().st_size:,} bytes")
    print(f"🕒 Modified: {datetime.fromtimestamp(most_recent_file.stat().st_mtime)}")
    
    # Confirm upload
    print(f"\n🚀 Uploading to OpenAI API...")
    
    # Upload to OpenAI
    file_id = upload_to_openai(most_recent_file, api_key)
    
    if file_id:
        print(f"\n✅ Upload successful!")
        print(f"📋 OpenAI File ID: {file_id}")
        print(f"📄 File name: {most_recent_file.name}")
        print(f"\n💡 You can now use this file ID with OpenAI's API")
    else:
        print(f"\n❌ Upload failed!")
        print("   Check your API key and internet connection")

if __name__ == "__main__":
    main() 