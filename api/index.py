import os
import sys
import traceback

try:
    # Add the backend directory to Python path
    backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
    sys.path.insert(0, backend_path)
    
    # Import the Flask app
    from app.app import app
    
    print("Successfully imported Flask app")
    
except Exception as e:
    print(f"Error importing Flask app: {e}")
    print(f"Traceback: {traceback.format_exc()}")
    
    # Create a minimal error app
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/<path:path>')
    def error_handler(path):
        return jsonify({
            'error': 'Failed to load application',
            'details': str(e),
            'path': path
        }), 500

# For Vercel serverless deployment
if __name__ == '__main__':
    app.run()
