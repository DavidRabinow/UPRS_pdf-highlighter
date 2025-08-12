#!/usr/bin/env python3
"""
Startup Script for Azure Form Filler
Checks configuration and starts the service
"""

import os
import sys
from pathlib import Path

def check_environment():
    """Check if environment is properly configured"""
    from dotenv import load_dotenv
    load_dotenv()
    
    azure_endpoint = os.getenv('AZURE_DI_ENDPOINT')
    azure_key = os.getenv('AZURE_DI_KEY')
    
    if not azure_endpoint or azure_endpoint == 'https://YOUR-RESOURCE-NAME.cognitiveservices.azure.com/':
        print("❌ Azure endpoint not configured!")
        print("Please set AZURE_DI_ENDPOINT in your .env file")
        return False
    
    if not azure_key or azure_key == 'YOUR-AZURE-KEY':
        print("❌ Azure key not configured!")
        print("Please set AZURE_DI_KEY in your .env file")
        return False
    
    print("✅ Azure credentials configured")
    return True

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import flask
        import azure.ai.documentintelligence
        import pypdf
        import reportlab
        from PIL import Image
        print("✅ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def main():
    """Main startup function"""
    print("🚀 Starting Azure Form Filler Service")
    print("=" * 40)
    
    # Check if .env file exists
    if not Path('.env').exists():
        print("❌ .env file not found!")
        print("Please copy env.sample to .env and configure your Azure credentials")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Get configuration
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"✅ Starting service on port {port}")
    if debug:
        print("⚠️  Debug mode enabled")
    
    # Import and run the app
    try:
        from app import app
        app.run(host='0.0.0.0', port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n👋 Service stopped by user")
    except Exception as e:
        print(f"❌ Failed to start service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
