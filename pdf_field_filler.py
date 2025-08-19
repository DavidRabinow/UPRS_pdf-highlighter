#!/usr/bin/env python3
"""
PDF Field Filler Script

This script takes ChatGPT's analysis and actually fills the PDF fields programmatically.
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
import fitz  # PyMuPDF
import re

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

def find_most_recent_pdf():
    """Find the most recently downloaded PDF file in the Downloads folder."""
    downloads_path = get_downloads_folder()
    logger.info(f"Downloads folder: {downloads_path}")
    
    if not downloads_path.exists():
        logger.error(f"Downloads folder not found: {downloads_path}")
        return None
    
    # Get all PDF files in Downloads folder
    pdf_files = [f for f in downloads_path.iterdir() if f.is_file() and f.suffix.lower() == '.pdf']
    
    if not pdf_files:
        logger.error("No PDF files found in Downloads folder")
        return None
    
    # Find the most recent PDF file
    most_recent = max(pdf_files, key=lambda f: f.stat().st_mtime)
    logger.info(f"Found most recent PDF: {most_recent.name}")
    
    return most_recent

def find_most_recent_folder():
    """Find the most recently created folder in the Downloads folder."""
    downloads_path = get_downloads_folder()
    logger.info(f"Downloads folder: {downloads_path}")
    
    if not downloads_path.exists():
        logger.error(f"Downloads folder not found: {downloads_path}")
        return None
    
    # Get all folders in Downloads folder
    folders = [f for f in downloads_path.iterdir() if f.is_dir()]
    
    if not folders:
        logger.error("No folders found in Downloads folder")
        return None
    
    # Find the most recent folder
    most_recent = max(folders, key=lambda f: f.stat().st_mtime)
    logger.info(f"Found most recent folder: {most_recent.name}")
    
    return most_recent

def get_pdfs_from_folder(folder_path):
    """Get all PDF files from a specific folder."""
    if not folder_path.exists():
        logger.error(f"Folder not found: {folder_path}")
        return []
    
    # Get all PDF files in the folder
    pdf_files = [f for f in folder_path.iterdir() if f.is_file() and f.suffix.lower() == '.pdf']
    
    if not pdf_files:
        logger.warning(f"No PDF files found in folder: {folder_path.name}")
        return []
    
    # Sort by modification time (newest first)
    pdf_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    logger.info(f"Found {len(pdf_files)} PDF files in folder: {folder_path.name}")
    for pdf_file in pdf_files:
        logger.info(f"  - {pdf_file.name}")
    
    return pdf_files

def rename_folder_to_completion(folder_path):
    """Rename the folder to 'completion' followed by a number."""
    if not folder_path.exists():
        logger.error(f"Folder not found: {folder_path}")
        return False
    
    downloads_path = get_downloads_folder()
    
    # Find the next available completion number
    completion_number = 1
    while True:
        new_name = f"completion{completion_number}"
        new_path = downloads_path / new_name
        
        if not new_path.exists():
            break
        completion_number += 1
    
    try:
        # Rename the folder
        new_path = folder_path.rename(new_path)
        logger.info(f"✅ Successfully renamed folder to: {new_name}")
        print(f"✅ Folder renamed to: {new_name}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to rename folder: {e}")
        print(f"❌ Failed to rename folder: {e}")
        return False

def list_all_pdfs():
    """List all PDF files in the Downloads folder."""
    downloads_path = get_downloads_folder()
    
    if not downloads_path.exists():
        print(f"Downloads folder not found: {downloads_path}")
        return
    
    # Get all PDF files in Downloads folder
    pdf_files = [f for f in downloads_path.iterdir() if f.is_file() and f.suffix.lower() == '.pdf']
    
    if not pdf_files:
        print("No PDF files found in Downloads folder")
        return
    
    print(f"\nPDF files in Downloads folder:")
    print("=" * 50)
    
    # Sort by modification time (newest first)
    pdf_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    for i, pdf_file in enumerate(pdf_files[:10], 1):  # Show top 10
        mod_time = pdf_file.stat().st_mtime
        from datetime import datetime
        mod_date = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{i:2d}. {pdf_file.name}")
        print(f"    Modified: {mod_date}")
        print()

def fill_pdf_fields(pdf_path, field_values):
    """
    Fill PDF fields with provided values.
    
    Args:
        pdf_path (Path): Path to the PDF file
        field_values (dict): Dictionary of field names and values to fill
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Filling PDF fields in: {pdf_path.name}")
        
        # Open the PDF with PyMuPDF for better field detection
        doc = fitz.open(str(pdf_path))
        
        # Create output filename
        output_path = pdf_path.parent / f"filled_{pdf_path.name}"
        
        # Try to fill form fields first (AcroForm)
        try:
            if hasattr(doc, 'is_form') and doc.is_form:
                logger.info("PDF has form fields - attempting to fill them")
                success = fill_form_fields(doc, field_values)
                if success:
                    doc.save(str(output_path))
                    doc.close()
                    logger.info(f"✅ Form fields filled successfully: {output_path}")
                    return True
        except Exception as e:
            logger.warning(f"Form field detection failed: {e}")
        
        # If no form fields or filling failed, try text insertion
        logger.info("Attempting text insertion method")
        success = insert_text_fields(doc, field_values)
        if success:
            doc.save(str(output_path))
            doc.close()
            logger.info(f"✅ Text fields inserted successfully: {output_path}")
            return True
        
        doc.close()
        logger.error("❌ Failed to fill PDF fields")
        return False
        
    except Exception as e:
        logger.error(f"Error filling PDF fields: {e}")
        return False

