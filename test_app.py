"""
Legacy test file - maintained for backward compatibility
This file provides basic tests that work with the old structure
For comprehensive testing, use the tests/ directory
"""
import os
import tempfile
import pytest
from datetime import datetime, timedelta

# Import the app factory
from __init__ import create_app
from models import db, User, Task, Category


@pytest.fixture
def client():
    """Create a test client for the app."""
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })
    
    client = app.test_client()
    
    with app.app_context():
        db.create_all()
    yield client
    
    os.close(db_fd)
    os.unlink(db_path)


def register(client, username, email, password):
    """Helper function to register a user."""
    return client.post('/register', data={
        'username': username,
        'email': email,
        'password': password,
        'confirm_password': password
    }, follow_redirects=True)


def login(client, username, password):
    """Helper function to login a user."""
    return client.post('/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)


def test_register_login(client):
    """Test user registration and login functionality."""
    # Test registration
    rv = register(client, 'testuser', 'test@example.com', 'testpass')
    assert b'Registration successful' in rv.data
    
    # Test login
    rv = login(client, 'testuser', 'testpass')
    assert b'Login successful' in rv.data


def test_create_task(client):
    """Test task creation functionality."""
    # Register and login
    register(client, 'testuser2', 'test2@example.com', 'testpass')
    login(client, 'testuser2', 'testpass')
    
    # Create a task
    rv = client.post('/task/create', data={
        'title': 'Test Task',
        'description': 'Test Description',
        'due_date': '',
        'status': 'pending'
    }, follow_redirects=True)
    
    assert b'Task created successfully' in rv.data


def test_dashboard_access(client):
    """Test dashboard access with authentication."""
    # Try to access dashboard without login
    rv = client.get('/dashboard', follow_redirects=True)
    assert b'Login' in rv.data  # Should redirect to login
    
    # Register and login
    register(client, 'testuser3', 'test3@example.com', 'testpass')
    login(client, 'testuser3', 'testpass')
    
    # Now access dashboard
    rv = client.get('/dashboard')
    assert b'Dashboard' in rv.data


def test_search_functionality(client):
    """Test search functionality."""
    # Register and login
    register(client, 'testuser4', 'test4@example.com', 'testpass')
    login(client, 'testuser4', 'testpass')
    
    # Create a task
    client.post('/task/create', data={
        'title': 'Searchable Task',
        'description': 'This task should be found by search',
        'status': 'pending'
    }, follow_redirects=True)
    
    # Test search
    rv = client.get('/search?q=Searchable')
    assert b'Searchable Task' in rv.data


def test_category_management(client):
    """Test category management functionality."""
    # Register and login
    register(client, 'testuser5', 'test5@example.com', 'testpass')
    login(client, 'testuser5', 'testpass')
    
    # Create a category
    rv = client.post('/category/create', data={
        'name': 'Test Category',
        'color': '#ff0000',
        'description': 'A test category'
    }, follow_redirects=True)
    
    assert b'Category created successfully' in rv.data


def test_dark_mode_toggle(client):
    """Test dark mode toggle functionality."""
    rv = client.get('/')
    assert rv.status_code == 200
    
    # Check if dark mode toggle button exists
    assert b'toggle-dark' in rv.data


def test_error_handling(client):
    """Test error handling."""
    # Test 404 error
    rv = client.get('/nonexistent-page')
    assert rv.status_code == 404


if __name__ == '__main__':
    # Run basic tests
    pytest.main([__file__, '-v']) 