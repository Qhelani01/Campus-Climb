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

@app.route('/api/admin/load-csv', methods=['POST'])
def admin_load_csv():
    """Admin endpoint to reload CSV data"""
    try:
        load_opportunities_from_csv()
        return jsonify({'message': 'CSV data loaded successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Create database tables and load initial data
with app.app_context():
    db.create_all()
    load_opportunities_from_csv()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
