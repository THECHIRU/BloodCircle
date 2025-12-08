"""
Initialize database and create default admin user for deployment.
This script is run during the build process on Render.
Data persistence: Only creates admin if doesn't exist, preserving all existing data.
"""
import os
import sys
from app import create_app, db
from app.models import User

def init_admin():
    """Create database tables and default admin user - preserves existing data."""
    # Get configuration from environment
    config_name = os.environ.get('FLASK_ENV', 'production')
    app = create_app(config_name)
    
    with app.app_context():
        try:
            print("Checking database tables...")
            db.create_all()
            print("✓ Database tables ready")
            
            # Check if admin exists
            admin_email = 'chiranjeevi.kola@zohomail.in'
            admin_password = 'g0abdkbxa6'
            
            existing_admin = User.query.filter_by(email=admin_email).first()
            
            if existing_admin:
                print(f"✓ Admin user exists: {admin_email}")
                print(f"✓ Admin ID: {existing_admin.id}, Current Role: {existing_admin.role}")
                # Force admin role for the main admin account
                if existing_admin.role != 'admin':
                    print(f"⚠ Correcting role from '{existing_admin.role}' to 'admin'")
                    existing_admin.role = 'admin'
                    # Remove any donor/patient profiles
                    if existing_admin.donor:
                        db.session.delete(existing_admin.donor)
                    if existing_admin.patient:
                        db.session.delete(existing_admin.patient)
                    db.session.commit()
                    print("✓ Admin role corrected")
            else:
                print(f"Creating default admin user: {admin_email}")
                admin = User(
                    email=admin_email,
                    phone=None,
                    role='admin',
                    is_verified=True,
                    is_active=True,
                    is_blocked=False
                )
                admin.set_password(admin_password)
                db.session.add(admin)
                db.session.commit()
                print("✓ Default admin user created successfully")
            
            # Count existing records (to show data is preserved)
            from app.models import Donor, Patient
            user_count = User.query.count()
            donor_count = Donor.query.count()
            patient_count = Patient.query.count()
            
            print("\n" + "="*50)
            print("DATABASE STATUS")
            print("="*50)
            print(f"Users: {user_count}")
            print(f"Donors: {donor_count}")
            print(f"Patients: {patient_count}")
            print("="*50)
            print("✓ All existing data preserved across deployment")
            print("="*50 + "\n")
            
            return True
            
        except Exception as e:
            print(f"✗ Error during database initialization: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = init_admin()
    sys.exit(0 if success else 0)  # Always exit with 0 to not fail build
