"""
Database initialization script.
Creates all database tables and sets up the initial schema.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, Donor, Patient, Feedback, OTP

def init_database():
    """Initialize the database with all tables."""
    print("Initializing database...")
    
    # Create Flask app
    app = create_app('development')
    
    with app.app_context():
        try:
            # Drop all existing tables (use with caution!)
            print("Dropping existing tables...")
            db.drop_all()
            
            # Create all tables
            print("Creating new tables...")
            db.create_all()
            
            print("\n✓ Database initialized successfully!")
            print("\nCreated tables:")
            print("  - users")
            print("  - donors")
            print("  - patients")
            print("  - feedback")
            print("  - otps")
            print("\nNext step: Run 'python create_admin.py' to create an admin user")
            
        except Exception as e:
            print(f"\n✗ Error initializing database: {str(e)}")
            sys.exit(1)


if __name__ == '__main__':
    init_database()
