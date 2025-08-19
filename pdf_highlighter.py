#!/usr/bin/env python3
"""
PDF Highlighter Script

This script extracts PDFs from ZIP files, adds highlights using Python libraries,
and creates highlighted versions that are re-zipped for download.
"""

import os
import logging
from pathlib import Path
from datetime import datetime
import zipfile
import shutil
import tempfile
from typing import List, Tuple, Optional

# PDF processing libraries
try:
    import PyPDF2
    from PyPDF2 import PdfReader, PdfWriter
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

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
    
    # Get all files in Downloads folder, excluding already highlighted files
    files = [f for f in downloads_path.iterdir() if f.is_file() and not f.name.startswith('highlighted_')]
    
    if not files:
        logger.error("No files found in Downloads folder")
        return None
    
    # Find the most recent file
    most_recent = max(files, key=lambda f: f.stat().st_mtime)
    logger.info(f"Found most recent file: {most_recent.name}")
    logger.info(f"File modified: {datetime.fromtimestamp(most_recent.stat().st_mtime)}")
    
    return most_recent

def check_pdf_libraries():
    """Check which PDF processing libraries are available."""
    libraries = []
    
    if PYPDF2_AVAILABLE:
        libraries.append("PyPDF2")
    if PYMUPDF_AVAILABLE:
        libraries.append("PyMuPDF")
    
    if not libraries:
        logger.error("No PDF processing libraries found!")
        logger.info("Installing required libraries...")
        return False
    
    logger.info(f"Available PDF libraries: {', '.join(libraries)}")
    return True

def extract_zip_file(zip_path: Path) -> Path:
    """
    Extract a ZIP file and return the extraction directory.
    
    Args:
        zip_path (Path): Path to the ZIP file
    
    Returns:
        Path: Path to the extraction directory
    """
    try:
        # Create extraction directory
        extract_dir = zip_path.parent / f"extracted_{zip_path.stem}"
        extract_dir.mkdir(exist_ok=True)
        
        # Extract ZIP file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        logger.info(f"Extracted ZIP to: {extract_dir}")
        return extract_dir
        
    except Exception as e:
        logger.error(f"Error extracting ZIP file: {e}")
        raise

def find_pdf_files(directory: Path) -> List[Path]:
    """
    Find all PDF files in a directory and subdirectories.
    
    Args:
        directory (Path): Directory to search
    
    Returns:
        List[Path]: List of PDF file paths
    """
    pdf_files = []
    for file_path in directory.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() == '.pdf':
            pdf_files.append(file_path)
    
    logger.info(f"Found {len(pdf_files)} PDF files")
    return pdf_files

