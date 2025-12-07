"""
Quick admin creation script with predefined credentials.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User

app = create_app('development')

with app.app_context():
    # Check if admin exists
    existing_admin = User.query.filter_by(email='chirukola123@gmail.com').first()
    if existing_admin:
        # Update password for existing admin
        existing_admin.set_password('g0abdkbxa6')
        db.session.commit()
        print("Admin password updated!")
        print(f"Email: chirukola123@gmail.com")
        print(f"Password: g0abdkbxa6")
    else:
        # Create admin
        admin_user = User(
            email='chirukola123@gmail.com',
            phone='+9876543210',
            role='admin',
            is_verified=True,
            is_active=True
        )
        admin_user.set_password('g0abdkbxa6')
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("✓ Admin created successfully!")
        print("\nLogin credentials:")
        print("Email: chirukola123@gmail.com")
        print("Password: g0abdkbxa6")
        print("\nLogin at: http://localhost:5000/auth/login")
