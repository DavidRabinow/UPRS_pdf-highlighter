#!/usr/bin/env python3
"""
Selenium Web Automation Script
Automates browser tasks across multiple websites with visible browser window.
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os

# Import configuration
try:
    from config import WEBSITE_CONFIG as CONFIG, BROWSER_CONFIG
except ImportError:
    # Fallback configuration if config.py doesn't exist
    CONFIG = {
        'login_url': 'https://rears.retainedequity.com/#/',
        'username_selector': '#username',
        'password_selector': '#password',
        'login_button_selector': 'button[type="submit"]',
        'username': 'aaron',
        'password': 'Welcome1',
        'success_indicator': '.nav',
        'next_url': 'https://rears.retainedequity.com/#/'
    }
    BROWSER_CONFIG = {
        'headless': False,
        'window_size': '1200,800',
        'timeout': 15,
        'implicit_wait': 3
    }

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WebAutomation:
    def __init__(self, headless=False):
        """
        Initialize the WebAutomation class.
        
        Args:
            headless (bool): If True, run browser in headless mode. Default is False for visible browser.
        """
        self.driver = None
        self.wait = None
        self.headless = headless
        self.setup_driver()
    
    def setup_driver(self):
        """Set up Chrome driver with appropriate options."""
        try:
            chrome_options = Options()
            
            # Keep browser visible (not headless) unless specified otherwise
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # Additional options for better automation
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Set window size for better visibility
            chrome_options.add_argument(f"--window-size={BROWSER_CONFIG['window_size']}")
            
            # Initialize the driver
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set up explicit wait
            self.wait = WebDriverWait(self.driver, BROWSER_CONFIG['timeout'])
            
            # Set implicit wait
            self.driver.implicitly_wait(BROWSER_CONFIG['implicit_wait'])
            
            logger.info("Chrome browser initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            raise
    
    def navigate_to(self, url):
        """
        Navigate to a specific URL.
        
        Args:
            url (str): The URL to navigate to
        """
        try:
            logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            time.sleep(2)  # Brief pause to let page load
            logger.info(f"Successfully navigated to: {url}")
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            raise
    
    def find_and_click(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """
        Find an element and click it.
        
        Args:
            selector (str): The selector to find the element
            by: The method to find the element (By.ID, By.NAME, By.CSS_SELECTOR, etc.)
            timeout (int): Timeout in seconds
        """
        try:
            logger.info(f"Looking for element: {selector}")
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, selector))
            )
            element.click()
            logger.info(f"Successfully clicked element: {selector}")
            time.sleep(1)  # Brief pause after click
        except TimeoutException:
            logger.error(f"Element not found or not clickable: {selector}")
            raise
        except Exception as e:
            logger.error(f"Failed to click element {selector}: {e}")
            raise
    
    def find_and_input(self, selector, text, by=By.CSS_SELECTOR, timeout=10):
        """
        Find an input field and enter text.
        
        Args:
            selector (str): The selector to find the input field
            text (str): The text to enter
            by: The method to find the element (By.ID, By.NAME, By.CSS_SELECTOR, etc.)
            timeout (int): Timeout in seconds
        """
        try:
            logger.info(f"Looking for input field: {selector}")
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            element.clear()
            element.send_keys(text)
            logger.info(f"Successfully entered text in: {selector}")
            time.sleep(0.5)  # Brief pause after input
        except TimeoutException:
            logger.error(f"Input field not found: {selector}")
            raise
        except Exception as e:
            logger.error(f"Failed to enter text in {selector}: {e}")
            raise
    
    def wait_for_element(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """
        Wait for an element to be present on the page.
        
        Args:
            selector (str): The selector to find the element
            by: The method to find the element (By.ID, By.NAME, By.CSS_SELECTOR, etc.)
            timeout (int): Timeout in seconds
        
        Returns:
            The found element
        """
        try:
            logger.info(f"Waiting for element: {selector}")
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            logger.info(f"Element found: {selector}")
            return element
        except TimeoutException:
            logger.error(f"Element not found within timeout: {selector}")
            raise
        except Exception as e:
            logger.error(f"Error waiting for element {selector}: {e}")
            raise
    
    def login(self, url, username_selector, password_selector, login_button_selector, 
              username, password, success_indicator=None, by_username=By.CSS_SELECTOR, 
              by_password=By.CSS_SELECTOR, by_login=By.CSS_SELECTOR, by_success=By.CSS_SELECTOR):
        """
        Perform login on a website.
        
        Args:
            url (str): The login page URL
            username_selector (str): Selector for username field
            password_selector (str): Selector for password field
            login_button_selector (str): Selector for login button
            username (str): Username to enter
            password (str): Password to enter
            success_indicator (str): Selector for element that indicates successful login
            by_username: Method to find username field
            by_password: Method to find password field
            by_login: Method to find login button
            by_success: Method to find success indicator
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            logger.info("Starting login process...")
            
            # Navigate to login page
            self.navigate_to(url)
            
            # Wait for page to load completely
            time.sleep(3)
            
            # Debug page elements to help identify login fields
            self.debug_page_elements()
            
            # Try different common selectors for login fields
            username_selectors = [
                username_selector,
                'input[name="username"]',
                'input[name="email"]',
                'input[type="text"]',
                '#email',
                '#user',
                '#login'
            ]
            
            password_selectors = [
                password_selector,
                'input[name="password"]',
                'input[type="password"]',
                '#pass',
                '#pwd'
            ]
            
            login_button_selectors = [
                login_button_selector,
                '.loginBtn',  # Actual UPRS login button class
                'button[type="submit"]',
                'input[type="submit"]',
                '.login-btn',
                '.btn-login',
                '#login-btn',
                '#submit'
            ]
            
            # Try to find and fill username field
            username_found = False
            for selector in username_selectors:
                try:
                    self.find_and_input(selector, username, By.CSS_SELECTOR, timeout=3)
                    username_found = True
                    logger.info(f"Username entered using selector: {selector}")
                    break
                except:
                    continue
            
            if not username_found:
                logger.error("Could not find username field")
                return False
            
            # Try to find and fill password field
            password_found = False
            for selector in password_selectors:
                try:
                    self.find_and_input(selector, password, By.CSS_SELECTOR, timeout=3)
                    password_found = True
                    logger.info(f"Password entered using selector: {selector}")
                    break
                except:
                    continue
            
            if not password_found:
                logger.error("Could not find password field")
                return False
            
            # Try to find and click login button
            login_clicked = False
            for selector in login_button_selectors:
                try:
                    logger.info(f"Attempting to click login button with selector: {selector}")
                    self.find_and_click(selector, By.CSS_SELECTOR, timeout=3)
                    login_clicked = True
                    logger.info(f"Login button successfully clicked using selector: {selector}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to click login button with selector '{selector}': {e}")
                    continue
            
            if not login_clicked:
                logger.error("Could not find or click login button with any selector")
                logger.info("Attempting to find login button by text content...")
                
                # Try to find login button by text content
                try:
                    # Look for buttons with login-related text
                    login_text_selectors = [
                        "//button[contains(text(), 'Login')]",
                        "//button[contains(text(), 'Sign In')]",
                        "//button[contains(text(), 'Log In')]",
                        "//input[@value='Login']",
                        "//input[@value='Sign In']",
                        "//input[@value='Log In']"
                    ]
                    
                    for xpath_selector in login_text_selectors:
                        try:
                            self.find_and_click(xpath_selector, By.XPATH, timeout=3)
                            login_clicked = True
                            logger.info(f"Login button clicked using XPath: {xpath_selector}")
                            break
                        except:
                            continue
                            
                except Exception as e:
                    logger.error(f"Failed to find login button by text: {e}")
                
                if not login_clicked:
                    logger.error("All login button attempts failed")
                    logger.info("Attempting force click as last resort...")
                    
                    # Try force click as last resort
                    if self.force_login_click():
                        login_clicked = True
                        logger.info("Force click login button successful")
                    else:
                        logger.error("All login button attempts including force click failed")
                        return False
            
            # Wait for page to load after login
            time.sleep(5)
            
            # Check if login was successful
            if success_indicator:
                try:
                    self.wait_for_element(success_indicator, by_success, timeout=10)
                    logger.info("Login successful!")
                    return True
                except TimeoutException:
                    logger.error("Login failed - success indicator not found")
                    return False
            else:
                logger.info("Login completed (no success indicator specified)")
                return True
                
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    def perform_task(self, task_name, task_function):
        """
        Execute a custom task function.
        
        Args:
            task_name (str): Name of the task for logging
            task_function (callable): Function to execute
        """
        try:
            logger.info(f"Starting task: {task_name}")
            result = task_function()
            logger.info(f"Completed task: {task_name}")
            return result
        except Exception as e:
            logger.error(f"Task '{task_name}' failed: {e}")
            raise
    
    def wait_for_user_input(self, message="Press Enter to continue..."):
        """
        Wait for user input before continuing.
        
        Args:
            message (str): Message to display to user
        """
        input(message)
    
    def take_screenshot(self, filename=None):
        """
        Take a screenshot of the current page.
        
        Args:
            filename (str): Optional filename for the screenshot
        """
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        try:
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
    
    def debug_page_elements(self):
        """
        Debug method to find and log all potential login elements on the page.
        """
        try:
            logger.info("=== DEBUGGING PAGE ELEMENTS ===")
            
            # Find all input fields
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            logger.info(f"Found {len(inputs)} input elements:")
            for i, inp in enumerate(inputs):
                input_type = inp.get_attribute("type") or "text"
                input_id = inp.get_attribute("id") or "no-id"
                input_name = inp.get_attribute("name") or "no-name"
                input_class = inp.get_attribute("class") or "no-class"
                logger.info(f"  Input {i+1}: type='{input_type}', id='{input_id}', name='{input_name}', class='{input_class}'")
            
            # Find all buttons
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            logger.info(f"Found {len(buttons)} button elements:")
            for i, btn in enumerate(buttons):
                button_text = btn.text or "no-text"
                button_id = btn.get_attribute("id") or "no-id"
                button_class = btn.get_attribute("class") or "no-class"
                button_type = btn.get_attribute("type") or "no-type"
                logger.info(f"  Button {i+1}: text='{button_text}', id='{button_id}', class='{button_class}', type='{button_type}'")
            
            # Find all submit inputs
            submits = self.driver.find_elements(By.CSS_SELECTOR, "input[type='submit']")
            logger.info(f"Found {len(submits)} submit input elements:")
            for i, sub in enumerate(submits):
                submit_value = sub.get_attribute("value") or "no-value"
                submit_id = sub.get_attribute("id") or "no-id"
                submit_class = sub.get_attribute("class") or "no-class"
                logger.info(f"  Submit {i+1}: value='{submit_value}', id='{submit_id}', class='{submit_class}'")
            
            logger.info("=== END DEBUGGING ===")
            
        except Exception as e:
            logger.error(f"Error during page debugging: {e}")
    
    def force_login_click(self):
        """
        Force click login button using JavaScript if normal click fails.
        """
        try:
            logger.info("Attempting to force click login button using JavaScript...")
            
            # Try to find any element that might be a login button
            possible_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                ".login-btn",
                ".btn-login",
                "#login-btn",
                "#submit",
                "button:contains('Login')",
                "button:contains('Sign In')",
                "input[value='Login']",
                "input[value='Sign In']"
            ]
            
            for selector in possible_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed() and element.is_enabled():
                        # Try JavaScript click
                        self.driver.execute_script("arguments[0].click();", element)
                        logger.info(f"Force clicked login button using JavaScript: {selector}")
                        return True
                except:
                    continue
            
            logger.error("Force click login button failed")
            return False
            
        except Exception as e:
            logger.error(f"Error during force login click: {e}")
            return False
    
    def close_browser(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_browser()


def uprs_specific_tasks(automation):
    """
    Perform UPRS-specific tasks after login.
    
    Args:
        automation: WebAutomation instance
    """
    try:
        logger.info("Starting UPRS-specific tasks...")
        
        # Wait for the page to fully load
        time.sleep(3)
        
        # Take a screenshot of the dashboard
        automation.take_screenshot("uprs_dashboard.png")
        
        # Try to navigate to different sections based on the website structure
        sections_to_try = [
            ("Search Properties", "a[href*='search'], .search-link, #search"),
            ("Client Detail", "a[href*='client'], .client-link, #client"),
            ("All Notes", "a[href*='notes'], .notes-link, #notes"),
            ("Marketing", "a[href*='marketing'], .marketing-link, #marketing")
        ]
        
        for section_name, selector in sections_to_try:
            try:
                logger.info(f"Attempting to navigate to: {section_name}")
                automation.find_and_click(selector, By.CSS_SELECTOR, timeout=5)
                time.sleep(2)
                automation.take_screenshot(f"uprs_{section_name.lower().replace(' ', '_')}.png")
                logger.info(f"Successfully navigated to: {section_name}")
                
                # Wait for user to see the page
                automation.wait_for_user_input(f"Currently viewing {section_name}. Press Enter to continue...")
                
            except Exception as e:
                logger.warning(f"Could not navigate to {section_name}: {e}")
                continue
        
        logger.info("UPRS-specific tasks completed")
        
    except Exception as e:
        logger.error(f"UPRS-specific tasks failed: {e}")
        raise


def main():
    """
    Main function to demonstrate the automation script for UPRS website.
    """
    
    try:
        # Initialize the automation
        with WebAutomation(headless=BROWSER_CONFIG['headless']) as automation:
            logger.info("Starting UPRS web automation...")
            
            # Step 1: Perform login
            login_success = automation.login(
                url=CONFIG['login_url'],
                username_selector=CONFIG['username_selector'],
                password_selector=CONFIG['password_selector'],
                login_button_selector=CONFIG['login_button_selector'],
                username=CONFIG['username'],
                password=CONFIG['password'],
                success_indicator=CONFIG['success_indicator']
            )
            
            if login_success:
                logger.info("Login successful! Proceeding with UPRS tasks...")
                
                # Step 2: Navigate to next page/section
                automation.navigate_to(CONFIG['next_url'])
                
                # Step 3: Perform UPRS-specific tasks
                automation.perform_task("UPRS Navigation Tasks", lambda: uprs_specific_tasks(automation))
                
                # Step 4: Wait for user to finish
                automation.wait_for_user_input("All tasks completed. Press Enter to close browser...")
                
                logger.info("UPRS automation completed successfully!")
                
            else:
                logger.error("Login failed. Stopping automation.")
                
    except Exception as e:
        logger.error(f"UPRS automation failed: {e}")
        raise


if __name__ == "__main__":
    main() 