def fill_name_fields(doc, name_text: str):
    """
    Fill in name fields in a PDF document.
    
    Args:
        doc: PyMuPDF document object
        name_text (str): Name to fill in the fields
    """
    try:
        # Track filled fields to avoid duplicates
        filled_fields = set()
        
        # Process each page
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Get text blocks to find name fields
            text_blocks = page.get_text("dict")["blocks"]
            
            for block in text_blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].lower().strip()
                            
                            # Look for name field indicators (both simple and complex patterns)
                            name_indicators = [
                                # Simple patterns with colons
                                "name:", "name :", "name(s):", "name(s) :", "full name:", "full name :",
                                "applicant name:", "applicant name :", "signer name:", "signer name :",
                                "printed name:", "printed name :", "legal name:", "legal name :",
                                "business name:", "business name :", "company name:", "company name :",
                                "entity name:", "entity name :", "organization name:", "organization name :",
                                
                                # Complex patterns without colons (like form fields)
                                "name (last)", "name (first)", "name (middle)", "name (maiden)",
                                "(last)", "(first)", "(middle)", "(maiden)",
                                "last name", "first name", "middle name", "maiden name",
                                "claimant name", "owner name", "additional owner"
                            ]
                            
                            # Check if this text matches a name indicator (exact match or contains the pattern)
                            should_fill = False
                            matched_indicator = None
                            
                            for indicator in name_indicators:
                                # For simple patterns with colons, use exact match or ends with
                                if ":" in indicator:
                                    if text == indicator or text.endswith(indicator):
                                        should_fill = True
                                        matched_indicator = indicator
                                        break
                                # For complex patterns without colons, check if text contains the pattern
                                else:
                                    if indicator in text or text == indicator:
                                        should_fill = True
                                        matched_indicator = indicator
                                        break
                            
                            if should_fill:
                                # Found a name field, check if already filled
                                field_key = f"{page_num}_{matched_indicator}"
                                if field_key in filled_fields:
                                    logger.info(f"Skipping already filled field '{matched_indicator}'")
                                    continue
                                
                                # Check if there's already text after the name field
                                rect = fitz.Rect(span["bbox"])
                                check_area = fitz.Rect(
                                    rect.x1 + 2,  # Right after the name field
                                    rect.y0,      # Same vertical position
                                    rect.x1 + 200, # Extend horizontally
                                    rect.y1       # Same height
                                )
                                
                                # Get text in the area where we would fill the name
                                existing_text = page.get_text("text", clip=check_area).strip()
                                
                                # If there's already text there, skip this field
                                if existing_text:
                                    logger.info(f"Skipping field '{matched_indicator}' - already has text: '{existing_text}'")
                                    continue
                                
                                # Found a name field, try to fill it
                                try:
                                    # Calculate position for the name text
                                    # Position it slightly to the right of the name field
                                    x_pos = rect.x1 + 5  # Slightly to the right
                                    y_pos = rect.y0 + (rect.y1 - rect.y0) / 2  # Center vertically
                                    
                                    # Insert plain text (not an annotation)
                                    page.insert_text(
                                        point=(x_pos, y_pos),
                                        text=name_text,
                                        fontsize=span.get("size", 12),  # Match font size
                                        color=(0, 0, 0)  # Black text
                                    )
                                    
                                    # Mark this field as filled
                                    filled_fields.add(field_key)
                                    logger.info(f"Filled name field '{matched_indicator}' with '{name_text}'")
                                    break  # Found and filled this field, move to next
                                    
                                except Exception as e:
                                    logger.warning(f"Could not fill name field '{matched_indicator}': {e}")
                                    continue
                            
                            # Also look for very short text that might be just "name:" or similar
                            if len(text) <= 15 and text in name_indicators:
                                field_key = f"{page_num}_{text}"
                                if field_key in filled_fields:
                                    logger.info(f"Skipping already filled short field '{text}'")
                                    continue
                                
                                try:
                                    # Check if there's empty space after this text
                                    rect = fitz.Rect(span["bbox"])
                                    
                                    # Check if there's already text after the name field
                                    check_area = fitz.Rect(
                                        rect.x1 + 2,  # Right after the text
                                        rect.y0,      # Same vertical position
                                        rect.x1 + 200, # Extend horizontally
                                        rect.y1       # Same height
                                    )
                                    
                                    # Get text in the area where we would fill the name
                                    existing_text = page.get_text("text", clip=check_area).strip()
                                    
                                    # If there's already text there, skip this field
                                    if existing_text:
                                        logger.info(f"Skipping short field '{text}' - already has text: '{existing_text}'")
                                        continue
                                    
                                    # Calculate position for the name text
                                    x_pos = rect.x1 + 2  # Right after the text
                                    y_pos = rect.y0 + (rect.y1 - rect.y0) / 2  # Center vertically
                                    
                                    # Insert plain text (not an annotation)
                                    page.insert_text(
                                        point=(x_pos, y_pos),
                                        text=name_text,
                                        fontsize=span.get("size", 12),  # Match font size
                                        color=(0, 0, 0)  # Black text
                                    )
                                    
                                    # Mark this field as filled
                                    filled_fields.add(field_key)
                                    logger.info(f"Filled short name field with '{name_text}'")
                                    
                                except Exception as e:
                                    logger.warning(f"Could not fill short name field: {e}")
                                    continue
                                    
    except Exception as e:
        logger.error(f"Error filling name fields: {e}")

