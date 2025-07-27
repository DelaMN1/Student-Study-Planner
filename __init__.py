from flask import Flask
from datetime import timedelta
from models import db
from config import Config
from utils import ensure_upload_folder

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Set session lifetime
    app.permanent_session_lifetime = timedelta(days=30)
    
    # Initialize extensions
    db.init_app(app)
    
    # Ensure upload folder exists
    ensure_upload_folder()
    
    # Register blueprints
    from routes.auth import auth
    from routes.main import main
    from routes.calendar import calendar_bp
    
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(calendar_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app 