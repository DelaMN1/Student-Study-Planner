import os
import tempfile
import pytest
from app import app, db, User, Task

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
    app.config['WTF_CSRF_ENABLED'] = False
    client = app.test_client()

    with app.app_context():
        db.create_all()
    yield client

    os.close(db_fd)
    os.unlink(db_path)

def register(client, username, email, password):
    return client.post('/register', data={
        'username': username,
        'email': email,
        'password': password,
        'confirm_password': password
    }, follow_redirects=True)

def login(client, username, password):
    return client.post('/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)

def test_register_login(client):
    rv = register(client, 'testuser', 'test@example.com', 'testpass')
    assert b'Registration successful' in rv.data
    rv = login(client, 'testuser', 'testpass')
    assert b'Login successful' in rv.data

def test_create_task(client):
    register(client, 'testuser2', 'test2@example.com', 'testpass')
    login(client, 'testuser2', 'testpass')
    rv = client.post('/task/create', data={
        'title': 'Test Task',
        'description': 'Test Description',
        'due_date': '',
        'status': 'pending'
    }, follow_redirects=True)
    assert b'Task created successfully' in rv.data 