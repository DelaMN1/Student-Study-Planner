from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid
import os
from sqlalchemy import or_
from models import db, User, Task, Category
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
    
    # Get search query
    search_query = request.args.get('search', '')
    
    # Build query
    query = Task.query.filter_by(user_id=user.id)
    
    # Apply search filter if query provided
    if search_query:
        query = query.filter(
            or_(
                Task.title.ilike(f'%{search_query}%'),
                Task.description.ilike(f'%{search_query}%')
            )
        )
    
    # Apply status filter
    status_filter = request.args.get('status', '')
    if status_filter:
        query = query.filter(Task.status == status_filter)
    
    # Apply priority filter
    priority_filter = request.args.get('priority', '')
    if priority_filter:
        query = query.filter(Task.priority == priority_filter)
    
    # Apply category filter
    category_filter = request.args.get('category', '')
    if category_filter:
        query = query.filter(Task.category_id == category_filter)
    
    # Order by creation date
    tasks = query.order_by(Task.created_at.desc()).all()
    
    # Get categories for filter dropdown
    categories = Category.query.filter_by(user_id=user.id).all()
    
    return render_template('dashboard.html', 
                         tasks=tasks, 
                         user=user, 
                         search_query=search_query,
                         status_filter=status_filter,
                         priority_filter=priority_filter,
                         category_filter=category_filter,
                         categories=categories)

@main.route('/search')
@login_required
def search_tasks():
    user = db.session.get(User, session['user_id'])
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('auth.logout'))
    
    query = request.args.get('q', '')
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    category_filter = request.args.get('category', '')
    
    # Build query
    task_query = Task.query.filter_by(user_id=user.id)
    
    # Apply search filter
    if query:
        task_query = task_query.filter(
            or_(
                Task.title.ilike(f'%{query}%'),
                Task.description.ilike(f'%{query}%')
            )
        )
    
    # Apply filters
    if status_filter:
        task_query = task_query.filter(Task.status == status_filter)
    
    if priority_filter:
        task_query = task_query.filter(Task.priority == priority_filter)
    
    if category_filter:
        task_query = task_query.filter(Task.category_id == category_filter)
    
    tasks = task_query.order_by(Task.created_at.desc()).all()
    categories = Category.query.filter_by(user_id=user.id).all()
    
    return render_template('search_results.html', 
                         tasks=tasks, 
                         query=query,
                         status_filter=status_filter,
                         priority_filter=priority_filter,
                         category_filter=category_filter,
                         categories=categories,
                         user=user)

@main.route('/task/create', methods=['GET', 'POST'])
@login_required
def create_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        due_date_str = request.form['due_date']
        status = request.form['status']
        priority = request.form.get('priority', 'Medium')
        category_id = request.form.get('category_id', '')
        
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
            priority=priority,
            category_id=category_id if category_id else None
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
    
    # Get categories for the dropdown
    categories = Category.query.filter_by(user_id=session['user_id']).order_by(Category.name).all()
    return render_template('create_task.html', categories=categories)

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
        category_id = request.form.get('category_id', '')
        
        if due_date_str:
            try:
                task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format!', 'error')
                return render_template('edit_task.html', task=task)
        else:
            task.due_date = None
        
        # Update category
        task.category_id = category_id if category_id else None
        
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
    
    # Get categories for the dropdown
    categories = Category.query.filter_by(user_id=session['user_id']).order_by(Category.name).all()
    return render_template('edit_task.html', task=task, categories=categories)

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

@main.route('/categories')
@login_required
def categories():
    user = db.session.get(User, session['user_id'])
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('auth.logout'))
    
    categories = Category.query.filter_by(user_id=user.id).order_by(Category.name).all()
    return render_template('categories.html', categories=categories, user=user)

@main.route('/category/create', methods=['GET', 'POST'])
@login_required
def create_category():
    if request.method == 'POST':
        name = request.form['name']
        color = request.form['color']
        description = request.form.get('description', '')
        
        # Check if category name already exists for this user
        existing_category = Category.query.filter_by(user_id=session['user_id'], name=name).first()
        if existing_category:
            flash('A category with this name already exists!', 'error')
            return render_template('create_category.html')
        
        category = Category(
            name=name,
            color=color,
            description=description,
            user_id=session['user_id']
        )
        
        db.session.add(category)
        db.session.commit()
        
        flash('Category created successfully!', 'success')
        return redirect(url_for('main.categories'))
    
    return render_template('create_category.html')

@main.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    category = db.session.get(Category, category_id)
    if not category:
        flash('Category not found!', 'error')
        return redirect(url_for('main.categories'))
    if category.user_id != session['user_id']:
        flash('Access denied!', 'error')
        return redirect(url_for('main.categories'))
    
    if request.method == 'POST':
        name = request.form['name']
        color = request.form['color']
        description = request.form.get('description', '')
        
        # Check if name is already taken by another category
        existing_category = Category.query.filter_by(user_id=session['user_id'], name=name).first()
        if existing_category and existing_category.id != category.id:
            flash('A category with this name already exists!', 'error')
            return render_template('edit_category.html', category=category)
        
        category.name = name
        category.color = color
        category.description = description
        
        db.session.commit()
        flash('Category updated successfully!', 'success')
        return redirect(url_for('main.categories'))
    
    return render_template('edit_category.html', category=category)

@main.route('/category/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    category = db.session.get(Category, category_id)
    if not category:
        flash('Category not found!', 'error')
        return redirect(url_for('main.categories'))
    if category.user_id != session['user_id']:
        flash('Access denied!', 'error')
        return redirect(url_for('main.categories'))
    
    # Check if category has tasks
    if category.tasks:
        flash('Cannot delete category that has tasks. Please move or delete the tasks first.', 'error')
        return redirect(url_for('main.categories'))
    
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('main.categories')) 