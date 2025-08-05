#!/usr/bin/env python3
"""
Test different highlighting profiles on PDF files
"""

import sys
import os
from pathlib import Path
from pdf_highlighter import get_highlighting_profile, highlight_pdf_pymupdf, analyze_pdf_structure
import logging

# Enable debug logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_all_profiles(pdf_path: str):
    """Test all available profiles on a PDF file."""
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    print(f"Testing all profiles on: {pdf_path.name}")
    
    # Get all available profiles
    profiles = ["notary", "signature", "claimant", "affidavit", "comprehensive"]
    
    # Analyze PDF structure first
    print("\n🔍 Analyzing PDF structure...")
    analysis = analyze_pdf_structure(pdf_path)
    
    if analysis:
        print(f"PDF Analysis:")
        print(f"  - Pages: {analysis.get('total_pages', 0)}")
        print(f"  - Text spans: {len(analysis.get('text_spans', []))}")
        print(f"  - Sample texts: {analysis.get('sample_texts', [])[:3]}")  # Show first 3
    
    # Test each profile
    for profile_name in profiles:
        print(f"\n🎨 Testing profile: '{profile_name}'")
        
        # Get profile data
        profile_data = get_highlighting_profile(profile_name)
        keywords = profile_data.get('keywords', [])
        description = profile_data.get('description', '')
        
        print(f"  Description: {description}")
        print(f"  Keywords: {keywords}")
        
        # Check which keywords are found in the PDF
        found_keywords = []
        for keyword in keywords:
            for span in analysis.get('text_spans', []):
                if keyword in span['text'].lower():
                    found_keywords.append(keyword)
                    break
        
        if found_keywords:
            print(f"  ✅ Found keywords: {found_keywords}")
        else:
            print(f"  ❌ No keywords found")
        
        # Create highlighted PDF with this profile
        output_path = pdf_path.parent / f"test_profile_{profile_name}_{pdf_path.name}"
        
        success = highlight_pdf_pymupdf(pdf_path, output_path, profile=profile_name)
        
        if success:
            print(f"  ✅ Created: {output_path.name}")
        else:
            print(f"  ❌ Failed to create highlighted PDF")

def show_profile_info():
    """Show information about all available profiles."""
    print("Available highlighting profiles:")
    print("=" * 50)
    
    profiles = ["notary", "signature", "claimant", "affidavit", "comprehensive"]
    
    for profile_name in profiles:
        profile_data = get_highlighting_profile(profile_name)
        keywords = profile_data.get('keywords', [])
        description = profile_data.get('description', '')
        
        print(f"\n📋 {profile_name.upper()} PROFILE:")
        print(f"  Description: {description}")
        print(f"  Keywords: {keywords}")
    
    print(f"\nUsage examples:")
    print(f"  python pdf_highlighter.py --profile notary")
    print(f"  python pdf_highlighter.py --profile comprehensive")
    print(f"  python pdf_highlighter.py 'notary,signature' --profile claimant")

def main():
    """Main function for testing profiles."""
    if len(sys.argv) < 2:
        print("Usage: python test_profiles.py <pdf_file>")
        print("       python test_profiles.py --info")
        print("Examples:")
        print("  python test_profiles.py form.pdf")
        print("  python test_profiles.py --info")
        return
    
    if sys.argv[1] == "--info":
        show_profile_info()
        return
    
    pdf_file = sys.argv[1]
    test_all_profiles(pdf_file)

if __name__ == "__main__":
    main() 