"""
Unit tests for database models
"""
import pytest
from datetime import datetime, timedelta, timezone
from werkzeug.security import check_password_hash
import uuid

from models import User, Task, Category, db


class TestUser:
    """Test cases for User model."""
    
    def test_user_creation(self, app):
        """Test creating a new user."""
        with app.app_context():
            unique_id = str(uuid.uuid4())[:8]
            user = User(
                username=f'testuser_{unique_id}',
                email=f'test_{unique_id}@example.com',
                password_hash='hashed_password'
            )
            assert user.username == f'testuser_{unique_id}'
            assert user.email == f'test_{unique_id}@example.com'
            assert user.password_hash == 'hashed_password'
    
    def test_user_relationships(self, app, test_user, test_task, test_category):
        """Test user relationships with tasks and categories."""
        with app.app_context():
            # Test user has the expected IDs
            assert test_user['id'] is not None
            assert test_task['user_id'] == test_user['id']
            assert test_category['user_id'] == test_user['id']
    
    def test_user_repr(self, app):
        """Test user string representation."""
        with app.app_context():
            unique_id = str(uuid.uuid4())[:8]
            user = User(username=f'testuser_{unique_id}', email=f'test_{unique_id}@example.com')
            assert str(user) == f'<User testuser_{unique_id}>'


class TestCategory:
    """Test cases for Category model."""
    
    def test_category_creation(self, app, test_user):
        """Test creating a new category."""
        with app.app_context():
            unique_id = str(uuid.uuid4())[:8]
            
            category = Category(
                name=f'Test Category {unique_id}',
                color='#ff0000',
                description='A test category',
                user_id=test_user['id']
            )
            assert category.name == f'Test Category {unique_id}'
            assert category.color == '#ff0000'
            assert category.description == 'A test category'
            assert category.user_id == test_user['id']
    
    def test_category_default_color(self, app, test_user):
        """Test category default color."""
        with app.app_context():
            unique_id = str(uuid.uuid4())[:8]
            
            category = Category(
                name=f'Test Category {unique_id}',
                user_id=test_user['id']
            )
            # Save to database to get the default value
            db.session.add(category)
            db.session.commit()
            
            # The default should be set when the object is saved
            assert category.color == '#007bff'  # Default color
    
    def test_category_relationships(self, app, test_user, test_category, test_task):
        """Test category relationships."""
        with app.app_context():
            # Test category belongs to user
            assert test_category['user_id'] == test_user['id']
            
            # Test task belongs to category
            assert test_task['category_id'] == test_category['id']
    
    def test_category_repr(self, app, test_user):
        """Test category string representation."""
        with app.app_context():
            unique_id = str(uuid.uuid4())[:8]
            
            category = Category(name=f'Test Category {unique_id}', user_id=test_user['id'])
            assert str(category) == f'<Category Test Category {unique_id}>'


