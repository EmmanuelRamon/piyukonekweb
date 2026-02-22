#!/usr/bin/env python3
"""
Database migration script to add online status tracking columns to students table.
Run this script to update your existing database.
"""

import sqlite3
import os

def run_migration():
    # Get the database path
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'piyukonek.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Starting database migration...")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(students)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_online' not in columns:
            print("Adding is_online column...")
            cursor.execute("ALTER TABLE students ADD COLUMN is_online BOOLEAN DEFAULT FALSE")
        
        if 'last_seen' not in columns:
            print("Adding last_seen column...")
            cursor.execute("ALTER TABLE students ADD COLUMN last_seen DATETIME")
        
        # Update existing students to have offline status
        print("Updating existing students...")
        cursor.execute("UPDATE students SET is_online = FALSE WHERE is_online IS NULL")
        
        # Create index for better performance
        print("Creating index...")
        try:
            cursor.execute("CREATE INDEX idx_students_online_status ON students(is_online, last_seen)")
        except sqlite3.OperationalError:
            print("Index already exists, skipping...")
        
        # Commit changes
        conn.commit()
        print("Migration completed successfully!")
        
        # Show updated table structure
        cursor.execute("PRAGMA table_info(students)")
        print("\nUpdated table structure:")
        for column in cursor.fetchall():
            print(f"  {column[1]} ({column[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Migration failed: {e}")
        return False

def add_response_attachment_column():
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'piyukonek.db')
    
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the columns already exist
        cursor.execute("PRAGMA table_info(concerns)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'response_attachment' not in columns:
            # Add the response_attachment column
            cursor.execute("ALTER TABLE concerns ADD COLUMN response_attachment VARCHAR(255)")
            print("Column 'response_attachment' added successfully to concerns table.")
        else:
            print("Column 'response_attachment' already exists in concerns table.")
            
        if 'resolution_notes' not in columns:
            # Add the resolution_notes column
            cursor.execute("ALTER TABLE concerns ADD COLUMN resolution_notes TEXT")
            print("Column 'resolution_notes' added successfully to concerns table.")
        else:
            print("Column 'resolution_notes' already exists in concerns table.")
        
        conn.commit()
        conn.close()
        print("Response attachment and resolution notes migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during migration: {e}")
        return False

def create_concern_history_table():
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'piyukonek.db')
    
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='concern_history'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("Table 'concern_history' already exists.")
        else:
            # Create the concern_history table
            cursor.execute("""
                CREATE TABLE concern_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    concern_id INTEGER NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    action VARCHAR(255) NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (concern_id) REFERENCES concerns(id)
                )
            """)
            print("Table 'concern_history' created successfully.")
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX idx_concern_history_concern_id ON concern_history(concern_id)")
            cursor.execute("CREATE INDEX idx_concern_history_timestamp ON concern_history(timestamp)")
            print("Indexes created for concern_history table.")
        
        conn.commit()
        conn.close()
        print("Concern history table migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during concern history migration: {e}")
        return False

def add_rating_feedback_columns():
    """Add rating and feedback columns to concerns table"""
    try:
        conn = sqlite3.connect('instance/piyukonek.db')
        cursor = conn.cursor()
        
        # Add rating column (1-5 stars)
        cursor.execute('''
            ALTER TABLE concerns ADD COLUMN rating INTEGER;
        ''')
        
        # Add feedback text column
        cursor.execute('''
            ALTER TABLE concerns ADD COLUMN feedback TEXT;
        ''')
        
        # Add feedback submission timestamp
        cursor.execute('''
            ALTER TABLE concerns ADD COLUMN feedback_submitted_at DATETIME;
        ''')
        
        # Add feedback submission status
        cursor.execute('''
            ALTER TABLE concerns ADD COLUMN is_feedback_submitted BOOLEAN DEFAULT 0;
        ''')
        
        conn.commit()
        print("✅ Successfully added rating and feedback columns to concerns table")
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️  Rating and feedback columns already exist")
        else:
            print(f"❌ Error adding rating and feedback columns: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    print("🚀 Starting database migration...")
    
    # Add response attachment column
    add_response_attachment_column()
    
    # Create concern history table
    create_concern_history_table()
    
    # Add rating and feedback columns
    add_rating_feedback_columns()
    
    print("🎉 Database migration completed!") 