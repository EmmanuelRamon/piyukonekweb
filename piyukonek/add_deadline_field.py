#!/usr/bin/env python3
"""
Database Migration Script: Add Deadline Field to Concerns
This script adds a deadline field to the concerns table to track 3-day resolution requirement.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text
from datetime import datetime, timedelta

def add_deadline_field():
    """Add deadline field to concerns table and populate existing records"""
    
    with app.app_context():
        try:
            # Check if deadline field already exists
            inspector = db.inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('concerns')]
            
            if 'deadline' not in existing_columns:
                # Add deadline column
                sql = "ALTER TABLE concerns ADD COLUMN deadline DATETIME NULL"
                db.engine.execute(text(sql))
                print("Added column: deadline")
                
                # Populate deadline for existing concerns (3 days from submission)
                update_sql = """
                UPDATE concerns 
                SET deadline = datetime(submitted_at, '+3 days')
                WHERE deadline IS NULL
                """
                db.engine.execute(text(update_sql))
                print("Populated deadline for existing concerns")
                
            else:
                print("Column deadline already exists")
            
            print("Migration completed successfully!")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            db.session.rollback()

if __name__ == "__main__":
    print("Starting deadline field migration...")
    add_deadline_field()
    print("Migration finished!")
