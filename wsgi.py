#!/usr/bin/env python3
"""
WSGI entry point for Render deployment
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.app import app

if __name__ == "__main__":
    app.run()
