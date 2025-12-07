"""
Migration script to add deleted_at column to users table
"""
from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Check if column already exists
        result = db.session.execute(text("SHOW COLUMNS FROM users LIKE 'deleted_at'"))
        if result.fetchone():
            print("Column 'deleted_at' already exists in users table")
        else:
            # Add the deleted_at column
            db.session.execute(text("ALTER TABLE users ADD COLUMN deleted_at DATETIME NULL AFTER is_active"))
            db.session.commit()
            print("Successfully added 'deleted_at' column to users table")
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
