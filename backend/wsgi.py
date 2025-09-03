#!/usr/bin/env python3
"""
WSGI entry point for Render deployment
"""

from app.app import app

if __name__ == "__main__":
    app.run()
