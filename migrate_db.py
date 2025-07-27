#!/usr/bin/env python3
"""
Database migration script to add Category model and category_id to Task table
"""
import os
import sqlite3
from app import app

def migrate_database():
    """Migrate the database to include new Category model and category_id column"""
    with app.app_context():
        from models import db
        
        # Get the database file path - it's in the instance folder
        db_path = os.path.join('instance', 'study_planner.db')
        
        if not os.path.exists(db_path):
            print(f"Database file {db_path} not found. Creating new database...")
            db.create_all()
            print("Database created successfully!")
            return
        
        print(f"Migrating database: {db_path}")
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Check if category table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='category'")
            category_table_exists = cursor.fetchone() is not None
            
            if not category_table_exists:
                print("Creating category table...")
                cursor.execute("""
                    CREATE TABLE category (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name VARCHAR(50) NOT NULL,
                        color VARCHAR(7) DEFAULT '#007bff',
                        description VARCHAR(200),
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        user_id INTEGER NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES user (id)
                    )
                """)
                print("Category table created successfully!")
            else:
                print("Category table already exists!")
            
            # Check if category_id column exists in task table
            cursor.execute("PRAGMA table_info(task)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'category_id' not in columns:
                print("Adding category_id column to task table...")
                cursor.execute("ALTER TABLE task ADD COLUMN category_id INTEGER REFERENCES category (id)")
                print("category_id column added successfully!")
            else:
                print("category_id column already exists!")
            
            # Commit changes
            conn.commit()
            print("Database migration completed successfully!")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

if __name__ == "__main__":
    print("Starting database migration...")
    migrate_database()
    print("Migration script completed!") 