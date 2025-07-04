#!/usr/bin/env python3
"""
Debug script to analyze page structure and find the correct selectors
for the search field under "File".
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def debug_page_structure():
    """
    Debug the page structure to understand how to locate the search field.
    """
    print("=== DEBUGGING PAGE STRUCTURE ===")
    print("This will analyze the page to find the search field under 'File'")
    print()
    
    # Set up browser
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1200,800")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate and login
        logger.info("Navigating to website...")
        driver.get("https://rears.retainedequity.com/#/")
        time.sleep(3)
        
        # Login
        logger.info("Logging in...")
        username_field = driver.find_element(By.CSS_SELECTOR, "#usern")
        username_field.send_keys("aaron")
        
        password_field = driver.find_element(By.CSS_SELECTOR, "#pass")
        password_field.send_keys("Welcome1")
        
        login_button = driver.find_element(By.CSS_SELECTOR, ".loginBtn")
        login_button.click()
        time.sleep(5)
        
        # Navigate to Search Properties
        logger.info("Navigating to Search Properties...")
        search_properties = driver.find_element(By.XPATH, "//a[contains(text(), 'Search Properties')]")
        search_properties.click()
        time.sleep(2)
        
        # Navigate to Process Imported Files
        logger.info("Navigating to Process Imported Files...")
        process_files = driver.find_element(By.XPATH, "//a[contains(text(), 'Process Imported Files')]")
        process_files.click()
        time.sleep(5)
        
        # Now analyze the page structure
        logger.info("=== ANALYZING PAGE STRUCTURE ===")
        
        # Find all "File" elements
        file_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'File')]")
        logger.info(f"Found {len(file_elements)} elements containing 'File' text")
        
        for i, file_element in enumerate(file_elements):
            try:
                tag_name = file_element.tag_name
                text = file_element.text.strip()
                class_attr = file_element.get_attribute('class') or ''
                id_attr = file_element.get_attribute('id') or ''
                
                logger.info(f"File element {i+1}: <{tag_name}> '{text}' class='{class_attr}' id='{id_attr}'")
                
                # Look for input fields near this file element
                try:
                    # Check following siblings
                    following_inputs = file_element.find_elements(By.XPATH, "following-sibling::input")
                    logger.info(f"  - Following sibling inputs: {len(following_inputs)}")
                    
                    # Check parent's children
                    parent = file_element.find_element(By.XPATH, "./..")
                    parent_inputs = parent.find_elements(By.TAG_NAME, "input")
                    logger.info(f"  - Parent's input children: {len(parent_inputs)}")
                    
                    # Check descendants
                    descendant_inputs = file_element.find_elements(By.XPATH, ".//input")
                    logger.info(f"  - Descendant inputs: {len(descendant_inputs)}")
                    
                except Exception as e:
                    logger.warning(f"  - Error analyzing file element {i+1}: {e}")
                    
            except Exception as e:
                logger.error(f"Error with file element {i+1}: {e}")
        
        # Find all input fields with "select" in placeholder
        select_inputs = driver.find_elements(By.XPATH, "//input[contains(@placeholder, 'select')]")
        logger.info(f"\nFound {len(select_inputs)} input fields with 'select' in placeholder")
        
        for i, input_field in enumerate(select_inputs):
            try:
                placeholder = input_field.get_attribute('placeholder') or ''
                visible = input_field.is_displayed()
                enabled = input_field.is_enabled()
                class_attr = input_field.get_attribute('class') or ''
                id_attr = input_field.get_attribute('id') or ''
                name_attr = input_field.get_attribute('name') or ''
                
                logger.info(f"Select input {i+1}: placeholder='{placeholder}' visible={visible} enabled={enabled}")
                logger.info(f"  - class='{class_attr}' id='{id_attr}' name='{name_attr}'")
                
                # Check if this input is near a "File" element
                try:
                    # Look for "File" text in parent elements
                    parent_with_file = input_field.find_element(By.XPATH, "ancestor::*[contains(text(), 'File')]")
                    logger.info(f"  - ✅ Found 'File' text in ancestor: {parent_with_file.tag_name}")
                except NoSuchElementException:
                    logger.info(f"  - ❌ No 'File' text found in ancestors")
                
            except Exception as e:
                logger.error(f"Error analyzing select input {i+1}: {e}")
        
        # Look for any hidden or collapsed sections
        hidden_elements = driver.find_elements(By.XPATH, "//*[contains(@style, 'display: none') or contains(@class, 'hidden') or contains(@class, 'collapsed')]")
        logger.info(f"\nFound {len(hidden_elements)} potentially hidden elements")
        
        # Look for expandable sections
        expandable_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'expand') or contains(@class, 'toggle') or contains(@class, 'accordion')]")
        logger.info(f"Found {len(expandable_elements)} potentially expandable elements")
        
        # Take a screenshot for manual inspection
        logger.info("Taking screenshot for manual inspection...")
        driver.save_screenshot("debug_screenshot.png")
        logger.info("Screenshot saved as 'debug_screenshot.png'")
        
        # Keep browser open for manual inspection
        logger.info("Keeping browser open for 60 seconds for manual inspection...")
        time.sleep(60)
        
    except Exception as e:
        logger.error(f"Debug failed: {e}")
        raise
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_page_structure() 