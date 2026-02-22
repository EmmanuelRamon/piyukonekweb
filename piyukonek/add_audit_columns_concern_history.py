#!/usr/bin/env python3
"""
Migration: Add audit trail columns to concern_history for transparency & accountability.
Records: sino nag-submit, kailan binago ang priority, sino nag-review, kailan na-resolve.
"""

import mysql.connector
from mysql.connector import Error

def add_audit_columns():
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'piyukonek'
    }
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("DESCRIBE concern_history")
            columns = [row[0] for row in cursor.fetchall()]
            for col, dtype in [
                ('actor_type', 'VARCHAR(20)'),
                ('actor_id', 'INT'),
                ('actor_name', 'VARCHAR(100)'),
                ('old_value', 'VARCHAR(100)'),
                ('new_value', 'VARCHAR(100)'),
            ]:
                if col not in columns:
                    cursor.execute(f"ALTER TABLE concern_history ADD COLUMN {col} {dtype} NULL")
                    print(f"Added column '{col}' to concern_history.")
                else:
                    print(f"Column '{col}' already exists.")
            connection.commit()
            cursor.close()
        connection.close()
        print("Audit columns migration completed.")
    except Error as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    add_audit_columns()
