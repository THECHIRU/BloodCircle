"""
Migration script to make phone column nullable in User table.
Run this once to update the database schema.
"""
from app import create_app, db
from sqlalchemy import text

app = create_app('production')

with app.app_context():
    try:
        # Make phone column nullable
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE "user" ALTER COLUMN phone DROP NOT NULL'))
            conn.commit()
            print("✓ Successfully made phone column nullable")
    except Exception as e:
        print(f"✗ Error updating schema: {e}")
        print("Note: If column is already nullable, this error can be ignored")
