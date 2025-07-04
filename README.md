# Flask + Selenium Automation Project

A web-based automation control panel that uses Selenium to automate browser tasks on the REARS website. The automation includes login, navigation, and search functionality with a user-friendly web interface.

## Features

- **Web Interface**: Flask-based control panel accessible from any network
- **Browser Automation**: Selenium automation with visible Chrome browser
- **Search Functionality**: Enter custom search text via web interface
- **Real-time Status**: Live updates on automation progress
- **Error Handling**: Comprehensive error handling and logging
- **Modular Design**: Easy to extend with additional automation steps

## Project Structure

```
├── app.py                 # Flask web application
├── automation.py          # Selenium automation logic
├── test_automation.py     # Standalone test script
├── templates/
│   └── index.html        # Web interface template
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Installation

1. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Install Chrome WebDriver:**

   - Download ChromeDriver from: https://chromedriver.chromium.org/
   - Ensure it's in your system PATH or in the project directory

3. **Configure credentials** (if needed):
   - Edit `automation.py` to update website URL, username, and password

## Usage

### Option 1: Web Interface (Recommended)

1. **Start the Flask server:**

   ```bash
   python app.py
   ```

2. **Access the web interface:**

   - Local: http://localhost:5000
   - Network: http://[your-ip]:5000

3. **Use the automation:**
   - Enter search text in the input field
   - Click "Start Automation"
   - Watch real-time status updates
   - Browser will open and perform automation

### Option 2: Standalone Test

1. **Run the test script:**

   ```bash
   python test_automation.py
   ```

2. **Watch the automation:**
   - Chrome browser will open automatically
   - Follow the console logs for progress
   - Browser stays open for 30 seconds after completion

## Automation Process

The automation performs the following steps:

1. **Browser Setup**: Opens Chrome browser (visible, not headless)
2. **Website Navigation**: Navigates to https://rears.retainedequity.com/#/
3. **Login**: Enters credentials and logs in
4. **Navigation**:
   - Clicks "Search Properties"
   - Selects "Process Imported Files" from dropdown
5. **Search Functionality**:
   - Locates search field under "File" label
   - Enters user-provided search text
   - Clicks green search button
6. **Completion**: Takes screenshot and keeps browser open

## Search Field Handling

The automation is specifically designed to handle the search field that:

- Is positioned under the "File" label
- Displays placeholder text "select..."
- Looks like a dropdown but functions as a text input
- Requires clicking to activate before typing

### Selector Strategies

The automation uses multiple selector strategies to find the search field:

```python
# Direct input field selectors
"input[placeholder='select...']"
"input[placeholder*='select']"

# XPath selectors near "File" text
"//label[contains(text(), 'File')]/following-sibling::input"
"//*[contains(text(), 'File')]/../input"

# Fallback strategies
# Look for input fields near "File" text elements
```

### Green Search Button

The automation also uses multiple strategies to find the green search button:

```python
# Common green button patterns
"button[class*='green']"
"button[class*='search']"
"button[class*='btn-success']"

# XPath selectors
"//button[contains(@class, 'green')]"
"//button[contains(@class, 'search')]"

# Fallback: Look for any button near search field
```

## Configuration

### Website Configuration

Edit `automation.py` to update:

```python
# Website and credentials
self.website_url = "https://rears.retainedequity.com/#/"
self.username = "aaron"
self.password = "Welcome1"

