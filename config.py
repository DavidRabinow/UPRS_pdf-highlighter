# Configuration for UPRS Website (rears.retainedequity.com)
# Website: https://rears.retainedequity.com/#/

WEBSITE_CONFIG = {
    # Login page details
    'login_url': 'https://rears.retainedequity.com/#/',
    'username_selector': '#usern',  # Actual username field ID from debug output
    'password_selector': '#pass',  # Actual password field ID from debug output
    'login_button_selector': '.loginBtn',  # Actual login button class from debug output
    
    # Your credentials
    'username': 'aaron',
    'password': 'Welcome1',
    
    # Success indicator (element that appears after successful login)
    # Based on the website structure, look for navigation elements
    'success_indicator': '.nav',  # or '.navbar' or any navigation element
    
    # Next page to navigate to after login
    'next_url': 'https://rears.retainedequity.com/#/'
}

# Browser Configuration
BROWSER_CONFIG = {
    'headless': False,  # Keep browser visible
    'window_size': '1200,800',
    'timeout': 15,  # Increased timeout for this site
    'implicit_wait': 3
}

# Task Configuration for UPRS
TASK_CONFIG = {
    'tasks': [
        {
            'name': 'Navigate to Home',
            'url': 'https://rears.retainedequity.com/#/',
            'action': 'navigate'
        },
        {
            'name': 'Search Properties',
            'selector': 'a[href*="search"], .search-link, #search',
            'action': 'click'
        },
        {
            'name': 'View Client Detail',
            'selector': 'a[href*="client"], .client-link, #client',
            'action': 'click'
        }
    ]
} 