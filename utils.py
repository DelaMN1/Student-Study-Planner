import os
from functools import wraps
from flask import session, redirect, url_for, flash
from config import Config

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def login_required(f):
    """Decorator to require user login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def ensure_upload_folder():
    """Ensure the upload folder exists"""
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True) 