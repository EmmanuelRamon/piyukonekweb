from app import app, db
from sqlalchemy import text

def create_attachments_table():
    with app.app_context():
        # Create the concern_attachments table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS concern_attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            concern_id INTEGER NOT NULL,
            filename VARCHAR(255) NOT NULL,
            original_filename VARCHAR(255) NOT NULL,
            file_size INTEGER,
            file_type VARCHAR(50),
            uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (concern_id) REFERENCES concerns (id) ON DELETE CASCADE
        );
        """
        
        try:
            db.session.execute(text(create_table_sql))
            db.session.commit()
            print("✅ ConcernAttachment table created successfully!")
            
            # Create index for better performance
            index_sql = "CREATE INDEX IF NOT EXISTS idx_concern_attachments_concern_id ON concern_attachments(concern_id);"
            db.session.execute(text(index_sql))
            db.session.commit()
            print("✅ Index created successfully!")
            
        except Exception as e:
            print(f"❌ Error creating table: {e}")
            db.session.rollback()

if __name__ == "__main__":
    create_attachments_table()
