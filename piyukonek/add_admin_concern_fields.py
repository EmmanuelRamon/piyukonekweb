#!/usr/bin/env python3
"""
Migration script to add admin concern handling fields to the concerns table.
This script adds the missing fields needed for admin responses and rejections.
"""

import mysql.connector
from mysql.connector import Error

def add_admin_concern_fields():
    """Add missing fields for admin concern handling"""
    
    # Database configuration
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'piyukonek'
    }
    
    try:
        # Establish connection
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Get existing columns
            cursor.execute("DESCRIBE concerns")
            columns = [column[0] for column in cursor.fetchall()]
            print(f"Existing columns: {columns}")
            
            # Add response_notes column if it doesn't exist
            if 'response_notes' not in columns:
                cursor.execute("ALTER TABLE concerns ADD COLUMN response_notes TEXT")
                print("Column 'response_notes' added successfully to concerns table.")
            else:
                print("Column 'response_notes' already exists in concerns table.")
            
            # Add responded_by column if it doesn't exist
            if 'responded_by' not in columns:
                cursor.execute("ALTER TABLE concerns ADD COLUMN responded_by INT")
                print("Column 'responded_by' added successfully to concerns table.")
            else:
                print("Column 'responded_by' already exists in concerns table.")
            
            # Add responded_at column if it doesn't exist
            if 'responded_at' not in columns:
                cursor.execute("ALTER TABLE concerns ADD COLUMN responded_at DATETIME")
                print("Column 'responded_at' added successfully to concerns table.")
            else:
                print("Column 'responded_at' already exists in concerns table.")
            
            # Add rejection_reason column if it doesn't exist
            if 'rejection_reason' not in columns:
                cursor.execute("ALTER TABLE concerns ADD COLUMN rejection_reason TEXT")
                print("Column 'rejection_reason' added successfully to concerns table.")
            else:
                print("Column 'rejection_reason' already exists in concerns table.")
            
            # Add rejected_by column if it doesn't exist
            if 'rejected_by' not in columns:
                cursor.execute("ALTER TABLE concerns ADD COLUMN rejected_by INT")
                print("Column 'rejected_by' added successfully to concerns table.")
            else:
                print("Column 'rejected_by' already exists in concerns table.")
            
            # Add rejected_at column if it doesn't exist
            if 'rejected_at' not in columns:
                cursor.execute("ALTER TABLE concerns ADD COLUMN rejected_at DATETIME")
                print("Column 'rejected_at' added successfully to concerns table.")
            else:
                print("Column 'rejected_at' already exists in concerns table.")
            
            # Commit changes
            connection.commit()
            print("All changes committed successfully!")
            
    except Error as e:
        print(f"Error: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    print("Starting migration to add admin concern handling fields...")
    add_admin_concern_fields()
    print("Migration completed!")
