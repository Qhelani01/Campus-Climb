#!/usr/bin/env python3
"""Simple script to run fetch and generate logs"""
import sys
import os

# Add api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))
os.chdir(os.path.join(os.path.dirname(__file__), 'api'))

from index import app
from scheduler import fetch_all_opportunities

with app.app_context():
    print("Starting fetch...")
    try:
        results = fetch_all_opportunities()
        print(f"Fetch completed. Results: {results}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
