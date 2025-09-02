#!/usr/bin/env python3
"""
Campus Climb - WVSU Opportunities Platform
API-only Flask backend for managing student opportunities.
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import os
from datetime import datetime
import re
from functools import wraps

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///campus_climb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': self.created_at.isoformat()
        }

class Opportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # internship, job, conference, workshop, competition
    category = db.Column(db.String(50), nullable=False)  # tech, business, arts, etc.
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    salary = db.Column(db.String(50))
    deadline = db.Column(db.Date)
    application_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'type': self.type,
            'category': self.category,
            'description': self.description,
            'requirements': self.requirements,
            'salary': self.salary,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'application_url': self.application_url,
            'created_at': self.created_at.isoformat()
        }

# Helper Functions
def is_wvsu_email(email):
    """Check if email ends with @wvstateu.edu"""
    return email.lower().endswith('@wvstateu.edu')

def is_admin_email(email):
    """Check if email is admin email"""
    return email.lower() == 'admin@wvstateu.edu'

def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # For now, we'll use a simple admin check
        # In production, you'd want proper session management
        return f(*args, **kwargs)
    return decorated_function

def load_opportunities_from_csv():
    """Load opportunities from CSV file"""
    csv_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'opportunities.csv')
    if not os.path.exists(csv_file):
        return
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Check if opportunity already exists
            existing = Opportunity.query.filter_by(title=row['title'], company=row['company']).first()
            if not existing:
                opportunity = Opportunity(
                    title=row['title'],
                    company=row['company'],
                    location=row['location'],
                    type=row['type'],
                    category=row['category'],
                    description=row['description'],
                    requirements=row.get('requirements', ''),
                    salary=row.get('salary', ''),
                    deadline=datetime.strptime(row['deadline'], '%Y-%m-%d').date() if row['deadline'] else None,
                    application_url=row.get('application_url', '')
                )
                db.session.add(opportunity)
    
    db.session.commit()

# API Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Campus Climb API is running'})

@app.route('/api/opportunities', methods=['GET'])
def get_opportunities():
    """Get all opportunities with optional filtering"""
    # Query parameters for filtering
    type_filter = request.args.get('type', '')
    category_filter = request.args.get('category', '')
    search_query = request.args.get('search', '')
    
    query = Opportunity.query
    
    if type_filter:
        query = query.filter(Opportunity.type == type_filter)
    if category_filter:
        query = query.filter(Opportunity.category == category_filter)
    if search_query:
        query = query.filter(
            Opportunity.title.contains(search_query) |
            Opportunity.company.contains(search_query) |
            Opportunity.description.contains(search_query)
        )
    
    opportunities = query.order_by(Opportunity.created_at.desc()).all()
    return jsonify([opp.to_dict() for opp in opportunities])

@app.route('/api/opportunities/<int:id>', methods=['GET'])
def get_opportunity(id):
    """Get a specific opportunity by ID"""
    opportunity = Opportunity.query.get_or_404(id)
    return jsonify(opportunity.to_dict())

@app.route('/api/opportunities/types', methods=['GET'])
def get_opportunity_types():
    """Get all unique opportunity types"""
    types = db.session.query(Opportunity.type).distinct().all()
    return jsonify([t[0] for t in types])

@app.route('/api/opportunities/categories', methods=['GET'])
def get_opportunity_categories():
    """Get all unique opportunity categories"""
    categories = db.session.query(Opportunity.category).distinct().all()
    return jsonify([c[0] for c in categories])

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email = data.get('email', '').strip()
    password = data.get('password', '')
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    
    # Validation
    if not all([email, password, first_name, last_name]):
        return jsonify({'error': 'All fields are required'}), 400
    
    if not is_wvsu_email(email):
        return jsonify({'error': 'Only WVSU email addresses (@wvstateu.edu) are allowed'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create user
    user = User(email=email, first_name=first_name, last_name=last_name)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'Registration successful',
        'user': user.to_dict()
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate user and return user data"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    if not is_wvsu_email(email):
        return jsonify({'error': 'Only WVSU email addresses (@wvstateu.edu) are allowed'}), 400
    
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        })
    else:
        return jsonify({'error': 'Invalid email or password'}), 401

@app.route('/api/auth/profile', methods=['GET'])
def get_profile():
    """Get user profile by email"""
    email = request.args.get('email', '').strip()
    
    if not email:
        return jsonify({'error': 'Email parameter is required'}), 400
    
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify(user.to_dict())
    else:
        return jsonify({'error': 'User not found'}), 404

# Admin Authentication
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Admin login endpoint"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    if not is_admin_email(email):
        return jsonify({'error': 'Admin access required'}), 403
    
    # For now, we'll use a simple admin password check
    # In production, you'd want proper admin user management
    if email.lower() == 'admin@wvstateu.edu' and password == 'admin123':
        return jsonify({
            'message': 'Admin login successful',
            'admin': {
                'email': email,
                'role': 'admin'
            }
        })
    else:
        return jsonify({'error': 'Invalid admin credentials'}), 401

# Admin Dashboard Routes
@app.route('/api/admin/dashboard', methods=['GET'])
def admin_dashboard():
    """Get admin dashboard statistics"""
    try:
        total_users = User.query.count()
        total_opportunities = Opportunity.query.count()
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        recent_opportunities = Opportunity.query.order_by(Opportunity.created_at.desc()).limit(5).all()
        
        return jsonify({
            'total_users': total_users,
            'total_opportunities': total_opportunities,
            'recent_users': [user.to_dict() for user in recent_users],
            'recent_opportunities': [opp.to_dict() for opp in recent_opportunities]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users', methods=['GET'])
def admin_get_users():
    """Get all users for admin management"""
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        return jsonify([user.to_dict() for user in users])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def admin_delete_user(user_id):
    """Delete a user (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/opportunities', methods=['GET'])
def admin_get_opportunities():
    """Get all opportunities for admin management"""
    try:
        opportunities = Opportunity.query.order_by(Opportunity.created_at.desc()).all()
        return jsonify([opp.to_dict() for opp in opportunities])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/opportunities/<int:opp_id>', methods=['PUT'])
def admin_update_opportunity(opp_id):
    """Update an opportunity (admin only)"""
    try:
        opportunity = Opportunity.query.get(opp_id)
        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404
        
        data = request.get_json()
        if data.get('title'):
            opportunity.title = data['title']
        if data.get('company'):
            opportunity.company = data['company']
        if data.get('location'):
            opportunity.location = data['location']
        if data.get('type'):
            opportunity.type = data['type']
        if data.get('category'):
            opportunity.category = data['category']
        if data.get('description'):
            opportunity.description = data['description']
        if data.get('requirements'):
            opportunity.requirements = data['requirements']
        if data.get('salary'):
            opportunity.salary = data['salary']
        if data.get('deadline'):
            opportunity.deadline = datetime.strptime(data['deadline'], '%Y-%m-%d').date()
        if data.get('application_url'):
            opportunity.application_url = data['application_url']
        
        db.session.commit()
        return jsonify({'message': 'Opportunity updated successfully', 'opportunity': opportunity.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/opportunities/<int:opp_id>', methods=['DELETE'])
def admin_delete_opportunity(opp_id):
    """Delete an opportunity (admin only)"""
    try:
        opportunity = Opportunity.query.get(opp_id)
        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404
        
        db.session.delete(opportunity)
        db.session.commit()
        return jsonify({'message': 'Opportunity deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/load-csv', methods=['POST'])
def admin_load_csv():
    """Admin endpoint to reload CSV data"""
    try:
        load_opportunities_from_csv()
        return jsonify({'message': 'CSV data loaded successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/export-csv', methods=['GET'])
def admin_export_csv():
    """Export current opportunities to CSV"""
    try:
        opportunities = Opportunity.query.all()
        
        # Create CSV data
        csv_data = []
        for opp in opportunities:
            csv_data.append({
                'title': opp.title,
                'company': opp.company,
                'location': opp.location,
                'type': opp.type,
                'category': opp.category,
                'description': opp.description,
                'requirements': opp.requirements or '',
                'salary': opp.salary or '',
                'deadline': opp.deadline.isoformat() if opp.deadline else '',
                'application_url': opp.application_url or ''
            })
        
        return jsonify({'csv_data': csv_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Create database tables and load initial data
with app.app_context():
    db.create_all()
    load_opportunities_from_csv()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
