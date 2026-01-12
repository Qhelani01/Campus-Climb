#!/usr/bin/env python3
"""
Test script to verify admin login works
"""
import sys
import os
import requests

# Add api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))
os.chdir(os.path.join(os.path.dirname(__file__), 'api'))

from index import app, db, User

def test_login():
    """Test login functionality"""
    with app.app_context():
        email = 'qhestoemoyo@gmail.com'
        password = 'admin123'
        
        print("Testing login for:", email)
        print("-" * 50)
        
        # Check user exists
        try:
            user = User.query.filter_by(email=email.lower().strip()).first()
            if not user:
                print("✗ User not found in database")
                return False
            
            print(f"✓ User found: {user.first_name} {user.last_name}")
            print(f"✓ Email: {user.email}")
            print(f"✓ Is Admin: {user.is_admin}")
            
            # Check password
            if user.check_password(password):
                print(f"✓ Password check passed")
                print("\n✓ All checks passed! Login should work.")
                print("\nIf login still fails, try:")
                print("1. Restart your Flask app server")
                print("2. Clear browser cache/cookies")
                print("3. Check browser console for errors")
                return True
            else:
                print(f"✗ Password check failed")
                print("  The password 'admin123' does not match the stored hash")
                return False
                
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_login()
    sys.exit(0 if success else 1)
