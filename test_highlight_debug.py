#!/usr/bin/env python3
"""
Test script to debug PDF highlighting issues
"""

import sys
import os
from pathlib import Path
from pdf_highlighter import analyze_pdf_structure, highlight_pdf_pymupdf
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def test_highlighting_on_pdf(pdf_path: str, highlight_text: str, name_text: str = None):
    """Test highlighting on a specific PDF file."""
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    print(f"Testing highlighting on: {pdf_path.name}")
    print(f"Highlight text: '{highlight_text}'")
    if name_text:
        print(f"Name text: '{name_text}'")
    
    # Analyze PDF structure
    print("\n🔍 Analyzing PDF structure...")
    analysis = analyze_pdf_structure(pdf_path)
    
    if analysis:
        print(f"PDF Analysis:")
        print(f"  - Pages: {analysis.get('total_pages', 0)}")
        print(f"  - Text spans: {len(analysis.get('text_spans', []))}")
        print(f"  - Fonts: {list(analysis.get('fonts_used', set()))}")
        
        # Check for highlight keywords in text spans
        keywords = [kw.strip().lower() for kw in highlight_text.split(',')]
        print(f"\nLooking for keywords: {keywords}")
        
        found_matches = []
        for span in analysis.get('text_spans', []):
            text = span['text'].lower()
            for keyword in keywords:
                if keyword in text:
                    found_matches.append({
                        'keyword': keyword,
                        'text': span['text'],
                        'font': span['font'],
                        'size': span['size']
                    })
        
        if found_matches:
            print(f"✅ Found {len(found_matches)} potential matches:")
            for match in found_matches:
                print(f"  - '{match['keyword']}' in '{match['text']}' (font: {match['font']}, size: {match['size']})")
        else:
            print("❌ No keyword matches found in PDF")
            
            # Show sample texts for debugging
            print(f"\nSample texts from PDF:")
            for i, text in enumerate(analysis.get('sample_texts', [])[:10]):
                print(f"  {i+1}. '{text}'")
    
    # Test highlighting
    print(f"\n🎨 Testing highlighting...")
    output_path = pdf_path.parent / f"test_highlighted_{pdf_path.name}"
    
    success = highlight_pdf_pymupdf(pdf_path, output_path, highlight_text, name_text)
    
    if success:
        print(f"✅ Highlighting completed successfully!")
        print(f"Output file: {output_path}")
    else:
        print(f"❌ Highlighting failed!")

def main():
    """Main function for testing highlighting."""
    if len(sys.argv) < 3:
        print("Usage: python test_highlight_debug.py <pdf_file> <highlight_text> [name_text]")
        print("Example: python test_highlight_debug.py form.pdf 'notary,public' 'John Doe'")
        return
    
    pdf_file = sys.argv[1]
    highlight_text = sys.argv[2]
    name_text = sys.argv[3] if len(sys.argv) > 3 else None
    
    test_highlighting_on_pdf(pdf_file, highlight_text, name_text)

if __name__ == "__main__":
    main() 