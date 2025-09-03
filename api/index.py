import os
import sys

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

# Import the Flask app
from app.app import app

# For Vercel serverless deployment
if __name__ == '__main__':
    app.run()