def analyze_pdf_structure(pdf_path: Path) -> dict:
    """
    Analyze the text structure of a PDF to understand how text is organized.
    This helps debug why highlighting works differently across PDF formats.
    
    Args:
        pdf_path (Path): Path to the PDF file
    
    Returns:
        dict: Analysis results including text spans, fonts, and positioning
    """
    try:
        doc = fitz.open(str(pdf_path))
        analysis = {
            'total_pages': len(doc),
            'text_spans': [],
            'fonts_used': set(),
            'text_positions': [],
            'sample_texts': []
        }
        
        for page_num in range(min(len(doc), 3)):  # Analyze first 3 pages
            page = doc[page_num]
            text_blocks = page.get_text("dict")["blocks"]
            
            for block in text_blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if text:  # Only analyze non-empty text
                                analysis['text_spans'].append({
                                    'text': text,
                                    'font': span.get('font', 'unknown'),
                                    'size': span.get('size', 0),
                                    'bbox': span.get('bbox', []),
                                    'page': page_num
                                })
                                analysis['fonts_used'].add(span.get('font', 'unknown'))
                                analysis['text_positions'].append(span.get('bbox', []))
                                
                                # Collect sample texts for analysis
                                if len(analysis['sample_texts']) < 20:  # Limit samples
                                    analysis['sample_texts'].append(text)
        
        doc.close()
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing PDF structure: {e}")
        return {}

def get_highlighting_profile(profile_name: str = None) -> dict:
    """
    Get highlighting profiles for different form types.
    These profiles define what should be highlighted for each form type.
    
    Args:
        profile_name (str): Name of the profile to use
    
    Returns:
        dict: Profile with keywords and settings
    """
    profiles = {
        "notary": {
            "keywords": [
                "notary",
                "notary public",
                "notary signature", 
                "sworn and subscribed",
                "before me",
                "personally appeared"
            ],
            "exclude_patterns": [
                "commission expires",  # This is just a label, not a field to highlight
                "my commission expires",
                "commission expires on",
                "expires on",
                "expires:",
                "expires :"
            ],
            "description": "Highlights notary-related fields and language"
        },
        "signature": {
            "keywords": [
                "signature",
                "signature of claimant",
                "signature of co-claimant",
                "printed name",
                "date"
            ],
            "exclude_patterns": [
                "signature line",
                "signature block",
                "signature area"
            ],
            "description": "Highlights signature fields and dates"
        },
        "claimant": {
            "keywords": [
                "claimant",
                "claimant name",
                "printed name",
                "title",
                "state of",
                "county of"
            ],
            "exclude_patterns": [
                "claimant information",
                "claimant section"
            ],
            "description": "Highlights claimant information fields"
        },
        "affidavit": {
            "keywords": [
                "affidavit",
                "sworn",
                "perjury",
                "true",
                "correct",
                "full",
                "certify"
            ],
            "exclude_patterns": [
                "affidavit section",
                "affidavit block"
            ],
            "description": "Highlights affidavit language and certifications"
        },
        "comprehensive": {
            "keywords": [
                "notary",
                "notary public",
                "notary signature",
                "signature",
                "signature of claimant",
                "signature of co-claimant",
                "printed name",
                "date",
                "claimant",
                "affidavit",
                "sworn",
                "perjury"
            ],
            "exclude_patterns": [
                "commission expires",
                "my commission expires",
                "signature line",
                "signature block"
            ],
            "description": "Comprehensive highlighting for all important fields"
        }
    }
    
    if profile_name and profile_name in profiles:
        return profiles[profile_name]
    else:
        # Return default profile
        return {
            "keywords": ["signature", "notary", "claimant", "date"],
            "exclude_patterns": ["commission expires", "signature line"],
            "description": "Default highlighting profile"
        }

