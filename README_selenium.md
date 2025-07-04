# Selenium Web Automation Script

This Python script automates browser tasks across multiple websites using Selenium WebDriver with a visible browser window.

## Features

- ✅ Visible browser window (not headless)
- ✅ Automated login functionality
- ✅ Extensible task structure
- ✅ Comprehensive logging
- ✅ Error handling and timeouts
- ✅ Screenshot capabilities
- ✅ User interaction pauses
- ✅ Clean browser setup and teardown

## Prerequisites

1. **Python 3.7+** installed on your system
2. **Chrome browser** installed
3. **ChromeDriver** (automatically managed by webdriver-manager)

## Installation

1. Install the required Python packages:

```bash
pip install -r requirements.txt
```

2. The script will automatically download and manage ChromeDriver for you.

## Configuration

Before running the script, you need to update the `CONFIG` dictionary in the `main()` function with your actual website details:

```python
CONFIG = {
    'login_url': 'https://example.com/login',  # Your login page URL
    'username_selector': '#username',  # CSS selector for username field
    'password_selector': '#password',  # CSS selector for password field
    'login_button_selector': '#login-btn',  # CSS selector for login button
    'username': 'your_username',  # Your username
    'password': 'your_password',  # Your password
    'success_indicator': '.dashboard',  # Element that indicates successful login
    'next_url': 'https://example.com/dashboard'  # URL to navigate to after login
}
```

## Usage

### Basic Usage

Run the script:

```bash
python selenium_automation.py
```

### Customizing the Script

The script is structured to be easily extensible. Here's how to add your own tasks:

#### 1. Add Tasks After Login

In the `main()` function, after the login success check, add your custom tasks:

```python
if login_success:
    # Navigate to next page
    automation.navigate_to(CONFIG['next_url'])

    # Your custom tasks here:

    # Example: Click a button
    automation.find_and_click('.some-button', By.CSS_SELECTOR)

    # Example: Fill a form
    automation.find_and_input('#form-field', 'Some text', By.CSS_SELECTOR)

    # Example: Wait for user input
    automation.wait_for_user_input("Check the page and press Enter...")

    # Example: Take a screenshot
    automation.take_screenshot("task_completed.png")
```

#### 2. Create Custom Task Functions

For complex tasks, create custom functions:

```python
def my_custom_task(automation):
    """Custom task function"""
    automation.navigate_to("https://example.com/some-page")
    automation.find_and_click("#some-button")
    automation.wait_for_element(".result")
    return True

# In main():
if login_success:
    automation.perform_task("My Custom Task", lambda: my_custom_task(automation))
```

## Available Methods

### Navigation

- `navigate_to(url)` - Navigate to a URL
- `wait_for_element(selector, by, timeout)` - Wait for an element to appear

### Interaction

- `find_and_click(selector, by, timeout)` - Find and click an element
- `find_and_input(selector, text, by, timeout)` - Find and enter text in an input field

### Login

- `login(url, username_selector, password_selector, login_button_selector, username, password, success_indicator)` - Complete login process

### Utilities

- `take_screenshot(filename)` - Take a screenshot
- `wait_for_user_input(message)` - Pause for user input
- `perform_task(task_name, task_function)` - Execute a custom task

## Selector Types

The script supports multiple ways to locate elements:

- `By.ID` - Find by element ID
- `By.NAME` - Find by element name
- `By.CSS_SELECTOR` - Find by CSS selector (default)
- `By.XPATH` - Find by XPath
- `By.CLASS_NAME` - Find by class name
- `By.TAG_NAME` - Find by tag name

## Examples

### Example 1: Simple Login and Navigation

```python
# Login to a website
login_success = automation.login(
    url="https://example.com/login",
    username_selector="#email",
    password_selector="#password",
    login_button_selector="button[type='submit']",
    username="myuser@example.com",
    password="mypassword",
    success_indicator=".user-profile"
)

if login_success:
    # Navigate to dashboard
    automation.navigate_to("https://example.com/dashboard")
```

### Example 2: Form Filling

```python
# Fill out a contact form
automation.find_and_input("#name", "John Doe", By.ID)
automation.find_and_input("#email", "john@example.com", By.ID)
automation.find_and_input("#message", "Hello world!", By.ID)
automation.find_and_click("#submit", By.ID)
```

### Example 3: Multi-step Process

```python
# Step 1: Navigate to page
automation.navigate_to("https://example.com/process")

# Step 2: Fill form
automation.find_and_input("#field1", "Value 1")
automation.find_and_input("#field2", "Value 2")

# Step 3: Submit and wait
automation.find_and_click("#submit")
automation.wait_for_element(".success-message")

# Step 4: Take screenshot
automation.take_screenshot("process_completed.png")
```

## Logging

The script provides comprehensive logging:

- Console output for real-time progress tracking
- Log file (`automation.log`) for detailed history
- Different log levels (INFO, ERROR, etc.)

## Error Handling

The script includes robust error handling:

- Timeout exceptions for elements not found
- Graceful handling of login failures
- Automatic browser cleanup on errors
- Detailed error messages and logging

## Tips

1. **Test selectors first**: Use browser developer tools to verify your selectors work
2. **Add delays**: Use `time.sleep()` or `wait_for_user_input()` for complex pages
3. **Take screenshots**: Use `take_screenshot()` to debug issues
4. **Check logs**: Review `automation.log` for detailed execution history
5. **Start simple**: Begin with basic navigation before adding complex interactions

## Troubleshooting

### Common Issues

1. **ChromeDriver not found**: The script automatically downloads ChromeDriver
2. **Elements not found**: Check your selectors using browser developer tools
3. **Login failures**: Verify your credentials and success indicator selector
4. **Timeout errors**: Increase timeout values or check page load times

### Debug Mode

To run with more verbose logging:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Security Notes

- Never commit passwords to version control
- Consider using environment variables for sensitive data
- Use the script responsibly and in accordance with website terms of service

## License

This script is provided as-is for educational and automation purposes.
