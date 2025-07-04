#!/usr/bin/env python3
"""
Navigation Automation - Process Imported Files
Continues from authenticated homepage to navigate to Process Imported Files section.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time

def main():
    # Configuration - UPDATE THESE SELECTORS IF NEEDED
    SEARCH_PROPERTIES_SELECTOR = "a[href*='search'], .search-link, #search"  # Search Properties navigation
    PROCESS_IMPORTED_FILES_SELECTOR = "a[href*='process'], .process-link, #process"  # Process Imported Files option
    
    driver = None
    
    try:
        print("Starting navigation to Process Imported Files...")
        
        # 1. Set up Chrome browser (visible, not headless)
        print("Setting up Chrome browser...")
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1200,800")
        
        # 2. Open Chrome browser
        driver = webdriver.Chrome(options=chrome_options)
        print("Chrome browser opened successfully")
        
        # 3. Navigate to the authenticated homepage
        print("Navigating to authenticated homepage...")
        driver.get("https://rears.retainedequity.com/#/")
        
        # Wait for page to load
        time.sleep(3)
        print("Homepage loaded successfully")
        
        # 4. Locate and click "Search Properties" navigation option
        print("Looking for 'Search Properties' navigation option...")
        try:
            # Try multiple selectors for Search Properties
            search_selectors = [
                "a[href*='search']",
                ".search-link", 
                "#search",
                "a:contains('Search Properties')",
                "//a[contains(text(), 'Search Properties')]"
            ]
            
            search_properties_found = False
            for selector in search_selectors:
                try:
                    if selector.startswith("//"):
                        # XPath selector
                        search_element = driver.find_element(By.XPATH, selector)
                    else:
                        # CSS selector
                        search_element = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    print(f"Found 'Search Properties' with selector: {selector}")
                    search_element.click()
                    print("Clicked 'Search Properties' successfully")
                    search_properties_found = True
                    break
                    
                except NoSuchElementException:
                    continue
            
            if not search_properties_found:
                print("ERROR: 'Search Properties' navigation option not found")
                return
                
        except Exception as e:
            print(f"ERROR: Failed to click 'Search Properties': {e}")
            return
        
        # 5. Wait for dropdown menu to appear
        print("Waiting for dropdown menu to appear...")
        time.sleep(2)
        
        # 6. Locate and click "Process Imported Files" in dropdown
        print("Looking for 'Process Imported Files' option in dropdown...")
        try:
            # Try multiple selectors for Process Imported Files
            process_selectors = [
                "a[href*='process']",
                ".process-link",
                "#process", 
                "a:contains('Process Imported Files')",
                "//a[contains(text(), 'Process Imported Files')]",
                "//li[contains(text(), 'Process Imported Files')]",
                "//div[contains(text(), 'Process Imported Files')]"
            ]
            
            process_files_found = False
            for selector in process_selectors:
                try:
                    if selector.startswith("//"):
                        # XPath selector
                        process_element = driver.find_element(By.XPATH, selector)
                    else:
                        # CSS selector
                        process_element = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    print(f"Found 'Process Imported Files' with selector: {selector}")
                    process_element.click()
                    print("Clicked 'Process Imported Files' successfully")
                    process_files_found = True
                    break
                    
                except NoSuchElementException:
                    continue
            
            if not process_files_found:
                print("ERROR: 'Process Imported Files' option not found in dropdown")
                return
                
        except Exception as e:
            print(f"ERROR: Failed to click 'Process Imported Files': {e}")
            return
        
        # 7. Wait for the next page to load
        print("Waiting for Process Imported Files page to load...")
        time.sleep(5)
        
        # 8. Verify we're on the correct page
        print("Navigation completed successfully!")
        print("You should now be on the Process Imported Files page.")
        print("Browser will remain open. Close it manually when you're done.")
        print("You can add more automation steps here...")
        
        # Keep the script running so browser stays open
        input("Press Enter to close the browser...")
        
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
    
    finally:
        # 9. Basic error handling - safely close browser
        if driver:
            print("Closing browser...")
            driver.quit()
            print("Browser closed successfully")

if __name__ == "__main__":
    main() 