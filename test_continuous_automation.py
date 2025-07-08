#!/usr/bin/env python3
"""
Test script for continuous automation functionality.
This script demonstrates how to use the new tracking and continuous processing features.
"""

import logging
from automation import SeleniumAutomation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('continuous_automation.log'),
        logging.StreamHandler()
    ]
)

def test_continuous_automation():
    """
    Test the continuous automation functionality.
    """
    print("=== TESTING CONTINUOUS AUTOMATION ===")
    print("This will process multiple Payee Names from the table automatically.")
    print("The system will track the last processed Payee Name and continue from where it left off.")
    print()
    
    # Create automation instance
    automation = SeleniumAutomation()
    
    # Configure settings (optional - these are the defaults)
    automation.max_companies = 10  # Process up to 10 companies
    automation.last_payee_name = None  # Start from the beginning
    
    try:
        # Run the continuous automation
        # The search_text parameter is used for the initial search to populate the table
        search_text = "your_search_criteria_here"  # Replace with your actual search criteria
        
        print(f"Starting continuous automation with search text: '{search_text}'")
        print(f"Maximum companies to process: {automation.max_companies}")
        print()
        
        automation.run(search_text)
        
        print()
        print("=== AUTOMATION COMPLETED ===")
        print(f"Total companies processed: {automation.companies_processed}")
        print(f"Last processed Payee Name: {automation.last_payee_name}")
        print(f"Consecutive failures: {automation.consecutive_failures}")
        
    except Exception as e:
        print(f"❌ Automation failed: {e}")
        logging.error(f"Automation failed: {e}")
    finally:
        print("Test completed.")

def test_resume_automation():
    """
    Test resuming automation from a specific Payee Name.
    This is useful if the automation was interrupted and you want to continue from where it left off.
    """
    print("=== TESTING RESUME AUTOMATION ===")
    print("This will resume automation from a specific Payee Name.")
    print()
    
    # Create automation instance
    automation = SeleniumAutomation()
    
    # Set the last processed Payee Name to resume from that point
    automation.last_payee_name = "EXAMPLE COMPANY LLC"  # Replace with the actual Payee Name
    automation.max_companies = 5  # Process up to 5 more companies
    
    try:
        # Run the continuous automation
        search_text = "your_search_criteria_here"  # Replace with your actual search criteria
        
        print(f"Resuming automation from Payee Name: '{automation.last_payee_name}'")
        print(f"Maximum additional companies to process: {automation.max_companies}")
        print()
        
        automation.run(search_text)
        
        print()
        print("=== RESUME AUTOMATION COMPLETED ===")
        print(f"Total companies processed: {automation.companies_processed}")
        print(f"Final Payee Name processed: {automation.last_payee_name}")
        
    except Exception as e:
        print(f"❌ Resume automation failed: {e}")
        logging.error(f"Resume automation failed: {e}")
    finally:
        print("Resume test completed.")

if __name__ == "__main__":
    # Choose which test to run
    print("Choose a test to run:")
    print("1. Test continuous automation (start from beginning)")
    print("2. Test resume automation (continue from specific Payee Name)")
    print()
    
    choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice == "1":
        test_continuous_automation()
    elif choice == "2":
        test_resume_automation()
    else:
        print("Invalid choice. Running continuous automation test by default.")
        test_continuous_automation() 