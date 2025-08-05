#!/bin/bash

# Digital Ocean Setup Script for Selenium Automation
# Run this on your Digital Ocean droplet

echo "Setting up Digital Ocean environment for Selenium automation..."

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update
sudo apt-get install -y google-chrome-stable

# Install ChromeDriver
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | awk -F'.' '{print $1}')
echo "Chrome version: $CHROME_VERSION"

# Download matching ChromeDriver
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION"
CHROMEDRIVER_VERSION=$(cat /tmp/chromedriver.zip)
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"

# Extract and install ChromeDriver
sudo unzip /tmp/chromedriver.zip -d /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Install Python dependencies
sudo apt-get install -y python3-pip python3-venv

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install flask selenium

# Install additional system dependencies
sudo apt-get install -y xvfb

echo "Setup complete! You can now run your Flask application."
echo "To start the application:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run: python app.py" 