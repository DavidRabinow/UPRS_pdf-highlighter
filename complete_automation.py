#!/usr/bin/env python3
"""
Complete UPRS Automation
Handles login and navigation to Process Imported Files in one script.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time

def main():
    # Configuration
    WEBSITE_URL = "https://rears.retainedequity.com/#/"
    USERNAME = "aaron"
    PASSWORD = "Welcome1"
    
    # Login selectors
    USERNAME_SELECTOR = "#usern"
    PASSWORD_SELECTOR = "#pass"
    LOGIN_BUTTON_SELECTOR = ".loginBtn"
    
    # Navigation selectors
    SEARCH_PROPERTIES_SELECTOR = "a[href*='search'], .search-link, #search"
    PROCESS_IMPORTED_FILES_SELECTOR = "a[href*='process'], .process-link, #process"
    
    driver = None
    
    try:
        print("Starting complete UPRS automation...")
        
        # 1. Set up Chrome browser (visible, not headless)
        print("Setting up Chrome browser...")
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1200,800")
        
        # 2. Open Chrome browser
        driver = webdriver.Chrome(options=chrome_options)
        print("Chrome browser opened successfully")
        
        # 3. Navigate to the website
        print(f"Navigating to: {WEBSITE_URL}")
        driver.get(WEBSITE_URL)
        time.sleep(3)
        print("Page loaded successfully")
        
        # 4. LOGIN PROCESS
        print("=== STARTING LOGIN PROCESS ===")
        
        # Enter username
        print("Looking for username field...")
        try:
            username_field = driver.find_element(By.CSS_SELECTOR, USERNAME_SELECTOR)
            username_field.clear()
            username_field.send_keys(USERNAME)
            print(f"Username '{USERNAME}' entered successfully")
        except NoSuchElementException:
            print(f"ERROR: Username field not found with selector: {USERNAME_SELECTOR}")
            return
        
        # Enter password
        print("Looking for password field...")
        try:
            password_field = driver.find_element(By.CSS_SELECTOR, PASSWORD_SELECTOR)
            password_field.clear()
            password_field.send_keys(PASSWORD)
            print("Password entered successfully")
        except NoSuchElementException:
            print(f"ERROR: Password field not found with selector: {PASSWORD_SELECTOR}")
            return
        
        # Click login button
        print("Looking for login button...")
        try:
            login_button = driver.find_element(By.CSS_SELECTOR, LOGIN_BUTTON_SELECTOR)
            print("Login button found successfully")
        except NoSuchElementException:
            print(f"ERROR: Login button not found with selector: {LOGIN_BUTTON_SELECTOR}")
            return
        
        print("Clicking login button...")
        login_button.click()
        print("Login button clicked successfully")
        
        # Wait for login to complete
        print("Waiting for login to complete...")
        time.sleep(5)
        print("Login completed successfully!")
        
        # 5. NAVIGATION PROCESS
        print("=== STARTING NAVIGATION PROCESS ===")
        
        # Click "Search Properties" navigation option
        print("Looking for 'Search Properties' navigation option...")
        try:
            # Try multiple selectors for Search Properties
            search_selectors = [
                "a[href*='search']",
                ".search-link", 
                "#search",
                "//a[contains(text(), 'Search Properties')]",
                "//span[contains(text(), 'Search Properties')]"
            ]
            
            search_properties_found = False
            for selector in search_selectors:
                try:
                    if selector.startswith("//"):
                        search_element = driver.find_element(By.XPATH, selector)
                    else:
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
        
        # Wait for dropdown menu to appear
        print("Waiting for dropdown menu to appear...")
        time.sleep(2)
        
        # Click "Process Imported Files" in dropdown
        print("Looking for 'Process Imported Files' option in dropdown...")
        try:
            # Try multiple selectors for Process Imported Files
            process_selectors = [
                "a[href*='process']",
                ".process-link",
                "#process", 
                "//a[contains(text(), 'Process Imported Files')]",
                "//li[contains(text(), 'Process Imported Files')]",
                "//div[contains(text(), 'Process Imported Files')]",
                "//span[contains(text(), 'Process Imported Files')]"
            ]
            
            process_files_found = False
            for selector in process_selectors:
                try:
                    if selector.startswith("//"):
                        process_element = driver.find_element(By.XPATH, selector)
                    else:
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
        
        # Wait for the next page to load
        print("Waiting for Process Imported Files page to load...")
        time.sleep(5)
        
        # 6. COMPLETION
        print("=== AUTOMATION COMPLETED SUCCESSFULLY ===")
        print("You should now be on the Process Imported Files page.")
        print("Browser will remain open. Close it manually when you're done.")
        print("You can add more automation steps here...")
        
        # Keep the script running so browser stays open
        input("Press Enter to close the browser...")
        
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
    
    finally:
        # Basic error handling - safely close browser
        if driver:
            print("Closing browser...")
            driver.quit()
            print("Browser closed successfully")

if __name__ == "__main__":
    main() 