"""
PDF Utilities
Handles rendering overlays and highlights on PDF pages
"""

import os
import tempfile
from typing import List, Dict, Any, Tuple
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import yellow
from reportlab.lib.units import point
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def get_page_dimensions(pdf_path: str, page_num: int) -> Tuple[float, float]:
    """
    Get the dimensions of a specific page in a PDF
    
    Args:
        pdf_path: Path to the PDF file
        page_num: Page number (1-indexed)
        
    Returns:
        Tuple of (width, height) in points
    """
    reader = PdfReader(pdf_path)
    if page_num < 1 or page_num > len(reader.pages):
        raise ValueError(f"Page {page_num} does not exist in PDF")
    
    page = reader.pages[page_num - 1]
    mediabox = page.mediabox
    
    width = float(mediabox.width)
    height = float(mediabox.height)
    
    return width, height

def create_overlay_page(
    page_width: float, 
    page_height: float, 
    overlays: List[Dict[str, Any]], 
    highlights: List[Dict[str, Any]],
    page_num: int
) -> bytes:
    """
    Create a PDF overlay page with text and highlights
    
    Args:
        page_width: Width of the page in points
        page_height: Height of the page in points
        overlays: List of overlay dicts with page, x, y, text
        highlights: List of highlight dicts with page, polygon
        page_num: Current page number
        
    Returns:
        PDF overlay as bytes
    """
    # Create temporary file for the overlay
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Create canvas with same dimensions as original page
        c = canvas.Canvas(temp_path, pagesize=(page_width, page_height))
        
        # Filter overlays and highlights for this page
        page_overlays = [o for o in overlays if o['page'] == page_num]
        page_highlights = [h for h in highlights if h['page'] == page_num]
        
        # Draw highlights first (so they appear behind text)
        for highlight in page_highlights:
            polygon = highlight['polygon']
            if len(polygon) >= 4:  # Need at least 2 points
                # Convert polygon to reportlab format
                points = []
                for i in range(0, len(polygon), 2):
                    if i + 1 < len(polygon):
                        x, y = polygon[i], polygon[i + 1]
                        # Convert to reportlab coordinates (PDF coordinates are bottom-left origin)
                        points.extend([x, page_height - y])
                
                if len(points) >= 4:  # Need at least 2 points for a shape
                    # Draw semi-transparent yellow rectangle
                    c.setFillColorRGB(1, 1, 0, alpha=0.3)  # Yellow with 30% opacity
                    c.setStrokeColorRGB(1, 1, 0, alpha=0.5)  # Yellow border with 50% opacity
                    c.setLineWidth(1)
                    
                    # Draw polygon or bounding box
                    if len(points) == 4:  # Rectangle
                        c.rect(points[0], points[1], points[2] - points[0], points[3] - points[1], fill=1, stroke=1)
                    else:  # Polygon
                        c.polygon(points, fill=1, stroke=1)
        
        # Draw text overlays
        c.setFillColorRGB(0, 0, 0)  # Black text
        c.setFont("Helvetica", 10)  # Default font and size
        
        for overlay in page_overlays:
            x = overlay['x']
            y = overlay['y']
            text = overlay['text']
            
            # Convert to reportlab coordinates
            y_reportlab = page_height - y
            
            # Draw text
            c.drawString(x, y_reportlab, text)
        
        c.save()
        
        # Read the generated PDF
        with open(temp_path, 'rb') as f:
            return f.read()
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

def render_overlays_and_highlights(
    input_pdf_path: str, 
    output_pdf_path: str, 
    overlays: List[Dict[str, Any]], 
    highlights: List[Dict[str, Any]]
):
    """
    Render overlays and highlights on a PDF and save the result
    
    Args:
        input_pdf_path: Path to input PDF
        output_pdf_path: Path for output PDF
        overlays: List of overlay dicts with page, x, y, text
        highlights: List of highlight dicts with page, polygon
    """
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()
    
    # Process each page
    for page_num in range(1, len(reader.pages) + 1):
        page = reader.pages[page_num - 1]
        
        # Get page dimensions
        page_width, page_height = get_page_dimensions(input_pdf_path, page_num)
        
        # Check if this page has any overlays or highlights
        page_overlays = [o for o in overlays if o['page'] == page_num]
        page_highlights = [h for h in highlights if h['page'] == page_num]
        
        if page_overlays or page_highlights:
            # Create overlay for this page
            overlay_bytes = create_overlay_page(
                page_width, page_height, 
                overlays, highlights, page_num
            )
            
            # Create overlay PDF reader
            overlay_reader = PdfReader(overlay_bytes)
            overlay_page = overlay_reader.pages[0]
            
            # Merge overlay with original page
            page.merge_page(overlay_page)
        
        # Add page to writer
        writer.add_page(page)
    
    # Write output PDF
    with open(output_pdf_path, 'wb') as output_file:
        writer.write(output_file)

def create_sample_pdf(output_path: str = "sample_form.pdf"):
    """
    Create a sample PDF form for testing purposes
    
    Args:
        output_path: Path where to save the sample PDF
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Sample Medical Form")
    
    # Form fields
    c.setFont("Helvetica", 12)
    y_start = height - 100
    
    # Name field
    c.drawString(50, y_start, "Name:")
    c.rect(120, y_start - 5, 200, 20)
    
    # Date of Birth field
    c.drawString(50, y_start - 40, "Date of Birth:")
    c.rect(150, y_start - 45, 150, 20)
    
    # Phone field
    c.drawString(50, y_start - 80, "Phone:")
    c.rect(120, y_start - 85, 150, 20)
    
    # Address field
    c.drawString(50, y_start - 120, "Address:")
    c.rect(120, y_start - 125, 250, 20)
    
    # Signature section
    c.drawString(50, y_start - 160, "Signature:")
    c.rect(120, y_start - 165, 200, 40)
    
    # Consent section
    c.drawString(50, y_start - 220, "I consent to treatment:")
    c.rect(200, y_start - 225, 20, 20)
    
    # Emergency contact
    c.drawString(50, y_start - 260, "Emergency Contact:")
    c.rect(180, y_start - 265, 200, 20)
    
    # Insurance
    c.drawString(50, y_start - 300, "Insurance Provider:")
    c.rect(180, y_start - 305, 200, 20)
    
    # Allergies
    c.drawString(50, y_start - 340, "Allergies:")
    c.rect(120, y_start - 345, 250, 20)
    
    # Medications
    c.drawString(50, y_start - 380, "Current Medications:")
    c.rect(180, y_start - 385, 250, 20)
    
    # Diagnosis
    c.drawString(50, y_start - 420, "Diagnosis:")
    c.rect(120, y_start - 425, 250, 20)
    
    # Treatment
    c.drawString(50, y_start - 460, "Treatment Plan:")
    c.rect(140, y_start - 465, 250, 20)
    
    c.save()
    return output_path
