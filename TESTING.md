# Testing Documentation

## Overview

This document describes the comprehensive testing framework for the Student Study Planner application. The testing suite includes unit tests, integration tests, and frontend tests using Selenium.

## Test Structure

```
tests/
├── __init__.py          # Package marker
├── conftest.py          # Pytest configuration and fixtures
├── test_models.py       # Unit tests for database models
├── test_routes.py       # Integration tests for routes
├── test_utils.py        # Unit tests for utility functions
└── test_frontend.py     # Frontend tests using Selenium
```

## Test Categories

### 1. Unit Tests (`test_models.py`, `test_utils.py`)

**Purpose**: Test individual components in isolation

**Coverage**:
- Database models (User, Task, Category)
- Model relationships and constraints
- Utility functions and decorators
- Security features
- Error handling

**Example**:
```python
def test_user_creation(self, app):
    """Test creating a new user."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hashed_password'
        )
        assert user.username == 'testuser'
```

### 2. Integration Tests (`test_routes.py`)

**Purpose**: Test complete user workflows and API endpoints

**Coverage**:
- Authentication flows (register, login, logout)
- Task management (create, read, update, delete)
- Search and filtering functionality
- Category management
- File upload handling
- Error responses

**Example**:
```python
def test_create_task_success(self, client, auth, test_category):
    """Test successful task creation."""
    auth.login()
    response = client.post('/task/create', data={
        'title': 'New Test Task',
        'description': 'This is a new test task',
        'status': 'pending',
        'priority': 'High',
        'category_id': test_category.id
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Task created successfully' in response.data
```

### 3. Frontend Tests (`test_frontend.py`)

**Purpose**: Test user interface and browser interactions

**Coverage**:
- Page loading and navigation
- Form interactions
- Dark mode toggle
- Responsive design
- Accessibility features
- Cross-browser compatibility
- Performance metrics

**Example**:
```python
def test_dark_mode_toggle(self, driver, base_url):
    """Test dark mode toggle functionality."""
    driver.get(base_url)
    toggle_button = driver.find_element(By.ID, "toggle-dark")
    toggle_button.click()
    
    body = driver.find_element(By.TAG_NAME, "body")
    assert "dark-mode" in body.get_attribute("class")
```

## Running Tests

### Prerequisites

Install testing dependencies:
```bash
pip install -r requirements.txt
```

### Basic Test Execution

Run all tests:
```bash
python run_tests.py
```

Run specific test categories:
```bash
# Unit tests only
python run_tests.py --unit

# Integration tests only
python run_tests.py --integration

# Frontend tests only
python run_tests.py --frontend
```

### Coverage Reporting

Generate coverage report:
```bash
python run_tests.py --coverage
```

Generate HTML coverage report:
```bash
python run_tests.py --coverage --html
```

### Direct Pytest Usage

Run tests with pytest directly:
```bash
# All tests
pytest

# Specific test file
pytest tests/test_models.py

# Specific test class
pytest tests/test_models.py::TestUser

# Specific test method
pytest tests/test_models.py::TestUser::test_user_creation

# With coverage
pytest --cov=. --cov-report=html
```

## Test Fixtures

### Database Fixtures

- `app`: Flask application instance with test configuration
- `client`: Test client for making requests
- `test_user`: Pre-created user for testing
- `test_category`: Pre-created category for testing
- `test_task`: Pre-created task for testing

### Authentication Fixtures

- `auth`: Helper class for authentication actions
- `auth_headers`: Authenticated client for API requests

### Frontend Fixtures

- `driver`: Selenium WebDriver instance
- `base_url`: Base URL for frontend testing

## Test Configuration

### Pytest Configuration (`pytest.ini`)

- Test discovery patterns
- Markers for test categorization
- Warning filters
- Output formatting

### Test Environment

- Isolated test database
- Temporary file storage
- Mocked external services
- Headless browser for frontend tests

## Test Data Management

### Factory Boy Integration

