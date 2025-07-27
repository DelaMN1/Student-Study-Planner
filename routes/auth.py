from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from models import db, User
from utils import login_required

auth = Blueprint('auth', __name__)

@auth.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@auth.route('/register', methods=['GET', 'POST'])
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
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
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
                # Note: app.permanent_session_lifetime will be set in the main app
            
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.index'))

@auth.route('/profile')
@login_required
def profile():
    user = db.session.get(User, session['user_id'])
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('auth.logout'))
    return render_template('profile.html', user=user)

@auth.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    user = db.session.get(User, session['user_id'])
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('auth.logout'))
    
    username = request.form['username']
    email = request.form['email']
    
    # Check if username is already taken by another user
    existing_user = User.query.filter_by(username=username).first()
    if existing_user and existing_user.id != user.id:
        flash('Username already exists!', 'error')
        return redirect(url_for('auth.profile'))
    
    # Check if email is already taken by another user
    existing_email = User.query.filter_by(email=email).first()
    if existing_email and existing_email.id != user.id:
        flash('Email already registered!', 'error')
        return redirect(url_for('auth.profile'))
    
    user.username = username
    user.email = email
    db.session.commit()
    
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('auth.profile'))

@auth.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    user = db.session.get(User, session['user_id'])
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('auth.logout'))
    
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_new_password = request.form['confirm_new_password']
    
    # Verify current password
    if not check_password_hash(user.password_hash, current_password):
        flash('Current password is incorrect!', 'error')
        return redirect(url_for('auth.profile'))
    
    # Check if new passwords match
    if new_password != confirm_new_password:
        flash('New passwords do not match!', 'error')
        return redirect(url_for('auth.profile'))
    
    # Update password
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    
    flash('Password changed successfully!', 'success')
    return redirect(url_for('auth.profile')) 