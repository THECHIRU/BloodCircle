"""
Update main admin email to chirukola123@gmail.com
"""
from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Check if chirukola123@gmail.com already exists
    existing_gmail = User.query.filter_by(email='chirukola123@gmail.com').first()
    
    # Find admin user(s)
    admin_users = User.query.filter_by(role='admin').all()
    
    if existing_gmail and existing_gmail.role == 'admin':
        print(f"✅ Admin already exists: {existing_gmail.email}")
        existing_gmail.is_verified = True
        existing_gmail.is_active = True
        existing_gmail.is_blocked = False
        db.session.commit()
        
        # Remove other admin users
        for admin in admin_users:
            if admin.id != existing_gmail.id:
                print(f"Removing old admin: {admin.email}")
                db.session.delete(admin)
        db.session.commit()
    elif admin_users:
        for admin in admin_users:
            print(f"Found admin: {admin.email}")
            admin.email = 'chirukola123@gmail.com'
            admin.is_verified = True
            admin.is_active = True
            admin.is_blocked = False
            db.session.commit()
            print(f"✅ Updated admin email to: {admin.email}")
    else:
        # Create new admin if none exists
        print("No admin found, creating new admin user...")
        admin = User(
            email='chirukola123@gmail.com',
            phone='1234567890',  # Placeholder - update if needed
            role='admin',
            is_verified=True,
            is_active=True,
            is_blocked=False
        )
        admin.set_password('Admin@123')  # Default password
        db.session.add(admin)
        db.session.commit()
        print(f"✅ Created new admin: {admin.email}")
        print("📝 Default password: Admin@123 (please change after first login)")
    
    # Remove all sub_admin users
    sub_admins = User.query.filter_by(role='sub_admin').all()
    if sub_admins:
        for sub_admin in sub_admins:
            print(f"Removing sub_admin: {sub_admin.email}")
            db.session.delete(sub_admin)
        db.session.commit()
        print(f"✅ Removed {len(sub_admins)} sub_admin user(s)")
    else:
        print("No sub_admin users found")
    
    print("\n✅ Admin configuration updated successfully!")
    print(f"Admin email: chirukola123@gmail.com")
