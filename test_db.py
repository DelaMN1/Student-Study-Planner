#!/usr/bin/env python3
"""
Quick test to verify database schema
"""
import sqlite3
import os

def test_database():
    db_path = os.path.join('instance', 'study_planner.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    print(f"Testing database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check task table columns
        cursor.execute("PRAGMA table_info(task)")
        task_columns = [column[1] for column in cursor.fetchall()]
        print(f"Task table columns: {task_columns}")
        
        # Check if category_id exists
        if 'category_id' in task_columns:
            print("✅ category_id column exists in task table")
        else:
            print("❌ category_id column missing from task table")
        
        # Check if category table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='category'")
        category_exists = cursor.fetchone() is not None
        
        if category_exists:
            print("✅ category table exists")
            
            # Check category table columns
            cursor.execute("PRAGMA table_info(category)")
            category_columns = [column[1] for column in cursor.fetchall()]
            print(f"Category table columns: {category_columns}")
        else:
            print("❌ category table missing")
            
    except Exception as e:
        print(f"❌ Error testing database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_database() 