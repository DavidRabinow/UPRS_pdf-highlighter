#!/usr/bin/env python3
"""
Simple Selenium Login Automation
Opens Chrome browser, navigates to website, enters credentials, and clicks login button.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time

def main():
    # Configuration - UPDATE THESE VALUES
    WEBSITE_URL = "https://rears.retainedequity.com/#/"
    USERNAME = "aaron"
    PASSWORD = "Welcome1"
    
    # Element selectors - UPDATE THESE IF NEEDED
    USERNAME_SELECTOR = "#usern"  # Username field selector
    PASSWORD_SELECTOR = "#pass"   # Password field selector
    LOGIN_BUTTON_SELECTOR = ".loginBtn"  # Login button selector
    
    driver = None
    
    try:
        print("Starting login automation...")
        
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
        
        # Wait for page to load
        time.sleep(3)
        print("Page loaded successfully")
        
        # 4. Locate and fill username field
        print("Looking for username field...")
        try:
            username_field = driver.find_element(By.CSS_SELECTOR, USERNAME_SELECTOR)
            username_field.clear()
            username_field.send_keys(USERNAME)
            print(f"Username '{USERNAME}' entered successfully")
        except NoSuchElementException:
            print(f"ERROR: Username field not found with selector: {USERNAME_SELECTOR}")
            return
        
        # 5. Locate and fill password field
        print("Looking for password field...")
        try:
            password_field = driver.find_element(By.CSS_SELECTOR, PASSWORD_SELECTOR)
            password_field.clear()
            password_field.send_keys(PASSWORD)
            print(f"Password entered successfully")
        except NoSuchElementException:
            print(f"ERROR: Password field not found with selector: {PASSWORD_SELECTOR}")
            return
        
        # 6. Locate login button (no need to wait, it's always present)
        print("Looking for login button...")
        try:
            login_button = driver.find_element(By.CSS_SELECTOR, LOGIN_BUTTON_SELECTOR)
            print("Login button found successfully")
        except NoSuchElementException:
            print(f"ERROR: Login button not found with selector: {LOGIN_BUTTON_SELECTOR}")
            return
        
        # 7. Click the login button
        print("Clicking login button...")
        login_button.click()
        print("Login button clicked successfully")
        
        # 8. Keep browser open and visible
        print("Login process completed!")
        print("Browser will remain open. Close it manually when you're done.")
        print("You can add more automation steps here after login...")
        
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