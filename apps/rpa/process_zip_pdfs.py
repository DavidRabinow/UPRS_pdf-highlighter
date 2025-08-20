#!/usr/bin/env python3
"""
Script to extract ZIP file and process PDFs inside it
"""

import zipfile
import tempfile
import shutil
import os
import subprocess
import random
import string
from pathlib import Path
from datetime import datetime

def generate_random_folder_name():
    """Generate a random folder name with letters and numbers."""
    # Generate 8 random characters (letters and numbers)
    random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"filled_pdfs_{random_chars}"

def find_most_recent_highlighted_zip():
    """Find the most recent highlighted_files ZIP file in Downloads folder."""
    downloads_path = Path.home() / "Downloads"
    
    # Get all highlighted_files ZIP files in Downloads
    zip_files = list(downloads_path.glob("highlighted_files_*.zip"))
    
    if not zip_files:
        print("ERROR: No highlighted_files ZIP files found in Downloads folder")
        return None
    
    # Sort by modification time (most recent first)
    zip_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    most_recent = zip_files[0]
    print(f"Found most recent highlighted_files ZIP: {most_recent.name}")
    print(f"Modified: {datetime.fromtimestamp(most_recent.stat().st_mtime)}")
    
    return most_recent

def process_zip_pdfs(zip_path, field_values):
    """Extract ZIP file and process PDFs inside it."""
    
    print("=" * 70)
    print("ZIP PDF Processor")
    print("=" * 70)
    
    zip_path = Path(zip_path)
    if not zip_path.exists():
        print(f"ERROR: ZIP file not found: {zip_path}")
        return False
    
    print(f"Processing ZIP file: {zip_path.name}")
    print(f"Field values: {field_values}")
    
    # Create output folder in Downloads with random name
    downloads_path = Path.home() / "Downloads"
    output_folder = downloads_path / generate_random_folder_name()
    output_folder.mkdir(exist_ok=True)
    print(f"Output folder: {output_folder}")
    
    # Create temporary directory for extraction
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        print(f"Extracting to temporary directory: {temp_path}")
        
        # Extract ZIP file
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_path)
            print(f"SUCCESS: Extracted {len(zip_ref.namelist())} files")
        except Exception as e:
            print(f"ERROR: Failed to extract ZIP file: {e}")
            return False
        
        # Find PDF files in extracted directory
        pdf_files = list(temp_path.rglob("*.pdf"))
        if not pdf_files:
            print("WARNING: No PDF files found in ZIP")
            return False
        
        print(f"Found {len(pdf_files)} PDF files to process")
        
        # Process each PDF file
        success_count = 0
        for pdf_file in pdf_files:
            print(f"\nProcessing: {pdf_file.name}")
            
            # Build command for pdf_field_filler.py with more comprehensive field detection
            cmd = ["python", "pdf_field_filler.py", "--pdf", str(pdf_file)]
            
            # Add field values
            if field_values.get('name'):
                cmd.extend(["--name", field_values['name']])
            if field_values.get('ein'):
                cmd.extend(["--ein", field_values['ein']])
            if field_values.get('address'):
                cmd.extend(["--address", field_values['address']])
            if field_values.get('email'):
                cmd.extend(["--email", field_values['email']])
            if field_values.get('phone'):
                cmd.extend(["--phone", field_values['phone']])
            
            # Run the PDF filler
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)  # Increased timeout
                
                # Check if filled PDF was created (regardless of return code due to Unicode error)
                filled_pdf = temp_path / f"filled_{pdf_file.name}"
                if filled_pdf.exists():
                    print(f"SUCCESS: Processed {pdf_file.name}")
                    success_count += 1
                    
                    # Copy filled PDF to output folder
                    output_pdf = output_folder / f"filled_{pdf_file.name}"
                    shutil.copy2(filled_pdf, output_pdf)
                    print(f"SUCCESS: Saved filled PDF to: {output_pdf}")
                else:
                    print(f"WARNING: No filled PDF created for {pdf_file.name}")
                    print("This might be because:")
                    print("  - The PDF doesn't contain fillable form fields")
                    print("  - The form fields have different names than expected")
                    print("  - The fields are on different pages")
                    
                    # Copy the original PDF anyway so user can see what was processed
                    output_pdf = output_folder / f"original_{pdf_file.name}"
                    shutil.copy2(pdf_file, output_pdf)
                    print(f"Copied original PDF to: {output_pdf}")
                        
            except Exception as e:
                print(f"ERROR: Exception processing {pdf_file.name}: {e}")
        
        print(f"\n" + "=" * 70)
        print(f"Processing complete: {success_count}/{len(pdf_files)} PDFs processed successfully")
        print(f"All files saved to: {output_folder}")
        print("=" * 70)
        
        return success_count > 0

def main():
    """Main function to process the ZIP file."""
    
    # Find the most recent highlighted_files ZIP file automatically
    zip_path = find_most_recent_highlighted_zip()
    if not zip_path:
        return
    
    # Field values to fill
    field_values = {
        'name': 'John Doe',
        'ein': '12-3456789',
        'address': '123 Main Street',
        'email': 'john.doe@example.com',
        'phone': '555-123-4567'
    }
    
    # Process the ZIP file
    success = process_zip_pdfs(zip_path, field_values)
    
    if success:
        print("\nSUCCESS: ZIP processing completed!")
    else:
        print("\nWARNING: Some PDFs may not have been fillable forms")

if __name__ == "__main__":
    main()