def fill_form_fields(doc, field_values):
    """Fill AcroForm fields in the PDF."""
    try:
        # Get form fields
        form = doc.get_form()
        fields = form.get_fields()
        
        logger.info(f"Found {len(fields)} form fields")
        
        # Enhanced field mapping based on the form images provided
        field_mapping = {
            'name': ['name', 'full_name', 'claimant_name', 'name_s', 'name_of_claimant', 'name_of_co_claimant'],
            'ein': ['ein', 'tax_id', 'employer_id', 'federal_employer_identification_number', 'social_security_fein', 'ssn_fein'],
            'address': ['address', 'mailing_address', 'current_mailing_address', 'street_address', 'present_mailing_address', 'current_address'],
            'email': ['email', 'email_address', 'emailaddress', 'claimant_email', 'co_claimant_email'],
            'phone': ['phone', 'telephone', 'phone_number', 'daytime_telephone_number', 'daytime_phone', 'home_phone', 'telephone_number']
        }
        
        filled_count = 0
        
        for our_field, potential_names in field_mapping.items():
            if our_field in field_values and field_values[our_field]:
                value = field_values[our_field]
                
                # Try to find matching form field
                for field_name in potential_names:
                    if field_name in fields:
                        try:
                            form.set_text(field_name, value)
                            logger.info(f"✅ Filled form field '{field_name}' with '{value}'")
                            filled_count += 1
                            break
                        except Exception as e:
                            logger.warning(f"Failed to fill form field '{field_name}': {e}")
                            continue
        
        logger.info(f"Successfully filled {filled_count} form fields")
        return filled_count > 0
        
    except Exception as e:
        logger.error(f"Error filling form fields: {e}")
        return False

