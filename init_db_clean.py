"""
Database initialization script.
Creates all database tables and sets up the initial schema.
Fresh start - no old constraints.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app import create_app, db
from app.models import User, Donor, Patient, Feedback, OTP

def init_database():
    """Initialize the database with all tables."""
    print("=" * 70)
    print("Initializing database (CLEAN START)...")
    print("=" * 70)
    
    # Create Flask app
    app = create_app('production')
    
    with app.app_context():
        try:
            # Create all tables with correct schema
            print("\nCreating database tables...")
            db.create_all()
            
            print("\n✓ Database tables created:")
            print("  - users (phone: nullable, NO unique constraint)")
            print("  - donors")
            print("  - patients")
            print("  - feedback")
            print("  - otps")
            
            # Create default admin if it doesn't exist
            admin_email = 'chiranjeevi.kola@zohomail.in'
            existing_admin = User.query.filter_by(email=admin_email).first()
            
            if not existing_admin:
                print("\nCreating default admin account...")
                admin = User(
                    email=admin_email,
                    phone=None,  # No phone
                    role='admin',
                    is_verified=True,
                    is_active=True
                )
                admin.set_password('g0abdkbxa6')
                db.session.add(admin)
                db.session.commit()
                print(f"✓ Admin created: {admin_email}")
                print(f"  Password: g0abdkbxa6")
            else:
                print(f"\n✓ Admin already exists: {admin_email}")
            
            print("\n" + "=" * 70)
            print("✓ Database initialization completed successfully!")
            print("=" * 70)
            
        except Exception as e:
            print(f"\n✗ Error initializing database: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    init_database()
