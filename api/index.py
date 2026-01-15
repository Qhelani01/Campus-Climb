from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
import os
import json
import sys
import re
from datetime import datetime
from functools import wraps

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ai_assistant import generate_application_advice

# Import scheduler functions lazily to avoid circular imports
def get_fetch_functions():
    """Get fetch functions, importing only when needed"""
    import scheduler
    return scheduler.fetch_all_opportunities, scheduler.get_fetch_logs

def get_fetcher_config():
    """Get fetcher config, importing only when needed"""
    import fetcher_config
    return fetcher_config.FetcherConfig

app = Flask(__name__)

# Determine allowed origins from environment variable
# Format: comma-separated list of origins, e.g., "http://localhost:8080,https://yourdomain.com"
allowed_origins_str = os.environ.get('ALLOWED_ORIGINS', '')
if allowed_origins_str:
    allowed_origins = [origin.strip() for origin in allowed_origins_str.split(',') if origin.strip()]
else:
    # Default to localhost for development
    is_vercel = os.environ.get('VERCEL') is not None
    if is_vercel:
        # In production, require ALLOWED_ORIGINS to be set
        allowed_origins = []
        print("WARNING: ALLOWED_ORIGINS not set in production. CORS will be restrictive.")
    else:
        # Development defaults
        allowed_origins = ["http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:8000"]

# Configure CORS to allow requests from frontend
CORS(app, resources={
    r"/api/*": {
        "origins": allowed_origins,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  # Use in-memory storage (works for serverless)
)

# Session configuration
# Use null sessions for serverless (Vercel) - sessions stored in cookies only
# Filesystem sessions don't work on Vercel serverless functions
is_vercel = os.environ.get('VERCEL') is not None
if is_vercel:
    # On Vercel, use null session backend (sessions in cookies only)
    app.config['SESSION_TYPE'] = 'null'
else:
    # Local development can use filesystem
    app.config['SESSION_TYPE'] = 'filesystem'

# Require SECRET_KEY in production
secret_key = os.environ.get('SECRET_KEY')
is_vercel = os.environ.get('VERCEL') is not None

if is_vercel and not secret_key:
    raise ValueError(
        "SECRET_KEY environment variable is required in production. "
        "Please set it in your Vercel environment variables."
    )

if not secret_key:
    secret_key = 'dev-secret-key-change-in-production'  # Only for local development
    print("WARNING: Using default SECRET_KEY. Set SECRET_KEY environment variable in production.")

app.config['SECRET_KEY'] = secret_key
app.config['SESSION_COOKIE_SECURE'] = is_vercel  # HTTPS only in production
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
Session(app)

# Database configuration
# Force persistent database - no more in-memory SQLite
database_url = os.environ.get('DATABASE_URL')
is_postgres = False
if not database_url:
    # Fallback to a persistent SQLite file
    database_url = 'sqlite:///campus_climb.db'
elif database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
    is_postgres = True
elif database_url.startswith('postgresql://'):
    is_postgres = True

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Engine options - PostgreSQL-specific options only for PostgreSQL
engine_options = {
    'pool_pre_ping': True,
}
if is_postgres:
    # PostgreSQL-specific options
    # For Supabase Session Pooler, limit pool size to avoid "max clients reached" errors
    # Session Pooler typically allows 15 connections for free tier
    # Use small pool size for serverless (each function instance gets its own pool)
    is_vercel = os.environ.get('VERCEL') is not None
    if is_vercel:
        # Serverless: use small pool size to avoid exhausting Supabase Session Pooler
        # Session Pooler allows ~15 connections total, so we limit per instance
        # Use 1 connection per instance to minimize pool usage
        # Multiple instances can share the 15 connection limit
        # Increase pool slightly to allow for concurrent operations within same instance
        # Still conservative for Supabase Session Pooler (15 total connections)
        engine_options['pool_size'] = 2
        engine_options['max_overflow'] = 1  # Allow 1 overflow for burst traffic
        engine_options['pool_timeout'] = 10  # Reduced timeout since we have retry logic
        # Close connections after use to return them to pool quickly
        engine_options['pool_reset_on_return'] = 'commit'  # Reset connection state on return
    else:
        # Local development: can use more connections
        engine_options['pool_size'] = 5
        engine_options['max_overflow'] = 5
    
    engine_options['pool_recycle'] = 300  # Recycle connections after 5 minutes
    engine_options['connect_args'] = {'connect_timeout': 10}
else:
    # SQLite-specific options (if any)
    engine_options['connect_args'] = {'check_same_thread': False}

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = engine_options

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False, index=True)
    # AI Assistant profile fields
    resume_summary = db.Column(db.Text, nullable=True)
    skills = db.Column(db.Text, nullable=True)  # JSON string or comma-separated
    career_goals = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
            'is_admin': self.is_admin,
            'resume_summary': self.resume_summary,
            'skills': self.skills,
            'career_goals': self.career_goals,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_user_info_for_ai(self):
        """Get user info formatted for AI assistant"""
        skills_list = []
        if self.skills:
            try:
                # Try parsing as JSON first
                skills_list = json.loads(self.skills)
            except:
                # Fallback to comma-separated string
                skills_list = [s.strip() for s in self.skills.split(',') if s.strip()]
        
        return {
            'resume_summary': self.resume_summary or '',
            'skills': skills_list,
            'career_goals': self.career_goals or ''
        }

class Opportunity(db.Model):
    __tablename__ = 'opportunities'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    salary = db.Column(db.String(50))
    deadline = db.Column(db.Date, index=True)
    application_url = db.Column(db.String(500))
    # Source tracking fields
    source = db.Column(db.String(50), nullable=True, index=True)  # e.g., 'github_jobs', 'jooble', 'rss'
    source_id = db.Column(db.String(200), nullable=True, index=True)  # Unique ID from source
    source_url = db.Column(db.String(500), nullable=True)  # Original URL
    last_fetched = db.Column(db.DateTime, nullable=True)  # When last updated from source
    auto_fetched = db.Column(db.Boolean, default=False, index=True)  # Whether fetched automatically
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False, index=True)  # Soft delete flag
    
    # Composite index for common query pattern
    __table_args__ = (
        db.Index('idx_opp_active', 'is_deleted', 'type', 'category'),
    )
    
    @classmethod
    def active_query(cls):
        """Return a query filtered to only active (non-deleted) opportunities"""
        return cls.query.filter(
            (cls.is_deleted == False) | (cls.is_deleted.is_(None))
        )
    
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
            'source': self.source,
            'source_id': self.source_id,
            'source_url': self.source_url,
            'last_fetched': self.last_fetched.isoformat() if self.last_fetched else None,
            'auto_fetched': self.auto_fetched,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Helper Functions
