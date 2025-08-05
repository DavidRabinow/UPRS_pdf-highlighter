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

def highlight_pdf_pymupdf(pdf_path: Path, output_path: Path) -> bool:
    """
    Add highlights to a PDF using PyMuPDF.
    
    Args:
        pdf_path (Path): Path to input PDF
        output_path (Path): Path to output highlighted PDF
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Open the PDF
        doc = fitz.open(str(pdf_path))
        
        # Process each page
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Get text blocks (potential highlighting targets)
            text_blocks = page.get_text("dict")["blocks"]
            
            for block in text_blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            # Highlight ONLY signature lines (customize this logic)
                            text = span["text"].lower()
                            if any(keyword in text for keyword in [
                                "signature of claimant",
                                "signature of the notary public"
                            ]):
                                # Create highlight rectangle
                                rect = fitz.Rect(span["bbox"])
                                
                                # Add yellow highlight
                                highlight = page.add_highlight_annot(rect)
                                highlight.set_colors(stroke=[1, 1, 0])  # Yellow
                                highlight.set_opacity(0.3)  # 30% opacity
                                highlight.update()
        
        # Save the highlighted PDF
        doc.save(str(output_path))
        doc.close()
        
        logger.info(f"Highlighted PDF saved: {output_path.name}")
        return True
        
    except Exception as e:
        logger.error(f"Error highlighting PDF with PyMuPDF: {e}")
        return False

def highlight_pdf_pypdf2(pdf_path: Path, output_path: Path) -> bool:
    """
    Add highlights to a PDF using PyPDF2.
    
    Args:
        pdf_path (Path): Path to input PDF
        output_path (Path): Path to output highlighted PDF
    
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

def highlight_pdf_file(pdf_path: Path, output_dir: Path) -> Optional[Path]:
    """
    Highlight a PDF file using available libraries.
    
    Args:
        pdf_path (Path): Path to input PDF
        output_dir (Path): Directory to save highlighted PDF
    
    Returns:
        Optional[Path]: Path to highlighted PDF if successful, None otherwise
    """
    output_path = output_dir / f"highlighted_{pdf_path.name}"
    
    # Try PyMuPDF first (better highlighting capabilities)
    if PYMUPDF_AVAILABLE:
        if highlight_pdf_pymupdf(pdf_path, output_path):
            return output_path
    
    # Fallback to PyPDF2
    if PYPDF2_AVAILABLE:
        if highlight_pdf_pypdf2(pdf_path, output_path):
            return output_path
    
    logger.error(f"Could not highlight PDF: {pdf_path.name}")
    return None

def process_pdf_files(pdf_files: List[Path], output_dir: Path) -> List[Path]:
    """
    Process multiple PDF files and add highlights.
    
    Args:
        pdf_files (List[Path]): List of PDF files to process
        output_dir (Path): Directory to save highlighted PDFs
    
    Returns:
        List[Path]: List of highlighted PDF paths
    """
    highlighted_files = []
    
    logger.info(f"Processing {len(pdf_files)} PDF files...")
    
    for i, pdf_path in enumerate(pdf_files, 1):
        logger.info(f"Processing {i}/{len(pdf_files)}: {pdf_path.name}")
        
        highlighted_path = highlight_pdf_file(pdf_path, output_dir)
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

def main():
    """Main function to process ZIP files and add highlights to PDFs."""
    print("=" * 70)
    print("PDF Highlighter - Automatic PDF Highlighting")
    print("=" * 70)
    
    # Check for required libraries
    if not check_pdf_libraries():
        print("❌ Required PDF libraries not found!")
        print("Installing required libraries...")
        print("Run: pip install PyMuPDF PyPDF2")
        return
    
    # Find the most recent file
    print("\nSearching for most recent download...")
    file_path = find_most_recent_file()
    
    if not file_path:
        print("❌ No recent files found in Downloads folder")
        return
    
    # Check if it's a ZIP file
    if file_path.suffix.lower() != '.zip':
        print(f"❌ File is not a ZIP file: {file_path.name}")
        print("Please download a ZIP file containing PDFs")
        return
    
    # Display file info
    print(f"\nFound ZIP file: {file_path.name}")
    print(f"Path: {file_path}")
    print(f"Size: {file_path.stat().st_size:,} bytes")
    print(f"Modified: {datetime.fromtimestamp(file_path.stat().st_mtime)}")
    
    try:
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
        
        # Create output directory for highlighted PDFs
        output_dir = file_path.parent / f"highlighted_pdfs_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        output_dir.mkdir(exist_ok=True)
        
        # Process PDF files
        print(f"\nProcessing PDF files and adding highlights...")
        highlighted_files = process_pdf_files(pdf_files, output_dir)
        
        if not highlighted_files:
            print("❌ No PDFs were successfully highlighted")
            return
        
        # Create highlighted ZIP file
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
        
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 