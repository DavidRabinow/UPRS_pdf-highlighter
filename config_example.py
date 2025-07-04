# Example Configuration File
# Copy this file to config.py and update with your actual website details

# Website Configuration
WEBSITE_CONFIG = {
    # Login page details
    'login_url': 'https://example.com/login',
    'username_selector': '#username',  # or 'input[name="username"]' or '#email'
    'password_selector': '#password',  # or 'input[name="password"]'
    'login_button_selector': '#login-btn',  # or 'button[type="submit"]' or '.login-button'
    
    # Your credentials
    'username': 'your_username_here',
    'password': 'your_password_here',
    
    # Success indicator (element that appears after successful login)
    'success_indicator': '.dashboard',  # or '#user-profile' or '.welcome-message'
    
    # Next page to navigate to after login
    'next_url': 'https://example.com/dashboard'
}

# Task Configuration
TASK_CONFIG = {
    # Add your custom tasks here
    'tasks': [
        {
            'name': 'Navigate to Dashboard',
            'url': 'https://example.com/dashboard',
            'action': 'navigate'
        },
        {
            'name': 'Click Settings Button',
            'selector': '.settings-btn',
            'action': 'click'
        },
        {
            'name': 'Fill Contact Form',
            'action': 'form_fill',
            'fields': [
                {'selector': '#name', 'value': 'John Doe'},
                {'selector': '#email', 'value': 'john@example.com'},
                {'selector': '#message', 'value': 'Hello world!'}
            ],
            'submit_selector': '#submit'
        }
    ]
}

# Browser Configuration
BROWSER_CONFIG = {
    'headless': False,  # Set to True for headless mode
    'window_size': '1200,800',
    'timeout': 10,  # Default timeout in seconds
    'implicit_wait': 2  # Implicit wait time in seconds
}

# Example configurations for popular websites:

# GitHub Example
GITHUB_CONFIG = {
    'login_url': 'https://github.com/login',
    'username_selector': '#login_field',
    'password_selector': '#password',
    'login_button_selector': 'input[name="commit"]',
    'username': 'your_github_username',
    'password': 'your_github_password',
    'success_indicator': '.avatar',
    'next_url': 'https://github.com'
}

# LinkedIn Example
LINKEDIN_CONFIG = {
    'login_url': 'https://www.linkedin.com/login',
    'username_selector': '#username',
    'password_selector': '#password',
    'login_button_selector': 'button[type="submit"]',
    'username': 'your_linkedin_email',
    'password': 'your_linkedin_password',
    'success_indicator': '.global-nav',
    'next_url': 'https://www.linkedin.com/feed/'
}

# Twitter/X Example
TWITTER_CONFIG = {
    'login_url': 'https://twitter.com/i/flow/login',
    'username_selector': 'input[autocomplete="username"]',
    'password_selector': 'input[name="password"]',
    'login_button_selector': 'div[data-testid="LoginForm_Login_Button"]',
    'username': 'your_twitter_username',
    'password': 'your_twitter_password',
    'success_indicator': '[data-testid="SideNav_AccountSwitcher_Button"]',
    'next_url': 'https://twitter.com/home'
}

# How to use:
# 1. Copy this file to config.py
# 2. Update the WEBSITE_CONFIG with your actual website details
# 3. In selenium_automation.py, replace the CONFIG dictionary with:
#    from config import WEBSITE_CONFIG as CONFIG 