def insert_text_fields(doc, field_values):
    """Insert text at specific locations in the PDF."""
    try:
        # Enhanced field patterns based on the form images provided
        field_patterns = {
            'email': [
                r'email\s+address', 
                r'email\s*[:\-]', 
                r'claimant\s+email',
                r'co-claimant\s+email',
                r'email',  # Simple email pattern
                r'contact\s+email',
                r'business\s+email'
            ],
            'phone': [
                r'daytime\s+phone', 
                r'phone\s+number', 
                r'telephone\s+number',
                r'home\s+phone',
                r'phone\s*[:\-]', 
                r'telephone\s*[:\-]',
                r'cell\s+phone',
                r'phone',  # Simple phone pattern
                r'contact\s+phone',
                r'business\s+phone',
                r'fax'
            ],
            'name': [
                r'name\s+of\s+claimant', 
                r'name\s+of\s+co-claimant',
                r'name[s]?\s+if\s+different\s+than\s+above',
                r'name\s+and\s+address', 
                r'your\s+name', 
                r'name[s]?\s*[:\-]', 
                r'claimant\s+name', 
                r'full\s+name',
                r'name',  # Simple name pattern
                r'contact\s+name',
                r'business\s+name',
                r'company\s+name',
                r'owner\s+name'
            ],
            'ein': [
                r'social\s+security\s*/\s*fein', 
                r'ein\s*[:\-]', 
                r'tax\s+id', 
                r'employer\s+identification', 
                r'ssn/fein', 
                r'social\s+security.*tax\s+identifier',
                r'claimant\'s\s+ssn',
                r'joint\s+claimant\'s\s+ssn',
                r'ein',  # Simple EIN pattern
                r'fein',
                r'tax\s+identification',
                r'employer\s+id'
            ],
            'address': [
                r'present\s+mailing\s+address', 
                r'current\s+mailing\s+address', 
                r'mailing\s+address', 
                r'address\s*[:\-]', 
                r'street\s+address', 
                r'current\s+address',
                r'city,\s+state,\s+zip',
                r'address',  # Simple address pattern
                r'business\s+address',
                r'contact\s+address',
                r'location',
                r'street'
            ]
        }
        
        # Track which fields we've already filled to avoid duplicates
        filled_fields = set()
        
        filled_count = 0
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            logger.info(f"Processing page {page_num + 1}")
            
            # Get text blocks on the page
            text_blocks = page.get_text("dict")["blocks"]
            
            # Debug: Print all text found on the page
            page_text = page.get_text("text").lower()
            logger.info(f"Page text contains: {page_text[:200]}...")
            
            for block in text_blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].lower()
                            
                            # Check if this text matches any field pattern
                            for field_name, patterns in field_patterns.items():
                                 if field_name in field_values and field_values[field_name]:
                                     # Skip if we've already filled this field type on this page
                                     field_key = f"{field_name}_{page_num}"
                                     if field_key in filled_fields:
                                         continue
                                         
                                     for pattern in patterns:
                                         if re.search(pattern, text):
                                             # Skip if this is "email address" but we're looking for generic "address"
                                             if field_name == 'address' and 'email' in text.lower():
                                                 logger.debug(f"Skipping 'email address' for generic address field")
                                                 continue
                                             
                                             # Skip if this is "phone" but we're looking for "email" or vice versa
                                             if field_name == 'email' and 'phone' in text.lower():
                                                 logger.debug(f"Skipping 'phone' field for email")
                                                 continue
                                             if field_name == 'phone' and 'email' in text.lower():
                                                 logger.debug(f"Skipping 'email' field for phone")
                                                 continue
                                             
                                             # Skip sensitive fields that shouldn't be filled automatically
                                             if 'social\s+security' in text.lower() or 'date\s+of\s+birth' in text.lower():
                                                 logger.debug(f"Skipping sensitive field: {text}")
                                                 continue
                                                 
                                             logger.info(f"✅ Found field '{field_name}' with pattern '{pattern}' in text: '{text}'")
                                             # Found a field label, try to insert text nearby
                                             value = field_values[field_name]
                                             
                                             # Calculate position for text insertion
                                             # Look for blank lines or underscores nearby
                                             success = insert_text_near_field(page, span, value, field_name)
                                             if success:
                                                 filled_count += 1
                                                 filled_fields.add(field_key)
                                                 logger.info(f"✅ Inserted '{value}' for {field_name} field")
                                                 break
                                         else:
                                             logger.debug(f"Pattern '{pattern}' not found in text: '{text}'")
        
        logger.info(f"Successfully inserted {filled_count} text fields")
        return filled_count > 0
        
    except Exception as e:
        logger.error(f"Error inserting text fields: {e}")
        return False

