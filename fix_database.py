"""
Fix database schema issues - remove unique constraint from phone column
"""
from app import create_app, db
from sqlalchemy import text

app = create_app('production')

with app.app_context():
    try:
        print("Fixing database schema...")
        
        with db.engine.connect() as conn:
            # Drop unique constraint from phone column if it exists
            try:
                conn.execute(text('ALTER TABLE users DROP CONSTRAINT IF EXISTS users_phone_key'))
                conn.commit()
                print("✓ Removed unique constraint from phone column")
            except Exception as e:
                print(f"Note: {e}")
            
            # Make phone column nullable
            try:
                conn.execute(text('ALTER TABLE users ALTER COLUMN phone DROP NOT NULL'))
                conn.commit()
                print("✓ Made phone column nullable")
            except Exception as e:
                print(f"Note: {e}")
        
        print("\n✓ Database schema fixed successfully!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
