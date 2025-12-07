"""
Migration script to add is_blocked column to users table
"""
from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Check if column already exists
        result = db.session.execute(text("SHOW COLUMNS FROM users LIKE 'is_blocked'"))
        if result.fetchone():
            print("Column 'is_blocked' already exists in users table")
        else:
            # Add the is_blocked column
            db.session.execute(text("ALTER TABLE users ADD COLUMN is_blocked BOOLEAN DEFAULT FALSE AFTER deleted_at"))
            db.session.commit()
            print("Successfully added 'is_blocked' column to users table")
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
