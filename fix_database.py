"""
Fix database schema issues - remove unique constraint from phone column
"""
from app import create_app, db
from sqlalchemy import text, inspect

app = create_app('production')

with app.app_context():
    try:
        print("=" * 50)
        print("Starting database schema migration...")
        print("=" * 50)
        
        # Get inspector to check current state
        inspector = inspect(db.engine)
        
        # Check if users table exists
        if 'users' not in inspector.get_table_names():
            print("⚠️  Users table doesn't exist yet, skipping migration")
        else:
            print("✓ Users table found, applying fixes...")
            
            with db.engine.begin() as conn:
                # Step 1: Drop unique constraint from phone column
                try:
                    result = conn.execute(text("""
                        SELECT constraint_name 
                        FROM information_schema.table_constraints 
                        WHERE table_name='users' AND constraint_type='UNIQUE' 
                        AND constraint_name LIKE '%phone%'
                    """))
                    constraints = result.fetchall()
                    for constraint in constraints:
                        constraint_name = constraint[0]
                        conn.execute(text(f'ALTER TABLE users DROP CONSTRAINT IF EXISTS {constraint_name} CASCADE'))
                        print(f"✓ Dropped constraint: {constraint_name}")
                    
                    # Also try common constraint names
                    conn.execute(text('ALTER TABLE users DROP CONSTRAINT IF EXISTS users_phone_key CASCADE'))
                    print("✓ Removed phone unique constraint")
                except Exception as e:
                    print(f"⚠️  Constraint removal: {e}")
                
                # Step 2: Make phone column nullable
                try:
                    conn.execute(text('ALTER TABLE users ALTER COLUMN phone DROP NOT NULL'))
                    print("✓ Phone column is now nullable")
                except Exception as e:
                    print(f"⚠️  Nullable change: {e}")
                
                # Step 3: Drop unique index from phone if it exists
                try:
                    # Get all indexes on users table
                    result = conn.execute(text("""
                        SELECT indexname 
                        FROM pg_indexes 
                        WHERE tablename='users' AND indexname LIKE '%phone%'
                    """))
                    indexes = result.fetchall()
                    for index in indexes:
                        index_name = index[0]
                        # Don't drop the regular index, only if it's unique
                        if 'key' in index_name.lower() or 'unique' in index_name.lower():
                            conn.execute(text(f'DROP INDEX IF EXISTS {index_name} CASCADE'))
                            print(f"✓ Dropped unique index: {index_name}")
                    
                    # Recreate as non-unique index
                    conn.execute(text('CREATE INDEX IF NOT EXISTS ix_users_phone ON users(phone) WHERE phone IS NOT NULL'))
                    print("✓ Created non-unique index on phone (for non-null values)")
                except Exception as e:
                    print(f"⚠️  Index handling: {e}")
        
        print("=" * 50)
        print("✓ Database schema migration completed!")
        print("=" * 50)
        
    except Exception as e:
        print("=" * 50)
        print(f"✗ Migration Error: {e}")
        print("=" * 50)
        import traceback
        traceback.print_exc()
        
    except Exception as e:
        print(f"✗ Error: {e}")
