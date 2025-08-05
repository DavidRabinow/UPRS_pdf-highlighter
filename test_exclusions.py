#!/usr/bin/env python3
"""
Test script to verify that exclude patterns work correctly
"""

import sys
import os
from pathlib import Path
from pdf_highlighter import get_highlighting_profile, highlight_pdf_pymupdf, analyze_pdf_structure
import logging

# Enable debug logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_exclusion_patterns(pdf_path: str):
    """Test that exclude patterns prevent unwanted highlighting."""
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    print(f"Testing exclusion patterns on: {pdf_path.name}")
    
    # Test notary profile specifically
    profile_name = "notary"
    profile_data = get_highlighting_profile(profile_name)
    
    print(f"\n📋 Testing {profile_name.upper()} PROFILE:")
    print(f"  Keywords: {profile_data.get('keywords', [])}")
    print(f"  Exclude patterns: {profile_data.get('exclude_patterns', [])}")
    
    # Analyze PDF structure
    analysis = analyze_pdf_structure(pdf_path)
    
    if analysis:
        print(f"\n🔍 PDF Analysis:")
        print(f"  - Pages: {analysis.get('total_pages', 0)}")
        print(f"  - Text spans: {len(analysis.get('text_spans', []))}")
        
        # Check for keywords and exclusions
        keywords = profile_data.get('keywords', [])
        exclude_patterns = profile_data.get('exclude_patterns', [])
        
        print(f"\n🔍 Checking for keywords and exclusions:")
        
        found_keywords = []
        found_exclusions = []
        
        for span in analysis.get('text_spans', []):
            text = span['text'].lower()
            
            # Check for keywords
            for keyword in keywords:
                if keyword in text:
                    found_keywords.append({
                        'keyword': keyword,
                        'text': span['text'],
                        'font': span['font'],
                        'size': span['size']
                    })
            
            # Check for exclusions
            for exclude_pattern in exclude_patterns:
                if exclude_pattern in text:
                    found_exclusions.append({
                        'pattern': exclude_pattern,
                        'text': span['text'],
                        'font': span['font'],
                        'size': span['size']
                    })
        
        if found_keywords:
            print(f"  ✅ Found keywords: {len(found_keywords)}")
            for item in found_keywords:
                print(f"    - '{item['keyword']}' in '{item['text']}'")
        else:
            print(f"  ❌ No keywords found")
        
        if found_exclusions:
            print(f"  🚫 Found exclusions: {len(found_exclusions)}")
            for item in found_exclusions:
                print(f"    - '{item['pattern']}' in '{item['text']}' (should NOT be highlighted)")
        else:
            print(f"  ✅ No exclusions found")
    
    # Test highlighting
    print(f"\n🎨 Testing highlighting with {profile_name} profile...")
    output_path = pdf_path.parent / f"test_exclusions_{profile_name}_{pdf_path.name}"
    
    success = highlight_pdf_pymupdf(pdf_path, output_path, profile=profile_name)
    
    if success:
        print(f"  ✅ Created: {output_path.name}")
        print(f"  📝 Check the output PDF to verify 'Commission Expires' is NOT highlighted")
    else:
        print(f"  ❌ Failed to create highlighted PDF")

def main():
    """Main function for testing exclusions."""
    if len(sys.argv) < 2:
        print("Usage: python test_exclusions.py <pdf_file>")
        print("Example: python test_exclusions.py form.pdf")
        return
    
    pdf_file = sys.argv[1]
    test_exclusion_patterns(pdf_file)

if __name__ == "__main__":
    main() 