# Element selectors (update if website changes)
self.username_selector = "#usern"
self.password_selector = "#pass"
self.login_button_selector = ".loginBtn"
```

### Flask Configuration

Edit `app.py` to update server settings:

```python
HOST = '0.0.0.0'  # Bind to all interfaces
PORT = 5000       # Port to listen on
```

## Logging and Debugging

### Console Logs

The automation provides detailed console logs:

```
2025-07-03 20:48:32,895 - INFO - Starting Flask server on 0.0.0.0:5000
2025-07-03 20:48:32,895 - INFO - Server will be accessible from any network interface
2025-07-03 20:48:32,895 - INFO - For testing: http://localhost:5000 or http://[your-ip]:5000
```

### Automation Logs

During automation, you'll see logs like:

```
=== STARTING SELENIUM AUTOMATION ===
Search text provided: 'test_file_123'
Setting up Chrome browser...
Chrome browser initialized successfully
Navigating to: https://rears.retainedequity.com/#/
Successfully navigated to website
=== STARTING LOGIN PROCESS ===
Looking for username field...
Username 'aaron' entered successfully
Looking for password field...
Password entered successfully
Looking for login button...
Login button found successfully
Clicking login button...
Login button clicked successfully
Waiting for login to complete...
Login completed successfully!
=== NAVIGATING TO SEARCH PROPERTIES ===
Found 'Search Properties' with selector: a[href*='search']
Clicked 'Search Properties' successfully
Waiting for dropdown menu to appear...
=== NAVIGATING TO PROCESS IMPORTED FILES ===
Found 'Process Imported Files' with selector: //a[contains(text(), 'Process Imported Files')]
Clicked 'Process Imported Files' successfully
Waiting for Process Imported Files page to load...
=== PERFORMING CUSTOM AUTOMATION STEPS ===
=== SEARCHING FOR FILE SEARCH FIELD ===
Looking for search field to enter text: 'test_file_123'
Found search field with selector: input[placeholder='select...']
Successfully entered search text: 'test_file_123'
Search text entry completed
=== SEARCHING FOR GREEN SEARCH BUTTON ===
Found green search button with selector: button[class*='search']
Successfully clicked green search button
Search button click completed
Taking screenshot of current page...
Screenshot saved as 'automation_screenshot.png'
Waiting 10 seconds for manual review...
=== AUTOMATION COMPLETED SUCCESSFULLY ===
Successfully searched for text: 'test_file_123'
You should now be on the Process Imported Files page with search results.
Keeping browser open for 30 seconds...
```

## Error Handling

The automation includes comprehensive error handling:

- **Element Not Found**: Tries multiple selector strategies
- **Timeout Issues**: Waits for elements to load
- **Network Issues**: Retries navigation
- **Browser Issues**: Graceful cleanup and restart

### Common Issues and Solutions

1. **ChromeDriver not found:**

   - Download ChromeDriver and add to PATH
   - Or place in project directory

2. **Elements not found:**

   - Website may have changed
   - Update selectors in `automation.py`

3. **Login fails:**

   - Check credentials in `automation.py`
   - Verify website is accessible

4. **Search field not found:**
   - Check if "File" label exists
   - Verify search field is visible
   - Update selectors if needed

## Extending the Automation

### Adding New Steps

1. **Add new methods** to `SeleniumAutomation` class:

```python
def perform_new_step(self):
    """Add your new automation step here."""
    logger.info("=== PERFORMING NEW STEP ===")
    # Your automation logic here
    logger.info("New step completed")
```

2. **Call the method** in `perform_custom_automation()`:

```python
def perform_custom_automation(self, search_text):
    # Existing steps...
    self.perform_new_step()  # Add your new step
    # More steps...
```

### Adding New Configuration

1. **Add new selectors** to `__init__()` method:

```python
self.new_element_selector = "button.new-element"
```

2. **Use in automation methods**:

```python
new_element = self.driver.find_element(By.CSS_SELECTOR, self.new_element_selector)
```

## Security Notes

- **Credentials**: Store sensitive data in environment variables
- **Network Access**: Server binds to 0.0.0.0 for public access
- **Production**: Use production WSGI server for deployment

## Troubleshooting

### Flask Server Issues

```bash
# Check if port is in use
netstat -an | findstr :5000

# Kill process using port
taskkill /PID <process_id> /F
```

### Selenium Issues

```bash
# Update ChromeDriver
# Download latest version from chromedriver.chromium.org

# Check Chrome version
chrome://version/

# Verify ChromeDriver compatibility
```

### Network Access Issues

```bash
# Check firewall settings
# Allow Python/Flask through firewall

# Test network access
curl http://localhost:5000
```

## Support

For issues or questions:

1. Check the console logs for error messages
2. Verify all dependencies are installed
3. Test with the standalone script first
4. Update selectors if website has changed

## License

This project is provided as-is for educational and automation purposes.