For complex test data generation:
```python
import factory
from factory.fuzzy import FuzzyText, FuzzyChoice

class UserFactory(factory.Factory):
    class Meta:
        model = User
    
    username = FuzzyText(length=10)
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password_hash = factory.LazyFunction(lambda: generate_password_hash('testpass'))
```

### Faker Integration

For realistic test data:
```python
from faker import Faker

fake = Faker()

def test_with_fake_data(self):
    user_data = {
        'username': fake.user_name(),
        'email': fake.email(),
        'password': fake.password()
    }
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: python run_tests.py --coverage
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## Best Practices

### Test Organization

1. **Arrange-Act-Assert**: Structure tests with clear sections
2. **Descriptive Names**: Use clear, descriptive test method names
3. **Single Responsibility**: Each test should verify one specific behavior
4. **Isolation**: Tests should not depend on each other

### Test Data

1. **Fresh Data**: Use fixtures to create fresh test data
2. **Minimal Data**: Only include data necessary for the test
3. **Realistic Data**: Use realistic but safe test data
4. **Cleanup**: Ensure test data is properly cleaned up

### Assertions

1. **Specific Assertions**: Test specific outcomes, not implementation details
2. **Multiple Assertions**: Use multiple assertions to verify complete behavior
3. **Clear Messages**: Provide clear failure messages
4. **Edge Cases**: Test boundary conditions and error cases

## Debugging Tests

### Common Issues

1. **Database Conflicts**: Ensure test isolation with temporary databases
2. **Session Issues**: Clear sessions between tests
3. **File System**: Use temporary directories for file operations
4. **Timing Issues**: Use explicit waits in frontend tests

### Debugging Commands

```bash
# Run tests with debug output
pytest -v -s

# Run single test with debugger
pytest tests/test_models.py::TestUser::test_user_creation -s

# Run tests with coverage and show missing lines
pytest --cov=. --cov-report=term-missing
```

## Performance Testing

### Load Testing

For performance testing, consider using tools like:
- **Locust**: Python-based load testing
- **Apache Bench**: Simple HTTP load testing
- **JMeter**: Java-based load testing

### Example Load Test

```python
import locust

class StudyPlannerLoadTest(locust.HttpUser):
    @locust.task
    def test_dashboard(self):
        self.client.get("/dashboard")
    
    @locust.task
    def test_create_task(self):
        self.client.post("/task/create", {
            "title": "Load Test Task",
            "description": "Task created during load test"
        })
```

## Security Testing

### OWASP Testing

Include security-focused tests:
- SQL injection prevention
- XSS protection
- CSRF protection
- File upload security
- Authentication bypass attempts

### Example Security Test

```python
def test_sql_injection_prevention(self, client):
    """Test SQL injection prevention."""
    malicious_input = "'; DROP TABLE users; --"
    response = client.post('/register', data={
        'username': malicious_input,
        'email': 'test@example.com',
        'password': 'testpass'
    })
    # Should handle gracefully without error
    assert response.status_code == 200
```

## Coverage Goals

### Target Coverage

- **Models**: 100% coverage
- **Routes**: 95% coverage
- **Utils**: 100% coverage
- **Frontend**: 80% coverage
- **Overall**: 90% coverage

### Coverage Reports

Generate detailed coverage reports:
```bash
# Terminal coverage
pytest --cov=. --cov-report=term-missing

# HTML coverage report
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

## Maintenance

### Regular Tasks

1. **Update Dependencies**: Keep testing dependencies current
2. **Review Coverage**: Regularly review and improve coverage
3. **Update Tests**: Update tests when features change
4. **Performance**: Monitor test execution time
5. **Documentation**: Keep test documentation current

### Test Review Checklist

- [ ] All new features have corresponding tests
- [ ] Edge cases are covered
- [ ] Error conditions are tested
- [ ] Performance is acceptable
- [ ] Documentation is updated
- [ ] Coverage meets targets 