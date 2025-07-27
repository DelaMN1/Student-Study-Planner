from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid
import os
from models import db, User, Task
from utils import login_required, allowed_file
from config import Config

main = Blueprint('main', __name__)

@main.route('/dashboard')
@login_required
def dashboard():
    user = db.session.get(User, session['user_id'])
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('auth.logout'))
    tasks = Task.query.filter_by(user_id=user.id).order_by(Task.created_at.desc()).all()
    return render_template('dashboard.html', tasks=tasks, user=user)

@main.route('/task/create', methods=['GET', 'POST'])
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
                file_path = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
                file.save(file_path)
                task.file_path = unique_filename
        
        db.session.add(task)
        db.session.commit()
        
        flash('Task created successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('create_task.html')

@main.route('/task/<int:task_id>')
@login_required
def view_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        flash('Task not found!', 'error')
        return redirect(url_for('main.dashboard'))
    if task.user_id != session['user_id']:
        flash('Access denied!', 'error')
        return redirect(url_for('main.dashboard'))
    return render_template('view_task.html', task=task)

@main.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        flash('Task not found!', 'error')
        return redirect(url_for('main.dashboard'))
    if task.user_id != session['user_id']:
        flash('Access denied!', 'error')
        return redirect(url_for('main.dashboard'))
    
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
                    old_file_path = os.path.join(Config.UPLOAD_FOLDER, task.file_path)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                file_path = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
                file.save(file_path)
                task.file_path = unique_filename
        
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('edit_task.html', task=task)

@main.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        flash('Task not found!', 'error')
        return redirect(url_for('main.dashboard'))
    if task.user_id != session['user_id']:
        flash('Access denied!', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Delete associated file if exists
    if task.file_path:
        file_path = os.path.join(Config.UPLOAD_FOLDER, task.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)

@main.route('/task/<int:task_id>/toggle_status', methods=['POST'])
@login_required
def toggle_task_status(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        flash('Task not found!', 'error')
        return redirect(url_for('main.dashboard'))
    if task.user_id != session['user_id']:
        flash('Access denied!', 'error')
        return redirect(url_for('main.dashboard'))
    
    if task.status == 'pending':
        task.status = 'in_progress'
    elif task.status == 'in_progress':
        task.status = 'completed'
    else:
        task.status = 'pending'
    
    db.session.commit()
    flash('Task status updated!', 'success')
    return redirect(url_for('main.dashboard')) 