#!/usr/bin/env python3
"""
Database Migration Script: Add Bulk Concern Operation Fields
This script adds new fields to the concerns table to support bulk operations.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

def add_bulk_concern_fields():
    """Add new fields to concerns table for bulk operations"""
    
    with app.app_context():
        try:
            # Check if fields already exist
            inspector = db.inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('concerns')]
            
            fields_to_add = [
                'assigned_to',
                'processing_at', 
                'processed_by',
                'closed_at',
                'closed_by'
            ]
            
            # Add missing fields
            for field in fields_to_add:
                if field not in existing_columns:
                    if field in ['assigned_to', 'processed_by', 'closed_by']:
                        # Integer foreign key fields
                        sql = f"ALTER TABLE concerns ADD COLUMN {field} INT NULL"
                        db.engine.execute(text(sql))
                        print(f"Added column: {field}")
                        
                        # Add foreign key constraint
                        fk_sql = f"ALTER TABLE concerns ADD CONSTRAINT fk_concerns_{field} FOREIGN KEY ({field}) REFERENCES ssc(id)"
                        try:
                            db.engine.execute(text(fk_sql))
                            print(f"Added foreign key constraint for: {field}")
                        except Exception as e:
                            print(f"Foreign key constraint for {field} already exists or failed: {e}")
                            
                    elif field in ['processing_at', 'closed_at']:
                        # DateTime fields
                        sql = f"ALTER TABLE concerns ADD COLUMN {field} DATETIME NULL"
                        db.engine.execute(text(sql))
                        print(f"Added column: {field}")
                else:
                    print(f"Column {field} already exists")
            
            print("Migration completed successfully!")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            db.session.rollback()

if __name__ == "__main__":
    print("Starting bulk concern fields migration...")
    add_bulk_concern_fields()
    print("Migration finished!")
