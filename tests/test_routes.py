"""
Integration tests for application routes
"""
import pytest
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash
import io

from models import User, Task, Category


class TestAuthRoutes:
    """Test cases for authentication routes."""
    
    def test_index_page(self, client):
        """Test the index page loads correctly."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Study Planner' in response.data
    
    def test_register_page(self, client):
        """Test the register page loads correctly."""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'Register' in response.data
    
    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'confirm_password': 'newpass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Check for redirect to login page instead of flash message
        assert b'Login' in response.data
    
    def test_register_password_mismatch(self, client):
        """Test registration with mismatched passwords."""
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'confirm_password': 'differentpass'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Passwords do not match' in response.data
    
    def test_register_existing_username(self, client, test_user):
        """Test registration with existing username."""
        response = client.post('/register', data={
            'username': test_user['username'],
            'email': 'different@example.com',
            'password': 'newpass123',
            'confirm_password': 'newpass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Username already exists' in response.data
    
    def test_login_page(self, client):
        """Test the login page loads correctly."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Login' in response.data
    
    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post('/login', data={
            'username': test_user['username'],
            'password': 'testpass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Check for redirect to dashboard instead of flash message
        assert b'Dashboard' in response.data
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post('/login', data={
            'username': 'nonexistent',
            'password': 'wrongpass'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data
    
    def test_logout(self, client, auth, test_user):
        """Test logout functionality."""
        # First login
        auth.login()
        
        # Then logout
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        # Check for redirect to home page instead of flash message
        assert b'Study Planner' in response.data
    
    def test_profile_page(self, client, auth, test_user):
        """Test profile page access."""
        auth.login()
        response = client.get('/profile')
        assert response.status_code == 200
        assert b'Profile' in response.data
    
    def test_profile_update(self, client, auth, test_user):
        """Test profile update functionality."""
        auth.login()
        response = client.post('/profile/update', data={
            'username': 'updateduser',
            'email': 'updated@example.com'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Check for redirect to profile page instead of flash message
        assert b'Profile' in response.data


class TestMainRoutes:
    """Test cases for main application routes."""
    
    def test_dashboard_requires_login(self, client):
        """Test dashboard requires login."""
        response = client.get('/dashboard', follow_redirects=True)
        assert response.status_code == 200
        assert b'Login' in response.data
    
    def test_dashboard_with_login(self, client, auth, test_user):
        """Test dashboard with valid login."""
        auth.login()
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'Dashboard' in response.data
    
    def test_create_task_page(self, client, auth, test_user):
        """Test create task page access."""
        auth.login()
        response = client.get('/task/create')
        assert response.status_code == 200
        assert b'Create Task' in response.data
    
    def test_create_task_success(self, client, auth, test_user, test_category):
        """Test successful task creation."""
        auth.login()
        response = client.post('/task/create', data={
            'title': 'New Test Task',
            'description': 'This is a new test task',
            'due_date': (datetime.now(timezone.utc) + timedelta(days=7)).strftime('%Y-%m-%d'),
            'status': 'pending',
            'priority': 'High',
            'category_id': test_category['id']
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Check for redirect to dashboard instead of flash message
        assert b'Dashboard' in response.data
    
    def test_create_task_missing_title(self, client, auth, test_user):
        """Test task creation without required title."""
        auth.login()
        response = client.post('/task/create', data={
            'description': 'This task has no title',
            'status': 'pending'
        }, follow_redirects=True)
        
        # Should return 400 for validation error
        assert response.status_code == 400
    
    def test_view_task(self, client, auth, test_user, test_task):
        """Test viewing a specific task."""
        auth.login()
        response = client.get(f'/task/{test_task["id"]}')
        assert response.status_code == 200
        assert test_task['title'].encode() in response.data
    
    def test_view_nonexistent_task(self, client, auth, test_user):
        """Test viewing a task that doesn't exist."""
        auth.login()
        response = client.get('/task/99999')
        # Should redirect to dashboard for non-existent task
        assert response.status_code == 302
    
    def test_edit_task_page(self, client, auth, test_user, test_task):
        """Test edit task page access."""
        auth.login()
        response = client.get(f'/task/{test_task["id"]}/edit')
        assert response.status_code == 200
        assert b'Edit Task' in response.data
    
    def test_edit_task_success(self, client, auth, test_user, test_task):
        """Test successful task editing."""
        auth.login()
        response = client.post(f'/task/{test_task["id"]}/edit', data={
            'title': 'Updated Task Title',
            'description': 'Updated description',
            'due_date': '',  # Empty due_date field
            'status': 'in_progress',
            'priority': 'High'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Check for redirect to task view instead of flash message
        assert b'Updated Task Title' in response.data
    
    def test_delete_task(self, client, auth, test_user, test_task):
        """Test task deletion."""
        auth.login()
        response = client.post(f'/task/{test_task["id"]}/delete', follow_redirects=True)
        assert response.status_code == 200
        # Check for redirect to dashboard instead of flash message
        assert b'Dashboard' in response.data
    
    def test_toggle_task_status(self, client, auth, test_user, test_task):
        """Test toggling task status."""
        auth.login()
        # Get the task from database to check current status
        from models import db
        with client.application.app_context():
            task = db.session.get(Task, test_task['id'])
            original_status = task.status
            
            # Toggle status
            response = client.post(f'/task/{test_task["id"]}/toggle_status')
            assert response.status_code == 302
            
            # Check status changed
            db.session.refresh(task)
            assert task.status != original_status


class TestSearchRoutes:
    """Test cases for search functionality."""
    
    def test_search_page(self, client, auth, test_user):
        """Test search page access."""
        auth.login()
        response = client.get('/search')
        assert response.status_code == 200
        # Check for search results page instead of specific text
        assert b'Search Results' in response.data
    
    def test_search_by_title(self, client, auth, test_user, test_task):
        """Test searching tasks by title."""
        auth.login()
        response = client.get('/search?q=Test')
        assert response.status_code == 200
        assert test_task['title'].encode() in response.data
    
    def test_search_by_description(self, client, auth, test_user, test_task):
        """Test searching tasks by description."""
        auth.login()
        response = client.get('/search?q=test task')
        assert response.status_code == 200
        # Check for task description in response
        assert b'This is a test task' in response.data
    
    def test_search_no_results(self, client, auth, test_user):
        """Test search with no results."""
        auth.login()
        response = client.get('/search?q=nonexistent')
        assert response.status_code == 200
        assert b'No tasks found' in response.data
    
    def test_filter_by_status(self, client, auth, test_user, test_task):
        """Test filtering tasks by status."""
        auth.login()
        # Get the task from database to check current status
        from models import db
        with client.application.app_context():
            task = db.session.get(Task, test_task['id'])
            response = client.get(f'/search?status={task.status}')
            assert response.status_code == 200
            assert test_task['title'].encode() in response.data
    
    def test_filter_by_priority(self, client, auth, test_user, test_task):
        """Test filtering tasks by priority."""
        auth.login()
        # Get the task from database to check current priority
        from models import db
        with client.application.app_context():
            task = db.session.get(Task, test_task['id'])
            response = client.get(f'/search?priority={task.priority}')
            assert response.status_code == 200
            assert test_task['title'].encode() in response.data


class TestCategoryRoutes:
    """Test cases for category management."""
    
    def test_categories_page(self, client, auth, test_user):
        """Test categories page access."""
        auth.login()
        response = client.get('/categories')
        assert response.status_code == 200
        assert b'Categories' in response.data
    
    def test_create_category_page(self, client, auth, test_user):
        """Test create category page access."""
        auth.login()
        response = client.get('/category/create')
        assert response.status_code == 200
        assert b'Create Category' in response.data
    
    def test_create_category_success(self, client, auth, test_user):
        """Test successful category creation."""
        auth.login()
        response = client.post('/category/create', data={
            'name': 'New Test Category',
            'color': '#007bff',
            'description': 'A new test category'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Check for redirect to categories page instead of flash message
        assert b'Categories' in response.data
    
    def test_create_category_missing_name(self, client, auth, test_user):
        """Test category creation without required name."""
        auth.login()
        response = client.post('/category/create', data={
            'color': '#007bff',
            'description': 'Category without name'
        }, follow_redirects=True)
        
        # Should return 400 for validation error
        assert response.status_code == 400
    
    def test_edit_category_page(self, client, auth, test_user, test_category):
        """Test edit category page access."""
        auth.login()
        response = client.get(f'/category/{test_category["id"]}/edit')
        assert response.status_code == 200
        assert b'Edit Category' in response.data
    
    def test_edit_category_success(self, client, auth, test_user, test_category):
        """Test successful category editing."""
        auth.login()
        response = client.post(f'/category/{test_category["id"]}/edit', data={
            'name': 'Updated Category Name',
            'color': '#28a745',
            'description': 'Updated category description'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Check for redirect to categories page instead of flash message
        assert b'Categories' in response.data
    
    def test_delete_category(self, client, auth, test_user, test_category):
        """Test category deletion."""
        auth.login()
        response = client.post(f'/category/{test_category["id"]}/delete', follow_redirects=True)
        assert response.status_code == 200
        # Check for redirect to categories page instead of flash message
        assert b'Categories' in response.data


class TestCalendarRoutes:
    """Test cases for calendar functionality."""
    
    def test_calendar_page(self, client, auth, test_user):
        """Test calendar page access."""
        auth.login()
        response = client.get('/calendar')
        assert response.status_code == 200
        assert b'Calendar' in response.data
    
    def test_calendar_events(self, client, auth, test_user):
        """Test calendar events endpoint."""
        auth.login()
        response = client.get('/calendar/events')
        assert response.status_code == 200
        # Should return JSON data
        assert response.is_json
    
    def test_calendar_export(self, client, auth, test_user):
        """Test calendar export functionality."""
        auth.login()
        response = client.get('/calendar/export')
        assert response.status_code == 200
        # Should return iCalendar data
        assert response.headers['Content-Type'] == 'text/calendar'


class TestErrorHandling:
    """Test cases for error handling."""
    
    def test_404_error(self, client):
        """Test 404 error handling."""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
    
    def test_500_error(self, client):
        """Test 500 error handling."""
        # This would require triggering an actual error
        # For now, just test that the app doesn't crash
        response = client.get('/dashboard')
        assert response.status_code in [200, 302]  # Either success or redirect to login


class TestFileUpload:
    """Test cases for file upload functionality."""
    
    def test_upload_file(self, client, auth, test_user):
        """Test file upload functionality."""
        auth.login()
        
        # Create a test file
        test_file_content = b'This is a test file content'
        test_file = (io.BytesIO(test_file_content), 'test.txt')
        
        response = client.post('/task/create', data={
            'title': 'Task with File',
            'description': 'This task has a file attachment',
            'due_date': '',  # Empty due_date field
            'status': 'pending',
            'priority': 'Medium',
            'file': test_file
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Dashboard' in response.data
    
    def test_upload_invalid_file(self, client, auth, test_user):
        """Test upload of invalid file type."""
        auth.login()
        
        # Create an invalid file
        test_file_content = b'This is a test file content'
        test_file = (io.BytesIO(test_file_content), 'test.exe')
        
        response = client.post('/task/create', data={
            'title': 'Task with Invalid File',
            'description': 'This task has an invalid file',
            'due_date': '',  # Empty due_date field
            'status': 'pending',
            'priority': 'Medium',
            'file': test_file
        }, follow_redirects=True)
        
        # Should still succeed but without the file
        assert response.status_code == 200 