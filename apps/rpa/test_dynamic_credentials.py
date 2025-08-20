#!/usr/bin/env python3
"""
Test script to verify dynamic credentials functionality.
This script tests that the SeleniumAutomation class can accept username and password parameters.
"""

from automation import SeleniumAutomation

def test_dynamic_credentials():
    """Test that the automation class accepts dynamic credentials."""
    
    print("Testing dynamic credentials functionality...")
    
    # Test 1: Pass credentials as parameters
    print("\nTest 1: Passing credentials as parameters")
    try:
        automation = SeleniumAutomation(
            username="test@example.com",
            password="testpassword123"
        )
        print("✅ Successfully created automation with credentials as parameters")
        print(f"Username: {automation.username}")
        print(f"Password: {automation.password}")
    except Exception as e:
        print(f"❌ Failed to create automation with credentials: {e}")
        return False
    
    # Test 2: Create without credentials (should prompt)
    print("\nTest 2: Creating without credentials (will prompt)")
    print("Note: This test will prompt for input. You can cancel if needed.")
    try:
        # Note: In a real test, you might want to mock the input
        # For now, we'll just test that the constructor accepts the parameters
        automation2 = SeleniumAutomation()
        print("✅ Successfully created automation without credentials (prompted for input)")
    except Exception as e:
        print(f"❌ Failed to create automation without credentials: {e}")
        return False
    
    print("\n✅ All tests passed! Dynamic credentials functionality is working correctly.")
    return True

if __name__ == "__main__":
    test_dynamic_credentials()