def is_wvsu_email(email):
    """Check if email ends with @wvstateu.edu"""
    return email.lower().endswith('@wvstateu.edu')

def validate_password(password):
    """
    Validate password strength.
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    """
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    return True, None

def get_current_user():
    """Get current user from session or email parameter"""
    from flask import session, request as flask_request
    
    # Try to get user from session first
    user_id = session.get('user_id')
    if user_id:
        try:
            user = User.query.get(user_id)
            if user:
                return user
        except Exception as e:
            print(f"Error getting user by ID {user_id}: {e}")
    
    # Fallback 1: Check email in request args (for serverless)
    email = flask_request.args.get('email')
    if email:
        try:
            user = User.query.filter_by(email=email.lower().strip()).first()
            if user:
                # Try to create session for future requests
                try:
                    session['user_id'] = user.id
                    session['email'] = user.email
                except Exception as session_error:
                    print(f"Warning: Could not set session: {session_error}")
                return user
        except Exception as e:
            print(f"Error getting user by email from args: {e}")
    
    # Fallback 2: Check email in request JSON body (for POST requests)
    if flask_request.is_json:
        email = flask_request.json.get('email') if flask_request.json else None
        if email:
            try:
                user = User.query.filter_by(email=email.lower().strip()).first()
                if user:
                    try:
                        session['user_id'] = user.id
                        session['email'] = user.email
                    except Exception as session_error:
                        print(f"Warning: Could not set session: {session_error}")
                    return user
            except Exception as e:
                print(f"Error getting user by email from JSON: {e}")
    
    # Fallback 3: Check Authorization header (if frontend sends email)
    auth_header = flask_request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        # Could implement token-based auth here if needed
        pass
    
    return None

def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            user = get_current_user()
        except Exception as auth_error:
            # Catch database connection errors and return JSON instead of HTML
            error_msg = str(auth_error)
            if 'QueuePool' in error_msg or 'connection' in error_msg.lower() or 'timeout' in error_msg.lower():
                return jsonify({
                    'error': 'Database connection unavailable. Please try again in a moment.',
                    'details': 'Connection pool exhausted or timeout'
                }), 503
            return jsonify({'error': f'Authentication failed: {error_msg}'}), 500
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        if not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
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
        # Commit all changes at once
        try:
            db.session.commit()
            print(f"Cleaned test opportunities")
        except Exception as db_error:
            db.session.rollback()
            print(f"Error cleaning test opportunities: {db_error}")
    except Exception as e:
        print(f"Error cleaning test opportunities: {e}")
        db.session.rollback()

# Database initialization helper
def tables_exist():
    """Check if database tables already exist"""
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        # Check for both explicit table names (with __tablename__) and default SQLAlchemy names
        # We need both tables to exist
        has_users = 'users' in existing_tables or 'user' in existing_tables
        has_opportunities = 'opportunities' in existing_tables or 'opportunity' in existing_tables
        return has_users and has_opportunities
    except Exception as e:
        # If inspection fails, assume tables don't exist
        print(f"Error checking tables: {e}")
        return False

# Initialize database
def init_db():
    """
    Initialize database tables only if they don't exist.
    
    NOTE: If you're using the database/01_complete_schema.sql file,
    tables are created manually in Supabase. This function will detect
    existing tables and skip creation.
    """
    with app.app_context():
        try:
            if not tables_exist():
                print("Tables don't exist. Creating them...")
                db.create_all()
                print("Database tables created successfully")
            else:
                print("Database tables already exist (created via SQL schema)")
            # Clean up any test opportunities
            clean_test_opportunities()
        except Exception as e:
            print(f"Database initialization error: {e}")
            raise