def highlight_pdf_pymupdf(pdf_path: Path, output_path: Path, highlight_text: str = None, name_text: str = None, profile: str = None, signature_options: str = None) -> bool:
    """
    Add highlights to a PDF using PyMuPDF.
    
    Args:
        pdf_path (Path): Path to input PDF
        output_path (Path): Path to output highlighted PDF
        highlight_text (str): Custom text to highlight (e.g., "signatures", "dates", "names")
        name_text (str): Name to fill in PDF form fields
        profile (str): Profile name for predefined highlighting rules
        signature_options (str): JSON string of signature options from checkboxes
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Open the PDF
        doc = fitz.open(str(pdf_path))
        
        # Get highlighting profile if specified
        if profile:
            profile_data = get_highlighting_profile(profile)
            if highlight_text:
                # Combine custom text with profile keywords
                custom_keywords = [kw.strip().lower() for kw in highlight_text.split(',')]
                profile_keywords = profile_data.get('keywords', [])
                keywords = list(set(custom_keywords + profile_keywords))
                exclude_patterns = profile_data.get('exclude_patterns', [])
                logger.info(f"Using profile '{profile}' + custom keywords: {keywords}")
                logger.info(f"Exclude patterns: {exclude_patterns}")
            else:
                keywords = profile_data.get('keywords', [])
                exclude_patterns = profile_data.get('exclude_patterns', [])
                logger.info(f"Using profile '{profile}': {keywords}")
                logger.info(f"Exclude patterns: {exclude_patterns}")
        elif highlight_text:
            # Use custom highlight text
            keywords = [kw.strip().lower() for kw in highlight_text.split(',')]
            exclude_patterns = []
            logger.info(f"Using custom keywords: {keywords}")
        else:
            # Use default keywords
            keywords = ["signature of claimant", "notary signature"]
            exclude_patterns = ["commission expires", "signature line"]
            logger.info(f"Using default keywords: {keywords}")
        
        # Handle signature options from checkboxes
        if signature_options:
            try:
                import json
                # Try to parse as JSON first
                try:
                    sig_options = json.loads(signature_options)
                except json.JSONDecodeError:
                    # If that fails, try to reconstruct the JSON from the malformed string
                    # The string looks like: {notary: true, claimant: true, notaryPublic: true}
                    # We need to add quotes around the property names
                    reconstructed = signature_options.replace('{', '{"').replace(': ', '": "').replace(', ', '", "').replace('}', '"}')
                    reconstructed = reconstructed.replace('": "true', '": true').replace('": "false', '": false')
                    try:
                        sig_options = json.loads(reconstructed)
                    except json.JSONDecodeError:
                        # If that still fails, try a simpler approach
                        # Manually parse the string: {notary: true, claimant: true, notaryPublic: true}
                        sig_options = {}
                        if 'notary: true' in signature_options:
                            sig_options['notary'] = True
                        if 'claimant: true' in signature_options:
                            sig_options['claimant'] = True
                        if 'notaryPublic: true' in signature_options:
                            sig_options['notaryPublic'] = True
                
                logger.info(f"Processing signature options: {sig_options}")
                
                # Add signature-specific keywords based on selected options
                signature_keywords = []
                if sig_options.get('notary', False):
                    signature_keywords.extend([
                        "signature of notary", "notary signature", "notary public signature",
                        "notary's signature", "notary signature:", "notary public signature:",
                        "notary signature line", "notary public signature line"
                    ])
                    logger.info("Added notary signature keywords")
                if sig_options.get('claimant', False):
                    signature_keywords.extend([
                        "signature of claimant", "claimant signature", "signature of applicant",
                        "claimant's signature", "claimant signature:", "signature of claimant:",
                        "claimant signature line", "signature of claimant line"
                    ])
                    logger.info("Added claimant signature keywords")
                if sig_options.get('notaryPublic', False):
                    signature_keywords.extend([
                        "notary public", "public notary", "commissioned notary",
                        "notary public:", "public notary:", "commissioned notary:",
                        "notary public in", "notary public and", "notary public may",
                        "notary public services", "notary public notice"
                    ])
                    logger.info("Added notary public keywords")
                if sig_options.get('representative', False):
                    signature_keywords.extend([
                        "representative's signature", "representative signature",
                        "representative signature:", "representative's signature:",
                        "claimant's representative's signature", "representative signature line"
                    ])
                    logger.info("Added representative signature keywords")
                if sig_options.get('authorized', False):
                    signature_keywords.extend([
                        "authorized signer", "authorized signer signature",
                        "authorized signer:", "authorized signer signature:",
                        "authorized signer line", "signature of authorized signer"
                    ])
                    logger.info("Added authorized signer keywords")
                if sig_options.get('applicant', False):
                    signature_keywords.extend([
                        "signature of applicant", "applicant signature",
                        "applicant signature:", "signature of applicant:",
                        "applicant signature line", "applicant's signature"
                    ])
                    logger.info("Added applicant signature keywords")
                
                # Add signature keywords to the main keywords list
                if signature_keywords:
                    keywords.extend(signature_keywords)
                    logger.info(f"Added signature keywords: {signature_keywords}")
                    logger.info(f"Final keywords list: {keywords}")
                else:
                    logger.info("No signature keywords to add")
                    
            except Exception as e:
                logger.warning(f"Error parsing signature options: {e}")
        else:
            logger.info("No signature options provided")
        
        # Process each page
        for page_num in range(len(doc)):
            page = doc[page_num]
            logger.info(f"Processing page {page_num + 1}/{len(doc)}")
            
            # Get text blocks (potential highlighting targets)
            text_blocks = page.get_text("dict")["blocks"]
            
            # Debug: Show some sample text from this page
            sample_texts = []
            for block in text_blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if text and len(sample_texts) < 10:  # Show first 10 text samples
                                sample_texts.append(text)
            
            if sample_texts:
                logger.info(f"Sample texts from page {page_num + 1}: {sample_texts}")
            
            for block in text_blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].lower()
                            
                            # Check for keyword matches
                            should_highlight = False
                            matched_keyword = None
                            
                            # First check if this text should be excluded
                            should_exclude = False
                            for exclude_pattern in exclude_patterns:
                                if exclude_pattern in text:
                                    should_exclude = True
                                    logger.debug(f"Excluding text '{text}' due to pattern '{exclude_pattern}'")
                                    break
                            
                            if should_exclude:
                                continue  # Skip this text
                            
                            # Debug logging for troubleshooting
                            if any(keyword in text for keyword in keywords):
                                logger.debug(f"Potential match found - Text: '{text}', Keywords: {keywords}")
                            
                            for keyword in keywords:
                                # Check for exact word match
                                text_words = text.split()
                                if keyword in text_words:
                                    should_highlight = True
                                    matched_keyword = keyword
                                    logger.debug(f"Exact word match: '{keyword}' in '{text}'")
                                    break
                                
                                # Check for partial word match (e.g., "notary" in "notary public")
                                if keyword in text:
                                    should_highlight = True
                                    matched_keyword = keyword
                                    logger.debug(f"Partial word match: '{keyword}' in '{text}'")
                                    break
                                
                                # For multi-word terms, check if all parts are present as separate words
                                keyword_parts = keyword.split()
                                if len(keyword_parts) > 1:
                                    # Check if all keyword parts exist as separate words in the text
                                    if all(part in text_words for part in keyword_parts):
                                        should_highlight = True
                                        matched_keyword = keyword
                                        logger.debug(f"Multi-word match: all parts of '{keyword}' found in '{text}'")
                                        break
                                    
                                    # Also check if the full phrase appears anywhere in the text
                                    if keyword in text:
                                        should_highlight = True
                                        matched_keyword = keyword
                                        logger.debug(f"Full phrase match: '{keyword}' in '{text}'")
                                        break
                            
                            if should_highlight:
                                # Create highlight rectangle
                                rect = fitz.Rect(span["bbox"])
                                
                                # Add yellow highlight
                                highlight = page.add_highlight_annot(rect)
                                highlight.set_colors(stroke=[1, 1, 0])  # Yellow
                                highlight.set_opacity(0.7)  # 70% opacity for better visibility
                                highlight.update()
                                logger.info(f"✅ Highlighted: '{text}' (matched: '{matched_keyword}')")
                            else:
                                # Debug: Show when we find text that contains keywords but doesn't match exactly
                                for keyword in keywords:
                                    if keyword in text:
                                        logger.debug(f"Found keyword '{keyword}' in text '{text}' but didn't highlight (exact match failed)")
        
        # Fill in name fields if name_text is provided
        if name_text:
            logger.info(f"Filling in name fields with: '{name_text}'")
            fill_name_fields(doc, name_text)
        
        # Save the highlighted PDF
        doc.save(str(output_path))
        doc.close()
        
        logger.info(f"Highlighted PDF saved: {output_path.name}")
        if highlight_text:
            logger.info(f"Used custom highlight text: '{highlight_text}'")
        if profile:
            logger.info(f"Used profile: '{profile}'")
        if name_text:
            logger.info(f"Filled in name fields with: '{name_text}'")
        if signature_options:
            logger.info(f"Used signature options: '{signature_options}'")
        logger.info(f"Total keywords searched for: {len(keywords)}")
        logger.info(f"Keywords list: {keywords}")
        return True
        
    except Exception as e:
        logger.error(f"Error highlighting PDF with PyMuPDF: {e}")
        return False

def highlight_pdf_pypdf2(pdf_path: Path, output_path: Path, name_text: str = None) -> bool:
    """
    Add highlights to a PDF using PyPDF2.
    
    Args:
        pdf_path (Path): Path to input PDF
        output_path (Path): Path to output highlighted PDF
        name_text (str): Name to fill in PDF form fields
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the PDF
        reader = PdfReader(str(pdf_path))
        writer = PdfWriter()
        
        # Copy pages (PyPDF2 has limited annotation capabilities)
        for page in reader.pages:
            writer.add_page(page)
        
        # Save the PDF (basic copy for now)
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        logger.info(f"PDF processed with PyPDF2: {output_path.name}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing PDF with PyPDF2: {e}")
        return False

