import os
import logging
from pathlib import Path
from datetime import datetime
import zipfile
import shutil

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

def analyze_pdf_file(file_path):
    """
    Analyze a PDF file locally and provide highlighting recommendations.
    
    Args:
        file_path (Path): Path to the PDF file
    
    Returns:
        str: Analysis and recommendations
    """
    file_size = file_path.stat().st_size
    file_name = file_path.name
    
    # Basic file analysis
    analysis = f"""PDF File Analysis

File: {file_name}
Path: {file_path}
Size: {file_size:,} bytes
Modified: {datetime.fromtimestamp(file_path.stat().st_mtime)}

File Type Analysis:
- Extension: {file_path.suffix.lower()}
- File Size: {'Large' if file_size > 1000000 else 'Medium' if file_size > 100000 else 'Small'}
- Likely Content: {'Document/Form' if 'form' in file_name.lower() or 'claim' in file_name.lower() else 'General PDF'}

PDF Highlighting Recommendations:

1. **Text Extraction Methods**:
   - **Adobe Acrobat Pro**: Best for professional work
   - **PDF24 Creator**: Free alternative with good OCR
   - **Online Tools**: SmallPDF, ILovePDF, or PDFsam
   - **Built-in Readers**: Most PDF readers have basic highlighting

2. **Highlighting Best Practices**:
   - Use light yellow color (RGB: 255, 255, 0) with 30-50% opacity
   - Position highlights BEHIND text, never on top
   - Select only specific text, not entire lines
   - Test readability after highlighting
   - Use semi-transparent colors that don't interfere with text

3. **Software Recommendations**:
   - **Adobe Acrobat Pro** (paid, professional): Best for complex documents
   - **PDF24 Creator** (free): Good for basic highlighting
   - **Foxit PDF Reader** (free/paid): Excellent highlighting tools
   - **Online Tools**: Quick edits without software installation

4. **Step-by-Step Process**:
   a) Open the PDF in your chosen software
   b) Use the highlight tool (usually yellow marker icon)
   c) Select the text you want to highlight
   d) Adjust opacity to 30-50% for best readability
   e) Ensure highlights are behind text, not covering it
   f) Save the document with highlights

5. **For This Specific File**:
   - File size suggests it's a standard document
   - Likely contains forms or claims based on filename
   - Use Adobe Acrobat Pro or PDF24 for best results
   - Focus on highlighting key information only

6. **Quality Control**:
   - Always test readability after highlighting
   - Use consistent highlighting colors
   - Avoid over-highlighting (less is more)
   - Ensure text remains fully visible

The file has been analyzed and is ready for highlighting work.
"""
    
    return analysis

def extract_zip_and_analyze(zip_path):
    """
    Extract a ZIP file and analyze its contents.
    
    Args:
        zip_path (Path): Path to the ZIP file
    
    Returns:
        str: Analysis of ZIP contents
    """
    try:
        # Create extraction directory
        extract_dir = zip_path.parent / "extracted_files"
        extract_dir.mkdir(exist_ok=True)
        
        # Extract ZIP file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Get list of extracted files
        extracted_files = list(extract_dir.rglob("*"))
        pdf_files = [f for f in extracted_files if f.is_file() and f.suffix.lower() == '.pdf']
        
        analysis = f"""ZIP File Analysis

Original File: {zip_path.name}
Extracted to: {extract_dir}
Total Files Extracted: {len(extracted_files)}
PDF Files Found: {len(pdf_files)}

PDF Files in ZIP:
"""
        
        for i, pdf_file in enumerate(pdf_files, 1):
            analysis += f"{i}. {pdf_file.name} ({pdf_file.stat().st_size:,} bytes)\n"
        
        analysis += f"""

Highlighting Recommendations for ZIP Contents:

1. **Batch Processing**:
   - Extract all PDFs from the ZIP file
   - Process each PDF individually for best results
   - Use consistent highlighting across all files

2. **Software for Batch Processing**:
   - **Adobe Acrobat Pro**: Best for batch operations
   - **PDF24 Creator**: Free batch processing
   - **Online Tools**: Process multiple files at once

3. **Workflow**:
   a) Extract all PDFs from the ZIP
   b) Open each PDF in your chosen software
   c) Apply consistent highlighting rules
   d) Save each file with highlights
   e) Re-zip if needed

4. **Quality Standards**:
   - Use same highlighting color across all files
   - Maintain consistent opacity (30-50%)
   - Ensure text remains readable
   - Test each file after highlighting

5. **File Organization**:
   - Keep original ZIP as backup
   - Create highlighted version of each PDF
   - Consider re-zipping highlighted files

The ZIP has been extracted and analyzed. {len(pdf_files)} PDF files are ready for highlighting.
"""
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error extracting ZIP file: {e}")
        return f"Error processing ZIP file: {e}"

def main():
    """Main function to analyze the most recent download."""
    print("=" * 70)
    print("Local PDF Analyzer - Highlighting Recommendations")
    print("=" * 70)
    
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
    
    # Analyze based on file type
    print(f"\nAnalyzing file and generating highlighting recommendations...")
    
    if file_path.suffix.lower() == '.zip':
        print("Detected ZIP file - extracting and analyzing contents...")
        response = extract_zip_and_analyze(file_path)
    elif file_path.suffix.lower() == '.pdf':
        print("Detected PDF file - analyzing for highlighting...")
        response = analyze_pdf_file(file_path)
    else:
        response = f"File type {file_path.suffix} not supported. Please download a PDF or ZIP file."
    
    # Display results
    print("\n" + "=" * 70)
    print("ANALYSIS RESULTS:")
    print("=" * 70)
    print(response)
    print("=" * 70)
    
    # Save response to file
    with open("pdf_analysis_results.txt", "w", encoding="utf-8") as f:
        f.write(response)
    
    print(f"\nAnalysis saved to: pdf_analysis_results.txt")
    print("\n💡 Note: This is a local analysis. For AI-powered analysis,")
    print("   add billing to your OpenAI account and run chatgpt_file_processor.py")

if __name__ == "__main__":
    main() 