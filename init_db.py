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
from sqlalchemy import text, inspect

def init_database():
    """Initialize the database with all tables."""
    print("=" * 70)
    print("Initializing database...")
    print("=" * 70)
    
    # Create Flask app
    app = create_app('production')
    
    with app.app_context():
        try:
            # CRITICAL FIX: Make phone column nullable
            inspector = inspect(db.engine)
            
            if 'users' in inspector.get_table_names():
                print("\n⚠️  Users table exists, checking schema...")
                
                with db.engine.begin() as conn:
                    # Get current phone column info
                    columns = inspector.get_columns('users')
                    phone_col = next((col for col in columns if col['name'] == 'phone'), None)
                    
                    if phone_col:
                        print(f"   Phone column: nullable={phone_col['nullable']}")
                        
                        if not phone_col['nullable']:
                            print("   ⚠️  Phone is NOT nullable! Fixing...")
                            
                            # Drop all constraints on phone first
                            try:
                                result = conn.execute(text("""
                                    SELECT constraint_name 
                                    FROM information_schema.table_constraints 
                                    WHERE table_name='users' 
                                    AND constraint_name LIKE '%phone%'
                                """))
                                for (constraint,) in result.fetchall():
                                    try:
                                        conn.execute(text(f'ALTER TABLE users DROP CONSTRAINT "{constraint}" CASCADE'))
                                        print(f"     ✓ Dropped constraint: {constraint}")
                                    except:
                                        pass
                            except:
                                pass
                            
                            # Drop all indexes on phone
                            try:
                                result = conn.execute(text("""
                                    SELECT indexname 
                                    FROM pg_indexes 
                                    WHERE tablename='users' AND indexname LIKE '%phone%'
                                """))
                                for (idx,) in result.fetchall():
                                    try:
                                        conn.execute(text(f'DROP INDEX IF EXISTS "{idx}" CASCADE'))
                                        print(f"     ✓ Dropped index: {idx}")
                                    except:
                                        pass
                            except:
                                pass
                            
                            # NOW make it nullable
                            try:
                                # First set to nullable
                                conn.execute(text('ALTER TABLE users ALTER COLUMN phone DROP NOT NULL'))
                                print("     ✓ Made phone column nullable")
                            except Exception as e:
                                print(f"     ⚠️  Error making nullable: {e}")
                    else:
                        print("   Phone column not found in users table")
            
            # Create or update all tables
            print("\nCreating/updating database tables...")
            db.create_all()
            
            print("\n✓ Database tables ensured:")
            print("  - users (phone: nullable, no unique)")
            print("  - donors")
            print("  - patients")
            print("  - feedback")
            print("  - otps")
            print("\nExisting data is preserved!")
            
            # Create default admin if it doesn't exist
            admin_email = 'chiranjeevi.kola@zohomail.in'
            existing_admin = User.query.filter_by(email=admin_email).first()
            
            if not existing_admin:
                print("\nCreating default admin account...")
                admin = User(
                    email=admin_email,
                    phone=None,  # No phone for admin
                    role='admin',
                    is_verified=True,
                    is_active=True
                )
                admin.set_password('g0abdkbxa6')
                db.session.add(admin)
                db.session.commit()
                print(f"✓ Admin created: {admin_email}")
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
