#!/usr/bin/env python3
"""
Campus Climb - WVSU Opportunities Platform
Startup script for the Flask application
"""
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.app import app

if __name__ == '__main__':
    print("🚀 Starting Campus Climb - WVSU Opportunities Platform")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API endpoint: http://localhost:8000/api/opportunities")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    app.run(debug=True, host='0.0.0.0', port=8000)
