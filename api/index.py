from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from datetime import datetime
from functools import wraps

app = Flask(__name__)
CORS(app)

# Session configuration
# Use cookie-based sessions for better serverless compatibility
# In serverless environments, filesystem sessions don't persist
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('VERCEL') is not None  # HTTPS only in production
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
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
            'created_at': self.created_at.isoformat() if self.created_at else None
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

# CSV functions removed - using Supabase as primary database

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
                print(f"Database initialized with {Opportunity.query.count()} opportunities")
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
        # Read from database - include opportunities where is_deleted is False or null
        query = Opportunity.query.filter(
            (Opportunity.is_deleted == False) | (Opportunity.is_deleted.is_(None))
        )
        
        # Filters
        type_filter = request.args.get('type', '').strip()
        category_filter = request.args.get('category', '').strip()
        search_query = request.args.get('search', '').strip()
        
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
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/opportunities/<int:id>', methods=['GET'])
def get_opportunity(id):
    """Get a specific opportunity by ID"""
    try:
        opportunity = Opportunity.query.filter(
            Opportunity.id == id,
            (Opportunity.is_deleted == False) | (Opportunity.is_deleted.is_(None))
        ).first()
        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404
        return jsonify(opportunity.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/opportunities/types', methods=['GET'])
def get_opportunity_types():
    """Get all unique opportunity types"""
    try:
        types = db.session.query(Opportunity.type).filter(
            (Opportunity.is_deleted == False) | (Opportunity.is_deleted.is_(None))
        ).distinct().all()
        return jsonify([t[0] for t in types])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/opportunities/categories', methods=['GET'])
def get_opportunity_categories():
    """Get all unique opportunity categories"""
    try:
        categories = db.session.query(Opportunity.category).filter(
            (Opportunity.is_deleted == False) | (Opportunity.is_deleted.is_(None))
        ).distinct().all()
        return jsonify([c[0] for c in categories])
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
    """Get current logged in user from session or email parameter (for serverless fallback)"""
    try:
        from flask import session
        
        # Try to get user from session first
        user_id = session.get('user_id')
        email = request.args.get('email')  # Fallback for serverless environments
        
        if user_id:
            user = User.query.get(user_id)
            if user:
                return jsonify({'user': user.to_dict()})
        
        # Fallback: if email provided and session doesn't work (serverless), validate user exists
        if email:
            user = User.query.filter_by(email=email.lower().strip()).first()
            if user:
                # Create session for future requests
                session['user_id'] = user.id
                session['email'] = user.email
                return jsonify({'user': user.to_dict()})
        
        return jsonify({'error': 'Not authenticated'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Admin endpoints for opportunity management
@app.route('/api/admin/opportunities', methods=['GET'])
def admin_get_opportunities():
    """Get all opportunities for admin (including deleted)"""
    try:
        opportunities = Opportunity.query.order_by(Opportunity.created_at.desc()).all()
        return jsonify([opp.to_dict() for opp in opportunities])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/opportunities', methods=['POST'])
def admin_create_opportunity():
    """Create a new opportunity"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['title', 'company', 'location', 'type', 'category', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        new_opportunity = Opportunity(
            title=data['title'],
            company=data['company'],
            location=data['location'],
            type=data['type'],
            category=data['category'],
            description=data['description'],
            requirements=data.get('requirements', ''),
            salary=data.get('salary', ''),
            application_url=data.get('application_url', ''),
            is_deleted=False
        )
        
        db.session.add(new_opportunity)
        db.session.commit()
        
        return jsonify({
            'message': 'Opportunity created successfully',
            'opportunity': new_opportunity.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/opportunities/<int:id>', methods=['PUT'])
def admin_update_opportunity(id):
    """Update an opportunity"""
    try:
        opportunity = Opportunity.query.get(id)
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
        if data.get('application_url'):
            opportunity.application_url = data['application_url']
        if 'is_deleted' in data:
            opportunity.is_deleted = bool(data['is_deleted'])
        
        db.session.commit()
        return jsonify({
            'message': 'Opportunity updated successfully',
            'opportunity': opportunity.to_dict()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/opportunities/<int:id>', methods=['DELETE'])
def admin_delete_opportunity(id):
    """Delete an opportunity (soft delete)"""
    try:
        opportunity = Opportunity.query.get(id)
        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404
        
        opportunity.is_deleted = True
        db.session.commit()
        
        return jsonify({'message': 'Opportunity deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# CSV sync endpoints removed - using Supabase as primary database

# Additional admin endpoints
@app.route('/api/admin/users', methods=['GET'])
def admin_get_users():
    """Get all users for admin"""
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        return jsonify([user.to_dict() for user in users])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/dashboard', methods=['GET'])
def admin_dashboard():
    """Get admin dashboard data"""
    try:
        total_users = User.query.count()
        total_opportunities = Opportunity.query.filter_by(is_deleted=False).count()
        
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        recent_opportunities = Opportunity.query.filter_by(is_deleted=False).order_by(Opportunity.created_at.desc()).limit(5).all()
        
        return jsonify({
            'total_users': total_users,
            'total_opportunities': total_opportunities,
            'recent_users': [user.to_dict() for user in recent_users],
            'recent_opportunities': [opp.to_dict() for opp in recent_opportunities]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()
