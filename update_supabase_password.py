#!/usr/bin/env python3
"""
Script to update password for a user in Supabase.
Usage: python3 update_supabase_password.py <email> <password>
Requires DATABASE_URL environment variable to be set to your Supabase connection string.
"""
import sys
import os

# Add api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))
os.chdir(os.path.join(os.path.dirname(__file__), 'api'))

from index import app, db, User
from werkzeug.security import generate_password_hash

def update_password(email, password):
    """Update password for a user in Supabase"""
    with app.app_context():
        email_lower = email.lower().strip()
        password_hash = generate_password_hash(password)
        
        try:
            # Check if user exists (case-insensitive for PostgreSQL)
            is_postgres = 'postgresql' in str(db.engine.url) or 'postgres' in str(db.engine.url)
            if is_postgres:
                user = User.query.filter(User.email.ilike(email_lower)).first()
            else:
                user = User.query.filter_by(email=email_lower).first()
            
            if not user:
                print(f"✗ User with email {email} not found in database")
                return False
            
            print(f"✓ User found: {user.first_name} {user.last_name} ({user.email})")
            print(f"  Current is_admin: {user.is_admin}")
            
            # Update password
            user.set_password(password)
            db.session.commit()
            
            print(f"✓ Password updated successfully for {email}")
            print(f"  New password hash (first 50 chars): {user.password_hash[:50]}...")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error updating password: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 update_supabase_password.py <email> <password>")
        print("Example: python3 update_supabase_password.py qhestoemoyo@gmail.com admin123")
        print("\nNote: Requires DATABASE_URL environment variable set to your Supabase connection string")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    
    # Check if DATABASE_URL is set
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("✗ Error: DATABASE_URL environment variable not set")
        print("  Set it to your Supabase connection string:")
        print("  export DATABASE_URL='postgresql://postgres:[PASSWORD]@[HOST]/postgres'")
        sys.exit(1)
    
    print(f"Database: {'PostgreSQL (Supabase)' if 'postgresql' in database_url.lower() or 'postgres' in database_url.lower() else 'SQLite'}")
    print()
    
    success = update_password(email, password)
    sys.exit(0 if success else 1)
