#!/usr/bin/env python3
"""
Script to check admin user in Supabase database.
Usage: python3 check_supabase_user.py <email>
"""
import sys
import os

# Add api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))
os.chdir(os.path.join(os.path.dirname(__file__), 'api'))

from index import app, db, User
from werkzeug.security import check_password_hash
from sqlalchemy import text

def check_user(email):
    """Check user details in database"""
    with app.app_context():
        email_lower = email.lower().strip()
        
        try:
            # Try using the User model
            user = User.query.filter_by(email=email_lower).first()
            
            if user:
                print(f"✓ User found using User model:")
                print(f"  ID: {user.id}")
                print(f"  Email: {user.email}")
                print(f"  Name: {user.first_name} {user.last_name}")
                print(f"  Is Admin: {user.is_admin} (type: {type(user.is_admin).__name__})")
                print(f"  Has Password Hash: {bool(user.password_hash)}")
                if user.password_hash:
                    print(f"  Password Hash (first 50 chars): {user.password_hash[:50]}...")
                
                # Test password
                test_password = 'admin123'
                pwd_check = user.check_password(test_password)
                print(f"  Password check ('{test_password}'): {pwd_check}")
                
                return True
            else:
                print(f"✗ User not found using User model")
                
                # Try raw SQL query
                print("\nTrying raw SQL query...")
                result = db.session.execute(
                    text("SELECT id, email, first_name, last_name, is_admin, password_hash FROM users WHERE email = :email"),
                    {"email": email_lower}
                )
                row = result.fetchone()
                
                if row:
                    user_id, user_email, first_name, last_name, is_admin, pwd_hash = row
                    print(f"✓ User found using raw SQL:")
                    print(f"  ID: {user_id}")
                    print(f"  Email: {user_email}")
                    print(f"  Name: {first_name} {last_name}")
                    print(f"  Is Admin: {is_admin} (type: {type(is_admin).__name__})")
                    print(f"  Has Password Hash: {bool(pwd_hash)}")
                    if pwd_hash:
                        print(f"  Password Hash (first 50 chars): {pwd_hash[:50]}...")
                    
                    # Test password
                    if pwd_hash:
                        from werkzeug.security import check_password_hash
                        test_password = 'admin123'
                        pwd_check = check_password_hash(pwd_hash, test_password)
                        print(f"  Password check ('{test_password}'): {pwd_check}")
                    
                    return True
                else:
                    print(f"✗ User not found using raw SQL either")
                    print(f"\nChecking all users in database...")
                    all_users = db.session.execute(text("SELECT email, first_name, last_name, is_admin FROM users LIMIT 10"))
                    print("Users in database:")
                    for row in all_users:
                        print(f"  - {row[0]} ({row[1]} {row[2]}) - Admin: {row[3]}")
                    return False
                    
        except Exception as e:
            print(f"✗ Error checking user: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 check_supabase_user.py <email>")
        print("Example: python3 check_supabase_user.py qhestoemoyo@gmail.com")
        sys.exit(1)
    
    email = sys.argv[1]
    
    # Check database URL
    database_url = os.environ.get('DATABASE_URL', app.config.get('SQLALCHEMY_DATABASE_URI', ''))
    print(f"Database URL: {database_url[:50]}..." if len(database_url) > 50 else f"Database URL: {database_url}")
    print(f"Is PostgreSQL: {'postgresql' in database_url.lower() or 'postgres' in database_url.lower()}")
    print()
    
    success = check_user(email)
    sys.exit(0 if success else 1)
