# Student Study Planner

A comprehensive Flask-based web application for students to manage their study tasks, track deadlines, and organize study materials with file uploads.

## Features

### 🔐 Authentication System
- User registration and login with secure password hashing
- Session-based authentication using Flask sessions
- Password security with Werkzeug's `generate_password_hash` and `check_password_hash`

### 📘 Study Task Management (CRUD)
- **Create**: Add new study tasks with title, description, due date, and status
- **Read**: View task list with filtering and detailed task views
- **Update**: Edit existing tasks and update their status
- **Delete**: Remove tasks with confirmation

### 📁 File Upload System
- Upload study materials (PDFs, images, documents) for each task
- Secure file storage in local filesystem (`/uploads` folder)
- File type validation and size limits (16MB max)
- Unique filename generation to prevent conflicts

### 🎨 Modern UI/UX
- Responsive Bootstrap 5 design
- Font Awesome icons for better visual experience
- Interactive task cards with hover effects
- Status-based color coding (pending, in progress, completed)
- Floating action button for quick task creation

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Flask, Flask-SQLAlchemy |
| Frontend | Jinja2, HTML/CSS, Bootstrap 5 |
| Authentication | Flask Sessions, Werkzeug |
| File Upload | Local filesystem (`/uploads`) |
| Database | SQLite (development) / PostgreSQL (production) |
| Deployment | Gunicorn + Nginx on Ubuntu VPS |

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd student_study_planner
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage Guide

### 1. Registration & Login
- Visit the homepage and click "Get Started" to register
- Fill in username, email, and password
- Login with your credentials

### 2. Creating Study Tasks
- Click the "+" button or "New Task" link
- Fill in task details:
  - **Title**: Required task name
  - **Description**: Optional detailed description
  - **Due Date**: Optional deadline
  - **Status**: Pending, In Progress, or Completed
  - **File**: Optional study material upload

### 3. Managing Tasks
- **View**: Click on any task card to see full details
- **Edit**: Use the edit button to modify task information
- **Status Toggle**: Use the status button to change task progress
- **Delete**: Remove tasks with confirmation dialog

### 4. File Management
- Upload files when creating or editing tasks
- Supported formats: PDF, TXT, PNG, JPG, JPEG, GIF, DOC, DOCX
- Maximum file size: 16MB
- Download attached files from task detail pages

## Database Schema

### User Model
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='user', lazy=True)
```

### Task Model
```python
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')
    file_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
```

## Security Features

- **Password Hashing**: All passwords are hashed using Werkzeug's security functions
- **Session Management**: Secure session handling with Flask sessions
- **File Upload Security**: 
  - File type validation
  - Secure filename generation
  - Size limits to prevent abuse
- **Access Control**: Users can only access their own tasks
- **CSRF Protection**: Built-in Flask CSRF protection

## Production Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /uploads {
        alias /path/to/your/app/uploads;
    }
}
```

### Environment Variables
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secure-secret-key
export DATABASE_URL=postgresql://user:password@localhost/dbname
```

## File Structure

```
student_study_planner/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── templates/            # Jinja2 HTML templates
│   ├── base.html        # Base template with navigation
│   ├── index.html       # Landing page
│   ├── register.html    # User registration
│   ├── login.html       # User login
│   ├── dashboard.html   # Task dashboard
│   ├── create_task.html # Task creation form
│   ├── view_task.html   # Task detail view
│   └── edit_task.html   # Task edit form
├── uploads/             # File upload directory
└── study_planner.db     # SQLite database (created automatically)
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue in the repository or contact the development team. 