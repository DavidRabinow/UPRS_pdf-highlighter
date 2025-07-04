#!/usr/bin/env python3
"""
Selenium Automation Module
Contains the browser automation logic for the Flask web application.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import logging

# Configure logging
logger = logging.getLogger(__name__)

class SeleniumAutomation:
    """
    Selenium automation class that handles browser automation tasks.
    """
    
    def __init__(self):
        """
        Initialize the automation with configuration.
        """
        # Configuration - UPDATE THESE VALUES AS NEEDED
        self.website_url = "https://rears.retainedequity.com/#/"
        self.username = "aaron"
        self.password = "Welcome1"
        
        # Element selectors - UPDATE THESE IF NEEDED
        self.username_selector = "#usern"
        self.password_selector = "#pass"
        self.login_button_selector = ".loginBtn"
        
        # Navigation selectors
        self.search_properties_selector = "a[href*='search'], .search-link, #search"
        self.process_imported_files_selector = "a[href*='process'], .process-link, #process"
        
        # PRECISE selectors for the search field under "File" with dropdown arrow
        # These selectors are designed to find the specific field with "select..." placeholder
        self.file_search_field_selectors = [
            # Target the visible select input first (based on debug output)
            "input[placeholder='select...'][class*='ui-igcombo-field']",
            "//input[@placeholder='select...' and contains(@class, 'ui-igcombo-field')]",
            
            # Look for select inputs near the "File" label
            "//label[@id='lblFile']/following-sibling::input[@placeholder='select...']",
            "//label[@id='lblFile']/../input[@placeholder='select...']",
            "//label[@id='lblFile']/../../input[@placeholder='select...']",
            
            # Look for select inputs in the same container as "File" label
            "//label[contains(text(), 'File')]/following-sibling::input[@placeholder='select...']",
            "//label[contains(text(), 'File')]/../input[@placeholder='select...']",
            "//label[contains(text(), 'File')]/../../input[@placeholder='select...']",
            
            # Look for select inputs near "forFile" class
            "//span[@class='forFile floatR']/../input[@placeholder='select...']",
            "//span[@class='forFile floatR']/../../input[@placeholder='select...']",
            
            # Direct input field with exact placeholder
            "input[placeholder='select...']",
            "input[placeholder*='select'][placeholder*='...']",
            
            # Look for input fields with dropdown arrow (common patterns)
            "//input[@placeholder='select...' and following-sibling::*[contains(@class, 'arrow')]]",
            "//input[@placeholder='select...' and following-sibling::*[contains(@class, 'dropdown')]]",
            "//input[@placeholder='select...' and following-sibling::*[contains(@class, 'chevron')]]",
            
            # Fallback: Any input with "select..." placeholder
            "//input[contains(@placeholder, 'select')]",
            "input[placeholder*='select']",
            "input[placeholder*='Select']"
        ]
        
        # PRECISE selectors for the bright green "Search" button
        # These selectors target the small bright green "Search" button positioned below the input field
        self.green_search_button_selectors = [
            # Most specific selectors for bright green "Search" button with exact text
            "//button[text()='Search' and contains(@class, 'green')]",
            "//button[text()='Search' and contains(@class, 'btn-success')]",
            "//button[text()='Search' and contains(@class, 'btn-green')]",
            "//button[text()='Search' and contains(@style, 'green')]",
            "//button[text()='Search' and contains(@style, 'background-color: green')]",
            "//button[text()='Search' and contains(@style, 'background: green')]",
            
            # Look for "Search" button positioned BELOW the input field (vertically aligned)
            "//input[@placeholder='select...']/following-sibling::button[text()='Search']",
            "//input[@placeholder='select...']/../following-sibling::button[text()='Search']",
            "//input[@placeholder='select...']/../../button[text()='Search']",
            "//input[@placeholder='select...']/ancestor::div[1]//button[text()='Search']",
            
            # Look for "Search" button positioned below the "File" label area
            "//label[contains(text(), 'File')]/following-sibling::button[text()='Search']",
            "//label[contains(text(), 'File')]/../following-sibling::button[text()='Search']",
            "//label[contains(text(), 'File')]/../../button[text()='Search']",
            "//label[contains(text(), 'File')]/ancestor::div[1]//button[text()='Search']",
            
            # Look for "Search" button in the same container as the input field
            "//input[@placeholder='select...']/ancestor::div[1]//button[text()='Search']",
            "//input[@placeholder='select...']/ancestor::form[1]//button[text()='Search']",
            "//input[@placeholder='select...']/ancestor::section[1]//button[text()='Search']",
            
            # CSS selectors for bright green "Search" button
            "button[class*='green'][class*='search']",
            "button.btn-success:contains('Search')",
            "button.btn-green:contains('Search')",
            "button.search-btn:contains('Search')",
            "button[style*='green']:contains('Search')",
            
            # Input submit buttons with "Search" value
            "input[type='submit'][value='Search']",
            "input[type='submit'][value*='Search']",
            "//input[@type='submit' and @value='Search']",
            "//input[@type='submit' and contains(@value, 'Search')]",
            
            # Look for any button with "Search" text positioned after the input field
            "//input[@placeholder='select...']/following::button[contains(text(), 'Search')][1]",
            "//input[@placeholder='select...']/following::button[text()='Search'][1]",
            
            # Fallback: Any button with "Search" text (case-insensitive)
            "//button[contains(text(), 'Search')]",
            "//button[contains(text(), 'search')]",
            "//button[contains(translate(text(), 'SEARCH', 'search'), 'search')]",
            
            # Fallback: Any green button positioned after the input field
            "//input[@placeholder='select...']/following::button[contains(@class, 'green')][1]",
            "//input[@placeholder='select...']/following::button[contains(@class, 'btn-success')][1]",
            "//input[@placeholder='select...']/following::button[contains(@class, 'btn-green')][1]"
        ]
        
        self.driver = None
        
    def setup_browser(self):
        """
        Set up Chrome browser with appropriate options.
        """
        logger.info("Setting up Chrome browser...")
        
        chrome_options = Options()
        
        # Keep browser visible (not headless) - CRITICAL REQUIREMENT
        # chrome_options.add_argument("--headless")  # COMMENTED OUT - browser must be visible
        
        # Additional options for better automation
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Set window size for better visibility
        chrome_options.add_argument("--window-size=1200,800")
        
        # Initialize the driver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logger.info("Chrome browser initialized successfully - BROWSER IS VISIBLE")
        
    def navigate_to_website(self):
        """
        Navigate to the target website.
        """
        logger.info(f"Navigating to: {self.website_url}")
        self.driver.get(self.website_url)
        time.sleep(3)
        logger.info("Successfully navigated to website")
        
    def perform_login(self):
        """
        Perform login process (if needed).
        You can modify this method or remove it if login is not required.
        """
        logger.info("=== STARTING LOGIN PROCESS ===")
        
        # Enter username
        logger.info("Looking for username field...")
        try:
            username_field = self.driver.find_element(By.CSS_SELECTOR, self.username_selector)
            username_field.clear()
            username_field.send_keys(self.username)
            logger.info(f"Username '{self.username}' entered successfully")
        except NoSuchElementException:
            logger.error(f"ERROR: Username field not found with selector: {self.username_selector}")
            raise
        
        # Enter password
        logger.info("Looking for password field...")
        try:
            password_field = self.driver.find_element(By.CSS_SELECTOR, self.password_selector)
            password_field.clear()
            password_field.send_keys(self.password)
            logger.info("Password entered successfully")
        except NoSuchElementException:
            logger.error(f"ERROR: Password field not found with selector: {self.password_selector}")
            raise
        
        # Click login button
        logger.info("Looking for login button...")
        try:
            login_button = self.driver.find_element(By.CSS_SELECTOR, self.login_button_selector)
            logger.info("Login button found successfully")
        except NoSuchElementException:
            logger.error(f"ERROR: Login button not found with selector: {self.login_button_selector}")
            raise
        
        logger.info("Clicking login button...")
        login_button.click()
        logger.info("Login button clicked successfully")
        
        # Wait for login to complete
        logger.info("Waiting for login to complete...")
        time.sleep(5)
        logger.info("Login completed successfully!")
        
    def navigate_to_search_properties(self):
        """
        Navigate to Search Properties section.
        """
        logger.info("=== NAVIGATING TO SEARCH PROPERTIES ===")
        
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
                    search_element = self.driver.find_element(By.XPATH, selector)
                else:
                    search_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                
                logger.info(f"Found 'Search Properties' with selector: {selector}")
                search_element.click()
                logger.info("Clicked 'Search Properties' successfully")
                search_properties_found = True
                break
                
            except NoSuchElementException:
                continue
        
        if not search_properties_found:
            logger.error("ERROR: 'Search Properties' navigation option not found")
            raise Exception("Search Properties not found")
            
        # Wait for dropdown menu to appear
        logger.info("Waiting for dropdown menu to appear...")
        time.sleep(2)
        
    def navigate_to_process_imported_files(self):
        """
        Navigate to Process Imported Files section.
        """
        logger.info("=== NAVIGATING TO PROCESS IMPORTED FILES ===")
        
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
                    process_element = self.driver.find_element(By.XPATH, selector)
                else:
                    process_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                
                logger.info(f"Found 'Process Imported Files' with selector: {selector}")
                process_element.click()
                logger.info("Clicked 'Process Imported Files' successfully")
                process_files_found = True
                break
                
            except NoSuchElementException:
                continue
        
        if not process_files_found:
            logger.error("ERROR: 'Process Imported Files' option not found in dropdown")
            raise Exception("Process Imported Files not found")
        
        # Wait for the next page to load
        logger.info("Waiting for Process Imported Files page to load...")
        time.sleep(5)
        
    def find_and_fill_file_search_field(self, search_text):
        """
        Find the PRECISE search field under "File" with dropdown arrow and fill it with the provided text.
        
        This method uses precise selectors to locate the specific field that:
        - Is positioned under the "File" label
        - Shows "select..." placeholder text
        - Has a dropdown arrow on the right side
        
        Args:
            search_text (str): The text to enter in the search field
        """
        logger.info(f"=== SEARCHING FOR PRECISE FILE SEARCH FIELD ===")
        logger.info(f"Looking for search field under 'File' label to enter text: '{search_text}'")
        logger.info("Field should have 'select...' placeholder and dropdown arrow")
        
        # First, try to find ALL select inputs and prioritize visible ones
        logger.info("Searching for all select inputs to find the visible one...")
        all_select_inputs = self.driver.find_elements(By.XPATH, "//input[contains(@placeholder, 'select')]")
        
        visible_select_input = None
        for i, input_field in enumerate(all_select_inputs):
            try:
                placeholder = input_field.get_attribute('placeholder') or ''
                is_visible = input_field.is_displayed()
                is_enabled = input_field.is_enabled()
                class_attr = input_field.get_attribute('class') or ''
                
                logger.info(f"Select input {i+1}: placeholder='{placeholder}', visible={is_visible}, enabled={is_enabled}, class='{class_attr}'")
                
                # Prioritize visible fields
                if is_visible and is_enabled and 'select' in placeholder.lower():
                    logger.info(f"✅ Found visible select input {i+1} - this is our target!")
                    visible_select_input = input_field
                    break
                    
            except Exception as e:
                logger.warning(f"Error checking select input {i+1}: {e}")
        
        if visible_select_input:
            logger.info("✅ Using visible select input for interaction")
            search_field = visible_select_input
            used_selector = "visible_select_input"
        else:
            logger.error("❌ ERROR: Could not find a visible search field under 'File'.")
            raise Exception("Visible search field under 'File' not found - automation cannot continue.")
        
        # Now interact with the found search field
        try:
            logger.info("Clicking the search field to activate it...")
            search_field.click()
            time.sleep(1)
            logger.info(f"Clearing field and entering search text: '{search_text}'")
            search_field.clear()
            search_field.send_keys(search_text)
            logger.info(f"✅ SUCCESS: Successfully entered search text: '{search_text}'")
            
        except Exception as interaction_error:
            logger.error(f"❌ ERROR: Failed to interact with search field: {interaction_error}")
            raise Exception(f"Search field interaction failed: {interaction_error}")
        
        # Wait a moment for the text to be entered
        time.sleep(2)
        logger.info(f"✅ Search text entry completed using selector: {used_selector}")

    def find_and_click_green_search_button(self):
        """
        Find and click the PRECISE bright green "Search" button positioned below the input field.
        
        This method locates the small bright green "Search" button that is:
        - Bright green with white text "Search"
        - Horizontally aligned slightly to the left of the text input field
        - Vertically positioned below the input field where text was typed
        - Visually distinct from the dropdown suggestion list
        """
        logger.info("=== SEARCHING FOR PRECISE BRIGHT GREEN 'SEARCH' BUTTON ===")
        logger.info("Looking for small bright green 'Search' button positioned below the input field")
        logger.info("Button should be bright green with white text 'Search'")
        logger.info("Positioned horizontally to the left of the input field and vertically below it")
        logger.info("Visually distinct from any dropdown suggestion list")
        
        # Try to find the green "Search" button using PRECISE selectors
        search_button_found = False
        used_selector = None
        
        for i, selector in enumerate(self.green_search_button_selectors):
            try:
                logger.info(f"Trying selector {i+1}/{len(self.green_search_button_selectors)}: {selector}")
                
                if selector.startswith("//"):
                    search_button = self.driver.find_element(By.XPATH, selector)
                else:
                    search_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                
                # Verify this is the correct "Search" button
                is_visible = search_button.is_displayed()
                is_enabled = search_button.is_enabled()
                button_text = search_button.text.strip() if search_button.text else ''
                button_class = search_button.get_attribute('class') or ''
                button_type = search_button.get_attribute('type') or ''
                button_value = search_button.get_attribute('value') or ''
                
                logger.info(f"Found potential 'Search' button:")
                logger.info(f"  - Text: '{button_text}'")
                logger.info(f"  - Class: '{button_class}'")
                logger.info(f"  - Type: '{button_type}'")
                logger.info(f"  - Value: '{button_value}'")
                logger.info(f"  - Visible: {is_visible}")
                logger.info(f"  - Enabled: {is_enabled}")
                
                # Verify this is the correct "Search" button
                if is_visible and is_enabled:
                    # Check if it's a "Search" button (exact text match preferred)
                    if button_text == 'Search' or button_value == 'Search':
                        logger.info(f"✅ CONFIRMED: Found the correct bright green 'Search' button with selector: {selector}")
                        logger.info(f"Button text: '{button_text}', Class: '{button_class}'")
                        
                        # Click the "Search" button
                        logger.info("Clicking the bright green 'Search' button...")
                        search_button.click()
                        logger.info("✅ SUCCESS: Successfully clicked bright green 'Search' button")
                        
                        search_button_found = True
                        used_selector = selector
                        break
                    elif 'search' in button_text.lower() or 'search' in button_value.lower():
                        logger.info(f"✅ CONFIRMED: Found search button with text '{button_text}' using selector: {selector}")
                        logger.info(f"Button text: '{button_text}', Class: '{button_class}'")
                        
                        # Click the search button
                        logger.info("Clicking the search button...")
                        search_button.click()
                        logger.info("✅ SUCCESS: Successfully clicked search button")
                        
                        search_button_found = True
                        used_selector = selector
                        break
                    else:
                        logger.info(f"❌ Button found but text '{button_text}' doesn't match 'Search' - skipping")
                else:
                    logger.info(f"❌ Button found but not visible/enabled - skipping")
                    
            except NoSuchElementException:
                logger.debug(f"Selector not found: {selector}")
                continue
            except Exception as e:
                logger.warning(f"Error with search button selector '{selector}': {e}")
                continue
        
        if not search_button_found:
            logger.error("❌ CRITICAL ERROR: Could not find the bright green 'Search' button")
            logger.error("The bright green 'Search' button should be positioned below the input field")
            logger.error("Expected: Small bright green button with white text 'Search'")
            logger.error("Positioned horizontally to the left of the input field and vertically below it")
            logger.error("Visually distinct from any dropdown suggestion list")
            logger.error("Please verify the page structure and update selectors if needed")
            raise Exception("Bright green 'Search' button not found - automation cannot continue")
        
        # Wait a moment for the search to execute
        time.sleep(3)
        logger.info(f"✅ 'Search' button click completed using selector: {used_selector}")

    def perform_custom_automation(self, search_text):
        """
        Perform the custom automation steps: type into the search field and click the green search button.
        Args:
            search_text (str): The text to search for in the field
        """
        logger.info("=== PERFORMING CUSTOM AUTOMATION STEPS (TYPE + GREEN BUTTON) ===")
        logger.info(f"Automation will target the search field under 'File' label")
        logger.info(f"Search text to enter: '{search_text}'")
        self.find_and_fill_file_search_field(search_text)
        self.find_and_click_green_search_button()
        logger.info("=== SEARCH FIELD ENTRY AND GREEN BUTTON CLICK COMPLETED ===")
        # Wait for results to load (optional, for user observation)
        time.sleep(5)

    def cleanup(self):
        """
        Clean up resources and close browser.
        """
        if self.driver:
            logger.info("Closing browser...")
            self.driver.quit()
            logger.info("Browser closed successfully")
            
    def run(self, search_text):
        """
        Main method to run the complete automation process with precise targeting.
        
        This method orchestrates the entire automation process:
        1. Browser setup (visible Chrome)
        2. Website navigation
        3. Login (if required)
        4. Navigation to target page
        5. Precise search field interaction
        6. Search execution
        
        Args:
            search_text (str): The text to search for in the automation
        """
        try:
            logger.info("=== STARTING PRECISE SELENIUM AUTOMATION ===")
            logger.info(f"Search text provided: '{search_text}'")
            logger.info("Browser will remain VISIBLE throughout the process")
            
            # Step 1: Set up browser (VISIBLE - not headless)
            self.setup_browser()
            
            # Step 2: Navigate to website
            self.navigate_to_website()
            
            # Step 3: Perform login (modify or remove as needed)
            self.perform_login()
            
            # Step 4: Navigate to Search Properties
            self.navigate_to_search_properties()
            
            # Step 5: Navigate to Process Imported Files
            self.navigate_to_process_imported_files()
            
            # Step 6: Perform precise custom automation steps with search text
            self.perform_custom_automation(search_text)
            
            # Step 7: Completion
            logger.info("=== PRECISE AUTOMATION COMPLETED SUCCESSFULLY ===")
            logger.info(f"✅ Successfully searched for text: '{search_text}'")
            logger.info("✅ Search field under 'File' was located and filled correctly")
            logger.info("✅ Bright green 'Search' button was clicked successfully")
            logger.info("You should now be on the Process Imported Files page with search results.")
            
            # Keep browser open for a while so user can see the result
            logger.info("Keeping browser open for 30 seconds for manual verification...")
            time.sleep(30)
            
        except Exception as e:
            logger.error(f"❌ PRECISE AUTOMATION FAILED: {e}")
            logger.error("Please check the console logs above for detailed error information")
            raise
        finally:
            # Always clean up
            self.cleanup() 