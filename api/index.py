from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
import csv
from datetime import datetime
from functools import wraps

app = Flask(__name__)
CORS(app)

# Database configuration
database_url = os.environ.get('DATABASE_URL', 'sqlite:///campus_climb.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

# For Vercel serverless, use in-memory SQLite if no DATABASE_URL is set
if os.environ.get('VERCEL') and not os.environ.get('DATABASE_URL'):
    database_url = 'sqlite:///:memory:'

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'

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

def load_opportunities_from_csv():
    """Load opportunities from CSV file"""
    try:
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'data', 'opportunities.csv')
        if os.path.exists(csv_path):
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    opportunity = Opportunity(
                        title=row.get('title', ''),
                        company=row.get('company', ''),
                        location=row.get('location', ''),
                        type=row.get('type', ''),
                        category=row.get('category', ''),
                        description=row.get('description', ''),
                        requirements=row.get('requirements', ''),
                        salary=row.get('salary', ''),
                        application_url=row.get('application_url', '')
                    )
                    db.session.add(opportunity)
            db.session.commit()
    except Exception as e:
        print(f"Error loading CSV: {e}")

# Initialize database
def init_db():
    with app.app_context():
        db.create_all()
        # Add some test data if database is empty
        if Opportunity.query.count() == 0:
            # Try to load from CSV first
            load_opportunities_from_csv()
            
            # If no CSV data, add test data
            if Opportunity.query.count() == 0:
                test_opportunity = Opportunity(
                    title='Software Engineering Intern',
                    company='Tech Corp',
                    location='Remote',
                    type='internship',
                    category='tech',
                    description='Great opportunity for software engineering students',
                    requirements='Python, JavaScript, React',
                    salary='$25/hour',
                    application_url='https://example.com/apply'
                )
                db.session.add(test_opportunity)
                db.session.commit()

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
        # Initialize database if needed
        if hasattr(app, 'init_db') and not hasattr(app, '_db_initialized'):
            app.init_db()
            app._db_initialized = True
        
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
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/opportunities/<int:id>', methods=['GET'])
def get_opportunity(id):
    """Get a specific opportunity by ID"""
    try:
        opportunity = Opportunity.query.get(id)
        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404
        return jsonify(opportunity.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/opportunities/types', methods=['GET'])
def get_opportunity_types():
    """Get all unique opportunity types"""
    try:
        types = db.session.query(Opportunity.type).distinct().all()
        return jsonify([t[0] for t in types])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/opportunities/categories', methods=['GET'])
def get_opportunity_categories():
    """Get all unique opportunity categories"""
    try:
        categories = db.session.query(Opportunity.category).distinct().all()
        return jsonify([c[0] for c in categories])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
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
        
        # Initialize database if needed
        if hasattr(app, 'init_db') and not hasattr(app, '_db_initialized'):
            app.init_db()
            app._db_initialized = True
        
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
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Initialize database if needed
        if hasattr(app, 'init_db') and not hasattr(app, '_db_initialized'):
            app.init_db()
            app._db_initialized = True
        
        # Check if it's an admin login first
        if is_admin_email(email):
            expected_password = get_admin_password(email)
            if expected_password and password == expected_password:
                return jsonify({
                    'message': 'Admin login successful',
                    'user': {
                        'id': 0,
                        'email': email,
                        'first_name': 'Admin',
                        'last_name': 'User',
                        'is_admin': True
                    }
                })
            else:
                return jsonify({'error': 'Invalid admin credentials'}), 401
        
        # Regular user login - check WVSU email
        if not is_wvsu_email(email):
            return jsonify({'error': 'Only WVSU email addresses (@wvstateu.edu) are allowed'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        # For now, create a test user if none exists
        if not user:
            user = User(email=email, first_name='Test', last_name='User')
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
        
        if user.check_password(password):
            return jsonify({
                'message': 'Login successful',
                'user': user.to_dict()
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Admin endpoints
@app.route('/api/admin/opportunities', methods=['POST'])
@admin_required
def admin_create_opportunity():
    """Create a new opportunity (admin only)"""
    try:
        # Ensure database is initialized
        with app.app_context():
            db.create_all()
        
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
            application_url=data.get('application_url', '')
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

@app.route('/api/admin/opportunities/<int:opp_id>', methods=['PUT'])
@admin_required
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
@admin_required
def admin_delete_opportunity(opp_id):
    """Delete an opportunity (admin only)"""
    try:
        # Ensure database is initialized
        with app.app_context():
            db.create_all()
        
        opportunity = Opportunity.query.get(opp_id)
        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404
        
        db.session.delete(opportunity)
        db.session.commit()
        return jsonify({'message': 'Opportunity deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/load-csv', methods=['POST'])
@admin_required
def admin_load_csv():
    """Admin endpoint to reload CSV data"""
    try:
        # Clear existing opportunities
        Opportunity.query.delete()
        db.session.commit()
        
        # Load from CSV
        load_opportunities_from_csv()
        return jsonify({'message': 'CSV data loaded successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/export-csv', methods=['GET'])
@admin_required
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

@app.route('/api/admin/dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    """Get admin dashboard data"""
    try:
        # Ensure database is initialized
        with app.app_context():
            db.create_all()
        
        # Get basic stats
        total_users = User.query.count()
        total_opportunities = Opportunity.query.count()
        
        # Get recent users (last 5)
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        
        # Get recent opportunities (last 5)
        recent_opportunities = Opportunity.query.order_by(Opportunity.created_at.desc()).limit(5).all()
        
        return jsonify({
            'total_users': total_users,
            'total_opportunities': total_opportunities,
            'recent_users': [user.to_dict() for user in recent_users],
            'recent_opportunities': [opp.to_dict() for opp in recent_opportunities]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/opportunities', methods=['GET'])
@admin_required
def admin_get_opportunities():
    """Get all opportunities for admin"""
    try:
        opportunities = Opportunity.query.order_by(Opportunity.created_at.desc()).all()
        return jsonify([opp.to_dict() for opp in opportunities])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def admin_get_users():
    """Get all users for admin"""
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        return jsonify([user.to_dict() for user in users])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()
