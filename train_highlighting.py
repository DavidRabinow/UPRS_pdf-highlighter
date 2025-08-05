#!/usr/bin/env python3
"""
Training script for PDF highlighting - helps improve highlighting accuracy
by testing specific keywords against known examples.
"""

import sys
import os
from pathlib import Path
from pdf_highlighter import analyze_pdf_structure, highlight_pdf_pymupdf
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def test_keyword_accuracy(pdf_path: str, test_keywords: list):
    """Test how well specific keywords highlight the right text."""
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    print(f"Testing keyword accuracy on: {pdf_path.name}")
    
    # Analyze PDF structure first
    analysis = analyze_pdf_structure(pdf_path)
    
    if not analysis:
        print("❌ Could not analyze PDF structure")
        return
    
    print(f"\n📊 PDF Analysis:")
    print(f"  - Pages: {analysis.get('total_pages', 0)}")
    print(f"  - Text spans: {len(analysis.get('text_spans', []))}")
    
    # Test each keyword
    for keyword in test_keywords:
        print(f"\n🔍 Testing keyword: '{keyword}'")
        
        # Find all text that contains this keyword
        matches = []
        for span in analysis.get('text_spans', []):
            text = span['text'].lower()
            if keyword.lower() in text:
                matches.append({
                    'text': span['text'],
                    'font': span['font'],
                    'size': span['size'],
                    'page': span['page']
                })
        
        if matches:
            print(f"  ✅ Found {len(matches)} matches:")
            for i, match in enumerate(matches, 1):
                print(f"    {i}. '{match['text']}' (font: {match['font']}, size: {match['size']}, page: {match['page']})")
        else:
            print(f"  ❌ No matches found for '{keyword}'")
    
    # Test highlighting with each keyword
    print(f"\n🎨 Testing highlighting...")
    for keyword in test_keywords:
        print(f"\n  Testing: '{keyword}'")
        output_path = pdf_path.parent / f"test_{keyword.replace(' ', '_')}_{pdf_path.name}"
        
        success = highlight_pdf_pymupdf(pdf_path, output_path, keyword)
        
        if success:
            print(f"    ✅ Highlighted PDF created: {output_path.name}")
        else:
            print(f"    ❌ Highlighting failed for '{keyword}'")

def suggest_keywords_for_form(form_type: str):
    """Suggest appropriate keywords based on form type."""
    suggestions = {
        "notary": [
            "notary",
            "notary public", 
            "notary signature",
            "commission expires",
            "sworn and subscribed",
            "before me"
        ],
        "signature": [
            "signature",
            "signature of claimant",
            "signature of co-claimant",
            "printed name",
            "date"
        ],
        "claimant": [
            "claimant",
            "claimant name",
            "printed name",
            "title",
            "state of",
            "county of"
        ],
        "affidavit": [
            "affidavit",
            "sworn",
            "perjury",
            "true",
            "correct",
            "full"
        ]
    }
    
    if form_type in suggestions:
        return suggestions[form_type]
    else:
        return ["signature", "notary", "claimant", "date"]

def main():
    """Main function for training highlighting."""
    if len(sys.argv) < 2:
        print("Usage: python train_highlighting.py <pdf_file> [keywords...]")
        print("Examples:")
        print("  python train_highlighting.py form.pdf")
        print("  python train_highlighting.py form.pdf notary,signature,claimant")
        print("  python train_highlighting.py form.pdf --suggest notary")
        return
    
    pdf_file = sys.argv[1]
    
    if len(sys.argv) > 2 and sys.argv[2] == "--suggest":
        if len(sys.argv) > 3:
            form_type = sys.argv[3]
            keywords = suggest_keywords_for_form(form_type)
            print(f"Suggested keywords for {form_type} forms:")
            for keyword in keywords:
                print(f"  - {keyword}")
        else:
            print("Available form types: notary, signature, claimant, affidavit")
        return
    
    # Get keywords from command line or use defaults
    if len(sys.argv) > 2:
        keywords = sys.argv[2].split(',')
    else:
        # Default keywords for testing
        keywords = ["notary", "signature", "claimant", "date"]
    
    print(f"Testing keywords: {keywords}")
    test_keyword_accuracy(pdf_file, keywords)

if __name__ == "__main__":
    main() 