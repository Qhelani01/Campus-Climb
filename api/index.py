from flask import Flask, jsonify

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

@app.route('/api/opportunities', methods=['GET'])
def opportunities():
    return jsonify([
        {
            'id': 1,
            'title': 'Test Opportunity',
            'company': 'Test Company',
            'location': 'Test Location',
            'type': 'internship',
            'category': 'tech'
        }
    ])

@app.route('/api/auth/login', methods=['POST'])
def login():
    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': 1,
            'email': 'test@wvstateu.edu',
            'first_name': 'Test',
            'last_name': 'User'
        }
    })

if __name__ == '__main__':
    app.run()