def insert_text_near_field(page, span, value, field_name):
    """Insert text near a detected field label."""
    try:
        # Get the position of the field label
        x, y = span["origin"]
        
        # Get the bounding box of the span
        bbox = span["bbox"]
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        
        # Enhanced positioning based on form layout analysis
        positions_to_try = [
            # To the right of the label (most common for forms) - slightly above the line
            (x + width + 20, y + height/2 - 2),
            # Slightly to the right and aligned with the label - slightly above
            (x + width + 15, y + height/2 - 2),
            # Far to the right (for forms with long input fields) - slightly above
            (x + 200, y + height/2 - 2),
            # For "Name and Address" fields, try the first line position - slightly above
            (x, y + height/2 - 2),
            # Below the label (fallback) - but still above any line
            (x, y + height + 5),
            # Slightly to the right and below - but above line
            (x + width + 10, y + height + 5),
            # For phone fields with format indicators, try to the right
            (x + width + 30, y + height/2 - 2),
            # For email fields, try further right
            (x + width + 50, y + height/2 - 2),
        ]
        
        for pos_x, pos_y in positions_to_try:
            # Check if there's space at this position
            text_rect = fitz.Rect(pos_x - 5, pos_y - 5, pos_x + 150, pos_y + 15)
            existing_text = page.get_text("text", clip=text_rect).strip()
            
            # Check for underscores or blank lines that indicate input fields
            has_underscores = page.get_text("text", clip=text_rect).count('_') > 0
            has_blank_line = len(existing_text.strip()) == 0
            
            # For blank input fields, we should be more lenient
            # If there's no existing text or very little text, it's likely a blank input field
            if not existing_text or has_underscores or has_blank_line or len(existing_text) < 5:
                # Insert the text with better visibility and positioning
                page.insert_text((pos_x, pos_y), value, fontsize=11, color=(0, 0, 0))
                logger.info(f"✅ Inserted '{value}' at position ({pos_x}, {pos_y}) for {field_name}")
                return True
        
        logger.warning(f"Could not find space to insert text for {field_name}")
        return False
        
    except Exception as e:
        logger.warning(f"Failed to insert text near field: {e}")
        return False

def fill_all_pdfs_in_folder(folder_path, field_values):
    """
    Fill all PDF files in a folder with provided values.
    
    Args:
        folder_path (Path): Path to the folder containing PDFs
        field_values (dict): Dictionary of field names and values to fill
    
    Returns:
        dict: Results for each PDF file
    """
    results = {}
    
    # Get all PDF files in the folder
    pdf_files = get_pdfs_from_folder(folder_path)
    
    if not pdf_files:
        logger.error(f"No PDF files found in folder: {folder_path.name}")
        return results
    
    logger.info(f"Processing {len(pdf_files)} PDF files in folder: {folder_path.name}")
    
    for i, pdf_file in enumerate(pdf_files, 1):
        logger.info(f"\n{'='*50}")
        logger.info(f"Processing PDF {i}/{len(pdf_files)}: {pdf_file.name}")
        logger.info(f"{'='*50}")
        
        try:
            # Fill the PDF fields
            success = fill_pdf_fields(pdf_file, field_values)
            results[pdf_file.name] = {
                'success': success,
                'path': str(pdf_file)
            }
            
            if success:
                logger.info(f"✅ Successfully filled: {pdf_file.name}")
            else:
                logger.warning(f"⚠️ Failed to fill: {pdf_file.name}")
                
        except Exception as e:
            logger.error(f"❌ Error processing {pdf_file.name}: {e}")
            results[pdf_file.name] = {
                'success': False,
                'error': str(e),
                'path': str(pdf_file)
            }
    
    # Summary
    successful = sum(1 for result in results.values() if result['success'])
    total = len(results)
    
    logger.info(f"\n{'='*70}")
    logger.info(f"SUMMARY: {successful}/{total} PDFs filled successfully")
    logger.info(f"{'='*70}")
    
    return results

