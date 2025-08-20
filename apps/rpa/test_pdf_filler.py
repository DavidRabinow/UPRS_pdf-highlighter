#!/usr/bin/env python3
"""
Test script for PDF field filler improvements
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from pdf_field_filler import fill_pdf_fields, find_most_recent_pdf

def test_pdf_filler():
    """Test the PDF filler with sample data."""
    
    print("=" * 70)
    print("PDF Field Filler Test")
    print("=" * 70)
    
    # Sample field values based on the form images
    field_values = {
        'name': 'John Doe',
        'ein': '12-3456789',
        'address': '123 Main Street',
        'email': 'john.doe@example.com',
        'phone': '555-123-4567'
    }
    
    print(f"Field values to test:")
    for key, value in field_values.items():
        print(f"  {key}: {value}")
    
    # Find the most recent PDF
    pdf_path = find_most_recent_pdf()
    if not pdf_path:
        print("❌ No PDF file found in Downloads folder")
        print("Please download a PDF file first and try again.")
        return
    
    print(f"\nFound PDF: {pdf_path.name}")
    
    # Test the PDF filler
    print(f"\nTesting PDF field filling...")
    success = fill_pdf_fields(pdf_path, field_values)
    
    if success:
        print("\n✅ PDF field filling test completed successfully!")
        print(f"Check your Downloads folder for: filled_{pdf_path.name}")
    else:
        print("\n❌ PDF field filling test failed")
        print("Check the logs for more details.")

if __name__ == "__main__":
    test_pdf_filler()

