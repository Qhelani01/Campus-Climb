#!/usr/bin/env python3
"""
Script to create an admin user or set password if user exists.
Usage: python3 create_admin_user.py <email> <password> <first_name> <last_name>
"""
import sys
import os

# Add api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))
os.chdir(os.path.join(os.path.dirname(__file__), 'api'))

from index import app, db
from werkzeug.security import generate_password_hash
from sqlalchemy import text

def create_or_update_admin_user(email, password, first_name, last_name):
    """Create admin user or update password if exists"""
    with app.app_context():
        email_lower = email.lower().strip()
        password_hash = generate_password_hash(password)
        
        try:
            # Check if user exists
            result = db.session.execute(
                text("SELECT id, email, first_name, last_name, is_admin FROM users WHERE email = :email"),
                {"email": email_lower}
            )
            user_row = result.fetchone()
            
            if user_row:
                user_id, user_email, existing_first, existing_last, is_admin = user_row
                print(f"User already exists: {existing_first} {existing_last} ({user_email})")
                print(f"Current admin status: {bool(is_admin)}")
                
                # Update password and ensure admin status
                db.session.execute(
                    text("""
                        UPDATE users 
                        SET password_hash = :password_hash, 
                            is_admin = 1,
                            first_name = :first_name,
                            last_name = :last_name
                        WHERE email = :email
                    """),
                    {
                        "password_hash": password_hash,
                        "email": email_lower,
                        "first_name": first_name,
                        "last_name": last_name
                    }
                )
                db.session.commit()
                print(f"✓ Updated password and admin status for {email}")
                return True
            else:
                # Create new user
                # Check which columns exist by trying to insert
                try:
                    db.session.execute(
                        text("""
                            INSERT INTO users (email, password_hash, first_name, last_name, is_admin)
                            VALUES (:email, :password_hash, :first_name, :last_name, 1)
                        """),
                        {
                            "email": email_lower,
                            "password_hash": password_hash,
                            "first_name": first_name,
                            "last_name": last_name
                        }
                    )
                    db.session.commit()
                    print(f"✓ Created admin user: {first_name} {last_name} ({email})")
                    return True
                except Exception as insert_error:
                    # If is_admin column doesn't exist, try without it
                    if 'is_admin' in str(insert_error).lower():
                        print("Warning: is_admin column may not exist, trying without it...")
                        db.session.rollback()
                        try:
                            db.session.execute(
                                text("""
                                    INSERT INTO users (email, password_hash, first_name, last_name)
                                    VALUES (:email, :password_hash, :first_name, :last_name)
                                """),
                                {
                                    "email": email_lower,
                                    "password_hash": password_hash,
                                    "first_name": first_name,
                                    "last_name": last_name
                                }
                            )
                            db.session.commit()
                            print(f"✓ Created user: {first_name} {last_name} ({email})")
                            print("Note: is_admin column may need to be added manually")
                            return True
                        except Exception as e2:
                            print(f"Error creating user: {e2}")
                            db.session.rollback()
                            return False
                    else:
                        raise insert_error
                        
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Usage: python3 create_admin_user.py <email> <password> <first_name> <last_name>")
        print("Example: python3 create_admin_user.py qhestoemoyo@gmail.com admin123 Qhelani Moyo")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    first_name = sys.argv[3]
    last_name = sys.argv[4]
    
    success = create_or_update_admin_user(email, password, first_name, last_name)
    sys.exit(0 if success else 1)
