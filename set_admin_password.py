#!/usr/bin/env python3
"""
Script to set password for an admin user.
Usage: python3 set_admin_password.py <email> <password>
"""
import sys
import os

# Add api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))
os.chdir(os.path.join(os.path.dirname(__file__), 'api'))

from index import app, db
from werkzeug.security import generate_password_hash
from sqlalchemy import text

def set_admin_password(email, password):
    """Set password for a user using raw SQL to avoid model column issues"""
    with app.app_context():
        email_lower = email.lower().strip()
        password_hash = generate_password_hash(password)
        
        # First check if user exists
        try:
            result = db.session.execute(
                text("SELECT id, email, first_name, last_name, is_admin FROM users WHERE email = :email"),
                {"email": email_lower}
            )
            user_row = result.fetchone()
            
            if not user_row:
                print(f"Error: User with email {email} not found in database")
                return False
            
            user_id, user_email, first_name, last_name, is_admin = user_row
            print(f"Found user: {first_name} {last_name} ({user_email})")
            print(f"Is Admin: {bool(is_admin)}")
            
            # Update password
            db.session.execute(
                text("UPDATE users SET password_hash = :password_hash WHERE email = :email"),
                {"password_hash": password_hash, "email": email_lower}
            )
            db.session.commit()
            
            print(f"✓ Password set successfully for {email}")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 set_admin_password.py <email> <password>")
        print("Example: python3 set_admin_password.py qhestoemoyo@gmail.com mypassword123")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    
    success = set_admin_password(email, password)
    sys.exit(0 if success else 1)
