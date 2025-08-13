#!/usr/bin/env python3
"""
Test Setup Script
Creates sample files and tests the Azure Form Filler setup
"""

import os
import sys
import json
import tempfile
import zipfile
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import flask
        print("✓ Flask imported successfully")
    except ImportError as e:
        print(f"✗ Flask import failed: {e}")
        return False
    
    try:
        import azure.ai.documentintelligence
        print("✓ Azure Document Intelligence imported successfully")
    except ImportError as e:
        print(f"✗ Azure Document Intelligence import failed: {e}")
        return False
    
    try:
        import pypdf
        print("✓ PyPDF imported successfully")
    except ImportError as e:
        print(f"✗ PyPDF import failed: {e}")
        return False
    
    try:
        import reportlab
        print("✓ ReportLab imported successfully")
    except ImportError as e:
        print(f"✗ ReportLab import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("✓ Pillow imported successfully")
    except ImportError as e:
        print(f"✗ Pillow import failed: {e}")
        return False
    
    return True

def test_environment():
    """Test environment configuration"""
    print("\nTesting environment configuration...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    azure_endpoint = os.getenv('AZURE_DI_ENDPOINT')
    azure_key = os.getenv('AZURE_DI_KEY')
    api_secret = os.getenv('API_SHARED_SECRET')
    
    if azure_endpoint and azure_endpoint != 'https://YOUR-RESOURCE-NAME.cognitiveservices.azure.com/':
        print("✓ Azure endpoint configured")
    else:
        print("✗ Azure endpoint not configured (using default)")
    
    if azure_key and azure_key != 'YOUR-AZURE-KEY':
        print("✓ Azure key configured")
    else:
        print("✗ Azure key not configured (using default)")
    
    if api_secret and api_secret != 'change-me':
        print("✓ API secret configured")
    else:
        print("✗ API secret not configured (using default)")
    
    return True

def create_sample_files():
    """Create sample files for testing"""
    print("\nCreating sample files...")
    
    try:
        from pdf_utils import create_sample_pdf
        from converters import create_test_image
        
        # Create sample PDF
        pdf_path = create_sample_pdf("sample_form.pdf")
        print(f"✓ Created sample PDF: {pdf_path}")
        
        # Create sample image
        img_path = create_test_image("sample_image.png")
        print(f"✓ Created sample image: {img_path}")
        
        # Create sample ZIP
        with zipfile.ZipFile("sample_files.zip", 'w') as zip_ref:
            zip_ref.write(pdf_path, "form.pdf")
            zip_ref.write(img_path, "image.png")
        print("✓ Created sample ZIP: sample_files.zip")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to create sample files: {e}")
        return False

def test_api_endpoint():
    """Test the API endpoint (if service is running)"""
    print("\nTesting API endpoint...")
    
    try:
        import requests
        
        # Test health endpoint
        response = requests.get("http://localhost:5001/health", timeout=5)
        if response.status_code == 200:
            print("✓ Health endpoint responding")
            return True
        else:
            print(f"✗ Health endpoint returned {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Service not running on localhost:5001")
        print("  Start the service with: python app.py")
        return False
    except ImportError:
        print("✗ Requests library not available")
        return False
    except Exception as e:
        print(f"✗ API test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Azure Form Filler - Setup Test")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed. Install dependencies with:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Test environment
    test_environment()
    
    # Create sample files
    if not create_sample_files():
        print("\n❌ Sample file creation failed.")
        sys.exit(1)
    
    # Test API endpoint
    test_api_endpoint()
    
    print("\n" + "=" * 40)
    print("✅ Setup test completed!")
    print("\nNext steps:")
    print("1. Configure your Azure credentials in .env")
    print("2. Start the service: python app.py")
    print("3. Test with: curl -X POST http://localhost:5001/process \\")
    print("     -H 'X-API-KEY: your-api-key' \\")
    print("     -F 'file=@sample_form.pdf' \\")
    print("     -F 'fill_map={\"name\":\"Test User\"}' \\")
    print("     -F 'highlight_terms=[\"signature\"]' \\")
    print("     --output test_output.pdf")

if __name__ == "__main__":
    main()
