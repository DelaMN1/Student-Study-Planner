# Student Study Planner - Modular Structure

## Overview
The application has been restructured into a modular, organized pattern similar to how the HTML templates are structured. This makes editing easier and more seamless.

## File Structure

```
student_study_planner/
├── app.py                 # Main application entry point
├── run_dev.py            # Development server with OAuth workaround
├── __init__.py           # Application factory
├── models.py             # Database models (User, Task)
├── config.py             # Configuration settings
├── utils.py              # Utility functions and helpers
├── routes/               # Route handlers organized by feature
│   ├── __init__.py
│   ├── auth.py          # Authentication routes (login, register, profile)
│   ├── main.py          # Main application routes (dashboard, tasks)
│   └── calendar.py      # Calendar and Google OAuth routes
├── templates/            # HTML templates (unchanged)
├── uploads/             # File uploads directory
└── requirements.txt     # Dependencies
```

## Key Benefits

### 1. **Separation of Concerns**
- **Models** (`models.py`): Database models and relationships
- **Routes** (`routes/`): Organized by feature (auth, main, calendar)
- **Configuration** (`config.py`): All settings in one place
- **Utilities** (`utils.py`): Helper functions and decorators

### 2. **Easy Editing**
- Find specific functionality quickly
- Edit related features together
- Clear file organization

### 3. **Scalability**
- Easy to add new features
- Blueprint pattern for modularity
- Application factory for testing

## Running the Application

### For Development (with OAuth workaround):
```bash
python run_dev.py
```

### For Production:
```bash
python app.py
```

## Route Organization

### Authentication Routes (`routes/auth.py`)
- `/` - Index page
- `/register` - User registration
- `/login` - User login
- `/logout` - User logout
- `/profile` - User profile management

### Main Routes (`routes/main.py`)
- `/dashboard` - Main dashboard
- `/task/create` - Create new task
- `/task/<id>` - View task
- `/task/<id>/edit` - Edit task
- `/task/<id>/delete` - Delete task
- `/task/<id>/toggle_status` - Toggle task status
- `/uploads/<filename>` - Serve uploaded files

### Calendar Routes (`routes/calendar.py`)
- `/calendar` - Calendar view
- `/calendar/events` - Calendar events API
- `/calendar/export` - Export calendar
- `/google/auth` - Google OAuth
- `/google/callback` - Google OAuth callback
- `/google/sync` - Sync with Google Calendar

## OAuth Fix
The OAuth error you encountered has been fixed by:
1. Adding `os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'` in calendar routes
2. Creating `run_dev.py` for development with this workaround

## Migration Notes
- All functionality remains the same
- URLs and templates unchanged
- Database structure unchanged
- Just better organized code structure 