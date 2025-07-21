from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import uuid
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///study_planner.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='user', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed
    file_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    priority = db.Column(db.String(10), default='Medium')  # High, Medium, Low

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return render_template('register.html')
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = request.form.get('remember') == 'on'
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            
            # Set session to permanent if "remember me" is checked
            if remember:
                session.permanent = True
                app.permanent_session_lifetime = timedelta(days=30)  # 30 days
            
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = db.session.get(User, session['user_id'])
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('logout'))
    tasks = Task.query.filter_by(user_id=user.id).order_by(Task.created_at.desc()).all()
    return render_template('dashboard.html', tasks=tasks, user=user)

@app.route('/task/create', methods=['GET', 'POST'])
@login_required
def create_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        due_date_str = request.form['due_date']
        status = request.form['status']
        priority = request.form.get('priority', 'Medium')
        
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format!', 'error')
                return render_template('create_task.html')
        
        task = Task(
            title=title,
            description=description,
            due_date=due_date,
            status=status,
            user_id=session['user_id'],
            priority=priority
        )
        
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add unique identifier to prevent filename conflicts
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                task.file_path = unique_filename
        
        db.session.add(task)
        db.session.commit()
        
        flash('Task created successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('create_task.html')

@app.route('/task/<int:task_id>')
@login_required
def view_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        flash('Task not found!', 'error')
        return redirect(url_for('dashboard'))
    if task.user_id != session['user_id']:
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))
    return render_template('view_task.html', task=task)

@app.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        flash('Task not found!', 'error')
        return redirect(url_for('dashboard'))
    if task.user_id != session['user_id']:
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form['description']
        due_date_str = request.form['due_date']
        task.status = request.form['status']
        task.priority = request.form.get('priority', 'Medium')
        
        if due_date_str:
            try:
                task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format!', 'error')
                return render_template('edit_task.html', task=task)
        else:
            task.due_date = None
        
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename and file.filename != '' and allowed_file(file.filename):
                # Delete old file if exists
                if task.file_path:
                    old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], task.file_path)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                task.file_path = unique_filename
        
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_task.html', task=task)

@app.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        flash('Task not found!', 'error')
        return redirect(url_for('dashboard'))
    if task.user_id != session['user_id']:
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))
    
    # Delete associated file if exists
    if task.file_path:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], task.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/task/<int:task_id>/toggle_status', methods=['POST'])
@login_required
def toggle_task_status(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        flash('Task not found!', 'error')
        return redirect(url_for('dashboard'))
    if task.user_id != session['user_id']:
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))
    
    if task.status == 'pending':
        task.status = 'in_progress'
    elif task.status == 'in_progress':
        task.status = 'completed'
    else:
        task.status = 'pending'
    
    db.session.commit()
    flash('Task status updated!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/profile')
@login_required
def profile():
    user = db.session.get(User, session['user_id'])
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('logout'))
    return render_template('profile.html', user=user)

@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    user = db.session.get(User, session['user_id'])
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('logout'))
    
    username = request.form['username']
    email = request.form['email']
    
    # Check if username is already taken by another user
    existing_user = User.query.filter_by(username=username).first()
    if existing_user and existing_user.id != user.id:
        flash('Username already exists!', 'error')
        return redirect(url_for('profile'))
    
    # Check if email is already taken by another user
    existing_email = User.query.filter_by(email=email).first()
    if existing_email and existing_email.id != user.id:
        flash('Email already registered!', 'error')
        return redirect(url_for('profile'))
    
    user.username = username
    user.email = email
    db.session.commit()
    
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    user = db.session.get(User, session['user_id'])
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('logout'))
    
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_new_password = request.form['confirm_new_password']
    
    # Verify current password
    if not check_password_hash(user.password_hash, current_password):
        flash('Current password is incorrect!', 'error')
        return redirect(url_for('profile'))
    
    # Check if new passwords match
    if new_password != confirm_new_password:
        flash('New passwords do not match!', 'error')
        return redirect(url_for('profile'))
    
    # Update password
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    
    flash('Password changed successfully!', 'success')
    return redirect(url_for('profile'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5050) 