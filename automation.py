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
from selenium.webdriver.common.action_chains import ActionChains
import difflib
from datetime import datetime

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
        
        # Tracking variables for continuous processing
        self.last_payee_name = None  # Store the last processed Payee Name
        self.consecutive_failures = 0  # Track consecutive failures
        self.max_companies = 50  # Maximum number of companies to process
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
                best_elem.click()
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
                best_row.click()
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

    def find_and_click_exact_or_newest_entity(self, payee_name, property_tab=None):
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
                    self._wait_and_click_view_history(wait, property_tab=property_tab)
                else:
                    logger.warning("No blue clickable element found in the only result row.")
                    print("No blue clickable element found in the only result row.")
                return
            # Multiple rows: look for exact match
            found_exact = False
            search_name = payee_name.strip().lower()
            for row in rows:
                clickable = None
                entity_text = None
                for xpath in [
                    ".//td[1]//button",
                    ".//td[1]//div[contains(@class,'entity')]",
                    ".//td[1]//span"
                ]:
                    elems = row.find_elements(By.XPATH, xpath)
                    if elems:
                        clickable = elems[0]
                        entity_text = clickable.text.strip()
                        break
                if entity_text:
                    logger.info(f"Entity candidate: '{entity_text}' vs search: '{search_name}'")
                    if entity_text.strip().lower() == search_name:
                        logger.info(f"✅ Exact entity name match found: '{entity_text}'. Clicking clickable element.")
                        print(f"Exact entity name match found: '{entity_text}'. Clicking clickable element.")
                        clickable.click()
                        found_exact = True
                        # After click, wait for right panel and click 'View History'
                        self._wait_and_click_view_history(wait, property_tab=property_tab)
                        return
            if not found_exact:
                logger.info("No exact entity name match found. No click performed.")
                print("No exact entity name match found. No click performed.")
        except Exception as e:
            logger.error(f"❌ ERROR: Could not process BizFileOnline entity results: {e}")
            print(f"BizFileOnline entity results processing failed: {e}")
            raise

    def _wait_and_click_view_history(self, wait, property_tab=None):
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
                self._wait_and_click_statement_of_information_panel(wait, property_tab=property_tab)
            else:
                logger.warning("'View History' button not found after waiting.")
                print("'View History' button not found after waiting.")
        except Exception as e:
            logger.error(f"❌ ERROR: Could not click 'View History' button: {e}")
            print(f"Could not click 'View History' button: {e}")

    def _wait_and_click_statement_of_information_panel(self, wait, property_tab=None):
        """
        After clicking the 'View History' button, wait up to 3 seconds for the panel area to load.
        Then, left-click the button located at the fixed XPath /html/body/div[3]/div/div[1]/div[2]/div/div[2]/button.
        No scrolling is needed. If the button is not found, log an error and do not fail silently.
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
            logger.info("Clicking the fixed panel button to expand the 'Statement of Information' panel...")
            button.click()
            logger.info("✅ Clicked the fixed panel button.")
            print("Clicked the fixed panel button.")
            time.sleep(0.5)
            # Extract the link address from the 'Download' anchor after expansion
            download_xpath = "//a[contains(., 'Download')]"
            download_link = None
            
            try:
                # Wait for download button with a shorter timeout
                download_button = wait.until(EC.presence_of_element_located((By.XPATH, download_xpath)))
                download_link = download_button.get_attribute('href')
                logger.info(f"Download link found: {download_link}")
                print(f"Download link: {download_link}")
            except Exception:
                logger.warning("No download link found - will add 'no download link invalid' note")
                print("No download link found - will add 'no download link invalid' note")
                download_link = "no download link invalid"
            
            # Wait 3 seconds before switching back
            time.sleep(3)
            # Switch back to PropertyDetail tab as soon as download link is obtained
            if property_tab:
                    logger.info(f"Switching back to PropertyDetail tab: {property_tab}")
                    self.driver.switch_to.window(property_tab)
                    
                    # Close the BizFileOnline tab
                    try:
                        for handle in self.driver.window_handles:
                            self.driver.switch_to.window(handle)
                            if "bizfileonline.sos.ca.gov" in self.driver.current_url:
                                self.driver.close()
                                logger.info("✅ Closed BizFileOnline tab")
                                break
                        # Switch back to PropertyDetail tab
                        self.driver.switch_to.window(property_tab)
                    except Exception as e:
                        logger.warning(f"Could not close BizFileOnline tab: {e}")
                    
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
                                # If no specific element found, try to click on body and type
                                logger.info("No specific note box found, clicking on body")
                                print("No specific note box found, clicking on body")
                                body = self.driver.find_element(By.TAG_NAME, "body")
                                body.click()
                                time.sleep(0.5)
                                
                                # Type the download link directly to body
                                body.send_keys(download_link)
                                logger.info(f"Typed download link to body: {download_link}")
                                print(f"Typed download link to body: {download_link}")
                            else:
                                # Click on the found note box
                                note_box.click()
                                logger.info("Left-clicked on note text box")
                                print("Left-clicked on note text box")
                                time.sleep(0.5)  # Brief wait after clicking
                                
                                # Wait 3 seconds before pasting
                                time.sleep(3)
                                
                                # Type the download link directly into the note box
                                note_box.send_keys(download_link)
                                logger.info(f"Typed download link directly: {download_link}")
                                print(f"Typed download link directly: {download_link}")
                                
                        except Exception as e:
                            logger.error(f"Failed to click note box or type: {e}")
                            print(f"Failed to click note box or type: {e}")
                            
                            # Final fallback: try ActionChains with the download link variable
                            try:
                                actions = ActionChains(self.driver)
                                actions.send_keys(download_link).perform()
                                logger.info(f"Typed using ActionChains fallback: {download_link}")
                                print(f"Typed using ActionChains fallback: {download_link}")
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
            # Wait 3 seconds to allow the search results to fully render
            logger.info("Waiting 3 seconds for BizFileOnline search results to fully render...")
            time.sleep(3)
            # Scroll to the bottom of the page to ensure all content is visible
            logger.info("Scrolling to the bottom of the BizFileOnline page to ensure all content is visible...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
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
            
    def run(self, search_text):
        """
        Main method to run the complete automation process with continuous processing.
        
        This method orchestrates the entire automation process:
        1. Browser setup (visible Chrome)
        2. Website navigation
        3. Login (if required)
        4. Navigation to target page
        5. Continuous processing of Payee Names from the table
        
        Args:
            search_text (str): The text to search for in the initial search field
        """
        try:
            logger.info("=== STARTING CONTINUOUS SELENIUM AUTOMATION ===")
            logger.info(f"Initial search text provided: '{search_text}'")
            logger.info(f"Maximum companies to process: {self.max_companies}")
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
            
            # Step 6: Perform initial search to populate the table
            self.find_and_fill_file_search_field(search_text)
            logger.info("=== INITIAL SEARCH COMPLETED - TABLE SHOULD BE POPULATED ===")
            
            # Step 7: Continuous processing loop
            logger.info("=== STARTING CONTINUOUS PROCESSING LOOP ===")
            
            while not self.should_stop_processing():
                logger.info(f"=== PROCESSING ITERATION {self.companies_processed + 1} ===")
                logger.info(f"Companies processed so far: {self.companies_processed}")
                logger.info(f"Consecutive failures: {self.consecutive_failures}")
                
                # Find and process the next row
                payee_name = self.find_and_process_next_row()
                
                if payee_name is None:
                    logger.info("No more rows to process - reached end of table")
                    break
                
                # Process the Payee Name through BizFileOnline
                success = self.process_single_payee(payee_name)
                
                if success:
                    logger.info(f"✅ Successfully processed Payee: '{payee_name}'")
                    logger.info(f"Total companies processed: {self.companies_processed}")
                else:
                    logger.error(f"❌ Failed to process Payee: '{payee_name}'")
                    logger.warning(f"Consecutive failures: {self.consecutive_failures}")
                
                # Brief pause between iterations
                time.sleep(2)
            
            # Step 8: Completion
            logger.info("=== CONTINUOUS AUTOMATION COMPLETED ===")
            logger.info(f"✅ Total companies processed: {self.companies_processed}")
            logger.info(f"✅ Final consecutive failures: {self.consecutive_failures}")
            
            if self.consecutive_failures >= 3:
                logger.warning("⚠️ Automation stopped due to 3 consecutive failures")
            elif self.companies_processed >= self.max_companies:
                logger.info(f"✅ Automation completed - reached maximum limit of {self.max_companies} companies")
            else:
                logger.info("✅ Automation completed - reached end of table")
            
            # Keep browser open for a while so user can see the result
            logger.info("Keeping browser open for 30 seconds for manual verification...")
            time.sleep(30)
            
        except Exception as e:
            logger.error(f"❌ CONTINUOUS AUTOMATION FAILED: {e}")
            logger.error("Please check the console logs above for detailed error information")
            raise
        finally:
            # Always clean up
            self.cleanup()

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
        9. If multiple results: loop through rows, find exact match, else fall back to newest Filing Date
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import time
        logger.info("Navigating to BizFileOnline: https://bizfileonline.sos.ca.gov/search/business")
        # REMOVED: Open BizFileOnline in a new tab and switch to it
        # The tab is now opened and switched in perform_custom_automation only
        wait = WebDriverWait(self.driver, 15)
        try:
            # Wait for the business search input field to be present
            logger.info("Waiting for the business search input field to be present (//*[@id='root']//input)...")
            search_input = wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='root']//input"))
            )
            logger.info("✅ Business search input field is present and ready.")
            # Once present, type the Payee name (example: "100 BILLABLE DAYS LLC")
            search_input.clear()
            search_input.send_keys(payee_name)
            logger.info(f"✅ Typed Payee name into search: '{payee_name}'")
            # Immediately after typing, send the Enter/Return key to the input field to trigger the search
            search_input.send_keys(Keys.RETURN)
            logger.info("✅ Sent Enter/Return key to trigger the search.")
            # Wait exactly 4 seconds after pressing Enter for results to load
            logger.info("Waiting exactly 4 seconds for search results to load...")
            time.sleep(4)
            # Scroll down to bring results into view
            logger.info("Scrolling down to bring results into view...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # After scrolling, locate all result rows using XPath //table//tr[td]
            logger.info("Locating all result rows using XPath //table//tr[td]...")
            rows = self.driver.find_elements(By.XPATH, "//table//tr[td]")
            num_rows = len(rows)
            logger.info(f"Found {num_rows} result row(s).")
            print(f"Found {num_rows} result row(s).")
            if num_rows == 0:
                logger.warning("No result rows found.")
                print("No result rows found.")
                return
            # If there is exactly one result
            if num_rows == 1:
                logger.info("Exactly one result found. Extracting entity name...")
                print("Exactly one result found. Extracting entity name...")
                try:
                    # Extract the visible entity name from that row (text from the blue button, link, or name area)
                    row = rows[0]
                    # Try to find clickable elements in the row (button, a, or other clickable elements)
                    clickable_elements = row.find_elements(By.XPATH, ".//button | .//a | .//*[contains(@class, 'clickable')] | .//*[contains(@class, 'blue')]")
                    if clickable_elements:
                        entity_name = clickable_elements[0].text.strip()
                        logger.info(f"Extracted entity name: '{entity_name}'")
                        print(f"Extracted entity name: '{entity_name}'")
                        # If the entity name is an exact match to the Payee name (case-insensitive, ignoring extra spaces)
                        if self._normalize_text(entity_name) == self._normalize_text(payee_name):
                            logger.info(f"✅ Exact match found. Clicking the blue button/row immediately.")
                            print(f"✅ Exact match found. Clicking the blue button/row immediately.")
                            clickable_elements[0].click()
                            return
                        else:
                            logger.info("No exact match found in single result. Clicking anyway.")
                            print("No exact match found in single result. Clicking anyway.")
                            clickable_elements[0].click()
                            return
                    else:
                        logger.warning("No clickable elements found in the single result row.")
                        print("No clickable elements found in the single result row.")
                        return
                except Exception as e:
                    logger.error(f"Error processing single result: {e}")
                    print(f"Error processing single result: {e}")
                    return
            # If there are multiple results
            else:
                logger.info("Multiple results found. Looping through each result row...")
                print("Multiple results found. Looping through each result row...")
                found_exact = False
                for i, row in enumerate(rows):
                    try:
                        # Extract the visible entity name
                        clickable_elements = row.find_elements(By.XPATH, ".//button | .//a | .//*[contains(@class, 'clickable')] | .//*[contains(@class, 'blue')]")
                        if clickable_elements:
                            entity_name = clickable_elements[0].text.strip()
                            logger.info(f"Row {i+1} entity name: '{entity_name}'")
                            print(f"Row {i+1} entity name: '{entity_name}'")
                            # If an entity name is an exact match (case-insensitive, ignoring extra spaces) to the Payee name
                            if self._normalize_text(entity_name) == self._normalize_text(payee_name):
                                logger.info(f"✅ Exact match found in row {i+1}. Clicking the blue button/row and exiting loop.")
                                print(f"✅ Exact match found in row {i+1}. Clicking the blue button/row and exiting loop.")
                                clickable_elements[0].click()
                                found_exact = True
                                break
                    except Exception as row_e:
                        logger.warning(f"Error processing row {i+1}: {row_e}")
                        continue
                # If no exact match is found, fall back to existing logic that clicks the row with the newest Filing Date
                if not found_exact:
                    logger.info("No exact match found. Falling back to newest Filing Date logic.")
                    print("No exact match found. Falling back to newest Filing Date logic.")
                    self.find_and_click_most_recent_filing_bizfile_result()
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
        Check if processing should stop based on stopping conditions.
        Returns True if processing should stop, False otherwise.
        """
        if self.consecutive_failures >= 3:
            logger.warning(f"❌ Stopping: {self.consecutive_failures} consecutive failures")
            return True
        
        if self.companies_processed >= self.max_companies:
            logger.info(f"✅ Stopping: Reached maximum companies limit ({self.max_companies})")
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
            
            # Process the search results
            self.find_and_click_exact_or_newest_entity(payee_name, property_tab=property_tab)
            
            logger.info(f"✅ Successfully processed Payee: '{payee_name}'")
            self.reset_failure_count()
            return True
            
        except Exception as e:
            logger.error(f"❌ ERROR: Failed to process Payee '{payee_name}': {e}")
            self.consecutive_failures += 1
            return False 