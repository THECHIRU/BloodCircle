#!/usr/bin/env python3
"""
Diagnostic script to identify the exact registration issue
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app import create_app, db
from app.models import User
from sqlalchemy import text, inspect

app = create_app('production')

print("=" * 80)
print("DIAGNOSTIC CHECK")
print("=" * 80)

with app.app_context():
    try:
        # 1. Check database connection
        print("\n1. Testing database connection...")
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("   ✓ Database connected")
        
        # 2. Check users table structure
        print("\n2. Checking users table structure...")
        inspector = inspect(db.engine)
        
        if 'users' not in inspector.get_table_names():
            print("   ✗ Users table doesn't exist!")
        else:
            print("   ✓ Users table exists")
            
            # Get columns
            columns = inspector.get_columns('users')
            print("\n   Columns:")
            for col in columns:
                print(f"     - {col['name']}: {col['type']} (nullable={col['nullable']})")
            
            # Get constraints
            print("\n   Constraints:")
            constraints = inspector.get_unique_constraints('users')
            if constraints:
                for constraint in constraints:
                    print(f"     - {constraint}")
            else:
                print("     (none)")
            
            # Get indexes
            print("\n   Indexes:")
            indexes = inspector.get_indexes('users')
            for idx in indexes:
                print(f"     - {idx['name']}: columns={idx['column_names']}, unique={idx['unique']}")
        
        # 3. Try to create a test user
        print("\n3. Testing user creation...")
        test_email = 'test_diagnostic_12345@example.com'
        
        # Check if test user exists
        existing = User.query.filter_by(email=test_email).first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
            print(f"   Deleted existing test user")
        
        # Try to create
        try:
            test_user = User(
                email=test_email,
                phone=None,
                role=None,
                is_verified=True,
                is_active=True
            )
            test_user.set_password('TestPassword123')
            db.session.add(test_user)
            db.session.commit()
            print(f"   ✓ Successfully created test user with phone=None")
            
            # Clean up
            db.session.delete(test_user)
            db.session.commit()
            print(f"   ✓ Cleaned up test user")
            
        except Exception as e:
            print(f"   ✗ Failed to create user: {e}")
            import traceback
            traceback.print_exc()
        
        # 4. Show current users
        print("\n4. Current users in database:")
        users = User.query.all()
        if users:
            for user in users:
                print(f"   - {user.email} (phone={user.phone}, role={user.role})")
        else:
            print("   (no users)")
        
        print("\n" + "=" * 80)
        print("DIAGNOSTIC CHECK COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ Error during diagnostic: {e}")
        import traceback
        traceback.print_exc()