def highlight_pdf_file(pdf_path: Path, output_dir: Path, highlight_text: str = None, name_text: str = None, profile: str = None, signature_options: str = None) -> Optional[Path]:
    """
    Highlight a PDF file using available libraries.
    
    Args:
        pdf_path (Path): Path to input PDF
        output_dir (Path): Directory to save highlighted PDF
        highlight_text (str): Custom text to highlight (e.g., "signatures", "dates", "names")
        name_text (str): Name to fill in PDF form fields
        profile (str): Profile name for predefined highlighting rules
        signature_options (str): JSON string of signature options from checkboxes
    
    Returns:
        Optional[Path]: Path to highlighted PDF if successful, None otherwise
    """
    output_path = output_dir / f"highlighted_{pdf_path.name}"
    
    # Try PyMuPDF first (better highlighting capabilities)
    if PYMUPDF_AVAILABLE:
        if highlight_pdf_pymupdf(pdf_path, output_path, highlight_text, name_text, profile, signature_options):
            return output_path
    
    # Fallback to PyPDF2
    if PYPDF2_AVAILABLE:
        if highlight_pdf_pypdf2(pdf_path, output_path, name_text):
            return output_path
    
    logger.error(f"Could not highlight PDF: {pdf_path.name}")
    return None

def process_pdf_files(pdf_files: List[Path], output_dir: Path, highlight_text: str = None, name_text: str = None, profile: str = None, signature_options: str = None) -> List[Path]:
    """
    Process multiple PDF files and add highlights.
    
    Args:
        pdf_files (List[Path]): List of PDF files to process
        output_dir (Path): Directory to save highlighted PDFs
        highlight_text (str): Custom text to highlight (e.g., "signatures", "dates", "names")
        name_text (str): Name to fill in PDF form fields
        profile (str): Profile name for predefined highlighting rules
        signature_options (str): JSON string of signature options from checkboxes
    
    Returns:
        List[Path]: List of highlighted PDF paths
    """
    highlighted_files = []
    
    logger.info(f"Processing {len(pdf_files)} PDF files...")
    if highlight_text:
        logger.info(f"Using custom highlight text: '{highlight_text}'")
    if profile:
        profile_data = get_highlighting_profile(profile)
        logger.info(f"Using profile: '{profile}' - {profile_data['description']}")
        logger.info(f"Profile keywords: {profile_data['keywords']}")
    
    for i, pdf_path in enumerate(pdf_files, 1):
        logger.info(f"Processing {i}/{len(pdf_files)}: {pdf_path.name}")
        
        highlighted_path = highlight_pdf_file(pdf_path, output_dir, highlight_text, name_text, profile, signature_options)
        if highlighted_path:
            highlighted_files.append(highlighted_path)
    
    logger.info(f"Successfully highlighted {len(highlighted_files)} PDFs")
    return highlighted_files