# Store the initialization function
app.init_db = init_db

# Ensure database is initialized on first request in serverless environment
# Only check once per serverless function instance
_db_initialized = False

def check_and_add_is_admin_column():
    """Check if is_admin column exists, add it if missing"""
    try:
        # Check if PostgreSQL or SQLite
        is_postgres = 'postgresql' in str(db.engine.url)
        
        if is_postgres:
            # PostgreSQL: use information_schema
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'users' 
                AND column_name = 'is_admin'
            """))
            column_exists = result.fetchone() is not None
        else:
            # SQLite: use PRAGMA table_info
            result = db.session.execute(text("PRAGMA table_info(users)"))
            column_exists = any(row[1] == 'is_admin' for row in result.fetchall())
        
        if not column_exists:
            print("is_admin column missing. Adding it...")
            if is_postgres:
                # Add the column
                db.session.execute(text("""
                    ALTER TABLE public.users 
                    ADD COLUMN is_admin BOOLEAN DEFAULT FALSE NOT NULL
                """))
                # Create index
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_users_is_admin 
                    ON public.users(is_admin)
                """))
            else:
                # SQLite: no schema prefix, use INTEGER for boolean
                db.session.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN is_admin BOOLEAN DEFAULT 0 NOT NULL
                """))
                # Create index
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_users_is_admin 
                    ON users(is_admin)
                """))
            db.session.commit()
            print("is_admin column added successfully")
            return True
        else:
            print("is_admin column already exists")
            return False
    except Exception as e:
        print(f"Error checking/adding is_admin column: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return False

def check_and_add_user_profile_columns():
    """Check if user profile columns exist, add them if missing"""
    try:
        # Check if PostgreSQL or SQLite
        is_postgres = 'postgresql' in str(db.engine.url)
        
        if is_postgres:
            # PostgreSQL: use information_schema
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'users' 
                AND column_name IN ('resume_summary', 'skills', 'career_goals')
            """))
            existing_columns = {row[0] for row in result.fetchall()}
        else:
            # SQLite: use PRAGMA table_info
            result = db.session.execute(text("PRAGMA table_info(users)"))
            existing_columns = {row[1] for row in result.fetchall()}
        
        columns_to_add = []
        if 'resume_summary' not in existing_columns:
            columns_to_add.append('resume_summary TEXT')
        if 'skills' not in existing_columns:
            columns_to_add.append('skills TEXT')
        if 'career_goals' not in existing_columns:
            columns_to_add.append('career_goals TEXT')
        
        if columns_to_add:
            print(f"User profile columns missing. Adding: {', '.join([c.split()[0] for c in columns_to_add])}...")
            for column_def in columns_to_add:
                if is_postgres:
                    db.session.execute(text(f"""
                        ALTER TABLE public.users 
                        ADD COLUMN {column_def}
                    """))
                else:
                    # SQLite: no schema prefix
                    db.session.execute(text(f"""
                        ALTER TABLE users 
                        ADD COLUMN {column_def}
                    """))
            db.session.commit()
            print("User profile columns added successfully")
            return True
        else:
            print("User profile columns already exist")
            return False
    except Exception as e:
        print(f"Error checking/adding user profile columns: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return False

def check_and_add_opportunity_source_columns():
    """Check if opportunity source columns exist, add them if missing"""
    try:
        database_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        is_sqlite = 'sqlite' in database_url.lower()
        
        # Check which columns exist
        if is_sqlite:
            # SQLite: Use PRAGMA table_info
            result = db.session.execute(text("PRAGMA table_info(opportunities)"))
            existing_columns = {row[1] for row in result.fetchall()}  # Column name is at index 1
        else:
            # PostgreSQL: Use information_schema
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'opportunities' 
                AND column_name IN ('source', 'source_id', 'source_url', 'last_fetched', 'auto_fetched')
            """))
            existing_columns = {row[0] for row in result.fetchall()}
        
        columns_to_add = []
        if 'source' not in existing_columns:
            columns_to_add.append(('source', 'VARCHAR(50)' if not is_sqlite else 'TEXT'))
        if 'source_id' not in existing_columns:
            columns_to_add.append(('source_id', 'VARCHAR(200)' if not is_sqlite else 'TEXT'))
        if 'source_url' not in existing_columns:
            columns_to_add.append(('source_url', 'VARCHAR(500)' if not is_sqlite else 'TEXT'))
        if 'last_fetched' not in existing_columns:
            columns_to_add.append(('last_fetched', 'TIMESTAMP' if not is_sqlite else 'DATETIME'))
        if 'auto_fetched' not in existing_columns:
            columns_to_add.append(('auto_fetched', 'BOOLEAN DEFAULT FALSE' if not is_sqlite else 'INTEGER DEFAULT 0'))
        
        if columns_to_add:
            print(f"Opportunity source columns missing. Adding: {', '.join([c[0] for c in columns_to_add])}...")
            table_name = 'opportunities' if is_sqlite else 'public.opportunities'
            for column_name, column_type in columns_to_add:
                try:
                    db.session.execute(text(f"""
                        ALTER TABLE {table_name} 
                        ADD COLUMN {column_name} {column_type}
                    """))
                except Exception as col_error:
                    # Column might already exist (race condition)
                    print(f"Warning: Could not add column {column_name}: {col_error}")
            
            # Create indexes (SQLite and PostgreSQL both support IF NOT EXISTS)
            index_prefix = '' if is_sqlite else 'public.'
            try:
                if 'source' not in existing_columns:
                    db.session.execute(text(f"""
                        CREATE INDEX IF NOT EXISTS idx_opportunities_source 
                        ON {index_prefix}opportunities(source)
                    """))
            except Exception as e:
                print(f"Warning: Could not create source index: {e}")
            
            try:
                if 'source_id' not in existing_columns:
                    db.session.execute(text(f"""
                        CREATE INDEX IF NOT EXISTS idx_opportunities_source_id 
                        ON {index_prefix}opportunities(source_id)
                    """))
            except Exception as e:
                print(f"Warning: Could not create source_id index: {e}")
            
            try:
                if 'auto_fetched' not in existing_columns:
                    db.session.execute(text(f"""
                        CREATE INDEX IF NOT EXISTS idx_opportunities_auto_fetched 
                        ON {index_prefix}opportunities(auto_fetched)
                    """))
            except Exception as e:
                print(f"Warning: Could not create auto_fetched index: {e}")
            
            try:
                # Create composite index
                db.session.execute(text(f"""
                    CREATE INDEX IF NOT EXISTS idx_opportunities_source_lookup 
                    ON {index_prefix}opportunities(source, source_id)
                """))
            except Exception as e:
                print(f"Warning: Could not create composite index: {e}")
            
            db.session.commit()
            print("Opportunity source columns added successfully")
            return True
        else:
            print("Opportunity source columns already exist")
            return False
    except Exception as e:
        print(f"Error checking/adding opportunity source columns: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return False

@app.before_request
def ensure_db_initialized():
    """
    Ensure database is initialized, but only check once per serverless instance.
    
    This is a safety net - if tables don't exist, it will create them.
    However, if you've run the database/01_complete_schema.sql file,
    tables will already exist and this will just verify.
    """
    global _db_initialized
    is_vercel = os.environ.get('VERCEL') is not None
    
    # Always check on Vercel, but only once per function instance
    if is_vercel and not _db_initialized:
        try:
            # Test database connection first with timeout handling
            from sqlalchemy.exc import TimeoutError, OperationalError
            try:
                db.session.execute(text('SELECT 1'))
            except (TimeoutError, OperationalError) as conn_err:
                # If connection pool is exhausted, skip initialization for this request
                # It will be retried on the next request
                error_msg = str(conn_err)
                if 'QueuePool' in error_msg or 'connection' in error_msg.lower() or 'timeout' in error_msg.lower():
                    print(f"Database connection unavailable during initialization (will retry): {conn_err}")
                    return  # Don't fail the request, just skip initialization
                raise  # Re-raise other operational errors
            
            # Check if tables exist
            if not tables_exist():
                print("Tables don't exist in serverless. Creating them...")
                db.create_all()
                db.session.commit()
                print("Database tables created in serverless environment")
            else:
                print("Database tables already exist (verified)")
            
            # Check and add is_admin column if missing
            check_and_add_is_admin_column()
            
            # Check and add user profile columns if missing
            check_and_add_user_profile_columns()
            
            # Check and add opportunity source columns if missing
            check_and_add_opportunity_source_columns()
            
            _db_initialized = True
        except Exception as e:
            print(f"Database initialization error: {e}")
            import traceback
            traceback.print_exc()
            # Don't fail the request if initialization fails - just log it
            # Don't set _db_initialized to True on error, so we can retry
            # But don't fail the request - let individual endpoints handle errors

@app.route('/api/test', methods=['GET'])
def test():
    """Test endpoint - only available in development"""
    # Only allow in development (not on Vercel)
    if os.environ.get('VERCEL'):
        return jsonify({'error': 'Not found'}), 404
    
    return jsonify({
        'message': 'API is working!',
        'status': 'success'
    })

@app.route('/api/test/admin-fetch', methods=['POST'])
def test_admin_fetch():
    """Test endpoint - only available in development"""
    # Only allow in development (not on Vercel)
    if os.environ.get('VERCEL'):
        return jsonify({'error': 'Not found'}), 404
    
    try:
        fetch_all_opportunities, _ = get_fetch_functions()
        with app.app_context():
            results = fetch_all_opportunities()
        
        return jsonify({
            'message': 'Test fetch completed',
            'results': results
        })
    except Exception as e:
        print(f"ERROR in test_admin_fetch: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/test/register', methods=['POST'])
def test_register():
    """Test endpoint - only available in development"""
    # Only allow in development (not on Vercel)
    if os.environ.get('VERCEL'):
        return jsonify({'error': 'Not found'}), 404
    
    try:
        data = request.get_json() or {}
        return jsonify({
            'message': 'Test endpoint reached',
            'received_data': data
        }), 200
    except Exception as e:
        print(f"Error in test endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    try:
        # Test database connection
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
        # Ensure database connection
        db.session.execute(text('SELECT 1'))
        
        # Check and add source columns if missing (migration)
        try:
            check_and_add_opportunity_source_columns()
        except Exception as migration_error:
            print(f"Source columns migration check failed (non-critical): {migration_error}")
        
        # Read from database - use active_query to filter out deleted opportunities
        query = Opportunity.active_query()
        
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
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        per_page = min(per_page, 100)  # Limit max per_page to 100
        
        pagination = query.order_by(Opportunity.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'opportunities': [opp.to_dict() for opp in pagination.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
    except Exception as e:
        print(f"Error in opportunities endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to load opportunities: {str(e)}'}), 500

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
        # Ensure database connection with timeout
        try:
            db.session.execute(text('SELECT 1'))
        except Exception as conn_err:
            print(f"Database connection error in get_opportunity_types: {conn_err}")
            db.session.rollback()
            # Return empty list instead of error to prevent UI issues
            return jsonify([])
        
        types = db.session.query(Opportunity.type).filter(
            Opportunity.id.in_(
                db.session.query(Opportunity.id).filter(
                    (Opportunity.is_deleted == False) | (Opportunity.is_deleted.is_(None))
                )
            )
        ).distinct().all()
        return jsonify([t[0] for t in types if t[0]])  # Filter out None values
    except Exception as e:
        print(f"Error in get_opportunity_types: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        # Return empty list instead of error to prevent UI issues
        return jsonify([])

@app.route('/api/opportunities/categories', methods=['GET'])
def get_opportunity_categories():
    """Get all unique opportunity categories"""
    try:
        # Ensure database connection with timeout
        try:
            db.session.execute(text('SELECT 1'))
        except Exception as conn_err:
            print(f"Database connection error in get_opportunity_categories: {conn_err}")
            db.session.rollback()
            # Return empty list instead of error to prevent UI issues
            return jsonify([])
        
        categories = db.session.query(Opportunity.category).filter(
            Opportunity.id.in_(
                db.session.query(Opportunity.id).filter(
                    (Opportunity.is_deleted == False) | (Opportunity.is_deleted.is_(None))
                )
            )
        ).distinct().all()
        return jsonify([c[0] for c in categories if c[0]])  # Filter out None values
    except Exception as e:
        print(f"Error in get_opportunity_categories: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        # Return empty list instead of error to prevent UI issues
        return jsonify([])

@app.route('/api/auth/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """Register a new user. Only WVSU emails (@wvstateu.edu) are allowed."""
    try:
        # Ensure database connection
        try:
            db.session.execute(text('SELECT 1'))
        except Exception as conn_error:
            print(f"Database connection error: {conn_error}")
            return jsonify({'error': 'Database connection failed. Please try again later.'}), 500

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
        
        # Validate password strength
        is_valid, password_error = validate_password(password)
        if not is_valid:
            return jsonify({'error': password_error}), 400

        # Check and add is_admin column if missing (migration)
        try:
            check_and_add_is_admin_column()
        except Exception as migration_error:
            print(f"Migration check failed (non-critical): {migration_error}")

        # Check and add user profile columns if missing (migration)
        try:
            check_and_add_user_profile_columns()
        except Exception as migration_error:
            print(f"Profile columns migration check failed (non-critical): {migration_error}")

        # Uniqueness check
        try:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return jsonify({'error': 'Email already registered'}), 409
        except Exception as query_error:
            # Check if it's the is_admin column error
            error_str = str(query_error)
            if 'is_admin' in error_str and 'does not exist' in error_str:
                print("is_admin column missing. Attempting migration...")
                try:
                    check_and_add_is_admin_column()
                    # Retry the query
                    existing_user = User.query.filter_by(email=email).first()
                    if existing_user:
                        return jsonify({'error': 'Email already registered'}), 409
                except Exception as retry_error:
                    print(f"Migration failed: {retry_error}")
                    import traceback
                    traceback.print_exc()
                    return jsonify({'error': 'Database migration required. Please contact support or run database/04_add_admin_column.sql manually.'}), 500
            else:
                print(f"Error checking existing user: {query_error}")
                import traceback
                traceback.print_exc()
                db.session.rollback()
                return jsonify({'error': f'Database query error: {str(query_error)}'}), 500

        # Create user
        try:
            user = User(email=email, first_name=first_name, last_name=last_name)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
        except Exception as db_error:
            db.session.rollback()
            print(f"Database error during registration: {db_error}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Database error: {str(db_error)}'}), 500

        # Create session
        try:
            from flask import session
            session['user_id'] = user.id
            session['email'] = user.email
        except Exception as session_error:
            print(f"Session error (non-critical): {session_error}")
            # Session error is not critical, continue with registration

        return jsonify({
            'message': 'Registration successful', 
            'user': user.to_dict()
        }), 201
    except Exception as e:
        print(f"Unexpected error in register: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Authenticate existing user. Only WVSU emails allowed. No mock users."""
    try:
        # Ensure database connection with retry logic
        connection_attempts = 0
        max_attempts = 3
        conn_error = None
        
        while connection_attempts < max_attempts:
            try:
                db.session.execute(text('SELECT 1'))
                break  # Connection successful
            except Exception as e:
                connection_attempts += 1
                conn_error = e
                error_msg = str(e)
                
                # Check if it's a pool exhaustion error
                if 'MaxClientsInSessionMode' in error_msg or 'max clients' in error_msg.lower():
                    if connection_attempts < max_attempts:
                        print(f"Connection pool exhausted, retrying ({connection_attempts}/{max_attempts})...")
                        import time
                        time.sleep(1)  # Wait 1 second before retry
                        continue
                
                # For other errors, don't retry
                break
        
        # If all retries failed, return error
        if connection_attempts >= max_attempts:
            error_msg = str(conn_error)
            print(f"Database connection error after {max_attempts} attempts: {error_msg}")
            import traceback
            traceback.print_exc()
            
            # Check if DATABASE_URL is set
            has_db_url = bool(os.environ.get('DATABASE_URL'))
            
            # Return more helpful error message
            if not has_db_url:
                return jsonify({
                    'error': 'Database connection failed: DATABASE_URL environment variable is not set. Please configure it in Vercel.',
                    'debug': {
                        'has_database_url': False,
                        'is_vercel': os.environ.get('VERCEL') is not None
                    }
                }), 500
            else:
                # Check if it's a pool exhaustion error
                if 'MaxClientsInSessionMode' in error_msg or 'max clients' in error_msg.lower():
                    return jsonify({
                        'error': 'Database connection pool exhausted. Please try again in a few moments.',
                        'debug': {
                            'has_database_url': True,
                            'is_vercel': os.environ.get('VERCEL') is not None,
                            'error_type': 'PoolExhaustion',
                            'retries': max_attempts
                        }
                    }), 503  # Service Unavailable
                else:
                    # Don't expose full connection string, but show if it's configured
                    return jsonify({
                        'error': 'Database connection failed. Please check your DATABASE_URL configuration.',
                        'debug': {
                            'has_database_url': True,
                            'is_vercel': os.environ.get('VERCEL') is not None,
                            'error_type': type(conn_error).__name__,
                            'error_preview': error_msg[:100] if len(error_msg) > 100 else error_msg
                        }
                    }), 500

        data = request.get_json() or {}
        email = (data.get('email') or '').strip().lower()
        password = data.get('password') or ''

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Check and add missing columns (migration)
        try:
            check_and_add_is_admin_column()
            check_and_add_user_profile_columns()
            check_and_add_opportunity_source_columns()
        except Exception as migration_error:
            print(f"Migration check failed (non-critical): {migration_error}")

        try:
            # Try case-insensitive email lookup for PostgreSQL
            is_postgres = 'postgresql' in str(db.engine.url) or 'postgres' in str(db.engine.url)
            if is_postgres:
                # PostgreSQL: use ILIKE for case-insensitive search
                user = User.query.filter(User.email.ilike(email)).first()
            else:
                # SQLite: email is already lowercased, so direct match
                user = User.query.filter_by(email=email).first()
        except Exception as query_error:
            # Check if it's a missing column error
            error_str = str(query_error)
            if ('is_admin' in error_str or 'resume_summary' in error_str or 'skills' in error_str or 'career_goals' in error_str) and 'does not exist' in error_str:
                print("Missing column detected. Attempting migration...")
                try:
                    check_and_add_is_admin_column()
                    check_and_add_user_profile_columns()
                    # Retry the query
                    user = User.query.filter_by(email=email).first()
                except Exception as retry_error:
                    print(f"Migration failed: {retry_error}")
                    import traceback
                    traceback.print_exc()
                    return jsonify({'error': 'Database migration required. Please contact support.'}), 500
            else:
                print(f"Error querying user: {query_error}")
                import traceback
                traceback.print_exc()
                db.session.rollback()
                return jsonify({'error': f'Database query error: {str(query_error)}'}), 500

        if not user:
            # User doesn't exist - enforce WVSU email requirement
            if not is_wvsu_email(email):
                return jsonify({'error': 'Only WVSU email addresses (@wvstateu.edu) are allowed'}), 400
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # User exists - allow admin users regardless of email domain
        # For non-admin users, enforce WVSU email requirement
        # Ensure is_admin is properly converted to boolean (handle NULL from PostgreSQL)
        user_is_admin = bool(user.is_admin) if user.is_admin is not None else False
        if not user_is_admin and not is_wvsu_email(email):
            return jsonify({'error': 'Only WVSU email addresses (@wvstateu.edu) are allowed'}), 400

        try:
            password_check_result = user.check_password(password)
            if not password_check_result:
                return jsonify({'error': 'Invalid credentials'}), 401
        except Exception as password_error:
            print(f"Error checking password: {password_error}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': 'Authentication error'}), 500

        # Create session
        try:
            from flask import session
            session['user_id'] = user.id
            session['email'] = user.email
        except Exception as session_error:
            print(f"Session error (non-critical): {session_error}")
            # Session error is not critical, continue with login

        return jsonify({
            'message': 'Login successful', 
            'user': user.to_dict()
        })
    except Exception as e:
        print(f"Unexpected error in login: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

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
def get_current_user_endpoint():
    """Get current logged in user from session or email parameter (for serverless fallback)"""
    try:
        user = get_current_user()
        if user:
            return jsonify({'user': user.to_dict()})
        return jsonify({'error': 'Not authenticated'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Admin endpoints for opportunity management
@app.route('/api/admin/opportunities', methods=['GET'])
@admin_required
def admin_get_opportunities():
    """Get all opportunities for admin (including deleted)"""
    try:
        opportunities = Opportunity.query.order_by(Opportunity.created_at.desc()).all()
        return jsonify([opp.to_dict() for opp in opportunities])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/opportunities', methods=['POST'])
@admin_required
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
@admin_required
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
        
        try:
            db.session.commit()
            return jsonify({
                'message': 'Opportunity updated successfully',
                'opportunity': opportunity.to_dict()
            })
        except Exception as db_error:
            db.session.rollback()
            return jsonify({'error': f'Database error: {str(db_error)}'}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/opportunities/<int:id>', methods=['DELETE'])
@admin_required
def admin_delete_opportunity(id):
    """Delete an opportunity (soft delete)"""
    try:
        opportunity = Opportunity.query.get(id)
        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404
        
        opportunity.is_deleted = True
        try:
            db.session.commit()
            return jsonify({'message': 'Opportunity deleted successfully'})
        except Exception as db_error:
            db.session.rollback()
            return jsonify({'error': f'Database error: {str(db_error)}'}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# CSV sync endpoints removed - using Supabase as primary database

# Additional admin endpoints
@app.route('/api/admin/users', methods=['GET'])
@admin_required
def admin_get_users():
    """Get all users for admin"""
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        return jsonify([user.to_dict() for user in users])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/dashboard', methods=['GET'])
@admin_required
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

@app.route('/api/admin/fetch-opportunities', methods=['POST'])
@admin_required
def admin_fetch_opportunities():
    """Manually trigger opportunity fetch from all sources"""
    try:
        fetch_all_opportunities, _ = get_fetch_functions()
        # Ensure we're in app context for database operations
        try:
            with app.app_context():
                results = fetch_all_opportunities()
        finally:
            # Always cleanup database session to release connections
            try:
                db.session.remove()
            except Exception as cleanup_err:
                print(f"Warning: Failed to cleanup database session: {cleanup_err}")
        
        return jsonify({
            'message': 'Opportunities fetched successfully',
            'results': results
        })
    except Exception as e:
        import traceback
        print(f"ERROR in admin fetch opportunities: {e}")
        traceback.print_exc()
        # Always return JSON, never HTML
        return jsonify({
            'error': f'Failed to fetch opportunities: {str(e)}',
            'error_type': type(e).__name__
        }), 500

@app.route('/api/admin/fetch-logs', methods=['GET'])
@admin_required
def admin_get_fetch_logs():
    """Get fetch operation logs"""
    try:
        limit = int(request.args.get('limit', 50))
        _, get_fetch_logs = get_fetch_functions()
        logs = get_fetch_logs(limit)
        return jsonify({
            'logs': logs,
            'count': len(logs)
        })
    except Exception as e:
        print(f"Error getting fetch logs: {e}")
        return jsonify({'error': f'Failed to get fetch logs: {str(e)}'}), 500

@app.route('/api/admin/fetchers/status', methods=['GET'])
@admin_required
def admin_get_fetcher_status():
    """Get status of all fetchers"""
    try:
        FetcherConfig = get_fetcher_config()
        enabled_fetchers = FetcherConfig.get_enabled_fetchers()
        rss_feeds = FetcherConfig.get_rss_feeds()
        
        status = {
            'enabled_fetchers': enabled_fetchers,
            'rss_feeds': rss_feeds,
            'api_keys_configured': {
                'jooble': bool(FetcherConfig.JOOBLE_API_KEY),
                'authentic_jobs': bool(FetcherConfig.AUTHENTIC_JOBS_API_KEY),
                'meetup': bool(FetcherConfig.MEETUP_API_KEY)
            },
            'fetch_interval_hours': FetcherConfig.FETCH_INTERVAL_HOURS
        }
        
        return jsonify(status)
    except Exception as e:
        print(f"Error getting fetcher status: {e}")
        return jsonify({'error': f'Failed to get fetcher status: {str(e)}'}), 500

@app.route('/api/cron/fetch-opportunities', methods=['GET', 'POST'])
def cron_fetch_opportunities():
    """
    Cron endpoint for scheduled opportunity fetching.
    Can be called by Vercel Cron or external cron service.
    """
    try:
        # Optional: Add authentication for cron endpoint
        # For Vercel Cron, you can use a secret header
        cron_secret = os.environ.get('CRON_SECRET')
        if cron_secret:
            provided_secret = request.headers.get('X-Cron-Secret') or request.args.get('secret')
            if provided_secret != cron_secret:
                return jsonify({'error': 'Unauthorized'}), 401
        
        print("Cron job triggered: Fetching opportunities...")
        fetch_all_opportunities, _ = get_fetch_functions()
        # Ensure we're in app context for database operations
        with app.app_context():
            results = fetch_all_opportunities()
        return jsonify({
            'message': 'Cron job completed',
            'results': results
        })
    except Exception as e:
        print(f"Error in cron fetch opportunities: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Cron job failed: {str(e)}'}), 500

@app.route('/api/admin/promote', methods=['POST'])
def admin_promote_user():
    """
    Promote a user to admin. 
    Protected by ADMIN_SECRET_KEY environment variable for initial setup.
    After first admin is created, this endpoint should be disabled or further secured.
    """
    try:
        # Check for admin secret key (for initial setup only)
        admin_secret = os.environ.get('ADMIN_SECRET_KEY')
        if not admin_secret:
            return jsonify({'error': 'Admin promotion not configured'}), 403
        
        data = request.get_json() or {}
        secret_key = data.get('secret_key')
        email = (data.get('email') or '').strip().lower()
        
        if not secret_key or secret_key != admin_secret:
            return jsonify({'error': 'Invalid secret key'}), 403
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.is_admin = True
        try:
            db.session.commit()
            return jsonify({
                'message': 'User promoted to admin successfully',
                'user': user.to_dict()
            })
        except Exception as db_error:
            db.session.rollback()
            return jsonify({'error': f'Database error: {str(db_error)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/check-user', methods=['POST'])
def debug_check_user():
    """
    Debug endpoint to check user data in database.
    Only available in development or with DEBUG_TOKEN.
    """
    # Only allow in development or with DEBUG_TOKEN
    if os.environ.get('VERCEL'):
        debug_token = os.environ.get('DEBUG_TOKEN')
        provided_token = request.headers.get('X-Debug-Token') or (request.json.get('debug_token') if request.is_json else None)
        if not debug_token or provided_token != debug_token:
            return jsonify({'error': 'Not found'}), 404
    
    try:
        data = request.get_json() or {}
        email = (data.get('email') or '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        is_postgres = 'postgresql' in str(db.engine.url) or 'postgres' in str(db.engine.url)
        
        # Try case-insensitive lookup for PostgreSQL
        if is_postgres:
            user = User.query.filter(User.email.ilike(email)).first()
        else:
            user = User.query.filter_by(email=email).first()
        
        if not user:
            # Try raw SQL to see if user exists with different casing
            result = db.session.execute(
                text("SELECT email, is_admin FROM users WHERE LOWER(email) = LOWER(:email)"),
                {"email": email}
            )
            raw_user = result.fetchone()
            
            return jsonify({
                'user_found': False,
                'email_queried': email,
                'is_postgres': is_postgres,
                'raw_query_result': {
                    'found': raw_user is not None,
                    'email': raw_user[0] if raw_user else None,
                    'is_admin': raw_user[1] if raw_user else None
                } if raw_user else None,
                'database_url_preview': str(db.engine.url).split('@')[0] + '@...' if '@' in str(db.engine.url) else 'sqlite'
            }), 200
        
        # User found
        user_is_admin = bool(user.is_admin) if user.is_admin is not None else False
        
        return jsonify({
            'user_found': True,
            'email_queried': email,
            'user_email': user.email,
            'user_id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_admin': user_is_admin,
            'is_admin_raw': user.is_admin,
            'is_admin_type': type(user.is_admin).__name__,
            'has_password_hash': bool(user.password_hash),
            'is_postgres': is_postgres,
            'email_match': user.email.lower() == email.lower()
        }), 200
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/setup/admin', methods=['POST'])
def setup_admin_user():
    """
    One-time setup endpoint to create/update admin user.
    Requires SETUP_TOKEN environment variable for security.
    """
    try:
        # Check for setup token (set in Vercel environment variables)
        setup_token = os.environ.get('SETUP_TOKEN')
        provided_token = request.headers.get('X-Setup-Token') or request.json.get('setup_token') if request.is_json else None
        
        if setup_token and provided_token != setup_token:
            return jsonify({'error': 'Invalid setup token'}), 401
        
        data = request.get_json() or {}
        email = (data.get('email') or '').strip().lower()
        password = data.get('password') or ''
        first_name = data.get('first_name') or 'Admin'
        last_name = data.get('last_name') or 'User'
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Update existing user
            user.set_password(password)
            user.is_admin = True
            user.first_name = first_name
            user.last_name = last_name
            db.session.commit()
            return jsonify({
                'message': 'Admin user updated successfully',
                'user': user.to_dict()
            }), 200
        else:
            # Create new admin user
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_admin=True
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return jsonify({
                'message': 'Admin user created successfully',
                'user': user.to_dict()
            }), 201
            
    except Exception as e:
        db.session.rollback()
        print(f"Error setting up admin user: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to setup admin user: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
