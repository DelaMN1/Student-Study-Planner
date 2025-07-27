"""
Pytest configuration and fixtures for Student Study Planner tests
"""
import os
import tempfile
import pytest
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash
import uuid

# Import the app factory
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from __init__ import create_app
from models import db, User, Task, Category


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'UPLOAD_FOLDER': tempfile.mkdtemp()
    })

    # Create the database and load test data
    with app.app_context():
        db.create_all()
        yield app

    # Clean up the temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        # Generate unique username and email
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password_hash=generate_password_hash('testpass123')
        )
        db.session.add(user)
        db.session.commit()
        # Store the ID to avoid session issues
        user_id = user.id
        return {'id': user_id, 'username': user.username, 'email': user.email}


@pytest.fixture
def test_category(app, test_user):
    """Create a test category."""
    with app.app_context():
        unique_id = str(uuid.uuid4())[:8]
        category = Category(
            name=f'Test Category {unique_id}',
            color='#007bff',
            description='A test category',
            user_id=test_user['id']
        )
        db.session.add(category)
        db.session.commit()
        # Store the ID to avoid session issues
        category_id = category.id
        return {'id': category_id, 'name': category.name, 'user_id': test_user['id']}


@pytest.fixture
def test_task(app, test_user, test_category):
    """Create a test task."""
    with app.app_context():
        unique_id = str(uuid.uuid4())[:8]
        task = Task(
            title=f'Test Task {unique_id}',
            description='This is a test task',
            due_date=datetime.now(timezone.utc) + timedelta(days=7),
            status='pending',
            priority='Medium',
            user_id=test_user['id'],
            category_id=test_category['id']
        )
        db.session.add(task)
        db.session.commit()
        # Store the ID to avoid session issues
        task_id = task.id
        return {'id': task_id, 'title': task.title, 'user_id': test_user['id'], 'category_id': test_category['id']}


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for API requests."""
    # Login to get session
    client.post('/login', data={
        'username': test_user['username'],
        'password': 'testpass123'
    })
    return client


class AuthActions:
    """Helper class for authentication actions in tests."""
    
    def __init__(self, client):
        self.client = client

    def register(self, username='testuser', email='test@example.com', password='testpass123'):
        """Register a new user."""
        return self.client.post('/register', data={
            'username': username,
            'email': email,
            'password': password,
            'confirm_password': password
        }, follow_redirects=True)

    def login(self, username='testuser', password='testpass123'):
        """Login a user."""
        return self.client.post('/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)

    def logout(self):
        """Logout the current user."""
        return self.client.get('/logout', follow_redirects=True)


@pytest.fixture
def auth(client, test_user):
    """Authentication helper fixture."""
    auth_actions = AuthActions(client)
    # Store the original login method
    original_login = auth_actions.login
    # Override the login method to use the test user credentials
    def login_with_test_user(username=None, password=None):
        return original_login(test_user['username'], 'testpass123')
    
    auth_actions.login = login_with_test_user
    return auth_actions 