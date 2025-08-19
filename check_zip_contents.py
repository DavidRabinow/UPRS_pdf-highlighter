#!/usr/bin/env python3
"""
Check ZIP file contents
"""

import zipfile
from pathlib import Path

def check_zip_contents():
    """Check what's in the most recent highlighted_files ZIP."""
    
    downloads_path = Path.home() / "Downloads"
    zip_file_path = downloads_path / "highlighted_files_78b7ae5660cdde3f8450085bcaa824db.zip"
    
    if not zip_file_path.exists():
        print(f"ERROR: ZIP file not found: {zip_file_path}")
        return
    
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zf:
            all_files = zf.namelist()
            pdf_files = [name for name in all_files if name.lower().endswith('.pdf')]
            
            print(f"ZIP file: {zip_file_path.name}")
            print(f"Total files: {len(all_files)}")
            print(f"PDF files: {len(pdf_files)}")
            print("\nAll files:")
            for file in all_files:
                print(f"  - {file}")
            
            print(f"\nPDF files:")
            for pdf in pdf_files:
                print(f"  - {pdf}")
                
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_zip_contents()
