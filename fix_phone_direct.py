#!/usr/bin/env python3
"""
Direct database fix - makes phone column nullable
Run this after setting DATABASE_URL environment variable
"""
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set")
    exit(1)

# Fix postgres:// to postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print("Connecting to database...")
engine = create_engine(DATABASE_URL)

try:
    with engine.begin() as conn:
        print("✓ Connected!")
        
        # Make phone column nullable
        print("\nFixing phone column...")
        conn.execute(text('ALTER TABLE users ALTER COLUMN phone DROP NOT NULL'))
        print("✓ Phone column is now nullable!")
        
        # Verify
        result = conn.execute(text("""
            SELECT is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'phone'
        """))
        is_nullable = result.scalar()
        print(f"\nVerification: phone is_nullable = {is_nullable}")
        
        if is_nullable == 'YES':
            print("✓ SUCCESS! Phone column accepts NULL values now")
        else:
            print("✗ Something went wrong")
            
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
