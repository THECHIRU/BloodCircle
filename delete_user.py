"""
Delete a user by email.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User

app = create_app('development')

with app.app_context():
    # Find and delete the user
    user = User.query.filter_by(email='admin@blooddonation.com').first()
    if user:
        db.session.delete(user)
        db.session.commit()
        print(f"✓ User deleted successfully: admin@blooddonation.com")
    else:
        print(f"✗ User not found: admin@blooddonation.com")
