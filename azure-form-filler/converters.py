"""
File Converters
Handles conversion of various file types to PDF for processing
"""

import os
import tempfile
from typing import Optional
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image

def convert_to_pdf_if_needed(file_path: str) -> Optional[str]:
    """
    Convert file to PDF if it's not already a PDF
    
    Args:
        file_path: Path to the file to convert
        
    Returns:
        Path to converted PDF file, or None if conversion not supported
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.pdf':
        return None  # Already a PDF
    
    elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
        return image_to_pdf(file_path)
    
    elif file_ext in ['.docx', '.doc']:
        return docx_to_pdf(file_path)
    
    else:
        # Unsupported file type
        return None

def image_to_pdf(image_path: str) -> str:
    """
    Convert image file to PDF
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Path to the generated PDF file
    """
    # Open image to get dimensions
    with Image.open(image_path) as img:
        img_width, img_height = img.size
    
    # Create temporary PDF file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
        pdf_path = temp_file.name
    
    # Create PDF with same aspect ratio as image
    # Use letter size as base and scale image to fit
    letter_width, letter_height = letter
    
    # Calculate scaling to fit image on page
    scale_x = letter_width / img_width
    scale_y = letter_height / img_height
    scale = min(scale_x, scale_y) * 0.9  # 90% of max size to leave margins
    
    # Calculate centered position
    scaled_width = img_width * scale
    scaled_height = img_height * scale
    x_offset = (letter_width - scaled_width) / 2
    y_offset = (letter_height - scaled_height) / 2
    
    # Create PDF
    c = canvas.Canvas(pdf_path, pagesize=letter)
    
    # Draw image
    c.drawImage(image_path, x_offset, y_offset, width=scaled_width, height=scaled_height)
    
    c.save()
    return pdf_path

def docx_to_pdf(docx_path: str) -> Optional[str]:
    """
    Convert DOCX file to PDF (stub implementation)
    
    TODO: Implement using headless LibreOffice or python-docx2pdf
    
    Args:
        docx_path: Path to the DOCX file
        
    Returns:
        Path to the generated PDF file, or None if conversion failed
    """
    # TODO: Implement DOCX to PDF conversion
    # Options:
    # 1. Use headless LibreOffice: soffice --headless --convert-to pdf file.docx
    # 2. Use python-docx2pdf library
    # 3. Use cloud conversion service
    
    print(f"Warning: DOCX to PDF conversion not implemented for {docx_path}")
    print("TODO: Add headless LibreOffice or python-docx2pdf support")
    
    return None

def create_test_image(output_path: str = "test_image.png") -> str:
    """
    Create a test image for testing purposes
    
    Args:
        output_path: Path where to save the test image
        
    Returns:
        Path to the created image
    """
    # Create a simple test image
    width, height = 400, 300
    img = Image.new('RGB', (width, height), color='white')
    
    # Add some text-like content (simplified)
    from PIL import ImageDraw, ImageFont
    
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fall back to basic if not available
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    # Draw some text that looks like a form
    draw.text((20, 20), "Test Document", fill='black', font=font)
    draw.text((20, 60), "Name: ________________", fill='black', font=font)
    draw.text((20, 100), "Date: ________________", fill='black', font=font)
    draw.text((20, 140), "Signature: _____________", fill='black', font=font)
    draw.text((20, 180), "Consent: [ ] Yes  [ ] No", fill='black', font=font)
    
    img.save(output_path)
    return output_path
