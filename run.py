"""
Application entry point for the Blood Donation Network.
"""
import os
from app import create_app, db
from app.models import User, Donor, Patient, Feedback, OTP

# Get configuration from environment variable, default to production for safety
config_name = os.environ.get('FLASK_ENV', 'production')
app = create_app(config_name)


@app.shell_context_processor
def make_shell_context():
    """
    Make database models available in Flask shell.
    Usage: flask shell
    """
    return {
        'db': db,
        'User': User,
        'Donor': Donor,
        'Patient': Patient,
        'Feedback': Feedback,
        'OTP': OTP
    }


@app.cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()
    print("Database initialized successfully!")


@app.cli.command()
def drop_db():
    """Drop all database tables."""
    if input("Are you sure you want to drop all tables? (yes/no): ").lower() == 'yes':
        db.drop_all()
        print("Database tables dropped successfully!")
    else:
        print("Operation cancelled.")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
