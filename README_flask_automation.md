# Flask Selenium Automation Web Application

A Flask web application that provides a web interface to trigger Selenium browser automation processes.

## 🚀 Features

- **Web Interface**: Simple, modern web UI with a "Start Automation" button
- **Public Access**: Server binds to `0.0.0.0` for network/internet access
- **Background Processing**: Selenium runs in background threads while Flask stays responsive
- **Real-time Status**: Live status updates via AJAX polling
- **Visible Browser**: Chrome browser runs in visible mode (not headless)
- **Error Handling**: Comprehensive error handling and status reporting
- **Easy Extension**: Well-structured code for adding more automation steps

## 📁 Project Structure

```
├── app.py                 # Main Flask application
├── automation.py          # Selenium automation logic
├── templates/
│   └── index.html        # Web interface template
├── requirements_flask.txt # Python dependencies
└── README_flask_automation.md
```

## 🛠️ Installation

1. **Install Python dependencies**:

   ```bash
   pip install -r requirements_flask.txt
   ```

2. **Ensure Chrome browser is installed** on the server/machine

3. **ChromeDriver will be automatically managed** by webdriver-manager

## 🚀 Usage

### Starting the Server

```bash
python app.py
```

The server will start on:

- **Host**: `0.0.0.0` (accessible from any network interface)
- **Port**: `5000`
- **Local Access**: `http://localhost:5000`
- **Network Access**: `http://[your-ip-address]:5000`

### Using the Web Interface

1. **Open your browser** and navigate to the server URL
2. **Click "Start Automation"** to begin the Selenium process
3. **Watch the status updates** in real-time
4. **Monitor the Chrome browser** that opens on the server
5. **Use "Reset Status"** to clear the status and run again

## 🔧 Configuration

### Modifying the Target Website

Edit `automation.py` to change the target website and credentials:

```python
# In automation.py __init__ method
self.website_url = "https://your-website.com"
self.username = "your_username"
self.password = "your_password"
```

### Changing Server Settings

Edit `app.py` to modify server configuration:

```python
# In app.py main section
HOST = '0.0.0.0'  # Change for different binding
PORT = 5000       # Change for different port
```

### Adding Custom Automation Steps

Edit the `perform_custom_automation()` method in `automation.py`:

```python
def perform_custom_automation(self):
    logger.info("=== PERFORMING CUSTOM AUTOMATION STEPS ===")

    # Add your custom steps here
    logger.info("Performing custom action...")
    self.driver.find_element(By.CSS_SELECTOR, ".some-button").click()
    logger.info("Custom action completed")
```

## 🌐 Network Access

### Local Network Access

- Other devices on the same network can access: `http://[server-ip]:5000`
- Find your IP address with: `ipconfig` (Windows) or `ifconfig` (Linux/Mac)

### Internet Access (Production)

For internet access, you'll need:

1. **Public IP address** or domain name
2. **Port forwarding** on your router (port 5000)
3. **Firewall configuration** to allow incoming connections
4. **Production WSGI server** (Gunicorn, uWSGI) instead of Flask development server

### Security Note

⚠️ **This version has no authentication** - anyone with access can trigger automation. Add authentication for production use.

## 📊 API Endpoints

- `GET /` - Main web interface
- `POST /start_automation` - Start automation process
- `GET /status` - Get current automation status
- `POST /reset` - Reset automation status

## 🔍 Troubleshooting

### Common Issues

1. **ChromeDriver not found**:

   - The script automatically downloads ChromeDriver
   - Ensure Chrome browser is installed

2. **Port already in use**:

   - Change the PORT in `app.py`
   - Or kill the process using port 5000

3. **Elements not found**:

   - Check the selectors in `automation.py`
   - Update selectors if website structure changes

4. **Network access issues**:
   - Check firewall settings
   - Verify port forwarding (if needed)
   - Ensure server IP is correct

### Debug Mode

The Flask app runs in debug mode by default. For production, change:

```python
app.run(host=HOST, port=PORT, debug=False, threaded=True)
```

## 🔄 Extending the Automation

### Adding New Steps

1. **Add new methods** to the `SeleniumAutomation` class
2. **Call them** in the `run()` method
3. **Add logging** for status updates

Example:

```python
def navigate_to_new_section(self):
    logger.info("=== NAVIGATING TO NEW SECTION ===")
    # Your automation logic here
    logger.info("Navigation completed")

# In run() method:
self.navigate_to_new_section()
```

### Modifying the Web Interface

Edit `templates/index.html` to:

- Add new buttons
- Display additional status information
- Change the styling

## 📝 Logging

The application provides comprehensive logging:

- **Console output** for real-time monitoring
- **Status updates** in the web interface
- **Error reporting** with detailed messages

## 🚀 Production Deployment

For production deployment:

1. **Use a production WSGI server**:

   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Add authentication** to the web interface

3. **Use environment variables** for sensitive configuration

4. **Set up proper logging** to files

5. **Configure reverse proxy** (nginx) for better performance

## 📄 License

This project is provided as-is for educational and automation purposes.
