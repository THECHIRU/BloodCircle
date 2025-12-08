"""
Flask application initialization and configuration.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from config import config

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()
csrf = CSRFProtect()


def create_app(config_name='default'):
    """
    Application factory pattern for creating Flask app instances.
    
    Args:
        config_name (str): Configuration name (development, production, testing)
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Configure Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Import and register blueprints
    from app.auth import auth_bp
    from app.donor import donor_bp
    from app.patient import patient_bp
    from app.admin import admin_bp
    from app.main import main_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(donor_bp, url_prefix='/donor')
    app.register_blueprint(patient_bp, url_prefix='/patient')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register template filters
    register_template_filters(app)
    
    # Initialize database tables on startup (tables only, admin is created in build script)
    with app.app_context():
        try:
            db.create_all()
            print("Database tables initialized successfully")
        except Exception as e:
            print(f"Note: Database initialization during startup: {e}")
    
    return app


def register_error_handlers(app):
    """Register custom error handlers."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        from flask import render_template
        return render_template('errors/403.html'), 403


def register_template_filters(app):
    """Register custom Jinja2 template filters."""
    
    @app.template_filter('datetime')
    def format_datetime(value, format='%B %d, %Y %I:%M %p'):
        """Format datetime object for display."""
        if value is None:
            return ""
        return value.strftime(format)
    
    @app.template_filter('date')
    def format_date(value, format='%B %d, %Y'):
        """Format date object for display."""
        if value is None:
            return ""
        return value.strftime(format)


# Import models to ensure they are registered with SQLAlchemy
from app import models
