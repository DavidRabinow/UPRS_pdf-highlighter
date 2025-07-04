#!/usr/bin/env python3
"""
Test script for PRECISE Selenium automation
This script tests the automation functionality independently of the Flask app.
"""

import logging
from automation import SeleniumAutomation

# Configure logging to see console output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_automation():
    """
    Test the PRECISE automation with a sample search text.
    """
    print("=== TESTING PRECISE SELENIUM AUTOMATION ===")
    print("This will:")
    print("1. Open Chrome browser (VISIBLE - not headless)")
    print("2. Navigate to the website")
    print("3. Login with credentials")
    print("4. Navigate to Search Properties > Process Imported Files")
    print("5. Find the PRECISE search field under 'File' label")
    print("   - Field should have 'select...' placeholder")
    print("   - Field should have dropdown arrow on right side")
    print("6. Enter the test search text")
    print("7. Click the PRECISE green search button")
    print("8. Take screenshot for verification")
    print("9. Keep browser open for 30 seconds")
    print()
    
    # Test search text
    test_search_text = "test_file_123"
    
    print(f"Test search text: '{test_search_text}'")
    print()
    
    try:
        # Create automation instance
        automation = SeleniumAutomation()
        
        # Run the automation
        automation.run(test_search_text)
        
        print("=== PRECISE TEST COMPLETED SUCCESSFULLY ===")
        print("✅ Search field under 'File' was located correctly")
        print("✅ Search text was entered successfully")
        print("✅ Green search button was clicked")
        print("✅ Screenshot saved for verification")
        
    except Exception as e:
        print(f"=== PRECISE TEST FAILED: {e} ===")
        print("❌ Check the console logs above for detailed error information")
        print("❌ Verify the page structure and update selectors if needed")
        raise

if __name__ == "__main__":
    test_automation() 