def main():
    """Main function to fill PDF fields."""
    print("=" * 70)
    print("PDF Field Filler")
    print("=" * 70)
    
    # Get field values from command line arguments
    field_values = {}
    pdf_path = None
    folder_path = None
    process_folder = False
    
    if len(sys.argv) > 1:
        # Parse field values from command line
        i = 1
        while i < len(sys.argv):
            arg = sys.argv[i]
            
            if arg == "--list":
                # List all PDFs
                list_all_pdfs()
                return
            elif arg == "--process-folder":
                # Process most recent folder
                process_folder = True
                i += 1
            elif arg == "--folder" and i + 1 < len(sys.argv):
                # Specific folder path
                folder_path = Path(sys.argv[i + 1])
                i += 2
            elif arg == "--pdf" and i + 1 < len(sys.argv):
                # Specific PDF file path
                pdf_path = Path(sys.argv[i + 1])
                i += 2
            elif arg.startswith("--") and i + 1 < len(sys.argv):
                # Field value
                field_name = arg.replace('--', '')
                field_value = sys.argv[i + 1]
                field_values[field_name] = field_value
                i += 2
            else:
                i += 1
    
    # Determine what to process
    if process_folder:
        # Process most recent folder
        folder_path = find_most_recent_folder()
        if not folder_path:
            print("❌ No folder found in Downloads")
            return
        
        print(f"\nProcessing most recent folder: {folder_path.name}")
        print(f"Field values to fill: {field_values}")
        
        results = fill_all_pdfs_in_folder(folder_path, field_values)
        
        if results:
            successful = sum(1 for result in results.values() if result['success'])
            total = len(results)
            print(f"\n✅ Processed {successful}/{total} PDFs successfully!")
            
            # Rename the folder to completion
            print("\nRenaming folder to completion...")
            rename_folder_to_completion(folder_path)
        else:
            print("\n❌ No PDFs found in folder")
            
    elif folder_path is not None:
        # Process specific folder
        print(f"\nProcessing folder: {folder_path.name}")
        print(f"Field values to fill: {field_values}")
        
        results = fill_all_pdfs_in_folder(folder_path, field_values)
        
        if results:
            successful = sum(1 for result in results.values() if result['success'])
            total = len(results)
            print(f"\n✅ Processed {successful}/{total} PDFs successfully!")
        else:
            print("\n❌ No PDFs found in folder")
            
    elif pdf_path is not None:
        # Process specific PDF
        print(f"\nFound PDF: {pdf_path.name}")
        print(f"Field values to fill: {field_values}")
        
        success = fill_pdf_fields(pdf_path, field_values)
        
        if success:
            print("\n" + "=" * 70)
            print("✅ PDF fields filled successfully!")
            print("=" * 70)
            print(f"Check your Downloads folder for the filled PDF.")
        else:
            print("\n" + "=" * 70)
            print("❌ Failed to fill PDF fields")
            print("=" * 70)
    else:
        # Find the most recent PDF file and process it
        pdf_path = find_most_recent_pdf()
        if not pdf_path:
            print("❌ No PDF file found in Downloads")
            return
        
        print(f"\nProcessing most recent PDF: {pdf_path.name}")
        print(f"Field values to fill: {field_values}")
        
        success = fill_pdf_fields(pdf_path, field_values)
        
        if success:
            print("\n" + "=" * 70)
            print("✅ PDF fields filled successfully!")
            print("=" * 70)
            print(f"Check your Downloads folder for the filled PDF.")
        else:
            print("\n" + "=" * 70)
            print("❌ Failed to fill PDF fields")
            print("=" * 70)

if __name__ == "__main__":
    main()
