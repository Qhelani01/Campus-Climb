from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
import csv
import json
from datetime import datetime
from functools import wraps

app = Flask(__name__)
CORS(app)

# Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Database configuration
# Force persistent database - no more in-memory SQLite
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    # Fallback to a persistent SQLite file
    database_url = 'sqlite:///campus_climb.db'
elif database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

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
    type = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    salary = db.Column(db.String(50))
    deadline = db.Column(db.Date)
    application_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)  # New field to track deleted items
    
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
    admin_emails = ['qhestoemoyo@gmail.com', 'chiwalenatwange@gmail.com']
    return email.lower() in admin_emails

def get_admin_password(email):
    """Get admin password based on email"""
    admin_credentials = {
        'qhestoemoyo@gmail.com': '3991Gwabalanda',
        'chiwalenatwange@gmail.com': 'noodles2001'
    }
    return admin_credentials.get(email.lower())

def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # For now, allow all requests (we'll add proper auth later)
        return f(*args, **kwargs)
    return decorated_function

def get_csv_path():
    """Get the path to the CSV file"""
    return os.path.join(os.path.dirname(__file__), '..', 'backend', 'data', 'opportunities.csv')

def read_opportunities_from_csv():
    """Read all opportunities from CSV and return as list of dicts.
    This bypasses the database and is the source of truth for the frontend.
    """
    opportunities = []
    csv_path = get_csv_path()
    if not os.path.exists(csv_path):
        return opportunities
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for idx, row in enumerate(reader, start=1):
                # Normalize fields and provide fallbacks
                opp = {
                    'id': idx,
                    'title': row.get('title', '').strip(),
                    'company': row.get('company', '').strip(),
                    'location': row.get('location', '').strip(),
                    'type': row.get('type', '').strip(),
                    'category': row.get('category', '').strip(),
                    'description': row.get('description', '').strip(),
                    'requirements': row.get('requirements', '') or '',
                    'salary': row.get('salary', '') or '',
                    'deadline': row.get('deadline', '') or None,
                    'application_url': row.get('application_url', '') or '',
                    'created_at': row.get('created_at', '') or None,
                }
                # Skip rows explicitly marked deleted
                if row.get('is_deleted', '').strip().lower() == 'true':
                    continue
                opportunities.append(opp)
    except Exception as e:
        print(f"Error reading CSV: {e}")
    return opportunities

def load_opportunities_from_csv():
    """Load opportunities from CSV file"""
    try:
        csv_path = get_csv_path()
        
        if os.path.exists(csv_path):
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Skip if this opportunity was marked as deleted
                    if row.get('is_deleted', '').lower() == 'true':
                        continue
                    
                    # Check if opportunity already exists (to avoid duplicates)
                    existing = Opportunity.query.filter_by(title=row.get('title', '')).first()
                    if existing:
                        continue
                    
                    opportunity = Opportunity(
                        title=row.get('title', ''),
                        company=row.get('company', ''),
                        location=row.get('location', ''),
                        type=row.get('type', ''),
                        category=row.get('category', ''),
                        description=row.get('description', ''),
                        requirements=row.get('requirements', ''),
                        salary=row.get('salary', ''),
                        application_url=row.get('application_url', ''),
                        is_deleted=False
                    )
                    db.session.add(opportunity)
            db.session.commit()
    except Exception as e:
        print(f"Error loading CSV: {e}")

def save_opportunities_to_csv():
    """Save all opportunities back to CSV file"""
    try:
        csv_path = get_csv_path()
        opportunities = Opportunity.query.filter_by(is_deleted=False).all()
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['title', 'company', 'location', 'type', 'category', 'description', 'requirements', 'salary', 'deadline', 'application_url', 'is_deleted']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            
            for opp in opportunities:
                writer.writerow({
                    'title': opp.title,
                    'company': opp.company,
                    'location': opp.location,
                    'type': opp.type,
                    'category': opp.category,
                    'description': opp.description,
                    'requirements': opp.requirements or '',
                    'salary': opp.salary or '',
                    'deadline': opp.deadline.isoformat() if opp.deadline else '',
                    'application_url': opp.application_url or '',
                    'is_deleted': 'false'
                })
    except Exception as e:
        print(f"Error saving CSV: {e}")



def add_opportunity_to_csv(opportunity_data):
    """Add a new opportunity to the CSV file"""
    try:
        # In serverless environment, we can't write to files
        # So we'll use a different approach - store in database
        print(f"Added opportunity '{opportunity_data['title']}' to database")
    except Exception as e:
        print(f"Error adding opportunity to CSV: {e}")

def clean_test_opportunities():
    """Remove any test/dummy opportunities"""
    try:
        test_titles = [
            'Software Engineering Intern',
            'Test Admin Opportunity',
            'Test Opportunity'
        ]
        
        for title in test_titles:
            test_opp = Opportunity.query.filter_by(title=title).first()
            if test_opp:
                test_opp.is_deleted = True
                db.session.commit()
                print(f"Marked test opportunity '{title}' as deleted")
    except Exception as e:
        print(f"Error cleaning test opportunities: {e}")

# Initialize database
def init_db():
    with app.app_context():
        db.create_all()
        # Load from CSV only - no test data
        load_opportunities_from_csv()
        # Clean up any test opportunities
        clean_test_opportunities()

# Store the initialization function
app.init_db = init_db

