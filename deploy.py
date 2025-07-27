#!/usr/bin/env python3
"""
Deployment script for Student Study Planner
This script helps set up the application for production deployment
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"{description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_production_config():
    """Create production configuration"""
    config_content = """# Production Configuration
import os

class ProductionConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///study_planner.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    DEBUG = False
"""
    
    with open('config.py', 'w') as f:
        f.write(config_content)
    print("Production configuration created")

def create_gunicorn_config():
    """Create Gunicorn configuration file"""
    gunicorn_config = """# Gunicorn configuration
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True
"""
    
    with open('gunicorn.conf.py', 'w') as f:
        f.write(gunicorn_config)
    print("Gunicorn configuration created")

def create_systemd_service():
    """Create systemd service file"""
    service_content = """[Unit]
Description=Student Study Planner
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/app
Environment="PATH=/path/to/your/app/venv/bin"
ExecStart=/path/to/your/app/venv/bin/gunicorn --config gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
"""
    
    with open('study-planner.service', 'w') as f:
        f.write(service_content)
    print("Systemd service file created")
    print("Remember to update the paths in study-planner.service")

def create_nginx_config():
    """Create Nginx configuration"""
    nginx_config = """server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /uploads {
        alias /path/to/your/app/uploads;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /static {
        alias /path/to/your/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
"""
    
    with open('nginx-study-planner.conf', 'w') as f:
        f.write(nginx_config)
    print("Nginx configuration created")
    print("Remember to update the paths in nginx-study-planner.conf")

def main():
    """Main deployment setup function"""
    print("Setting up Student Study Planner for production deployment...")
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("Error: app.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Create necessary directories
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Install production dependencies
    if not run_command("pip install gunicorn", "Installing Gunicorn"):
        print("Failed to install Gunicorn")
        sys.exit(1)
    
    # Create configuration files
    create_production_config()
    create_gunicorn_config()
    create_systemd_service()
    create_nginx_config()
    
    # Create environment file template
    env_template = """# Environment variables for production
FLASK_ENV=production
SECRET_KEY=your-secure-secret-key-here
DATABASE_URL=postgresql://user:password@localhost/dbname
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_template)
    print("Environment template created")
    
    # Create deployment instructions
    instructions = """# Production Deployment Instructions

## 1. Environment Setup
- Copy .env.template to .env and update the values
- Set a secure SECRET_KEY
- Configure your database URL

## 2. Database Setup
- For PostgreSQL: Install and configure PostgreSQL
- For SQLite: The database will be created automatically

## 3. Web Server Setup
- Install Nginx: sudo apt-get install nginx
- Copy nginx-study-planner.conf to /etc/nginx/sites-available/
- Enable the site: sudo ln -s /etc/nginx/sites-available/study-planner /etc/nginx/sites-enabled/
- Test configuration: sudo nginx -t
- Restart Nginx: sudo systemctl restart nginx

## 4. Application Setup
- Update paths in study-planner.service
- Copy study-planner.service to /etc/systemd/system/
- Enable and start the service:
  sudo systemctl enable study-planner
  sudo systemctl start study-planner

## 5. SSL Certificate (Optional)
- Install Certbot: sudo apt-get install certbot python3-certbot-nginx
- Get SSL certificate: sudo certbot --nginx -d your-domain.com

## 6. File Permissions
- Set proper permissions: sudo chown -R www-data:www-data /path/to/your/app
- Ensure uploads directory is writable: sudo chmod 755 uploads/

## 7. Monitoring
- Check service status: sudo systemctl status study-planner
- View logs: sudo journalctl -u study-planner -f
"""
    
    with open('DEPLOYMENT.md', 'w') as f:
        f.write(instructions)
    print("Deployment instructions created")
    
    print("\n🎉 Production setup completed!")
    print("📋 Next steps:")
    print("1. Review and update the configuration files")
    print("2. Follow the instructions in DEPLOYMENT.md")
    print("3. Test the application in production mode")
    print("4. Set up monitoring and backups")

if __name__ == "__main__":
    main() 