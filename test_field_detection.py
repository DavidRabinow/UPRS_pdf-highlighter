#!/usr/bin/env python3
"""
Test script to debug PDF field detection issues
"""

import fitz  # PyMuPDF
import re
import zipfile
import tempfile
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_field_detection(pdf_path):
    """Test field detection on a PDF file"""
    try:
        doc = fitz.open(str(pdf_path))
        logger.info(f"Testing field detection on: {pdf_path}")
        
        # Field patterns to test
        field_patterns = {
            'name': [
                # Generic name patterns - most flexible
                r'name[s]?',  # Simple "name" or "names"
                r'name[s]?\s*[:\-]',  # "name:" or "names:"
                r'name[s]?\s*[:\-]\s*',  # "name: " or "names: "
                
                # Specific form variations
                r'name[s]?\s+if\s+different\s+than\s+above',  # Exact match for the form
                r'name[s]?\s+if\s+different',  # Partial match
                r'name\s+of\s+claimant', 
                r'name\s+of\s+co-claimant',
                r'name\s+and\s+address', 
                r'your\s+name', 
                r'claimant\s+name', 
                r'full\s+name',
                r'legal\s+name',
                r'business\s+name',
                r'company\s+name',
                r'organization\s+name',
                r'entity\s+name',
                
                                 # First/Last/Middle name variations
                 r'first\s+name',
                 r'given\s+name',
                 r'family\s+name',
                 r'surname',
                 
                 # Applicant/Claimant variations
                 r'applicant\s+name',
                 r'claimant\s+name',
                 r'owner\s+name',
                 r'authorized\s+name',
                 
                 # Form field variations
                 r'name\s+\(first\)',
                 r'\(first\)',
                 
                 # Additional variations
                 r'printed\s+name',
                 r'signer\s+name',
                 r'contact\s+name',
                 r'primary\s+name',
                 r'secondary\s+name',
                 r'preferred\s+name'
            ],
            'phone': [
                r'phone',  # Simple "Phone" label
                r'phone\s*[:\-]',  # Phone with colon or dash
                r'daytime\s+phone', 
                r'phone\s+number', 
                r'telephone\s+number',
                r'home\s+phone',
                r'telephone\s*[:\-]',
                r'cell\s+phone'
            ],
            'dob': [
                r'date\s+of\s+birth',
                r'date\s+of\s+birth\s*[:\-]',  # Date of birth with colon or dash
                r'dob',
                r'dob\s*[:\-]',  # DOB with colon or dash
                r'birth\s+date',
                r'birthdate'
            ]
        }
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            logger.info(f"\n=== Page {page_num + 1} ===")
            
            # Get text blocks on the page
            text_blocks = page.get_text("dict")["blocks"]
            
            # Print all text found
            page_text = page.get_text("text")
            logger.info(f"Full page text:\n{page_text}")
            
            # Test each field pattern
            for field_name, patterns in field_patterns.items():
                logger.info(f"\n--- Testing {field_name} field ---")
                
                for block in text_blocks:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                text = span["text"].lower()
                                
                                for pattern in patterns:
                                    if re.search(pattern, text):
                                        logger.info(f"✅ MATCH: '{text}' matches pattern '{pattern}' for field '{field_name}'")
                                        logger.info(f"   Position: {span['origin']}")
                                        break
                                else:
                                    logger.debug(f"   No match: '{text}'")
        
        doc.close()
        
    except Exception as e:
        logger.error(f"Error testing field detection: {e}")

def extract_and_test_pdfs(zip_path):
    """Extract PDFs from ZIP and test field detection"""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            pdf_files = [f for f in zip_ref.namelist() if f.lower().endswith('.pdf')]
            
            if not pdf_files:
                logger.error(f"No PDF files found in {zip_path}")
                return
            
            logger.info(f"Found {len(pdf_files)} PDF files in {zip_path}")
            
            # Test all PDFs in the ZIP
            for pdf_name in pdf_files:
                logger.info(f"\n{'='*50}")
                logger.info(f"Testing PDF: {pdf_name}")
                logger.info(f"{'='*50}")
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    zip_ref.extract(pdf_name, temp_dir)
                    pdf_path = Path(temp_dir) / pdf_name
                    test_field_detection(pdf_path)
                
    except Exception as e:
        logger.error(f"Error extracting from ZIP: {e}")

if __name__ == "__main__":
    # Test with the most recent ZIP in the uploads folder
    uploads_dir = Path("uploads")
    if uploads_dir.exists():
        zip_files = list(uploads_dir.glob("*.zip"))
        if zip_files:
            # Get the most recent ZIP
            latest_zip = max(zip_files, key=lambda x: x.stat().st_mtime)
            logger.info(f"Testing with latest ZIP: {latest_zip}")
            extract_and_test_pdfs(latest_zip)
        else:
            logger.error("No ZIP files found in uploads directory")
    else:
        logger.error("Uploads directory not found")
