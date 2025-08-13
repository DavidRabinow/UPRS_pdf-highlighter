#!/usr/bin/env python3
"""
ChatGPT File Processor with Custom Highlight Text

This script uploads the most recently downloaded file to ChatGPT and sends a custom prompt
about PDF highlighting based on user-specified text, then creates highlighted files.
"""

import sys
import os
import subprocess
from chatgpt_file_processor import main

def run_pdf_highlighter(highlight_text=None, name_text=None, ein_text=None, address_text=None, email_text=None, phone_text=None, signature_options=None):
    """Run the PDF highlighter to create highlighted files."""
    try:
        print("\n" + "=" * 70)
        print("CREATING HIGHLIGHTED FILES...")
        print("=" * 70)
        
        # Prepare command with highlight text, name text, and signature options if provided
        cmd = ["python", "pdf_highlighter.py"]
        if highlight_text:
            cmd.append(highlight_text)
            print(f"Using custom highlight text: '{highlight_text}'")
        
        if name_text:
            cmd.append("--name")
            cmd.append(name_text)
            print(f"Using name text: '{name_text}'")
        
        if ein_text:
            cmd.append("--ein")
            cmd.append(ein_text)
            print(f"Using EIN text: '{ein_text}'")
        
        if address_text:
            cmd.append("--address")
            cmd.append(address_text)
            print(f"Using address text: '{address_text}'")
        
        if email_text:
            cmd.append("--email")
            cmd.append(email_text)
            print(f"Using email text: '{email_text}'")
        
        if phone_text:
            cmd.append("--phone")
            cmd.append(phone_text)
            print(f"Using phone text: '{phone_text}'")
        
        if signature_options:
            cmd.append("--signature-options")
            cmd.append(signature_options)
            print(f"Using signature options: '{signature_options}'")
        
        # Run the PDF highlighter script
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Highlighted files created successfully!")
            print(f"Processing details: {result.stdout}")
            return True
        else:
            print(f"❌ PDF highlighting failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running PDF highlighter: {e}")
        return False

if __name__ == "__main__":
    # Get highlight text from command line argument
    highlight_text = None
    if len(sys.argv) > 1:
        highlight_text = sys.argv[1]
    
    # Get name text from command line arguments
    name_text = None
    if len(sys.argv) > 3 and sys.argv[2] == "--name":
        name_text = sys.argv[3]
    
    # Get EIN text from command line arguments
    ein_text = None
    if len(sys.argv) > 5 and sys.argv[4] == "--ein":
        ein_text = sys.argv[5]
    
    # Get address text from command line arguments
    address_text = None
    if len(sys.argv) > 7 and sys.argv[6] == "--address":
        address_text = sys.argv[7]
    
    # Get email text from command line arguments
    email_text = None
    if len(sys.argv) > 9 and sys.argv[8] == "--email":
        email_text = sys.argv[9]
    
    # Get phone text from command line arguments
    phone_text = None
    if len(sys.argv) > 11 and sys.argv[10] == "--phone":
        phone_text = sys.argv[11]
    
    # Get signature options from command line arguments
    signature_options = None
    if len(sys.argv) > 13 and sys.argv[12] == "--signature-options":
        signature_options = sys.argv[13]
    
    # Run the ChatGPT processing
    print("=" * 70)
    print("STEP 1: CHATGPT PROCESSING")
    print("=" * 70)
    main(highlight_text, name_text, ein_text, address_text, email_text, phone_text)
    
    # Run the PDF highlighter to create highlighted files
    print("\n" + "=" * 70)
    print("STEP 2: CREATING HIGHLIGHTED FILES")
    print("=" * 70)
    success = run_pdf_highlighter(highlight_text, name_text, ein_text, address_text, email_text, phone_text, signature_options)
    
    if success:
        print("\n" + "=" * 70)
        print("✅ COMPLETE: ChatGPT analysis + Highlighted files created!")
        print("=" * 70)
        print("Check your Downloads folder for the highlighted ZIP file.")
    else:
        print("\n" + "=" * 70)
        print("⚠️  PARTIAL: ChatGPT analysis completed, but file highlighting failed.")
        print("=" * 70) 