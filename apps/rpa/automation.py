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
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
import time
import logging
from selenium.webdriver.common.action_chains import ActionChains
import difflib
from datetime import datetime
import re
import traceback

# Configure logging
logger = logging.getLogger(__name__)

class SeleniumAutomation:
    """
    Selenium automation class that handles browser automation tasks.
    """
    
    def __init__(self, page_url=None):
        """
        Initialize the automation with configuration.
        Args:
            page_url (str): The URL or page path to navigate to (optional)
        """
        # Configuration - No credentials needed for ChatGPT navigation
        self.website_url = "https://chatgpt.com"
        
        # No credentials needed for ChatGPT
        self.username = None
        self.password = None
        
        # Dynamic page navigation - user can specify any page
        self.page_url = page_url
        
        # Element selectors - UPDATE THESE IF NEEDED
        self.username_selector = "input[type='email'], input[name='email'], #email"
        self.password_selector = "input[type='password'], input[name='password'], #password"
        self.login_button_selector = "button[type='submit'], input[type='submit'], .login-btn"
        
        # Navigation selectors - now dynamic based on page_url
        self.search_properties_selector = "a[href*='search'], .search-link, #search, .board-item"
        self.process_imported_files_selector = "a[href*='process'], .process-link, #process, .board-item"
        
        # Tracking variables for continuous processing
        self.last_payee_name = None  # Store the last processed Payee Name
        self.consecutive_failures = 0  # Track consecutive failures
        self.max_companies = 999999  # Maximum number of companies to process (set very high for unlimited)
        self.companies_processed = 0  # Counter for processed companies
        
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
        # Highest priority: button directly after the 'File' label
        self.green_search_button_selectors = [
            # Most precise selector as requested
            "//label[text()='File']/following::button[contains(text(),'Search')][1]",

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
        
        # EXPLICITLY ENSURE NO INCOGNITO MODE
        chrome_options.add_argument("--disable-incognito")
        chrome_options.add_argument("--disable-private-browsing")
        
        # Set window size for better visibility
        chrome_options.add_argument("--window-size=1200,800")
        
        # Initialize the driver
        logger.info("Chrome options being used:")
        for arg in chrome_options.arguments:
            logger.info(f"  Chrome arg: {arg}")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logger.info("Chrome browser initialized successfully - BROWSER IS VISIBLE (NOT INCOGNITO)")
        
    def navigate_to_website(self):
        """
        Navigate to the Monday.com board.
        """
        logger.info(f"Navigating to: {self.website_url}")
        self.driver.get(self.website_url)
        time.sleep(3)
        logger.info("Successfully navigated to website")
        
    def perform_login(self):
        """
        Perform login process with optimized username input.
        This method waits for the username field to become available and inputs immediately.
        """
        logger.info("=== STARTING OPTIMIZED LOGIN PROCESS ===")
        
        # Try multiple selectors for username field with immediate input
        username_selectors = [
            "//*[@id='user_email']",  # Exact XPath provided by user
            "#user_email",  # CSS selector for the same ID
            "input[type='email']",
            "input[name='email']", 
            "input[placeholder='Email']",
            "input[placeholder*='email']",
            "input[placeholder*='Email']",
            "#email",
            "//input[@placeholder='Email']",
            "//input[@type='email']"
        ]
        
        logger.info("Waiting for username field to become available...")
        username_field = None
        
        # Wait up to 10 seconds for username field to appear
        wait = WebDriverWait(self.driver, 10)
        
        for selector in username_selectors:
            try:
                if selector.startswith("//"):
                    username_field = wait.until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                else:
                    username_field = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                logger.info(f"Found username field with selector: {selector}")
                break
            except TimeoutException:
                continue
        
        if not username_field:
            logger.error("ERROR: Username field not found with any selector within 10 seconds")
            # Log all input fields on the page for debugging
            try:
                all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                logger.info(f"Found {len(all_inputs)} input fields on page:")
                for i, inp in enumerate(all_inputs):
                    logger.info(f"  Input {i}: type='{inp.get_attribute('type')}', placeholder='{inp.get_attribute('placeholder')}', name='{inp.get_attribute('name')}'")
            except Exception as e:
                logger.error(f"Error getting input fields: {e}")
            raise Exception("Username field not found")
        
        # Immediately clear and enter username as soon as field is found
        logger.info("Username field found - immediately entering username...")
        username_field.clear()
        username_field.send_keys(self.username)
        logger.info(f"Username '{self.username}' entered successfully")
        
        # Try multiple selectors for password field with immediate input
        password_selectors = [
            "//*[@id='user_password']",  # Exact XPath provided by user
            "#user_password",  # CSS selector for the same ID
            "input[type='password']",
            "input[name='password']",
            "input[placeholder='Password']", 
            "input[placeholder*='password']",
            "input[placeholder*='Password']",
            "#password",
            "//input[@placeholder='Password']",
            "//input[@type='password']"
        ]
        
        logger.info("Waiting for password field to become available...")
        password_field = None
        
        for selector in password_selectors:
            try:
                if selector.startswith("//"):
                    password_field = wait.until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                else:
                    password_field = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                logger.info(f"Found password field with selector: {selector}")
                break
            except TimeoutException:
                continue
        
        if not password_field:
            logger.error("ERROR: Password field not found with any selector")
            raise Exception("Password field not found")
        
        # Immediately clear and enter password as soon as field is found
        logger.info("Password field found - immediately entering password...")
        password_field.clear()
        password_field.send_keys(self.password)
        logger.info("Password entered successfully")
        
        # Try multiple selectors for login button with immediate click
        login_button_selectors = [
            "//*[@id='login-monday-container']/div/div[2]/div/div[1]/div/div[4]/div/button",  # Exact XPath provided by user
            "button[type='submit']",
            "input[type='submit']",
            "button:contains('Log in')",
            "button:contains('Login')",
            "button[data-testid='login-button']",
            "//button[contains(text(), 'Log in')]",
            "//button[contains(text(), 'Login')]",
            "//input[@type='submit']"
        ]
        
        logger.info("Waiting for login button to become available...")
        login_button = None
        
        for selector in login_button_selectors:
            try:
                if selector.startswith("//"):
                    login_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                else:
                    login_button = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                logger.info(f"Found login button with selector: {selector}")
                break
            except TimeoutException:
                continue
        
        if not login_button:
            logger.error("ERROR: Login button not found with any selector")
            # Log all buttons on the page for debugging
            try:
                all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                logger.info(f"Found {len(all_buttons)} buttons on page:")
                for i, btn in enumerate(all_buttons):
                    logger.info(f"  Button {i}: text='{btn.text}', type='{btn.get_attribute('type')}'")
            except Exception as e:
                logger.error(f"Error getting buttons: {e}")
            raise Exception("Login button not found")
        
        # Immediately click login button as soon as it's found and clickable
        logger.info("Login button found and clickable - immediately clicking...")
        login_button.click()
        logger.info("Login button clicked successfully")
        
        # Wait for login to complete with shorter wait time
        logger.info("Waiting for login to complete...")
        time.sleep(3)  # Reduced from 5 to 3 seconds
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
        After entering the text, locate and click the correct green 'Search' button using the confirmed XPath.
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
            
            # Wait for dropdown suggestion to appear
            logger.info("Waiting 1 second for dropdown suggestion to appear...")
            time.sleep(1)
            
            # Locate and click the correct green 'Search' button using the confirmed XPath
            logger.info("Waiting for the correct green 'Search' button to be clickable using XPath: //*[@id=\"btnSearchProps\"]")
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            wait = WebDriverWait(self.driver, 10)
            try:
                search_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btnSearchProps"]')))
                logger.info("✅ Correct green 'Search' button is clickable. Clicking now...")
                self.driver.execute_script("arguments[0].style.border='3px solid red'", search_button)
                time.sleep(1)
                search_button.click()
                logger.info("✅ Clicked the green 'Search' button successfully.")
            except Exception as e:
                logger.error(f"❌ ERROR: Could not find or click the green 'Search' button: {e}")
                raise Exception(f"Green 'Search' button interaction failed: {e}")
            
        except Exception as interaction_error:
            logger.error(f"❌ ERROR: Failed to interact with search field: {interaction_error}")
            raise Exception(f"Search field interaction failed: {interaction_error}")
        
        logger.info(f"✅ Search text entry and Search button click completed using selector: {used_selector}")

    def find_and_fill_ein_field(self, ein_text):
        """
        Search for EIN field and fill it with the provided text.
        Args:
            ein_text (str): The EIN number to enter in the field
        """
        logger.info(f"=== SEARCHING FOR EIN FIELD ===")
        logger.info(f"Looking for EIN field to enter text: '{ein_text}'")
        
        # Try multiple selectors for EIN field
        ein_selectors = [
            "//input[contains(@placeholder, 'EIN')]",
            "//input[contains(@placeholder, 'ein')]",
            "//input[contains(@placeholder, 'Employer Identification')]",
            "//input[contains(@placeholder, 'Tax ID')]",
            "//input[contains(@placeholder, 'tax id')]",
            "//input[@name='ein']",
            "//input[@id='ein']",
            "//input[@name='tax_id']",
            "//input[@id='tax_id']",
            "//input[@name='employer_id']",
            "//input[@id='employer_id']",
            "//label[contains(text(), 'EIN')]/following-sibling::input",
            "//label[contains(text(), 'Tax ID')]/following-sibling::input",
            "//label[contains(text(), 'Employer ID')]/following-sibling::input"
        ]
        
        ein_field = None
        for selector in ein_selectors:
            try:
                ein_field = self.driver.find_element(By.XPATH, selector)
                if ein_field.is_displayed() and ein_field.is_enabled():
                    logger.info(f"✅ Found EIN field with selector: {selector}")
                    break
            except Exception:
                continue
        
        if not ein_field:
            logger.error("❌ ERROR: Could not find EIN field")
            raise Exception("EIN field not found - automation cannot continue.")
        
        # Fill the EIN field
        try:
            logger.info("Clicking the EIN field to activate it...")
            ein_field.click()
            time.sleep(1)
            logger.info(f"Clearing field and entering EIN: '{ein_text}'")
            ein_field.clear()
            ein_field.send_keys(ein_text)
            logger.info(f"✅ SUCCESS: Successfully entered EIN: '{ein_text}'")
            
        except Exception as interaction_error:
            logger.error(f"❌ ERROR: Failed to interact with EIN field: {interaction_error}")
            raise Exception(f"EIN field interaction failed: {interaction_error}")

    def find_and_fill_address_field(self, address_text):
        """
        Search for Address field and fill it with the provided text.
        Args:
            address_text (str): The address to enter in the field
        """
        logger.info(f"=== SEARCHING FOR ADDRESS FIELD ===")
        logger.info(f"Looking for Address field to enter text: '{address_text}'")
        
        # Try multiple selectors for Address field
        address_selectors = [
            "//input[contains(@placeholder, 'Address')]",
            "//input[contains(@placeholder, 'address')]",
            "//input[contains(@placeholder, 'Street')]",
            "//input[contains(@placeholder, 'street')]",
            "//input[@name='address']",
            "//input[@id='address']",
            "//input[@name='street']",
            "//input[@id='street']",
            "//textarea[contains(@placeholder, 'Address')]",
            "//textarea[contains(@placeholder, 'address')]",
            "//label[contains(text(), 'Address')]/following-sibling::input",
            "//label[contains(text(), 'Street')]/following-sibling::input"
        ]
        
        address_field = None
        for selector in address_selectors:
            try:
                address_field = self.driver.find_element(By.XPATH, selector)
                if address_field.is_displayed() and address_field.is_enabled():
                    logger.info(f"✅ Found Address field with selector: {selector}")
                    break
            except Exception:
                continue
        
        if not address_field:
            logger.error("❌ ERROR: Could not find Address field")
            raise Exception("Address field not found - automation cannot continue.")
        
        # Fill the Address field
        try:
            logger.info("Clicking the Address field to activate it...")
            address_field.click()
            time.sleep(1)
            logger.info(f"Clearing field and entering Address: '{address_text}'")
            address_field.clear()
            address_field.send_keys(address_text)
            logger.info(f"✅ SUCCESS: Successfully entered Address: '{address_text}'")
            
        except Exception as interaction_error:
            logger.error(f"❌ ERROR: Failed to interact with Address field: {interaction_error}")
            raise Exception(f"Address field interaction failed: {interaction_error}")

    def find_and_fill_email_field(self, email_text):
        """
        Search for Email field and fill it with the provided text.
        Args:
            email_text (str): The email to enter in the field
        """
        logger.info(f"=== SEARCHING FOR EMAIL FIELD ===")
        logger.info(f"Looking for Email field to enter text: '{email_text}'")
        
        # Try multiple selectors for Email field
        email_selectors = [
            "//input[contains(@placeholder, 'Email')]",
            "//input[contains(@placeholder, 'email')]",
            "//input[@type='email']",
            "//input[@name='email']",
            "//input[@id='email']",
            "//input[@name='e-mail']",
            "//input[@id='e-mail']",
            "//label[contains(text(), 'Email')]/following-sibling::input",
            "//label[contains(text(), 'E-mail')]/following-sibling::input"
        ]
        
        email_field = None
        for selector in email_selectors:
            try:
                email_field = self.driver.find_element(By.XPATH, selector)
                if email_field.is_displayed() and email_field.is_enabled():
                    logger.info(f"✅ Found Email field with selector: {selector}")
                    break
            except Exception:
                continue
        
        if not email_field:
            logger.error("❌ ERROR: Could not find Email field")
            raise Exception("Email field not found - automation cannot continue.")
        
        # Fill the Email field
        try:
            logger.info("Clicking the Email field to activate it...")
            email_field.click()
            time.sleep(1)
            logger.info(f"Clearing field and entering Email: '{email_text}'")
            email_field.clear()
            email_field.send_keys(email_text)
            logger.info(f"✅ SUCCESS: Successfully entered Email: '{email_text}'")
            
        except Exception as interaction_error:
            logger.error(f"❌ ERROR: Failed to interact with Email field: {interaction_error}")
            raise Exception(f"Email field interaction failed: {interaction_error}")

    def find_and_fill_phone_field(self, phone_text):
        """
        Search for Phone field and fill it with the provided text.
        Args:
            phone_text (str): The phone number to enter in the field
        """
        logger.info(f"=== SEARCHING FOR PHONE FIELD ===")
        logger.info(f"Looking for Phone field to enter text: '{phone_text}'")
        
        # Try multiple selectors for Phone field
        phone_selectors = [
            "//input[contains(@placeholder, 'Phone')]",
            "//input[contains(@placeholder, 'phone')]",
            "//input[contains(@placeholder, 'Tel')]",
            "//input[contains(@placeholder, 'tel')]",
            "//input[@type='tel']",
            "//input[@name='phone']",
            "//input[@id='phone']",
            "//input[@name='telephone']",
            "//input[@id='telephone']",
            "//input[@name='tel']",
            "//input[@id='tel']",
            "//label[contains(text(), 'Phone')]/following-sibling::input",
            "//label[contains(text(), 'Telephone')]/following-sibling::input"
        ]
        
        phone_field = None
        for selector in phone_selectors:
            try:
                phone_field = self.driver.find_element(By.XPATH, selector)
                if phone_field.is_displayed() and phone_field.is_enabled():
                    logger.info(f"✅ Found Phone field with selector: {selector}")
                    break
            except Exception:
                continue
        
        if not phone_field:
            logger.error("❌ ERROR: Could not find Phone field")
            raise Exception("Phone field not found - automation cannot continue.")
        
        # Fill the Phone field
        try:
            logger.info("Clicking the Phone field to activate it...")
            phone_field.click()
            time.sleep(1)
            logger.info(f"Clearing field and entering Phone: '{phone_text}'")
            phone_field.clear()
            phone_field.send_keys(phone_text)
            logger.info(f"✅ SUCCESS: Successfully entered Phone: '{phone_text}'")
            
        except Exception as interaction_error:
            logger.error(f"❌ ERROR: Failed to interact with Phone field: {interaction_error}")
            raise Exception(f"Phone field interaction failed: {interaction_error}")

    def click_first_payee_and_store_name(self):
        """
        Locate all payee rows using XPath //*[@id="propsGrid"]/tbody/tr, extract only the Payee Name from the correct cell in the first row,
        store it in a variable, print it, and double-click the row. Do not reuse the element after navigation.
        """
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        logger.info("Waiting for payee grid rows to be present...")
        wait = WebDriverWait(self.driver, 20)
        try:
            payee_rows = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="propsGrid"]/tbody/tr')))
            logger.info(f"✅ Found {len(payee_rows)} payee rows in the grid.")
            if not payee_rows:
                raise Exception("No payee rows found in the grid.")
            first_row = payee_rows[0]
            # Extract only the Payee Name from the correct cell (replace N with the correct column index, e.g., 2 for the second cell)
            payee_name_cell = first_row.find_element(By.XPATH, ".//td[2]")  # <-- Change 2 to the correct column if needed
            payee_name = payee_name_cell.text.strip()
            logger.info(f"✅ Extracted Payee Name from grid cell: '{payee_name}' (type: {type(payee_name)})")
            print(f"Payee Name: {payee_name}")
            # Double-click the row (do not use the element after this)
            ActionChains(self.driver).double_click(first_row).perform()
            logger.info(f"✅ Double-clicked first payee row.")
            return payee_name  # Return the string, not the element
        except Exception as e:
            logger.error(f"❌ ERROR: Could not find or double-click a payee row: {e}")
            raise

    def find_and_click_best_bizfile_match(self, payee_name):
        """
        After searching BizFileOnline, wait for results, check if any are present, print/log each result's text and similarity score,
        and click the best match. If no results, print a warning and exit the step.
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import difflib
        import time
        wait = WebDriverWait(self.driver, 15)
        try:
            logger.info("Waiting 2 seconds for BizFileOnline search results to appear...")
            time.sleep(2)
            logger.info("Waiting for BizFileOnline search results to be present (//a[contains(@class, 'entityName')])...")
            results = wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'entityName')]"))
            )
            if not results:
                logger.warning("⚠️ No search results found on BizFileOnline.")
                print("No search results found on BizFileOnline.")
                return
            logger.info(f"✅ Found {len(results)} clickable search results.")
            best_score = -1
            best_elem = None
            best_text = None
            for elem in results:
                result_text = elem.text.strip()
                score = difflib.SequenceMatcher(None, payee_name.lower(), result_text.lower()).ratio()
                logger.info(f"Result: '{result_text}' | Similarity score: {score:.3f}")
                print(f"Result: '{result_text}' | Similarity score: {score:.3f}")
                if score > best_score:
                    best_score = score
                    best_elem = elem
                    best_text = result_text
            if best_elem is not None:
                logger.info(f"✅ Clicking best match: '{best_text}' (score: {best_score:.3f})")
                print(f"Best match: '{best_text}' (score: {best_score:.3f})")
                try:
                    # First, ensure the element is still valid and visible
                    logger.info("Ensuring best match element is still valid and visible...")
                    
                    # Get the element's location and size
                    element_location = best_elem.location
                    element_size = best_elem.size
                    logger.info(f"Element location: {element_location}, size: {element_size}")
                    
                    # Scroll the best match into view (centered) with better error handling
                    logger.info("Scrolling best match element to center of viewport...")
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", best_elem)
                    time.sleep(1)  # Give more time for scroll to complete
                    
                    # Verify the element is now visible and clickable
                    logger.info("Verifying element is visible and clickable...")
                    if best_elem.is_displayed() and best_elem.is_enabled():
                        logger.info("Element is visible and enabled, proceeding with click...")
                        
                        # Use JavaScript to click if regular click fails
                        try:
                            best_elem.click()
                            logger.info("✅ Successfully clicked best match using regular click.")
                        except Exception as click_error:
                            logger.warning(f"Regular click failed, trying JavaScript click: {click_error}")
                            self.driver.execute_script("arguments[0].click();", best_elem)
                            logger.info("✅ Successfully clicked best match using JavaScript.")
                    else:
                        logger.error("Element is not visible or enabled after scrolling")
                        raise Exception("Element not visible or enabled after scrolling")
                        
                except Exception as e:
                    logger.error(f"❌ ERROR: Click failed: {e}")
                    print(f"Click failed: {e}")
                    raise
            else:
                logger.warning("⚠️ No suitable search result found to click.")
                print("No suitable search result found to click.")
        except Exception as e:
            logger.error(f"❌ ERROR: Could not process BizFileOnline search results: {e}")
            raise

    def find_and_click_newest_matching_bizfile_result(self, payee_name):
        """
        After BizFileOnline search, locate all result rows, extract Entity Name and Filing Date, compare to Payee name,
        and click the newest matching result. Print/log which result was clicked and its date.
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import difflib
        from datetime import datetime
        import time
        wait = WebDriverWait(self.driver, 15)
        try:
            logger.info("Waiting 2 seconds for BizFileOnline search results to appear...")
            time.sleep(2)
            logger.info("Waiting for BizFileOnline result rows to be present (//table//tr[contains(@class, 'result-row')])...")
            rows = wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//table//tr[contains(@class, 'result-row')]"))
            )
            if not rows:
                logger.warning("⚠️ No result rows found on BizFileOnline.")
                print("No result rows found on BizFileOnline.")
                return
            logger.info(f"✅ Found {len(rows)} result rows.")
            best_score = -1
            newest_date = None
            best_row = None
            best_entity = None
            best_date_str = None
            for row in rows:
                try:
                    entity_name = row.find_element(By.XPATH, ".//td[1]").text.strip()
                    filing_date_str = row.find_element(By.XPATH, ".//td[2]").text.strip()
                    score = difflib.SequenceMatcher(None, payee_name.lower(), entity_name.lower()).ratio()
                    logger.info(f"Row: Entity='{entity_name}', Filing Date='{filing_date_str}', Similarity={score:.3f}")
                    print(f"Row: Entity='{entity_name}', Filing Date='{filing_date_str}', Similarity={score:.3f}")
                    # Parse date (assume MM/DD/YYYY or similar)
                    try:
                        filing_date = datetime.strptime(filing_date_str, "%m/%d/%Y")
                    except Exception:
                        filing_date = None
                    # Choose the newest matching result (highest score, then newest date)
                    if score > 0.8:  # Only consider strong matches
                        if (best_row is None or (filing_date and newest_date and filing_date > newest_date) or (filing_date and newest_date is None)):
                            best_score = score
                            best_row = row
                            best_entity = entity_name
                            best_date_str = filing_date_str
                            newest_date = filing_date
                except Exception as row_e:
                    logger.warning(f"Could not process a result row: {row_e}")
            if best_row is not None:
                logger.info(f"✅ Clicking newest matching result: '{best_entity}' (Filing Date: {best_date_str})")
                print(f"Clicked: '{best_entity}' (Filing Date: {best_date_str})")
                try:
                    # First, ensure the element is still valid and visible
                    logger.info("Ensuring best row element is still valid and visible...")
                    
                    # Get the element's location and size
                    element_location = best_row.location
                    element_size = best_row.size
                    logger.info(f"Element location: {element_location}, size: {element_size}")
                    
                    # Scroll the best row into view (centered) with better error handling
                    logger.info("Scrolling best row element to center of viewport...")
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", best_row)
                    time.sleep(1)  # Give more time for scroll to complete
                    
                    # Verify the element is now visible and clickable
                    logger.info("Verifying element is visible and clickable...")
                    if best_row.is_displayed() and best_row.is_enabled():
                        logger.info("Element is visible and enabled, proceeding with click...")
                        
                        row_text = best_row.text
                        print(f"[DEBUG] About to click row {best_index+1} with text: {row_text}")
                        
                        # Use JavaScript to click if regular click fails
                        try:
                            from selenium.webdriver.common.action_chains import ActionChains
                            ActionChains(self.driver).move_to_element(best_row).click().perform()
                            logger.info("✅ Successfully clicked best row using ActionChains.")
                            print(f"[DEBUG] Successfully clicked row {best_index+1}")
                        except Exception as click_error:
                            logger.warning(f"ActionChains click failed, trying JavaScript click: {click_error}")
                            self.driver.execute_script("arguments[0].click();", best_row)
                            logger.info("✅ Successfully clicked best row using JavaScript.")
                            print(f"[DEBUG] Successfully clicked row {best_index+1}")
                    else:
                        logger.error("Element is not visible or enabled after scrolling")
                        raise Exception("Element not visible or enabled after scrolling")
                        
                except Exception as e:
                    print(f"[ERROR] Failed to click row {best_index+1}: {e}")
                    # Print the outer HTML of the row for further debugging
                    try:
                        print("[ERROR] Row outerHTML:", best_row.get_attribute('outerHTML'))
                    except Exception as e2:
                        print(f"[ERROR] Could not get outerHTML: {e2}")
                    # Optionally, print the stack trace
                    traceback.print_exc()
            else:
                logger.warning("⚠️ No suitable matching result found to click.")
                print("No suitable matching result found to click.")
        except Exception as e:
            logger.error(f"❌ ERROR: Could not process BizFileOnline result rows: {e}")
            raise

    def find_and_click_most_recent_filing_bizfile_result(self):
        """
        After BizFileOnline search, scroll down, locate all result rows (//table//tr[td]),
        if one result, click the blue row's white arrow button. If multiple, extract Initial Filing Date from 2nd column,
        click the white arrow in the row with the newest date. Print total results, all dates, and which was clicked.
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from datetime import datetime
        import time
        wait = WebDriverWait(self.driver, 15)
        try:
            logger.info("Scrolling down to ensure all BizFileOnline results are visible...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            logger.info("Waiting 2 seconds for BizFileOnline search results to appear...")
            time.sleep(2)
            logger.info("Waiting for BizFileOnline result rows to be present (//table//tr[td])...")
            rows = wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//table//tr[td]"))
            )
            num_results = len(rows)
            logger.info(f"✅ Found {num_results} result row(s).")
            print(f"Found {num_results} result row(s).")
            if num_results == 0:
                logger.warning("⚠️ No result rows found on BizFileOnline.")
                print("No result rows found on BizFileOnline.")
                return
            if num_results == 1:
                logger.info("Only one result found. Clicking the blue row's white arrow button immediately.")
                print("Only one result found. Clicking the blue row's white arrow button immediately.")
                try:
                    arrow = rows[0].find_element(By.XPATH, ".//button | .//a")
                    arrow.click()
                    logger.info("✅ Clicked the white arrow button in the only result row.")
                    print("Clicked the white arrow button in the only result row.")
                except Exception as click_e:
                    logger.error(f"❌ ERROR: Could not click arrow/button in the row: {click_e}")
                    print(f"Could not click arrow/button in the row: {click_e}")
                return
            # Multiple results: extract Filing Dates and click the newest
            most_recent_date = None
            most_recent_row = None
            most_recent_date_str = None
            all_dates = []
            for row in rows:
                try:
                    date_str = row.find_element(By.XPATH, ".//td[2]").text.strip()
                    all_dates.append(date_str)
                    logger.info(f"Row Filing Date: {date_str}")
                    print(f"Row Filing Date: {date_str}")
                    try:
                        date_val = datetime.strptime(date_str, "%m/%d/%Y")
                    except Exception:
                        date_val = None
                    if date_val and (most_recent_date is None or date_val > most_recent_date):
                        most_recent_date = date_val
                        most_recent_row = row
                        most_recent_date_str = date_str
                except Exception as row_e:
                    logger.warning(f"Could not process a result row: {row_e}")
            logger.info(f"All Filing Dates: {all_dates}")
            print(f"All Filing Dates: {all_dates}")
            if most_recent_row is not None:
                try:
                    arrow = most_recent_row.find_element(By.XPATH, ".//button | .//a")
                    logger.info(f"✅ Clicking arrow/button for result with most recent Filing Date: {most_recent_date_str}")
                    print(f"Clicked result with most recent Filing Date: {most_recent_date_str}")
                    arrow.click()
                except Exception as click_e:
                    logger.error(f"❌ ERROR: Could not click arrow/button in the row: {click_e}")
                    print(f"Could not click arrow/button in the row: {click_e}")
            else:
                logger.warning("⚠️ No suitable result with a valid date found to click.")
                print("No suitable result with a valid date found to click.")
        except Exception as e:
            logger.error(f"❌ ERROR: Could not process BizFileOnline result rows: {e}")
            raise

    def _normalize_entity_name(self, name):
        import re
        # Remove parenthesis and their contents, punctuation, lowercase, collapse spaces
        name = re.sub(r'\\([^)]*\\)', '', name)
        name = re.sub(r'[^a-z0-9 ]+', '', name.lower())
        return ' '.join(name.split())

    def find_and_click_exact_or_newest_entity(self, payee_name, property_tab=None, multiple_results=False, already_clicked=False):
        if already_clicked:
            # Skip click logic, just continue with the rest of the process
            self._wait_and_click_view_history(wait, property_tab=property_tab, multiple_results=multiple_results)
            return
        """
        After BizFileOnline search, wait for results, then:
        - Locate result rows using //table//tr[td]
        - For each row, extract the entity name from the blue clickable area using:
          .//td[1]//button | .//td[1]//div[contains(@class,'entity')] | .//td[1]//span
        - Compare the extracted text to payee_name (case-insensitive, trim whitespace)
        - When an exact match is found, left-click the blue clickable element (button or div)
        - Fallback: If only one row exists, left-click the blue area regardless of match
        - Remove any .//td[1]//a lookups
        - After clicking, wait for the right-hand side panel to fully load, locate the 'View History' button by its visible text, wait for it to become clickable, and left-click it.
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import time
        wait = WebDriverWait(self.driver, 15)
        try:
            logger.info("Waiting for at least one result row (//table//tr[td])...")
            rows = wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//table//tr[td]"))
            )
            num_rows = len(rows)
            logger.info(f"Found {num_rows} result row(s).")
            print(f"Found {num_rows} result row(s).")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            if num_rows == 0:
                logger.warning("No result rows found on BizFileOnline.")
                print("No result rows found on BizFileOnline.")
                # Close all BizFileOnline tabs first
                bizfile_handles = []
                for handle in self.driver.window_handles:
                    self.driver.switch_to.window(handle)
                    if "bizfileonline.sos.ca.gov" in self.driver.current_url:
                        bizfile_handles.append(handle)
                for handle in bizfile_handles:
                    try:
                        self.driver.switch_to.window(handle)
                        self.driver.close()
                    except Exception as e:
                        logger.warning(f"Could not close BizFileOnline tab: {e}")
                # After closing, switch to property tab and add the note
                if property_tab in self.driver.window_handles:
                    self.driver.switch_to.window(property_tab)
                    self.add_note_to_property("NO RESULTS WERE FOUND")
                return
            # Fallback: If only one row, click the blue area regardless of match
            if num_rows == 1:
                logger.info("Only one result row. Clicking the blue clickable area regardless of match.")
                print("Only one result row. Clicking the blue clickable area regardless of match.")
                row = rows[0]
                clickable = None
                for xpath in [
                    ".//td[1]//button",
                    ".//td[1]//div[contains(@class,'entity')]",
                    ".//td[1]//span"
                ]:
                    elems = row.find_elements(By.XPATH, xpath)
                    if elems:
                        clickable = elems[0]
                        break
                if clickable:
                    clickable.click()
                    logger.info("✅ Clicked the blue clickable element in the only result row.")
                    print("Clicked the blue clickable element in the only result row.")
                    # After click, wait for right panel and click 'View History'
                    self._wait_and_click_view_history(wait, property_tab=property_tab, multiple_results=multiple_results)
                else:
                    logger.warning("No blue clickable element found in the only result row.")
                    print("No blue clickable element found in the only result row.")
                return
            # Multiple rows: look for best match using dynamic XPath
            normalized_payee = self._normalize_entity_name(payee_name)
            best_match = None
            best_score = 0
            best_length = float('inf')
            for i, row in enumerate(rows):
                clickable = None
                entity_text = None
                row_num = i + 1
                for xpath_pattern in [
                    "//*[@id='root']/div/div[1]/div/main/div[2]/table/tbody/tr[{row_num}]/td[1]//button",
                    "//*[@id='root']/div/div[1]/div/main/div[2]/table/tbody/tr[{row_num}]/td[1]//div[contains(@class,'entity')]",
                    "//*[@id='root']/div/div[1]/div/main/div[2]/table/tbody/tr[{row_num}]/td[1]//span"
                ]:
                    xpath = xpath_pattern.format(row_num=row_num)
                    elems = self.driver.find_elements(By.XPATH, xpath)
                    if elems:
                        clickable = elems[0]
                        entity_text = clickable.text.strip()
                        break
                if entity_text:
                    logger.info(f"Entity candidate: '{entity_text}' vs search: '{normalized_payee}'")
                    normalized_entity = self._normalize_entity_name(entity_text)
                    if normalized_entity == normalized_payee:
                        # Exact match, click and return
                        clickable.click()
                        logger.info(f"✅ Exact match found. Clicking element.")
                        print(f"Exact match found. Clicking element.")
                        # After click, wait for right panel and click 'View History'
                        self._wait_and_click_view_history(wait, property_tab=property_tab, multiple_results=multiple_results)
                        return
                    if normalized_payee in normalized_entity:
                        # Substring match, prefer shorter
                        if len(normalized_entity) < best_length:
                            best_match = clickable
                            best_length = len(normalized_entity)
                    else:
                        # Fallback: most letters in common
                        score = self._letters_in_common(normalized_entity, normalized_payee)
                        if score > best_score:
                            best_match = clickable
                            best_score = score
            if best_match:
                logger.info(f"✅ Best match found with score {best_score}. Clicking element.")
                print(f"Best match found with score {best_score}. Clicking element.")
                try:
                    # First, ensure the element is still valid and visible
                    logger.info("Ensuring best match element is still valid and visible...")
                    
                    # Get the element's location and size
                    element_location = best_match.location
                    element_size = best_match.size
                    logger.info(f"Element location: {element_location}, size: {element_size}")
                    
                    # Scroll the best match into view (centered) with better error handling
                    logger.info("Scrolling best match element to center of viewport...")
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", best_match)
                    time.sleep(1)  # Give more time for scroll to complete
                    
                    # Verify the element is now visible and clickable
                    logger.info("Verifying element is visible and clickable...")
                    if best_match.is_displayed() and best_match.is_enabled():
                        logger.info("Element is visible and enabled, proceeding with click...")
                        
                        # Use JavaScript to click if regular click fails
                        try:
                            from selenium.webdriver.common.action_chains import ActionChains
                            ActionChains(self.driver).move_to_element(best_match).click().perform()
                            logger.info("✅ Successfully clicked best match using ActionChains.")
                        except Exception as click_error:
                            logger.warning(f"ActionChains click failed, trying JavaScript click: {click_error}")
                            self.driver.execute_script("arguments[0].click();", best_match)
                            logger.info("✅ Successfully clicked best match using JavaScript.")
                        
                        # After click, wait for right panel and click 'View History'
                        self._wait_and_click_view_history(wait, property_tab=property_tab, multiple_results=multiple_results)
                    else:
                        logger.error("Element is not visible or enabled after scrolling")
                        raise Exception("Element not visible or enabled after scrolling")
                        
                except Exception as e:
                    logger.error(f"❌ ERROR: Click failed: {e}")
                    print(f"Click failed: {e}")
                    time.sleep(3)
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    logger.info("Waited 3 seconds and scrolled to bottom of page.")
                    print("Waited 3 seconds and scrolled to bottom of page.")
            else:
                logger.info("No suitable match found. No click performed.")
                print("No suitable match found. No click performed.")
                time.sleep(3)
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                logger.info("Waited 3 seconds and scrolled to bottom of page.")
                print("Waited 3 seconds and scrolled to bottom of page.")
        except Exception as e:
            logger.error(f"❌ ERROR: Could not process BizFileOnline entity results: {e}")
            print(f"BizFileOnline entity results processing failed: {e}")
            # Switch back to property tab and add note if possible
            if property_tab:
                self.driver.switch_to.window(property_tab)
                self.add_note_to_property(f"NO RESULTS WERE FOUND (error: {e})")
            return

    def _wait_and_click_view_history(self, wait, property_tab=None, multiple_results=False):
        """
        After clicking on a BizFileOnline result, wait for the right-hand side panel to load and click the 'View History' button.
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        import time
        try:
            logger.info("Waiting for the right-hand side panel to load and 'View History' button to appear...")
            # Wait for either the button or div to be present
            view_history = None
            for xpath in [
                "//button[.//text()[contains(.,'View History')]]",
                "//div[.='View History']"
            ]:
                try:
                    view_history = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                    if view_history:
                        logger.info(f"'View History' button found with XPath: {xpath}")
                        break
                except Exception:
                    continue
            if view_history:
                logger.info("Clicking 'View History' button...")
                view_history.click()
                logger.info("✅ Clicked 'View History' button.")
                print("Clicked 'View History' button.")
                # After clicking, wait for the History page to fully load and click the correct panel
                self._wait_and_click_statement_of_information_panel(wait, property_tab=property_tab, multiple_results=multiple_results)
            else:
                logger.warning("'View History' button not found after waiting.")
                print("'View History' button not found after waiting.")
        except Exception as e:
            logger.error(f"❌ ERROR: Could not click 'View History' button: {e}")
            print(f"Could not click 'View History' button: {e}")

    def _wait_and_click_statement_of_information_panel(self, wait, property_tab=None, multiple_results=False):
        """
        After clicking the 'View History' button, wait up to 3 seconds for the panel area to load.
        Check if the panel is already expanded by looking for download links or expanded content.
        Only click the button if the panel is not already expanded.
        After expanding the 'Statement of Information' panel, extract the link address from the 'Download' anchor by reading its href attribute. Immediately output the link to the terminal or console log as a debugging step to confirm the correct link was captured.
        If property_tab is provided, switch back to it immediately after obtaining the download link (not after any button click).
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        import time
        try:
            logger.info("Waiting up to 3 seconds for the fixed panel button to appear after 'View History' click...")
            button_xpath = "/html/body/div[3]/div/div[1]/div[2]/div/div[2]/button"
            try:
                button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
            except Exception:
                logger.error("Panel button not present: No button found at the fixed XPath after waiting.")
                print("Panel button not present: No button found at the fixed XPath after waiting.")
                return
            if not button:
                logger.error("Panel button not present: No button found at the fixed XPath after waiting.")
                print("Panel button not present: No button found at the fixed XPath after waiting.")
                return
            
            # Check if the panel is already expanded by looking for download links
            download_xpath = "//a[contains(., 'Download')]"
            try:
                # Wait a short time to see if download links are already visible
                download_button = wait.until(EC.presence_of_element_located((By.XPATH, download_xpath)))
                logger.info("Panel appears to be already expanded - download link found without clicking")
                print("Panel appears to be already expanded - download link found without clicking")
                panel_already_expanded = True
            except Exception:
                logger.info("Panel appears to be collapsed - will click to expand")
                print("Panel appears to be collapsed - will click to expand")
                panel_already_expanded = False
            
            # Only click if the panel is not already expanded
            if not panel_already_expanded:
                logger.info("Clicking the fixed panel button to expand the 'Statement of Information' panel...")
                button.click()
                logger.info("✅ Clicked the fixed panel button.")
                print("Clicked the fixed panel button.")
                time.sleep(0.5)
            else:
                logger.info("Panel already expanded - skipping click")
                print("Panel already expanded - skipping click")
            # Extract the link address from the 'Download' anchor after expansion
            download_link = None
            
            try:
                # Wait for download button with a shorter timeout
                download_button = wait.until(EC.presence_of_element_located((By.XPATH, download_xpath)))
                download_link = download_button.get_attribute('href')
                if multiple_results:
                    download_link = f"{download_link} MULTIPLE RESULTS"
                logger.info(f"Download link found: {download_link}")
                print(f"Download link: {download_link}")
            except Exception:
                logger.warning("No download link found - will add 'no download link invalid' note")
                print("No download link found - will add 'no download link invalid' note")
                download_link = "no download link invalid"

            # Extract the status (Active, Terminated, etc.)
            status_text = None
            import datetime
            from selenium.common.exceptions import StaleElementReferenceException
            # First attempt to extract status
            try:
                status_elem = self.driver.find_element(By.XPATH, "//*[@id='root']/div/div[1]/div/main/div[3]/div/div[2]/div/div/table/tbody/tr[2]/td[2]")
                status_text = status_elem.text.strip()
            except StaleElementReferenceException:
                status_text = "Status not found"
                logger.warning("Stale element reference on status extraction (first attempt). Will retry after re-hitting Enter and scrolling.")
            except Exception:
                try:
                    status_elem = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Status:')]")
                    status_text = status_elem.text.split('Status:')[-1].strip()
                    if not status_text:
                        raise Exception("No status after 'Status:'")
                except Exception:
                    try:
                        status_elem = self.driver.find_element(By.XPATH, "//*[text()='Status:']/following-sibling::*[1]")
                        status_text = status_elem.text.strip()
                    except Exception:
                        try:
                            status_elem = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Active') or contains(text(), 'Terminated')]")
                            status_text = status_elem.text.strip()
                        except Exception:
                            status_text = "Status not found"
            logger.info(f"Extracted status (first attempt): {status_text}")
            print(f"Extracted status (first attempt): {status_text}")

            # If status not found or stale, retry ONCE: re-hit Enter, wait, scroll, and try again
            if status_text == "Status not found":
                # Take a screenshot for debugging
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = f"status_not_found_{timestamp}.png"
                self.driver.save_screenshot(screenshot_path)
                logger.warning(f"Status not found, screenshot saved: {screenshot_path}")
                print(f"Status not found, screenshot saved: {screenshot_path}")
                # Try to refresh the panel by hitting Enter in the search field (if possible)
                try:
                    from selenium.webdriver.common.keys import Keys
                    search_inputs = self.driver.find_elements(By.XPATH, "//input[@id='SearchCriteria']")
                    if search_inputs:
                        search_inputs[0].send_keys(Keys.RETURN)
                        logger.info("Retried status extraction by hitting Enter in the search field.")
                        print("Retried status extraction by hitting Enter in the search field.")
                        time.sleep(3)
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        logger.info("Scrolled to the bottom of the page after retry.")
                        print("Scrolled to the bottom of the page after retry.")
                except Exception as e:
                    logger.warning(f"Could not re-hit Enter in search field: {e}")
                    print(f"Could not re-hit Enter in search field: {e}")
                # Retry status extraction ONCE
                try:
                    status_elem = self.driver.find_element(By.XPATH, "//*[@id='root']/div/div[1]/div/main/div[3]/div/div[2]/div/div/table/tbody/tr[2]/td[2]")
                    status_text = status_elem.text.strip()
                except StaleElementReferenceException:
                    status_text = "Status not found"
                    logger.warning("Stale element reference on status extraction (retry). Giving up.")
                except Exception:
                    try:
                        status_elem = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Status:')]")
                        status_text = status_elem.text.split('Status:')[-1].strip()
                        if not status_text:
                            raise Exception("No status after 'Status:'")
                    except Exception:
                        try:
                            status_elem = self.driver.find_element(By.XPATH, "//*[text()='Status:']/following-sibling::*[1]")
                            status_text = status_elem.text.strip()
                        except Exception:
                            try:
                                status_elem = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Active') or contains(text(), 'Terminated')]")
                                status_text = status_elem.text.strip()
                            except Exception:
                                status_text = "Status not found"
                logger.info(f"Extracted status (retry): {status_text}")
                print(f"Extracted status (retry): {status_text}")

            # Combine status and download link for the note
            note_text = f"Status: {status_text}\nDownload: {download_link}"

            # Wait 3 seconds before switching back
            time.sleep(3)
            # Switch back to PropertyDetail tab as soon as download link is obtained
            if property_tab:
                    logger.info(f"Switching back to PropertyDetail tab: {property_tab}")
                    self.driver.switch_to.window(property_tab)
                    
                    # Close the BizFileOnline tab
                    handles_before = self.driver.window_handles[:]
                    bizfile_tab_closed = False
                    for handle in handles_before:
                        self.driver.switch_to.window(handle)
                        if "bizfileonline.sos.ca.gov" in self.driver.current_url:
                            self.driver.close()
                            bizfile_tab_closed = True
                            break
                    # After closing, refresh the window handles
                    handles_after = self.driver.window_handles
                    if property_tab in handles_after:
                        self.driver.switch_to.window(property_tab)
                    
                    # Scroll to the bottom of the page
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    logger.info("Scrolled to the bottom of the PropertyDetail page.")
                    # Click the + Add Note button
                    try:
                        add_note_button = self.driver.find_element(By.XPATH, '//*[@id="btnAddNote"]')
                        add_note_button.click()
                        logger.info("Clicked the + Add Note button.")
                        
                        # Wait 1 second after clicking add note button
                        time.sleep(1)
                        
                        # First left-click the note text box, then type the download link
                        try:
                            # Try multiple selectors to find the note box since ID is dynamic
                            note_box = None
                            selectors = [
                                '//*[@id="1751926328502EditingInput"]',
                                '//input[contains(@id, "EditingInput")]',
                                '//textarea[contains(@id, "EditingInput")]',
                                '//input[contains(@class, "note")]',
                                '//textarea[contains(@class, "note")]',
                                '//input[contains(@placeholder, "note")]',
                                '//textarea[contains(@placeholder, "note")]'
                            ]
                            
                            for selector in selectors:
                                try:
                                    note_box = self.driver.find_element(By.XPATH, selector)
                                    logger.info(f"Found note box using selector: {selector}")
                                    print(f"Found note box using selector: {selector}")
                                    break
                                except:
                                    continue
                            
                            if note_box is None:
                                logger.info("No specific note box found, clicking on body")
                                print("No specific note box found, clicking on body")
                                body = self.driver.find_element(By.TAG_NAME, "body")
                                body.click()
                                time.sleep(0.5)
                                try:
                                    body.send_keys(note_text)
                                    logger.info(f"Typed note text to body: {note_text}")
                                    print(f"Typed note text to body: {note_text}")
                                except Exception as e:
                                    if 'stale element reference' in str(e).lower():
                                        # Handle stale element: re-hit Enter, wait, scroll, retry once
                                        logger.warning("Stale element reference on body. Retrying after re-hitting Enter and scrolling.")
                                        print("Stale element reference on body. Retrying after re-hitting Enter and scrolling.")
                                        search_inputs = self.driver.find_elements(By.XPATH, "//input[@id='SearchCriteria']")
                                        if search_inputs:
                                            search_inputs[0].send_keys(Keys.RETURN)
                                            time.sleep(3)
                                            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                                            time.sleep(1)
                                            # Try to find the body again and send keys
                                            body = self.driver.find_element(By.TAG_NAME, "body")
                                            body.click()
                                            time.sleep(0.5)
                                            body.send_keys(note_text)
                                    else:
                                        raise
                            else:
                                note_box.click()
                                logger.info("Left-clicked on note text box")
                                print("Left-clicked on note text box")
                                time.sleep(0.5)
                                time.sleep(3)
                                try:
                                    note_box.send_keys(note_text)
                                    logger.info(f"Typed note text directly: {note_text}")
                                    print(f"Typed note text directly: {note_text}")
                                except Exception as e:
                                    if 'stale element reference' in str(e).lower():
                                        # Handle stale element: re-hit Enter, wait, scroll, retry once
                                        logger.warning("Stale element reference on note box. Retrying after re-hitting Enter and scrolling.")
                                        print("Stale element reference on note box. Retrying after re-hitting Enter and scrolling.")
                                        search_inputs = self.driver.find_elements(By.XPATH, "//input[@id='SearchCriteria']")
                                        if search_inputs:
                                            search_inputs[0].send_keys(Keys.RETURN)
                                            time.sleep(3)
                                            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                                            time.sleep(1)
                                            # Try to find the note box again and send keys
                                            for selector in selectors:
                                                try:
                                                    note_box = self.driver.find_element(By.XPATH, selector)
                                                    note_box.click()
                                                    time.sleep(0.5)
                                                    note_box.send_keys(note_text)
                                                    logger.info(f"Retried typing note text after stale element: {note_text}")
                                                    print(f"Retried typing note text after stale element: {note_text}")
                                                    break
                                                except:
                                                    continue
                                    else:
                                        raise
                        except Exception as e:
                            logger.error(f"Failed to click note box or type: {e}")
                            print(f"Failed to click note box or type: {e}")
                            
                            # Final fallback: try ActionChains with the download link variable
                            try:
                                actions = ActionChains(self.driver)
                                actions.send_keys(note_text).perform()
                                logger.info(f"Typed using ActionChains fallback: {note_text}")
                                print(f"Typed using ActionChains fallback: {note_text}")
                            except Exception as e2:
                                logger.error(f"ActionChains fallback also failed: {e2}")
                                print(f"ActionChains fallback also failed: {e2}")
                        except Exception as e:
                            logger.error(f"Failed to click note box or paste: {e}")
                            print(f"Failed to click note box or paste: {e}")
                            
                            # Fallback: try ActionChains
                            try:
                                actions = ActionChains(self.driver)
                                actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
                                logger.info("Pasted using ActionChains fallback")
                                print("Pasted using ActionChains fallback")
                            except Exception as e2:
                                logger.error(f"ActionChains fallback also failed: {e2}")
                                print(f"ActionChains fallback also failed: {e2}")
                        
                        # Wait a moment for the paste to complete
                        time.sleep(1)
                        
                        # Click the Done button
                        try:
                            done_button = self.driver.find_element(By.XPATH, '//*[@id="notesGrid_updating_dialog_container_footer_buttonok"]')
                            done_button.click()
                            logger.info("Clicked the Done button.")
                            print("Clicked the Done button.")
                        except Exception as done_e:
                            logger.error(f"Could not click Done button: {done_e}")
                            print(f"Could not click Done button: {done_e}")
                        
                        # Wait a moment for the note to be saved
                        time.sleep(1)
                        
                        # Scroll up and click the save button
                        try:
                            # Scroll to the top of the page
                            self.driver.execute_script("window.scrollTo(0, 0);")
                            logger.info("Scrolled to the top of the page")
                            print("Scrolled to the top of the page")
                            time.sleep(0.5)  # Brief wait after scrolling
                            
                            # Click the save button
                            save_button = self.driver.find_element(By.XPATH, '//*[@id="btnPropertySave"]/span')
                            save_button.click()
                            logger.info("Clicked the save button")
                            print("Clicked the save button")
                            # Switch to Search Properties tab immediately after saving
                            self.switch_to_search_properties_tab()
                            print("[DEBUG] About to call check_first_unchecked_checkbox")
                            self.check_first_unchecked_checkbox()
                            # Close PropertyDetail tab if needed
                            self.close_propertydetail_tab_if_needed()
                        except Exception as save_e:
                            logger.error(f"Could not scroll up or click save button: {save_e}")
                            print(f"Could not scroll up or click save button: {save_e}")
                    except Exception as e:
                        logger.error(f"Could not click the + Add Note button: {e}")
        except Exception as e:
            logger.error(f"❌ ERROR: Could not click the fixed panel button or extract download link: {e}")
            print(f"Could not click the fixed panel button or extract download link: {e}")

    def search_bizfile_and_handle_results(self, payee_name):
        """
        On BizFileOnline:
        - Type payee_name, press Enter to search (never click any green button)
        - Wait for at least one result row (//table//tr[td])
        - Scroll down
        - Locate clickable entity name links (//table//tr//td[1]//a)
        - If one result, click it
        - If multiple, try for exact match, else fallback to newest Initial Filing Date
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        wait = WebDriverWait(self.driver, 15)
        try:
            # Find the search input, clear, and type payee_name, then press Enter
            logger.info("Locating BizFileOnline search input...")
            search_input = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@id='SearchCriteria']"))
            )
            search_input.clear()
            search_input.send_keys(payee_name)
            search_input.send_keys(Keys.ENTER)
            logger.info(f"Typed '{payee_name}' and pressed Enter.")
            print(f"Typed '{payee_name}' and pressed Enter.")
            # Wait for at least one result row
            logger.info("Waiting for at least one result row (//table//tr[td])...")
            rows = wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//table//tr[td]"))
            )
            num_rows = len(rows)
            logger.info(f"Found {num_rows} result row(s).")
            print(f"Found {num_rows} result row(s).")
            # Scroll after results are visible
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Locate all clickable entity name links
            links = self.driver.find_elements(By.XPATH, "//table//tr//td[1]//a")
            if not links:
                logger.error("❌ No clickable entity name links found.")
                print("No clickable entity name links found.")
                return
            if len(links) == 1:
                logger.info("Only one result. Clicking the entity name link.")
                print("Only one result. Clicking the entity name link.")
                try:
                    links[0].click()
                    logger.info("✅ Clicked the only entity link.")
                    print("Clicked the only entity link.")
                except Exception as click_e:
                    logger.error(f"❌ ERROR: Could not click entity link: {click_e}")
                    print(f"Could not click entity link: {click_e}")
                return
            # Multiple results: try for perfect match
            found_exact = False
            search_name = payee_name.strip().lower()
            for link in links:
                text = link.text.strip()
                entity_name = text.split('(')[0].strip().lower()
                logger.info(f"Entity link: '{entity_name}' vs search: '{search_name}'")
                if entity_name == search_name:
                    logger.info(f"✅ Perfect entity name match found: '{text}'. Clicking link.")
                    print(f"Perfect entity name match found: '{text}'. Clicking link.")
                    link.click()
                    found_exact = True
                    return
            if not found_exact:
                logger.info("No perfect entity name match found. Proceeding to Filing Date fallback.")
                print("No perfect entity name match found. Proceeding to Filing Date fallback.")
                self.find_and_click_most_recent_filing_bizfile_result()
        except Exception as e:
            logger.error(f"❌ ERROR: BizFileOnline search/handle failed: {e}")
            print(f"BizFileOnline search/handle failed: {e}")
            raise

    def perform_custom_automation(self, search_text):
        """
        Perform the custom automation steps: type into the search field, click the correct green Search button,
        then extract the Payee name from the first row, double-click it, immediately navigate to bizfileonline,
        and paste the Payee name into the search field. Only after this, pause or keep the browser open.
        Args:
            search_text (str): The text to search for in the field
        """
        logger.info("=== PERFORMING CUSTOM AUTOMATION STEPS (TYPE + CLICK SEARCH BUTTON + PAYEE NAME EXTRACTION + BIZFILE SEARCH) ===")
        logger.info(f"Automation will target the search field under 'File' label")
        logger.info(f"Search text to enter: '{search_text}'")
        self.find_and_fill_file_search_field(search_text)
        logger.info("=== SEARCH FIELD ENTRY AND SEARCH BUTTON CLICK COMPLETED ===")
        # Wait for results to load (optional, for user observation)
        time.sleep(2)
        payee_name = self.click_first_payee_and_store_name()
        logger.info(f"=== PAYEE NAME EXTRACTED AND ROW DOUBLE-CLICKED: '{payee_name}' ===")
        # Store the most recent PropertyDetail tab before opening BizFileOnline
        property_tab = None
        for handle in reversed(self.driver.window_handles):
            self.driver.switch_to.window(handle)
            url = self.driver.current_url
            if "/PropertyDetail/" in url and "id=" in url:
                property_tab = handle
                logger.info(f"Found PropertyDetail tab: {url} (handle: {handle})")
                break
        if not property_tab:
            property_tab = self.driver.current_window_handle
            logger.info(f"No PropertyDetail tab found, using current tab: {property_tab}")
        # Immediately navigate to bizfileonline and input the Payee name
        logger.info("Navigating to bizfileonline.sos.ca.gov/search/business for Payee name search...")
        # Open BizFileOnline in a new tab and switch to it
        self.driver.execute_script("window.open('https://bizfileonline.sos.ca.gov/search/business', '_blank');")
        time.sleep(1)  # Give the new tab a moment to open
        # Switch to the new BizFileOnline tab
        for handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
            if "bizfileonline.sos.ca.gov/search/business" in self.driver.current_url:
                logger.info(f"Switched to BizFileOnline tab: {handle}")
                break
        wait = WebDriverWait(self.driver, 15)
        try:
            # Locate the business search input field using XPath //*[@id='root']//input
            logger.info("Waiting for the business search input field to be present (//*[@id='root']//input)...")
            search_input = wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='root']//input"))
            )
            logger.info("✅ Business search input field is present and ready.")
            # Type the full business name into the search input field
            search_input.clear()
            for char in payee_name:
                search_input.send_keys(char)
                time.sleep(0.02)  # slight delay for realism
            logger.info(f"✅ Fully typed Payee name into search: '{payee_name}'")
            # Only after the name is fully typed, send Enter/Return key to trigger the search
            search_input.send_keys(Keys.RETURN)
            logger.info("✅ Sent Enter/Return key to trigger the search.")
            # Wait for at least one result row to appear before scrolling
            logger.info("Waiting for at least one result row (//table//tr[td]) to appear on BizFileOnline...")
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, "//table//tr[td]")))
                logger.info("✅ At least one result row is present.")
            except Exception as e:
                logger.warning(f"No result rows appeared after search: {e}")
            # Scroll to the bottom of the page to ensure all content is visible
            logger.info("Scrolling to the bottom of the BizFileOnline page to ensure all content is visible...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Add a longer delay to allow results to visually render after scrolling
            logger.info("Waiting 5 seconds after scrolling to allow results to visually render...")
            time.sleep(5)
            # After scrolling is complete, continue with the next automation steps
            self.find_and_click_exact_or_newest_entity(payee_name, property_tab=property_tab)
        except Exception as e:
            logger.error(f"❌ ERROR: Could not complete BizFileOnline automation: {e}")
            print(f"BizFileOnline automation failed: {e}")
            raise
        logger.info(f"=== PAYEE NAME SEARCHED ON BIZFILE: '{payee_name}' ===")

    def cleanup(self):
        """
        Clean up resources and close browser.
        """
        if self.driver:
            logger.info("Closing browser...")
            self.driver.quit()
            logger.info("Browser closed successfully")
            
    def run(self, highlight_text=None, name_text=None, signature_options=None, data_file_path=None):
        """
        Main method to run the complete automation process.
        This method orchestrates the entire automation process:
        1. Browser setup (visible Chrome)
        2. Navigate directly to ChatGPT
        3. Process uploaded data file with ChatGPT
        4. Create highlighted files
        Args:
            highlight_text (str): Optional custom text for ChatGPT highlighting
            name_text (str): Optional name to fill in PDF forms
            signature_options (dict): Optional signature options from checkboxes
            data_file_path (str): Path to the uploaded data file for ChatGPT processing
        """
        try:
            logger.info("=== STARTING RPA AUTOMATION ===")
            logger.info(f"Data file path: '{data_file_path}'")
            logger.info("Browser will remain VISIBLE throughout the process")
            
            # Step 1: Set up browser (VISIBLE - not headless)
            self.setup_browser()
            
            # Step 2: Navigate directly to ChatGPT
            logger.info("Navigating directly to ChatGPT...")
            self.driver.get("https://chatgpt.com")
            time.sleep(3)
            logger.info("Successfully navigated to ChatGPT")
            
            # Step 3: Wait for ChatGPT page to load
            logger.info("Waiting for ChatGPT page to fully load...")
            time.sleep(5)
            logger.info("✅ Successfully opened ChatGPT in browser!")
            
            # Step 4: Process uploaded data file with ChatGPT if provided
            if data_file_path:
                logger.info("=== PROCESSING UPLOADED DATA FILE WITH CHATGPT ===")
                
                try:
                    import subprocess
                    import sys
                    
                    # Run the ChatGPT file processor script
                    logger.info("Starting ChatGPT file processing...")
                    # Get the directory where this automation.py file is located
                    import os
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    cmd = ["python", os.path.join(current_dir, "chatgpt_file_processor.py"), "--file", data_file_path]
                    
                    if highlight_text:
                        cmd.extend(["--highlight", highlight_text])
                        logger.info(f"Using custom highlight text: '{highlight_text}'")
                    else:
                        logger.info("No custom highlight text provided, using default")
                    
                    if name_text:
                        cmd.extend(["--name", name_text])
                        logger.info(f"Using name text: '{name_text}'")
                    else:
                        logger.info("No name text provided")
                    
                    # Add signature options if provided
                    if signature_options:
                        cmd.extend(["--signature-options"])
                        import json
                        # Use a more robust JSON serialization that works with command line
                        signature_options_json = json.dumps(signature_options, separators=(',', ':'))
                        # Escape the JSON string for command line
                        signature_options_json = signature_options_json.replace('"', '\\"')
                        cmd.append(signature_options_json)
                        logger.info(f"Using signature options: '{signature_options}'")
                    else:
                        logger.info("No signature options provided")
                    
                    logger.info(f"Running command: {' '.join(cmd)}")
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0:
                        logger.info("✅ ChatGPT file processing completed successfully!")
                        logger.info(f"Processing details: {result.stdout}")
                        
                        # Step 5: Create highlighted files
                        logger.info("=== CREATING HIGHLIGHTED FILES ===")
                        highlight_cmd = ["python", os.path.join(current_dir, "chatgpt_processor_with_highlight.py")]
                        
                        if highlight_text:
                            highlight_cmd.append(highlight_text)
                        
                        if name_text:
                            highlight_cmd.extend(["--name", name_text])
                        
                        if signature_options:
                            highlight_cmd.extend(["--signature-options", signature_options_json])
                        
                        logger.info(f"Running highlight command: {' '.join(highlight_cmd)}")
                        highlight_result = subprocess.run(highlight_cmd, capture_output=True, text=True, timeout=300)
                        
                        if highlight_result.returncode == 0:
                            logger.info("SUCCESS: Highlighted files created successfully!")
                            logger.info(f"Highlight processing details: {highlight_result.stdout}")
                        else:
                            logger.error(f"ERROR: Highlight file creation failed: {highlight_result.stderr}")
                        
                        # Display success in browser
                        try:
                            self.driver.execute_script("""
                                // Create a notification in the browser
                                const notification = document.createElement('div');
                                notification.style.cssText = `
                                    position: fixed;
                                    top: 20px;
                                    right: 20px;
                                    background: #4CAF50;
                                    color: white;
                                    padding: 15px;
                                    border-radius: 5px;
                                    z-index: 10000;
                                    font-family: Arial, sans-serif;
                                    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                                `;
                                notification.innerHTML = 'SUCCESS: File processing completed! Check Downloads for processed files and chatgpt_response.txt for analysis.';
                                document.body.appendChild(notification);
                                
                                // Remove notification after 5 seconds
                                setTimeout(() => {
                                    if (notification.parentNode) {
                                        notification.parentNode.removeChild(notification);
                                    }
                                }, 5000);
                            """)
                        except Exception as e:
                            logger.warning(f"Could not display browser notification: {e}")
                            
                    else:
                        logger.warning(f"❌ ChatGPT file processing failed: {result.stderr}")
                        
                        # Display failure in browser
                        try:
                            self.driver.execute_script("""
                                // Create a notification in the browser
                                const notification = document.createElement('div');
                                notification.style.cssText = `
                                    position: fixed;
                                    top: 20px;
                                    right: 20px;
                                    background: #f44336;
                                    color: white;
                                    padding: 15px;
                                    border-radius: 5px;
                                    z-index: 10000;
                                    font-family: Arial, sans-serif;
                                    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                                `;
                                notification.innerHTML = 'ERROR: File processing failed! Check logs for details.';
                                document.body.appendChild(notification);
                                
                                // Remove notification after 5 seconds
                                setTimeout(() => {
                                    if (notification.parentNode) {
                                        notification.parentNode.removeChild(notification);
                                    }
                                }, 5000);
                            """)
                        except Exception as e:
                            logger.warning(f"Could not display browser notification: {e}")
                    
                except Exception as e:
                    logger.error(f"❌ ERROR: Failed to process uploaded file: {e}")
                    raise Exception(f"File processing failed: {e}")
            else:
                logger.info("No data file provided, skipping file processing")
            
            # Keep the browser open for user interaction
            logger.info("✅ Automation completed successfully!")
            logger.info("Browser will remain open for you to use ChatGPT")
            logger.info("You can now manually interact with ChatGPT to upload files, highlight them, and download them")
            
            try:
                # Wait indefinitely to keep browser open
                while True:
                    time.sleep(10)
                    # Check if browser is still open
                    try:
                        self.driver.current_url
                    except:
                        logger.info("Browser was closed by user")
                        break
            except KeyboardInterrupt:
                logger.info("Automation stopped by user")
            
            logger.info("✅ Automation completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ ERROR: Automation failed: {e}")
            raise Exception(f"Automation failed: {e}")
        finally:
            # Don't close the browser - let user interact with it
            logger.info("Browser will remain open for user interaction")

    def _is_login_required(self):
        """
        Check if login is required based on page content.
        Returns True if login elements are found, False otherwise.
        """
        try:
            # Look for common login indicators
            login_indicators = [
                "input[type='email']",
                "input[type='password']", 
                "input[name='email']",
                "input[name='password']",
                "#user_email",
                "#user_password",
                ".login-btn",
                "button[type='submit']"
            ]
            
            for selector in login_indicators:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed():
                        logger.info(f"Login required - found element: {selector}")
                        return True
                except NoSuchElementException:
                    continue
                    
            logger.info("No login elements found, proceeding without login")
            return False
        except Exception as e:
            logger.warning(f"Error checking for login elements: {e}")
            return False
            
    def _wait_for_download_completion(self):
        """
        Wait for download to complete by monitoring browser state and download indicators.
        This method waits until the download is finished before proceeding.
        """
        logger.info("Starting download completion monitoring...")
        
        # Method 1: Wait for any download progress indicators to disappear
        # Look for common download progress elements that disappear when download is complete
        download_progress_selectors = [
            ".download-progress",
            ".progress-bar",
            "[data-testid='download-progress']",
            ".loading",
            ".spinner",
            "[class*='progress']",
            "[class*='loading']"
        ]
        
        # Method 2: Wait for download button to become clickable again (if it was disabled during download)
        download_button_xpath = "//*[@id=\"overview-section-content_294433706\"]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/span/button"
        
        # Method 3: Wait for any success messages or completion indicators
        success_indicators = [
            ".download-complete",
            ".success-message",
            "[data-testid='download-success']",
            ".notification-success"
        ]
        
        max_wait_time = 60  # Maximum wait time in seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                # Check if any progress indicators are still visible
                progress_visible = False
                for selector in download_progress_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if element.is_displayed():
                                progress_visible = True
                        break
                        if progress_visible:
                            break
                    except:
                        continue
                
                # Check if download button is clickable again
                button_clickable = False
                try:
                    download_button = self.driver.find_element(By.XPATH, download_button_xpath)
                    button_clickable = download_button.is_enabled()
                except:
                    button_clickable = False
                
                # Check if success indicators are visible
                success_visible = False
                for selector in success_indicators:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if element.is_displayed():
                                success_visible = True
                            break
                        if success_visible:
                            break
                    except:
                        continue
                
                # If no progress indicators are visible and button is clickable, download might be complete
                if not progress_visible and button_clickable:
                    logger.info("Download appears to be complete (no progress indicators, button clickable)")
                    break
                
                # If success indicators are visible, download is complete
                if success_visible:
                    logger.info("Download completion indicators found")
                    break
                
                # Wait a bit before checking again
                time.sleep(2)
                logger.info("Download still in progress, waiting...")
                
            except Exception as e:
                logger.warning(f"Error checking download status: {e}")
                time.sleep(2)
        
        # Additional wait to ensure download is fully processed
        logger.info("Download monitoring completed, waiting additional 3 seconds for final processing...")
        time.sleep(3)
        
        logger.info("Download completion wait finished")

    def _process_monday_board_items(self, company_name=None, start_point="none", start_page=None):
        """
        Process Monday.com board items specifically.
        """
        logger.info("=== PROCESSING MONDAY.COM BOARD ITEMS ===")
        
        # Wait for the board to load
        wait = WebDriverWait(self.driver, 20)
        
        try:
            # Find all board items/rows
            board_item_selectors = [
                "//div[contains(@class, 'row')]",
                "//div[contains(@class, 'item')]",
                "//div[contains(@class, 'board-item')]",
                "//div[contains(@data-testid, 'row')]",
                "//div[contains(@class, 'board-row')]",
                "//div[contains(@class, 'clickable')]"
            ]
            
            board_items = []
            for selector in board_item_selectors:
                try:
                    board_items = self.driver.find_elements(By.XPATH, selector)
                    if board_items:
                        logger.info(f"Found {len(board_items)} board items using selector: {selector}")
                        break
                except Exception:
                    continue
            
            if not board_items:
                logger.warning("No board items found. The page may not be a Monday.com board or may be loading.")
                return
            
            logger.info(f"Processing {len(board_items)} board items")
            
            # Process each board item
            for item_index, item in enumerate(board_items):
                if self.companies_processed >= self.max_companies:
                    logger.info("Reached maximum companies limit")
                    break
                
                try:
                    # Extract company/lead information from the board item
                    company_info = self._extract_company_info_from_board_item(item)
                    
                    if not company_info:
                        logger.warning(f"Could not extract company info from item {item_index + 1}")
                        continue
                    
                    logger.info(f"=== PROCESSING BOARD ITEM {item_index + 1}: '{company_info}' ===")
                    
                    # Process the company through BizFileOnline
                    success = self.process_single_payee(company_info)
                    
                    if success:
                        logger.info(f"✅ Successfully processed company: '{company_info}'")
                        self.companies_processed += 1
                    else:
                        logger.error(f"❌ Failed to process company: '{company_info}'")
                        self.consecutive_failures += 1
                    
                    # Brief pause between items
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error processing board item {item_index + 1}: {e}")
                    self.consecutive_failures += 1
                    
                    if self.consecutive_failures >= 3:
                        logger.error("Too many consecutive failures, stopping automation")
                        break
                
        except Exception as e:
            logger.error(f"Error processing Monday.com board: {e}")

    def _extract_company_info_from_board_item(self, item):
        """
        Extract company/lead information from a Monday.com board item.
        """
        try:
            # Try multiple selectors to find company/lead name
            company_selectors = [
                ".//div[contains(@class, 'cell')]//span[contains(text(), '')]",
                ".//div[contains(@class, 'column')]//span[contains(text(), '')]",
                ".//span[contains(@class, 'text')]",
                ".//div[contains(@class, 'text')]",
                ".//span[not(contains(@class, 'icon'))]",
                ".//div[contains(@class, 'lead')]//span",
                ".//div[contains(@class, 'name')]//span",
                ".//div[contains(@class, 'title')]//span"
            ]
            
            for selector in company_selectors:
                try:
                    element = item.find_element(By.XPATH, selector)
                    text = element.text.strip()
                    if text and len(text) > 2:  # Ensure it's not just whitespace or very short
                        logger.info(f"Found company info with selector: {selector}")
                        return text
                except Exception:
                    continue
            
            return None
            
        except Exception as e:
            logger.warning(f"Error extracting company info: {e}")
            return None

    def _process_generic_page(self, company_name=None, start_point="none", start_page=None):
        """
        Process a generic page (not specifically Monday.com).
        """
        logger.info("=== PROCESSING GENERIC PAGE ===")
        logger.info("This is a generic page. You may need to add specific processing logic.")
        logger.info("Current URL: " + self.driver.current_url)
        
        # For now, just log the page information
        try:
            page_title = self.driver.title
            logger.info(f"Page title: {page_title}")
            
            # Take a screenshot for reference
            self.driver.save_screenshot("generic_page_screenshot.png")
            logger.info("Screenshot saved as 'generic_page_screenshot.png'")
            
        except Exception as e:
            logger.error(f"Error processing generic page: {e}")

    def navigate_to_website(self):
        """
        Navigate to the website. This method is now overridden by the dynamic navigation in run().
        """
        logger.info("This method is deprecated. Use run() with search_text parameter instead.")
        pass

    def search_payee_on_bizfile(self, payee_name):
        """
        1. Navigate to BizFileOnline explicitly
        2. Wait for the business search input field to be present (//*[@id='root']//input)
        3. Once present, type the Payee name (example: "100 BILLABLE DAYS LLC")
        4. Immediately after typing, send the Enter/Return key to the input field to trigger the search
        5. Wait exactly 4 seconds after pressing Enter for results to load
        6. Scroll down to bring results into view
        7. Locate all result rows using XPath //table//tr[td]
        8. If exactly one result: extract entity name, if exact match click immediately
        9. If multiple results: click only the first result, and append 'multiple search results' to the download link/note
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import time
        logger.info("Navigating to BizFileOnline: https://bizfileonline.sos.ca.gov/search/business")
        wait = WebDriverWait(self.driver, 15)
        try:
            logger.info("Waiting for the business search input field to be present (//*[@id='root']//input)...")
            search_input = wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='root']//input"))
            )
            logger.info("✅ Business search input field is present and ready.")
            search_input.clear()
            search_input.send_keys(payee_name)
            logger.info(f"✅ Typed Payee name into search: '{payee_name}'")
            search_input.send_keys(Keys.RETURN)
            logger.info("✅ Sent Enter/Return key to trigger the search.")
            logger.info("Waiting exactly 4 seconds for search results to load...")
            time.sleep(4)
            logger.info("Scrolling down to bring results into view...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            logger.info("Locating all result rows using XPath //table//tr[td]...")
            rows = self.driver.find_elements(By.XPATH, "//table//tr[td]")
            num_rows = len(rows)
            logger.info(f"Found {num_rows} result row(s).")
            print(f"Found {num_rows} result row(s).")
            multiple_results = False
            if num_rows == 0:
                logger.warning("No result rows found.")
                print("No result rows found.")
                return
            if num_rows == 1:
                logger.info("Exactly one result found. Extracting entity name...")
                print("Exactly one result found. Extracting entity name...")
                try:
                    row = rows[0]
                    clickable_elements = row.find_elements(By.XPATH, ".//button | .//a | .//*[contains(@class, 'clickable')] | .//*[contains(@class, 'blue')]")
                    if clickable_elements:
                        entity_name = clickable_elements[0].text.strip()
                        logger.info(f"Extracted entity name: '{entity_name}'")
                        print(f"Extracted entity name: '{entity_name}'")
                        if self._normalize_text(entity_name) == self._normalize_text(payee_name):
                            logger.info(f"✅ Exact match found. Clicking the blue button/row immediately.")
                            print(f"✅ Exact match found. Clicking the blue button/row immediately.")
                            clickable_elements[0].click()
                            self.find_and_click_exact_or_newest_entity(payee_name, property_tab=None, multiple_results=False)
                            return
                        else:
                            logger.info("No exact match found in single result. Clicking anyway.")
                            print("No exact match found in single result. Clicking anyway.")
                            clickable_elements[0].click()
                            self.find_and_click_exact_or_newest_entity(payee_name, property_tab=None, multiple_results=False)
                            return
                    else:
                        logger.warning("No clickable elements found in the single result row.")
                        print("No clickable elements found in the single result row.")
                        return
                except Exception as e:
                    logger.error(f"Error processing single result: {e}")
                    print(f"Error processing single result: {e}")
                    return
            else:
                logger.info("Multiple results found. Selecting and clicking the best match by most letters in common...")
                print("Multiple results found. Selecting and clicking the best match by most letters in common...")
                rows = self.driver.find_elements(By.XPATH, "//tr[contains(@class, 'div-table-row')]")
                max_common = -1
                best_index = -1
                best_entity_name = None

                for i, row in enumerate(rows):
                    spans = row.find_elements(By.XPATH, ".//span[@class='cell']")
                    if spans:
                        entity_name = spans[0].text.strip()
                        common = self._letters_in_common(payee_name, entity_name)
                        if common > max_common:
                            max_common = common
                            best_index = i
                            best_entity_name = entity_name

                if best_index != -1:
                    row_index = best_index + 1  # XPath is 1-based
                    xpath = f'//*[@id="root"]/div/div[1]/div/main/div[2]/table/tbody/tr[{row_index}]/td[2]'
                    try:
                        cell_elem = self.driver.find_element(By.XPATH, xpath)
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", cell_elem)
                        print(f"[DEBUG] Trying ActionChains click on row {row_index} td[2] with text: {cell_elem.text}")
                        from selenium.webdriver.common.action_chains import ActionChains
                        ActionChains(self.driver).move_to_element(cell_elem).click().perform()
                        print(f"[DEBUG] Successfully clicked row {row_index} td[2]")
                    except Exception as e:
                        print(f"[ERROR] Could not click row {row_index} td[2]: {e}")
                        try:
                            print("[ERROR] Cell outerHTML:", cell_elem.get_attribute('outerHTML'))
                        except Exception as e2:
                            print(f"[ERROR] Could not get outerHTML: {e2}")
                        import traceback
                        traceback.print_exc()
                    self.find_and_click_exact_or_newest_entity(payee_name, property_tab=None, multiple_results=True, already_clicked=True)
                    return
        except Exception as e:
            logger.error(f"❌ ERROR: Could not complete BizFileOnline automation: {e}")
            raise

    def _normalize_text(self, text):
        """
        Normalize text for comparison: lowercase, remove extra spaces, trim
        """
        if not text:
            return ""
        return " ".join(text.lower().split()) 

    def switch_to_search_properties_tab(self):
        """
        Switch to the already-open Search Properties tab (Process Imported Files) by URL.
        Logs the result. Does not close any tabs.
        """
        found = False
        for handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
            current_url = self.driver.current_url
            if "rears.retainedequity.com/#/Search/:type=file" in current_url:
                logger.info(f"Switched to Search Properties tab: {handle}")
                found = True
                break
        if not found:
            logger.warning("❌ Could not find Search Properties tab.") 

    def check_first_unchecked_checkbox(self):
        """
        After switching to the Search Properties tab, check the first unchecked checkbox in the table.
        If the first is checked, check the next unchecked one and stop.
        """
        import time
        from selenium.webdriver.common.by import By

        print("[DEBUG] Starting check_first_unchecked_checkbox")
        logger.info("[DEBUG] Starting check_first_unchecked_checkbox")
        time.sleep(2)  # Wait for the page to be ready
        try:
            rows = self.driver.find_elements(By.XPATH, '//*[@id="propsGrid"]/tbody/tr')
            print(f"[DEBUG] Found {len(rows)} rows in the table")
            logger.info(f"[DEBUG] Found {len(rows)} rows in the table")
            checked = False
            for idx, row in enumerate(rows, start=1):
                try:
                    checkbox_xpath = f'//*[@id="propsGrid"]/tbody/tr[{idx}]/th/span[2]/span'
                    print(f"[DEBUG] Trying to find checkbox at: {checkbox_xpath}")
                    logger.info(f"[DEBUG] Trying to find checkbox at: {checkbox_xpath}")
                    checkbox = self.driver.find_element(By.XPATH, checkbox_xpath)
                    print(f"[DEBUG] Found checkbox element for row {idx}")
                    logger.info(f"[DEBUG] Found checkbox element for row {idx}")
                    # Try to determine if the checkbox is checked (by class or aria-checked)
                    checkbox_class = checkbox.get_attribute("class")
                    aria_checked = checkbox.get_attribute("aria-checked")
                    print(f"[DEBUG] Row {idx}: checkbox class='{checkbox_class}', aria-checked='{aria_checked}'")
                    logger.info(f"[DEBUG] Row {idx}: checkbox class='{checkbox_class}', aria-checked='{aria_checked}'")
                    is_checked = "checked" in (checkbox_class or "") or aria_checked == "true"
                    print(f"[DEBUG] Row {idx}: Checkbox checked = {is_checked}")
                    logger.info(f"[DEBUG] Row {idx}: Checkbox checked = {is_checked}")
                    if not is_checked:
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                        time.sleep(0.2)
                        checkbox.click()
                        print(f"[DEBUG] Checked the box at row {idx}")
                        logger.info(f"Checked the box at row {idx}")
                        checked = True
                        break
                    else:
                        print(f"[DEBUG] Row {idx} already checked.")
                        logger.info(f"[DEBUG] Row {idx} already checked.")
                except Exception as e:
                    print(f"[DEBUG] Exception in row {idx}: {e}")
                    logger.warning(f"[DEBUG] Exception in row {idx}: {e}")
                    continue
            if not checked:
                print("[DEBUG] All checkboxes are already checked or none found.")
                logger.warning("All checkboxes are already checked or none found.")
        except Exception as e:
            print(f"[DEBUG] Could not check any box: {e}")
            logger.warning(f"[DEBUG] Could not check any box: {e}")

    def check_off_duplicate_payee_rows(self, payee_name, start_index):
        """
        Check off all rows with the same Payee Name starting from the given index.
        Returns the index of the next different Payee Name (or total rows if no more).
        """
        from selenium.webdriver.common.by import By
        import time
        
        logger.info(f"Checking off duplicate rows for Payee Name: '{payee_name}' starting from index {start_index}")
        
        try:
            rows = self.driver.find_elements(By.XPATH, '//*[@id="propsGrid"]/tbody/tr')
            checked_count = 0
            next_different_index = start_index
            
            for i in range(start_index, len(rows)):
                try:
                    # Extract Payee Name from the row
                    payee_name_cell = rows[i].find_element(By.XPATH, ".//td[2]")
                    current_payee_name = payee_name_cell.text.strip()
                    
                    # If Payee Name matches, check off the row
                    if current_payee_name == payee_name:
                        checkbox_xpath = f'//*[@id="propsGrid"]/tbody/tr[{i+1}]/th/span[2]/span'
                        checkbox = self.driver.find_element(By.XPATH, checkbox_xpath)
                        
                        # Check if already checked
                        checkbox_class = checkbox.get_attribute("class")
                        aria_checked = checkbox.get_attribute("aria-checked")
                        is_checked = "checked" in (checkbox_class or "") or aria_checked == "true"
                        
                        if not is_checked:
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                            time.sleep(0.2)
                            checkbox.click()
                            logger.info(f"✅ Checked off row {i+1} for Payee Name: '{payee_name}'")
                            checked_count += 1
                        else:
                            logger.info(f"Row {i+1} already checked for Payee Name: '{payee_name}'")
                            checked_count += 1
                        
                        next_different_index = i + 1  # Update to next position
                    else:
                        # Stop when we find a different Payee Name
                        logger.info(f"Found different Payee Name at row {i+1}: '{current_payee_name}' - stopping duplicate check")
                        next_different_index = i  # This is the next different Payee Name
                        break
                        
                except Exception as e:
                    logger.warning(f"Error checking row {i+1}: {e}")
                    continue
            
            logger.info(f"✅ Checked off {checked_count} rows for Payee Name: '{payee_name}'")
            logger.info(f"✅ Next different Payee Name will be at index: {next_different_index}")
            return next_different_index
            
        except Exception as e:
            logger.error(f"❌ ERROR: Could not check off duplicate rows: {e}")
            return start_index

    def find_and_process_next_row(self):
        """
        Find the next row to process based on the last processed Payee Name.
        If last_payee_name is None, process the first row.
        Otherwise, scan for the row with last_payee_name, then process the row immediately after it.
        If there are multiple rows with the same Payee Name, check them all off together.
        Returns the Payee Name of the processed row, or None if no row was processed.
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import time
        
        logger.info("=== FINDING AND PROCESSING NEXT ROW ===")
        logger.info(f"Last processed Payee Name: {self.last_payee_name}")
        
        try:
            # Wait for the table to be present
            wait = WebDriverWait(self.driver, 20)
            rows = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="propsGrid"]/tbody/tr')))
            
            if not rows:
                logger.warning("No rows found in the table")
                return None
            
            logger.info(f"Found {len(rows)} rows in the table")
            
            target_row_index = 0  # Default to first row
            
            if self.last_payee_name is not None:
                # Find the row with the last processed Payee Name
                logger.info(f"Searching for row with Payee Name: '{self.last_payee_name}'")
                found_last_row = False
                
                for i, row in enumerate(rows):
                    try:
                        # Extract Payee Name from the row (assuming it's in the 2nd column)
                        payee_name_cell = row.find_element(By.XPATH, ".//td[2]")
                        payee_name = payee_name_cell.text.strip()
                        
                        logger.info(f"Row {i+1} Payee Name: '{payee_name}'")
                        
                        if payee_name == self.last_payee_name:
                            logger.info(f"✅ Found last processed row at index {i}")
                            found_last_row = True
                            target_row_index = i + 1  # Process the next row
                            break
                            
                    except Exception as e:
                        logger.warning(f"Error processing row {i+1}: {e}")
                        continue
                
                if not found_last_row:
                    logger.warning(f"Could not find row with last processed Payee Name: '{self.last_payee_name}'")
                    logger.info("Starting from the first row")
                    target_row_index = 0
            else:
                logger.info("No last processed Payee Name - starting with first row")
            
            # Check if target row index is within bounds
            if target_row_index >= len(rows):
                logger.info("Target row index is beyond table bounds - reached end of table")
                return None
            
            # Process the target row
            target_row = rows[target_row_index]
            payee_name_cell = target_row.find_element(By.XPATH, ".//td[2]")
            payee_name = payee_name_cell.text.strip()
            
            logger.info(f"✅ Processing row {target_row_index + 1} with Payee Name: '{payee_name}'")
            print(f"Processing Payee Name: {payee_name}")
            
            # Check off all rows with the same Payee Name and get the next different index
            next_different_index = self.check_off_duplicate_payee_rows(payee_name, target_row_index)
            
            # Double-click the first row with this Payee Name to open it
            ActionChains(self.driver).double_click(target_row).perform()
            logger.info(f"✅ Double-clicked row {target_row_index + 1}")
            
            # Update tracking - store the next different Payee Name for the next iteration
            if next_different_index < len(rows):
                try:
                    next_row = rows[next_different_index]
                    next_payee_name_cell = next_row.find_element(By.XPATH, ".//td[2]")
                    next_different_payee_name = next_payee_name_cell.text.strip()
                    logger.info(f"Next iteration will start from Payee Name: '{next_different_payee_name}' at row {next_different_index + 1}")
                    # Store the next different Payee Name so we can find it in the next iteration
                    self.last_payee_name = next_different_payee_name
                except Exception as e:
                    logger.warning(f"Could not determine next Payee Name: {e}")
                    self.last_payee_name = payee_name
            else:
                logger.info("No more rows after processing duplicates - reached end of table")
                self.last_payee_name = payee_name
            
            self.companies_processed += 1
            
            return payee_name
            
        except Exception as e:
            logger.error(f"❌ ERROR: Could not find and process next row: {e}")
            self.consecutive_failures += 1
            return None

    def should_stop_processing(self):
        """
        Check if processing should stop based on failure count.
        """
        if self.consecutive_failures >= 3:
            logger.warning(f"❌ Stopping: {self.consecutive_failures} consecutive failures")
            return True
        
        return False

    def reset_failure_count(self):
        """
        Reset the consecutive failure count after a successful processing.
        """
        if self.consecutive_failures > 0:
            logger.info(f"Resetting consecutive failure count from {self.consecutive_failures} to 0")
            self.consecutive_failures = 0

    def process_single_payee(self, payee_name):
        """
        Process a single Payee Name through the complete automation workflow.
        This method assumes the browser is already set up and on the correct page.
        
        Args:
            payee_name (str): The Payee Name to process
            
        Returns:
            bool: True if processing was successful, False otherwise
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import time
        
        logger.info(f"=== PROCESSING SINGLE PAYEE: '{payee_name}' ===")
        
        try:
            # Store the most recent PropertyDetail tab before opening BizFileOnline
            property_tab = None
            for handle in reversed(self.driver.window_handles):
                self.driver.switch_to.window(handle)
                url = self.driver.current_url
                if "/PropertyDetail/" in url and "id=" in url:
                    property_tab = handle
                    logger.info(f"Found PropertyDetail tab: {url} (handle: {handle})")
                    break
            
            if not property_tab:
                property_tab = self.driver.current_window_handle
                logger.info(f"No PropertyDetail tab found, using current tab: {property_tab}")
            
            # Navigate to BizFileOnline and search for the Payee name
            logger.info("Navigating to bizfileonline.sos.ca.gov/search/business for Payee name search...")
            
            # Open BizFileOnline in a new tab and switch to it
            self.driver.execute_script("window.open('https://bizfileonline.sos.ca.gov/search/business', '_blank');")
            time.sleep(1)  # Give the new tab a moment to open
            
            # Switch to the new BizFileOnline tab
            for handle in self.driver.window_handles:
                self.driver.switch_to.window(handle)
                if "bizfileonline.sos.ca.gov/search/business" in self.driver.current_url:
                    logger.info(f"Switched to BizFileOnline tab: {handle}")
                    break
            
            wait = WebDriverWait(self.driver, 15)
            
            # Locate the business search input field and search
            logger.info("Waiting for the business search input field to be present (//*[@id='root']//input)...")
            search_input = wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='root']//input"))
            )
            logger.info("✅ Business search input field is present and ready.")
            
            # Type the full business name into the search input field
            search_input.clear()
            for char in payee_name:
                search_input.send_keys(char)
                time.sleep(0.02)  # slight delay for realism
            logger.info(f"✅ Fully typed Payee name into search: '{payee_name}'")
            
            # Send Enter/Return key to trigger the search
            search_input.send_keys(Keys.RETURN)
            logger.info("✅ Sent Enter/Return key to trigger the search.")
            
            # Wait for search results to fully render
            logger.info("Waiting 3 seconds for BizFileOnline search results to fully render...")
            time.sleep(3)
            
            # Scroll to the bottom of the page to ensure all content is visible
            logger.info("Scrolling to the bottom of the BizFileOnline page to ensure all content is visible...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Add a longer delay to allow results to visually render after scrolling
            logger.info("Waiting 5 seconds after scrolling to allow results to visually render...")
            time.sleep(5)
            
            # Process the search results
            self.find_and_click_exact_or_newest_entity(payee_name, property_tab=property_tab)
            
            logger.info(f"✅ Successfully processed Payee: '{payee_name}'")
            self.reset_failure_count()
            return True
            
        except Exception as e:
            logger.error(f"❌ ERROR: Failed to process Payee '{payee_name}': {e}")
            self.consecutive_failures += 1
            return False 

    def _normalize_for_similarity(self, text):
        if not text:
            return ""
        # Lowercase, remove non-alphanumeric except spaces, collapse spaces
        text = text.lower()
        text = re.sub(r'[^a-z0-9 ]+', '', text)
        text = re.sub(r'\\s+', ' ', text)
        return text.strip()

    def _letters_in_common(self, a, b):
        import re
        a = re.sub(r'[^a-z]', '', a.lower())
        b = re.sub(r'[^a-z]', '', b.lower())
        return len(set(a) & set(b))

    def add_note_to_property(self, note_text):
        """
        Add a note to the property using the + Add Note button and the provided note_text.
        Handles finding the note box, entering the note, clicking Done, and saving.
        """
        import time
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        # Always scroll to the bottom before looking for the Add Note button
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
        try:
            add_note_button = self.driver.find_element(By.XPATH, '//*[@id="btnAddNote"]')
            add_note_button.click()
            logger.info("Clicked the + Add Note button.")
            # Debug: print the HTML of the note area
            try:
                note_area = self.driver.find_element(By.XPATH, "//body")
                print("[DEBUG] Note area outerHTML:", note_area.get_attribute("outerHTML"))
            except Exception as debug_e:
                print("[DEBUG] Could not get note area HTML:", debug_e)
            # Wait for the note input to appear
            selectors = [
                '//textarea[@data-editor-for-notetext="true"]',
                '//textarea[contains(@class, "ui-igedit-textarea")]',
                '//textarea'
            ]
            note_box = None
            wait = WebDriverWait(self.driver, 5)
            for selector in selectors:
                try:
                    note_box = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                    logger.info(f"Found note box using selector: {selector}")
                    break
                except Exception:
                    continue
            if note_box is None:
                logger.warning("No note input box found after waiting. Trying body fallback.")
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.click()
                time.sleep(0.5)
                from selenium.webdriver.common.action_chains import ActionChains
                actions = ActionChains(self.driver)
                actions.send_keys(note_text).perform()
                logger.info(f"Typed '{note_text}' to body as note using ActionChains fallback.")
            else:
                note_box.click()
                time.sleep(0.2)
                try:
                    note_box.clear()
                except Exception:
                    pass
                time.sleep(0.2)
                note_box.send_keys(note_text)
                logger.info(f"Typed '{note_text}' directly as note.")
                # Fallback: if text not entered, try ActionChains
                if note_box.get_attribute('value') == '' and note_box.get_attribute('textContent') == '':
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(self.driver)
                    actions.move_to_element(note_box).click().send_keys(note_text).perform()
                    logger.info(f"Retried typing '{note_text}' using ActionChains on note_box.")
            time.sleep(1)
            # Click the Done button
            try:
                done_button = self.driver.find_element(By.XPATH, '//*[@id="notesGrid_updating_dialog_container_footer_buttonok"]')
                done_button.click()
                logger.info("Clicked the Done button.")
            except Exception as done_e:
                logger.error(f"Could not click Done button: {done_e}")
            time.sleep(1)
            # Save and return
            try:
                self.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(0.5)
                save_button = self.driver.find_element(By.XPATH, '//*[@id="btnPropertySave"]/span')
                save_button.click()
                logger.info("Clicked the save button")
                self.switch_to_search_properties_tab()
                self.check_first_unchecked_checkbox()
                # Close PropertyDetail tab if needed
                self.close_propertydetail_tab_if_needed()
            except Exception as save_e:
                logger.error(f"Could not scroll up or click save button: {save_e}")
        except Exception as note_e:
            logger.error(f"Could not add note: {note_e}")

    def close_propertydetail_tab_if_needed(self):
        """
        Close the current tab ONLY if it is a PropertyDetail page and NOT a Search page.
        """
        current_url = self.driver.current_url
        # Only close if it's a PropertyDetail page and NOT a Search page
        if "/PropertyDetail/" in current_url and "/Search/:type=file" not in current_url:
            logger.info(f"Closing PropertyDetail tab: {current_url}")
            self.driver.close()
        else:
            logger.info(f"Not closing tab: {current_url}")