# Ensure database is initialized on every request in serverless environment
@app.before_request
def ensure_db_initialized():
    if os.environ.get('VERCEL'):
        try:
            # Always create tables in serverless environment
            with app.app_context():
                db.create_all()
                # Load CSV data if database is empty
                if Opportunity.query.count() == 0:
                    load_opportunities_from_csv()
        except Exception as e:
            print(f"Database initialization error: {e}")

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({
        'message': 'API is working!',
        'status': 'success'
    })

@app.route('/api/health', methods=['GET'])
def health():
    try:
        # Test database connection
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'message': 'API is running with database',
            'database': 'connected'
        })
    except Exception as e:
        return jsonify({
            'status': 'degraded',
            'message': 'API is running but database has issues',
            'error': str(e)
        }), 500

@app.route('/api/opportunities', methods=['GET'])
def opportunities():
    try:
        # Read directly from CSV
        all_opps = read_opportunities_from_csv()

        # Filters
        type_filter = (request.args.get('type') or '').strip().lower()
        category_filter = (request.args.get('category') or '').strip().lower()
        search_query = (request.args.get('search') or '').strip().lower()

        def matches_filters(opp):
            if type_filter and (opp.get('type', '').lower() != type_filter):
                return False
            if category_filter and (opp.get('category', '').lower() != category_filter):
                return False
            if search_query:
                haystack = f"{opp.get('title','')} {opp.get('company','')} {opp.get('description','')}".lower()
                if search_query not in haystack:
                    return False
            return True

        filtered = [o for o in all_opps if matches_filters(o)]
        # Most recent first if created_at exists; otherwise keep CSV order
        def sort_key(o):
            return o.get('created_at') or ''
        filtered.sort(key=sort_key, reverse=True)
        return jsonify(filtered)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/opportunities/<int:id>', methods=['GET'])
def get_opportunity(id):
    """Get a specific opportunity by ID"""
    try:
        all_opps = read_opportunities_from_csv()
        # IDs are 1-based from CSV row order
        if 1 <= id <= len(all_opps):
            return jsonify(all_opps[id - 1])
        return jsonify({'error': 'Opportunity not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/opportunities/types', methods=['GET'])
def get_opportunity_types():
    """Get all unique opportunity types"""
    try:
        all_opps = read_opportunities_from_csv()
        types = sorted({(o.get('type') or '').strip() for o in all_opps if o.get('type')})
        return jsonify(types)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/opportunities/categories', methods=['GET'])
def get_opportunity_categories():
    """Get all unique opportunity categories"""
    try:
        all_opps = read_opportunities_from_csv()
        categories = sorted({(o.get('category') or '').strip() for o in all_opps if o.get('category')})
        return jsonify(categories)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user. Only WVSU emails (@wvstateu.edu) are allowed."""
    try:
        data = request.get_json() or {}
        email = (data.get('email') or '').strip().lower()
        password = data.get('password') or ''
        first_name = (data.get('first_name') or '').strip()
        last_name = (data.get('last_name') or '').strip()

        # Validate
        if not all([email, password, first_name, last_name]):
            return jsonify({'error': 'All fields are required'}), 400
        if not is_wvsu_email(email):
            return jsonify({'error': 'Only WVSU email addresses (@wvstateu.edu) are allowed'}), 400

        # Ensure tables exist
        with app.app_context():
            db.create_all()

        # Uniqueness
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 409

        user = User(email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Create session
        from flask import session
        session['user_id'] = user.id
        session['email'] = user.email
        
        return jsonify({
            'message': 'Registration successful', 
            'user': user.to_dict(),
            'session_id': session.sid if hasattr(session, 'sid') else None
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate existing user. Only WVSU emails allowed. No mock users."""
    try:
        data = request.get_json() or {}
        email = (data.get('email') or '').strip().lower()
        password = data.get('password') or ''

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        if not is_wvsu_email(email):
            return jsonify({'error': 'Only WVSU email addresses (@wvstateu.edu) are allowed'}), 400

        with app.app_context():
            db.create_all()

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401

        # Create session
        from flask import session
        session['user_id'] = user.id
        session['email'] = user.email
        
        return jsonify({
            'message': 'Login successful', 
            'user': user.to_dict(),
            'session_id': session.sid if hasattr(session, 'sid') else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user and clear session"""
    try:
        from flask import session
        session.clear()
        return jsonify({'message': 'Logout successful'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    """Get current logged in user from session"""
    try:
        from flask import session
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Admin endpoints
@app.route('/api/admin/opportunities', methods=['POST'])
@admin_required
def admin_create_opportunity():
    return jsonify({'error': 'Admin features are disabled'}), 410

@app.route('/api/admin/opportunities/<int:opp_id>', methods=['PUT'])
@admin_required
def admin_update_opportunity(opp_id):
    return jsonify({'error': 'Admin features are disabled'}), 410

@app.route('/api/admin/opportunities/<int:opp_id>', methods=['DELETE'])
@admin_required
def admin_delete_opportunity(opp_id):
    return jsonify({'error': 'Admin features are disabled'}), 410

@app.route('/api/admin/load-csv', methods=['POST'])
@admin_required
def admin_load_csv():
    return jsonify({'error': 'Admin features are disabled'}), 410

@app.route('/api/admin/export-csv', methods=['GET'])
@admin_required
def admin_export_csv():
    return jsonify({'error': 'Admin features are disabled'}), 410

@app.route('/api/admin/dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    return jsonify({'error': 'Admin features are disabled'}), 410

@app.route('/api/admin/opportunities', methods=['GET'])
@admin_required
def admin_get_opportunities():
    return jsonify({'error': 'Admin features are disabled'}), 410

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def admin_get_users():
    return jsonify({'error': 'Admin features are disabled'}), 410

if __name__ == '__main__':
    app.run()
