from flask import Flask, jsonify
import os

# Create a simple Flask app for testing
app = Flask(__name__)

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({
        'message': 'API is working!',
        'status': 'success'
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'message': 'Basic API is running'
    })

@app.route('/<path:path>')
def catch_all(path):
    return jsonify({
        'error': 'Endpoint not found',
        'path': path
    }), 404

if __name__ == '__main__':
    app.run()