def create_highlighted_zip(highlighted_files: List[Path], original_zip_path: Path) -> Path:
    """
    Create a new ZIP file containing highlighted PDFs.
    
    Args:
        highlighted_files (List[Path]): List of highlighted PDF paths
        original_zip_path (Path): Path to original ZIP file
    
    Returns:
        Path: Path to the new highlighted ZIP file
    """
    try:
        # Create output ZIP path
        output_zip_path = original_zip_path.parent / f"highlighted_{original_zip_path.name}"
        
        # Create ZIP file
        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for pdf_path in highlighted_files:
                # Add PDF to ZIP with relative path
                zipf.write(pdf_path, pdf_path.name)
        
        logger.info(f"Created highlighted ZIP: {output_zip_path.name}")
        return output_zip_path
        
    except Exception as e:
        logger.error(f"Error creating highlighted ZIP: {e}")
        raise

def cleanup_temp_files(extract_dir: Path, output_dir: Path):
    """Clean up temporary files."""
    try:
        if extract_dir.exists():
            shutil.rmtree(extract_dir)
        if output_dir.exists():
            shutil.rmtree(output_dir)
        logger.info("Cleaned up temporary files")
    except Exception as e:
        logger.warning(f"Could not clean up temporary files: {e}")

def main(highlight_text: str = None, name_text: str = None, debug_mode: bool = False, profile: str = None, signature_options: str = None, file_path: str = None):
    """Main function to process ZIP files and add highlights to PDFs."""
    print("=" * 70)
    print("PDF Highlighter - Automatic PDF Highlighting")
    print("=" * 70)
    
    if highlight_text:
        print(f"Custom highlight text: '{highlight_text}'")
    
    if name_text:
        print(f"Name text for form filling: '{name_text}'")
    
    if profile:
        profile_data = get_highlighting_profile(profile)
        print(f"Using profile: '{profile}' - {profile_data['description']}")
        print(f"Profile keywords: {profile_data['keywords']}")
    
    if signature_options:
        print(f"Using signature options: '{signature_options}'")
        # Try to parse and display the signature options
        try:
            import json
            sig_options = json.loads(signature_options)
            print(f"Parsed signature options: {sig_options}")
        except Exception as e:
            print(f"Error parsing signature options: {e}")
    
    if debug_mode:
        print("🔍 Debug mode enabled - will analyze PDF structure and show detailed logs")
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check for required libraries
    if not check_pdf_libraries():
        print("❌ Required PDF libraries not found!")
        print("Installing required libraries...")
        print("Run: pip install PyMuPDF PyPDF2")
        return
    
    # Use provided file path or find the most recent file
    if file_path:
        print(f"\nUsing provided file path: {file_path}")
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return
    else:
        # Find the most recent file
        print("\nSearching for most recent download...")
        file_path = find_most_recent_file()
        
        if not file_path:
            print("❌ No recent files found in Downloads folder")
            return
    
    # Check if it's a ZIP file or PDF file
    if file_path.suffix.lower() not in ['.zip', '.pdf']:
        print(f"❌ File is not a ZIP or PDF file: {file_path.name}")
        print("Please download a ZIP file containing PDFs or a PDF file directly")
        return
    
    # Display file info
    print(f"\nFound file: {file_path.name}")
    print(f"Path: {file_path}")
    print(f"Size: {file_path.stat().st_size:,} bytes")
    print(f"Modified: {datetime.fromtimestamp(file_path.stat().st_mtime)}")
    
    try:
        pdf_files = []
        
        if file_path.suffix.lower() == '.zip':
            # Extract ZIP file
            print(f"\nExtracting ZIP file...")
            extract_dir = extract_zip_file(file_path)
            
            # Find PDF files
            print("Finding PDF files...")
            pdf_files = find_pdf_files(extract_dir)
            
            if not pdf_files:
                print("❌ No PDF files found in ZIP")
                return
            
            print(f"Found {len(pdf_files)} PDF files to process")
        elif file_path.suffix.lower() == '.pdf':
            # Single PDF file
            print(f"\nProcessing single PDF file...")
            pdf_files = [file_path]
            print(f"Processing 1 PDF file")
        
        # Debug mode: Analyze first PDF structure
        if debug_mode and pdf_files:
            print("\n🔍 Analyzing PDF structure for debugging...")
            first_pdf = pdf_files[0]
            analysis = analyze_pdf_structure(first_pdf)
            if analysis:
                print(f"PDF Analysis Results:")
                print(f"  - Total pages: {analysis.get('total_pages', 0)}")
                print(f"  - Text spans found: {len(analysis.get('text_spans', []))}")
                print(f"  - Fonts used: {len(analysis.get('fonts_used', set()))}")
                print(f"  - Sample texts: {analysis.get('sample_texts', [])[:5]}")  # Show first 5
                
                # Show what keywords we're looking for
                if profile:
                    profile_data = get_highlighting_profile(profile)
                    keywords = profile_data.get('keywords', [])
                elif highlight_text:
                    keywords = [kw.strip().lower() for kw in highlight_text.split(',')]
                else:
                    keywords = ["signature", "notary", "claimant", "date"]
                
                # Add signature options keywords if provided
                if signature_options:
                    try:
                        import json
                        sig_options = json.loads(signature_options)
                        signature_keywords = []
                        if sig_options.get('notary', False):
                            signature_keywords.extend(["signature of notary", "notary signature", "notary public signature"])
                        if sig_options.get('claimant', False):
                            signature_keywords.extend(["signature of claimant", "claimant signature", "signature of applicant"])
                        if sig_options.get('notaryPublic', False):
                            signature_keywords.extend(["notary public", "public notary", "commissioned notary"])
                        keywords.extend(signature_keywords)
                        print(f"  - Added signature keywords: {signature_keywords}")
                    except Exception as e:
                        print(f"  - Error parsing signature options: {e}")
                
                print(f"  - Final keywords list: {keywords}")
                
                # Check if keywords appear in sample texts
                found_keywords = []
                for keyword in keywords:
                    for sample in analysis.get('sample_texts', []):
                        if keyword in sample.lower():
                            found_keywords.append(keyword)
                            break
                
                if found_keywords:
                    print(f"  - ✅ Keywords found in PDF: {found_keywords}")
                else:
                    print(f"  - ❌ No keywords found in PDF samples")
        
        # Create output directory for highlighted PDFs
        output_dir = file_path.parent / f"highlighted_pdfs_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        output_dir.mkdir(exist_ok=True)
        
        # Process PDF files
        print(f"\nProcessing PDF files and adding highlights...")
        highlighted_files = process_pdf_files(pdf_files, output_dir, highlight_text, name_text, profile, signature_options)
        
        if not highlighted_files:
            print("❌ No PDFs were successfully highlighted")
            return
        
        # Create highlighted output file
        if file_path.suffix.lower() == '.zip':
            print(f"\nCreating highlighted ZIP file...")
            highlighted_zip_path = create_highlighted_zip(highlighted_files, file_path)
            
            # Display results
            print("\n" + "=" * 70)
            print("PROCESSING COMPLETE!")
            print("=" * 70)
            print(f"Original ZIP: {file_path.name}")
            print(f"Highlighted ZIP: {highlighted_zip_path.name}")
            print(f"PDFs processed: {len(highlighted_files)}/{len(pdf_files)}")
            print(f"Output location: {highlighted_zip_path}")
            print("=" * 70)
            
            # Clean up temporary files
            cleanup_temp_files(extract_dir, output_dir)
            
            print(f"\n✅ Success! Your highlighted PDFs are ready in: {highlighted_zip_path.name}")
        else:
            # Single PDF file - the highlighted file is already in the output directory
            highlighted_pdf = highlighted_files[0] if highlighted_files else None
            
            print("\n" + "=" * 70)
            print("PROCESSING COMPLETE!")
            print("=" * 70)
            print(f"Original PDF: {file_path.name}")
            print(f"Highlighted PDF: {highlighted_pdf.name if highlighted_pdf else 'None'}")
            print(f"PDFs processed: {len(highlighted_files)}/1")
            print(f"Output location: {highlighted_pdf}")
            print("=" * 70)
            
            print(f"\n✅ Success! Your highlighted PDF is ready: {highlighted_pdf.name if highlighted_pdf else 'None'}")
        
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import sys
    
    # Initialize variables
    highlight_text = None
    name_text = None
    signature_options = None
    debug_mode = False
    profile = None
    file_path = None
    
    # Parse command line arguments
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == "--debug":
            debug_mode = True
        elif arg == "--profile":
            if i + 1 < len(sys.argv):
                profile = sys.argv[i + 1]
                i += 1
        elif arg == "--name":
            if i + 1 < len(sys.argv):
                name_text = sys.argv[i + 1]
                i += 1
        elif arg == "--signature-options":
            if i + 1 < len(sys.argv):
                signature_options = sys.argv[i + 1]
                i += 1
        elif arg == "--file":
            if i + 1 < len(sys.argv):
                file_path = sys.argv[i + 1]
                i += 1
        elif not arg.startswith("--"):
            # This is the highlight text (first non-flag argument)
            highlight_text = arg
        
        i += 1
    
    # Run the main function with the highlight text, name text, and signature options
    main(highlight_text, name_text, debug_mode, profile, signature_options, file_path) 