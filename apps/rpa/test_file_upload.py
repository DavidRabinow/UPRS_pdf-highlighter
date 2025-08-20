#!/usr/bin/env python3
"""
Test script for file upload functionality
"""

import requests
import os
import tempfile

def test_file_upload():
    """Test the file upload functionality"""
    
    # Create a test PDF file
    test_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Test PDF) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF"
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
        temp_file.write(test_content)
        temp_file_path = temp_file.name
    
    try:
        # Prepare the form data
        files = {
            'pdf_file': ('test.pdf', open(temp_file_path, 'rb'), 'application/pdf')
        }
        
        data = {
            'highlight_text': 'test, highlighting, signatures',
            'name_text': 'John Doe',
            'signature_options': '{"notary": true, "claimant": false, "notaryPublic": true, "representative": false, "authorized": false, "applicant": false}'
        }
        
        # Make the request
        response = requests.post('http://localhost:5002/start_automation', files=files, data=data)
        
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.json()}")
        
        if response.status_code == 200:
            print("✅ File upload test passed!")
        else:
            print("❌ File upload test failed!")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

if __name__ == "__main__":
    test_file_upload()
