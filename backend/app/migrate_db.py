"""
Database migration script to add citations column to chat_history table.
"""
import sqlite3
import os

def migrate_database():
    """Add citations column to chat_history table if it doesn't exist."""
    db_path = "chat_with_files.db"
    
    if not os.path.exists(db_path):
        print("Database file not found. It will be created on next init.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if citations column exists
        cursor.execute("PRAGMA table_info(chat_history)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'citations' not in columns:
            print("Adding citations column to chat_history table...")
            cursor.execute("ALTER TABLE chat_history ADD COLUMN citations TEXT")
            conn.commit()
            print("Citations column added successfully!")
        else:
            print("Citations column already exists.")
    except Exception as e:
        print(f"Error migrating database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