class TestTask:
    """Test cases for Task model."""
    
    def test_task_creation(self, app, test_user, test_category):
        """Test creating a new task."""
        with app.app_context():
            unique_id = str(uuid.uuid4())[:8]
            
            task = Task(
                title=f'Test Task {unique_id}',
                description='This is a test task',
                due_date=datetime.now(timezone.utc) + timedelta(days=7),
                status='pending',
                priority='High',
                user_id=test_user['id'],
                category_id=test_category['id']
            )
            assert task.title == f'Test Task {unique_id}'
            assert task.description == 'This is a test task'
            assert task.status == 'pending'
            assert task.priority == 'High'
            assert task.user_id == test_user['id']
            assert task.category_id == test_category['id']
    
    def test_task_default_values(self, app, test_user):
        """Test task default values."""
        with app.app_context():
            unique_id = str(uuid.uuid4())[:8]
            
            task = Task(
                title=f'Test Task {unique_id}',
                user_id=test_user['id']
            )
            # Save to database to get the default values
            db.session.add(task)
            db.session.commit()
            
            assert task.status == 'pending'  # Default status
            assert task.priority == 'Medium'  # Default priority
            assert task.category_id is None  # No default category
    
    def test_task_relationships(self, app, test_user, test_category, test_task):
        """Test task relationships."""
        with app.app_context():
            # Test task belongs to user
            assert test_task['user_id'] == test_user['id']
            
            # Test task belongs to category
            assert test_task['category_id'] == test_category['id']
    
    def test_task_repr(self, app, test_user):
        """Test task string representation."""
        with app.app_context():
            unique_id = str(uuid.uuid4())[:8]
            
            task = Task(title=f'Test Task {unique_id}', user_id=test_user['id'])
            assert str(task) == f'<Task Test Task {unique_id}>'
    
    def test_task_status_validation(self, app, test_user):
        """Test task status validation."""
        with app.app_context():
            # Valid statuses
            valid_statuses = ['pending', 'in_progress', 'completed']
            for status in valid_statuses:
                unique_id = str(uuid.uuid4())[:8]
                
                task = Task(title=f'Test Task {unique_id}', status=status, user_id=test_user['id'])
                assert task.status == status
    
    def test_task_priority_validation(self, app, test_user):
        """Test task priority validation."""
        with app.app_context():
            # Valid priorities
            valid_priorities = ['Low', 'Medium', 'High']
            for priority in valid_priorities:
                unique_id = str(uuid.uuid4())[:8]
                
                task = Task(title=f'Test Task {unique_id}', priority=priority, user_id=test_user['id'])
                assert task.priority == priority


class TestModelRelationships:
    """Test cases for model relationships."""
    
    def test_user_task_relationship(self, app, test_user, test_task):
        """Test user-task relationship."""
        with app.app_context():
            # Test the foreign key relationship
            assert test_task['user_id'] == test_user['id']
    
    def test_user_category_relationship(self, app, test_user, test_category):
        """Test user-category relationship."""
        with app.app_context():
            # Test the foreign key relationship
            assert test_category['user_id'] == test_user['id']
    
    def test_category_task_relationship(self, app, test_category, test_task):
        """Test category-task relationship."""
        with app.app_context():
            # Test the foreign key relationship
            assert test_task['category_id'] == test_category['id']
    
    def test_cascade_delete(self, app, test_user, test_category, test_task):
        """Test cascade delete behavior."""
        with app.app_context():
            # Store IDs for verification
            user_id = test_user['id']
            category_id = test_category['id']
            task_id = test_task['id']
            
            # Get the actual objects from the database
            user = db.session.get(User, user_id)
            category = db.session.get(Category, category_id)
            task = db.session.get(Task, task_id)
            
            # Delete user (should cascade to tasks and categories)
            db.session.delete(user)
            db.session.commit()
            
            # Verify user is deleted
            assert db.session.get(User, user_id) is None
            
            # Verify category is deleted
            assert db.session.get(Category, category_id) is None
            
            # Verify task is deleted
            assert db.session.get(Task, task_id) is None


class TestModelValidation:
    """Test cases for model validation."""
    
    def test_user_unique_constraints(self, app, test_user):
        """Test user unique constraints."""
        with app.app_context():
            # Try to create user with same username
            duplicate_user = User(
                username=test_user['username'],
                email='different@example.com',
                password_hash='hash'
            )
            db.session.add(duplicate_user)
            
            # Should raise integrity error
            with pytest.raises(Exception):
                db.session.commit()
            db.session.rollback()
            
            # Try to create user with same email
            duplicate_email = User(
                username='differentuser',
                email=test_user['email'],
                password_hash='hash'
            )
            db.session.add(duplicate_email)
            
            # Should raise integrity error
            with pytest.raises(Exception):
                db.session.commit()
    
    def test_required_fields(self, app):
        """Test required fields validation."""
        with app.app_context():
            # User without required fields
            user = User()
            with pytest.raises(Exception):
                db.session.add(user)
                db.session.commit()
            db.session.rollback()
            
            # Task without required fields
            task = Task()
            with pytest.raises(Exception):
                db.session.add(task)
                db.session.commit()
            db.session.rollback()
            
            # Category without required fields
            category = Category()
            with pytest.raises(Exception):
                db.session.add(category)
                db.session.commit() 