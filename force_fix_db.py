#!/usr/bin/env python3
"""
FORCE FIX: Remove all phone-related constraints aggressively
This script will be run before init_db.py to ensure clean state
"""
import os
import sys
from sqlalchemy import create_engine, text

# Get database URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL', '')

if not DATABASE_URL:
    print("⚠️  No DATABASE_URL found, skipping force fix")
    sys.exit(0)

# Fix postgres:// to postgresql:// if needed
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print("=" * 60)
print("FORCE FIXING DATABASE SCHEMA")
print("=" * 60)

try:
    engine = create_engine(DATABASE_URL)
    
    with engine.begin() as conn:
        # Check if users table exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'users'
            )
        """))
        table_exists = result.scalar()
        
        if not table_exists:
            print("⚠️  Users table doesn't exist yet, nothing to fix")
            sys.exit(0)
        
        print("✓ Found users table, applying fixes...")
        
        # 1. Find and drop ALL constraints containing 'phone'
        result = conn.execute(text("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name='users' 
            AND constraint_name LIKE '%phone%'
        """))
        constraints = result.fetchall()
        
        for (constraint_name,) in constraints:
            try:
                conn.execute(text(f'ALTER TABLE users DROP CONSTRAINT IF EXISTS "{constraint_name}" CASCADE'))
                print(f"✓ Dropped constraint: {constraint_name}")
            except Exception as e:
                print(f"⚠️  Could not drop {constraint_name}: {e}")
        
        # 2. Try common constraint names
        for constraint_name in ['users_phone_key', 'users_phone_key1', 'uq_users_phone']:
            try:
                conn.execute(text(f'ALTER TABLE users DROP CONSTRAINT IF EXISTS {constraint_name} CASCADE'))
                print(f"✓ Tried to drop: {constraint_name}")
            except Exception as e:
                pass
        
        # 3. Find and drop ALL indexes containing 'phone'
        result = conn.execute(text("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename='users' 
            AND indexname LIKE '%phone%'
        """))
        indexes = result.fetchall()
        
        for (index_name,) in indexes:
            try:
                conn.execute(text(f'DROP INDEX IF EXISTS "{index_name}" CASCADE'))
                print(f"✓ Dropped index: {index_name}")
            except Exception as e:
                print(f"⚠️  Could not drop {index_name}: {e}")
        
        # 4. Make phone nullable
        try:
            conn.execute(text('ALTER TABLE users ALTER COLUMN phone DROP NOT NULL'))
            print("✓ Made phone column nullable")
        except Exception as e:
            print(f"⚠️  Phone already nullable or error: {e}")
        
        # 5. Verify current state
        result = conn.execute(text("""
            SELECT column_name, is_nullable, data_type
            FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'phone'
        """))
        phone_info = result.fetchone()
        if phone_info:
            print(f"\n✓ Phone column state: nullable={phone_info[1]}, type={phone_info[2]}")
        
        print("\n" + "=" * 60)
        print("✓ FORCE FIX COMPLETED SUCCESSFULLY")
        print("=" * 60)

except Exception as e:
    print("\n" + "=" * 60)
    print(f"✗ ERROR: {e}")
    print("=" * 60)
    import traceback
    traceback.print_exc()
    sys.exit(1)
