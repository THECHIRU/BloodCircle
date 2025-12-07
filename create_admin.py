"""
Admin user creation script.
Creates the first admin user for the Blood Donation Network application.
"""
import sys
import os
import getpass

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User


def create_admin():
    """Create an admin user interactively."""
    print("=" * 60)
    print("Blood Donation Network - Admin User Creation")
    print("=" * 60)
    print()
    
    # Create Flask app
    app = create_app('development')
    
    with app.app_context():
        # Check if admin already exists
        existing_admin = User.query.filter_by(role='admin').first()
        if existing_admin:
            print("⚠ Warning: An admin user already exists!")
            print(f"Email: {existing_admin.email}")
            response = input("\nDo you want to create another admin user? (yes/no): ")
            if response.lower() != 'yes':
                print("Operation cancelled.")
                sys.exit(0)
        
        # Collect admin details
        print("\nEnter admin details:")
        print("-" * 60)
        
        while True:
            email = input("Email address: ").strip().lower()
            if not email:
                print("✗ Email is required!")
                continue
            if '@' not in email:
                print("✗ Invalid email format!")
                continue
            
            # Check if email already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                print("✗ This email is already registered!")
                continue
            break
        
        while True:
            phone = input("Phone number (with country code, e.g., +1234567890): ").strip()
            if not phone:
                print("✗ Phone number is required!")
                continue
            if len(phone) < 10:
                print("✗ Phone number too short!")
                continue
            
            # Check if phone already exists
            existing_user = User.query.filter(User.phone.like(f'%{phone}%')).first()
            if existing_user:
                print("✗ This phone number is already registered!")
                continue
            break
        
        while True:
            password = getpass.getpass("Password (min 8 characters): ")
            if not password:
                print("✗ Password is required!")
                continue
            if len(password) < 8:
                print("✗ Password must be at least 8 characters!")
                continue
            
            confirm_password = getpass.getpass("Confirm password: ")
            if password != confirm_password:
                print("✗ Passwords do not match!")
                continue
            break
        
        # Create admin user
        try:
            admin_user = User(
                email=email,
                phone=phone,
                role='admin',
                is_verified=True,  # Admin is pre-verified
                is_active=True
            )
            admin_user.set_password(password)
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("\n" + "=" * 60)
            print("✓ Admin user created successfully!")
            print("=" * 60)
            print(f"\nEmail: {email}")
            print(f"Phone: {phone}")
            print(f"Role: Admin")
            print("\nYou can now login at: http://localhost:5000/auth/login")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n✗ Error creating admin user: {str(e)}")
            db.session.rollback()
            sys.exit(1)


def create_sample_data():
    """Create sample donor and patient data for testing."""
    print("\n" + "=" * 60)
    response = input("Do you want to create sample data for testing? (yes/no): ")
    
    if response.lower() != 'yes':
        return
    
    app = create_app('development')
    
    with app.app_context():
        try:
            from app.models import Donor, Patient
            from datetime import datetime, timedelta
            
            print("\nCreating sample data...")
            
            # Create sample donors
            donor_data = [
                {
                    'email': 'donor1@example.com',
                    'phone': '+1234567801',
                    'password': 'donor123',
                    'full_name': 'John Doe',
                    'blood_group': 'O+',
                    'date_of_birth': datetime(1990, 5, 15).date(),
                    'gender': 'Male',
                    'address': '123 Main St',
                    'city': 'New York',
                    'state': 'NY',
                    'pincode': '10001'
                },
                {
                    'email': 'donor2@example.com',
                    'phone': '+1234567802',
                    'password': 'donor123',
                    'full_name': 'Jane Smith',
                    'blood_group': 'A+',
                    'date_of_birth': datetime(1985, 8, 20).date(),
                    'gender': 'Female',
                    'address': '456 Oak Ave',
                    'city': 'Los Angeles',
                    'state': 'CA',
                    'pincode': '90001'
                }
            ]
            
            for data in donor_data:
                user = User(
                    email=data['email'],
                    phone=data['phone'],
                    role='donor',
                    is_verified=True,
                    is_active=True
                )
                user.set_password(data['password'])
                db.session.add(user)
                db.session.commit()
                
                donor = Donor(
                    user_id=user.id,
                    full_name=data['full_name'],
                    blood_group=data['blood_group'],
                    date_of_birth=data['date_of_birth'],
                    gender=data['gender'],
                    address=data['address'],
                    city=data['city'],
                    state=data['state'],
                    pincode=data['pincode'],
                    is_available=True
                )
                db.session.add(donor)
            
            # Create sample patient
            patient_user = User(
                email='patient1@example.com',
                phone='+1234567803',
                role='patient',
                is_verified=True,
                is_active=True
            )
            patient_user.set_password('patient123')
            db.session.add(patient_user)
            db.session.commit()
            
            patient = Patient(
                user_id=patient_user.id,
                full_name='Bob Johnson',
                blood_group_required='O+',
                hospital_name='City Hospital',
                location='789 Hospital Rd',
                city='New York',
                state='NY',
                urgency_level='Urgent',
                required_by_date=datetime.now().date() + timedelta(days=7)
            )
            db.session.add(patient)
            
            db.session.commit()
            
            print("\n✓ Sample data created successfully!")
            print("\nSample Accounts:")
            print("-" * 60)
            print("Donors:")
            print("  Email: donor1@example.com | Password: donor123")
            print("  Email: donor2@example.com | Password: donor123")
            print("\nPatient:")
            print("  Email: patient1@example.com | Password: patient123")
            print("-" * 60)
            
        except Exception as e:
            print(f"\n✗ Error creating sample data: {str(e)}")
            db.session.rollback()


if __name__ == '__main__':
    create_admin()
    create_sample_data()
