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

def run_pdf_highlighter(highlight_text=None):
    """Run the PDF highlighter to create highlighted files."""
    try:
        print("\n" + "=" * 70)
        print("CREATING HIGHLIGHTED FILES...")
        print("=" * 70)
        
        # Prepare command with highlight text if provided
        cmd = ["python", "pdf_highlighter.py"]
        if highlight_text:
            cmd.append(highlight_text)
            print(f"Using custom highlight text: '{highlight_text}'")
        
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
    
    # Run the ChatGPT processing
    print("=" * 70)
    print("STEP 1: CHATGPT PROCESSING")
    print("=" * 70)
    main(highlight_text)
    
    # Run the PDF highlighter to create highlighted files
    print("\n" + "=" * 70)
    print("STEP 2: CREATING HIGHLIGHTED FILES")
    print("=" * 70)
    success = run_pdf_highlighter(highlight_text)
    
    if success:
        print("\n" + "=" * 70)
        print("✅ COMPLETE: ChatGPT analysis + Highlighted files created!")
        print("=" * 70)
        print("Check your Downloads folder for the highlighted ZIP file.")
    else:
        print("\n" + "=" * 70)
        print("⚠️  PARTIAL: ChatGPT analysis completed, but file highlighting failed.")
        print("=" * 70) 