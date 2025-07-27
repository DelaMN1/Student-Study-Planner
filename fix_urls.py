#!/usr/bin/env python3
"""
Script to fix all URL references in templates to use the new blueprint structure
"""
import os
import re

# Define the URL mappings
url_mappings = {
    # Auth routes
    "url_for('login')": "url_for('auth.login')",
    "url_for('register')": "url_for('auth.register')",
    "url_for('logout')": "url_for('auth.logout')",
    "url_for('profile')": "url_for('auth.profile')",
    "url_for('update_profile')": "url_for('auth.update_profile')",
    "url_for('change_password')": "url_for('auth.change_password')",
    
    # Main routes
    "url_for('dashboard')": "url_for('main.dashboard')",
    "url_for('create_task')": "url_for('main.create_task')",
    "url_for('view_task'": "url_for('main.view_task'",
    "url_for('edit_task'": "url_for('main.edit_task'",
    "url_for('delete_task'": "url_for('main.delete_task'",
    "url_for('toggle_task_status'": "url_for('main.toggle_task_status'",
    "url_for('uploaded_file'": "url_for('main.uploaded_file'",
    
    # Calendar routes
    "url_for('calendar_export')": "url_for('calendar.calendar_export')",
    "url_for('google_auth')": "url_for('calendar.google_auth')",
    "url_for('calendar_events')": "url_for('calendar.calendar_events')",
}

def fix_template_file(filepath):
    """Fix URLs in a single template file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all URL mappings
        for old_url, new_url in url_mappings.items():
            content = content.replace(old_url, new_url)
        
        # Only write if content changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed: {filepath}")
        else:
            print(f"No changes needed: {filepath}")
            
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

def main():
    """Fix all template files"""
    template_dir = "templates"
    
    if not os.path.exists(template_dir):
        print(f"Template directory {template_dir} not found!")
        return
    
    html_files = [f for f in os.listdir(template_dir) if f.endswith('.html')]
    
    print("Fixing URL references in templates...")
    for filename in html_files:
        filepath = os.path.join(template_dir, filename)
        fix_template_file(filepath)
    
    print("Done!")

if __name__ == "__main__":
    main() 