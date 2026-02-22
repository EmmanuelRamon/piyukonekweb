#!/usr/bin/env python3
"""
Database migration script to create Department and Course tables
Run this script to add the new tables to your existing database
"""

from app import app, db, Department, Course
import sys
import pymysql

def create_tables():
    """Create the Department and Course tables"""
    try:
        with app.app_context():
            print("🔍 Checking database connection...")
            
            # Check if tables already exist
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            print(f"📋 Existing tables: {existing_tables}")
            
            # Drop existing tables if they exist (to recreate with correct schema)
            if 'courses' in existing_tables:
                print("🗑️  Dropping existing courses table...")
                db.engine.execute("DROP TABLE IF EXISTS courses")
                
            if 'departments' in existing_tables:
                print("🗑️  Dropping existing departments table...")
                db.engine.execute("DROP TABLE IF EXISTS departments")
            
            print("✅ Creating Department and Course tables with correct schema...")
            
            # Create the tables with the correct schema
            db.create_all()
            
            print("✅ Database tables created successfully!")
            
            # Add some sample data
            add_sample_data()
            
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        print("🔧 Trying alternative approach...")
        try:
            create_tables_manually()
        except Exception as e2:
            print(f"❌ Alternative approach failed: {str(e2)}")
            sys.exit(1)

def create_tables_manually():
    """Manually create tables using raw SQL"""
    with app.app_context():
        print("🔧 Creating tables manually with SQL...")
        
        # Create departments table
        departments_sql = """
        CREATE TABLE IF NOT EXISTS departments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            code VARCHAR(20) NOT NULL UNIQUE,
            description TEXT,
            status VARCHAR(20) DEFAULT 'active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            created_by INT NOT NULL DEFAULT 1
        )
        """
        
        # Create courses table
        courses_sql = """
        CREATE TABLE IF NOT EXISTS courses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            code VARCHAR(20) NOT NULL,
            description TEXT,
            department_id INT NOT NULL,
            status VARCHAR(20) DEFAULT 'active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            created_by INT NOT NULL DEFAULT 1,
            FOREIGN KEY (department_id) REFERENCES departments(id),
            UNIQUE KEY unique_course_per_dept (code, department_id)
        )
        """
        
        try:
            db.engine.execute(departments_sql)
            print("✅ Departments table created")
            
            db.engine.execute(courses_sql)
            print("✅ Courses table created")
            
        except Exception as e:
            print(f"❌ Manual table creation failed: {str(e)}")
            raise

def add_sample_data():
    """Add sample departments and courses if tables are empty"""
    try:
        # Check if we have any departments
        if Department.query.count() == 0:
            print("📝 Adding sample departments...")
            
            # Sample departments
            departments_data = [
                {
                    'name': 'College of Computer Studies',
                    'code': 'CCS',
                    'description': 'Offers programs in computer science, information technology, and related fields',
                    'created_by': 1  # Assuming admin ID 1 exists
                },
                {
                    'name': 'College of Engineering',
                    'code': 'COE',
                    'description': 'Provides engineering programs including civil, mechanical, and electrical engineering',
                    'created_by': 1
                },
                {
                    'name': 'College of Business Administration',
                    'code': 'CBA',
                    'description': 'Offers business and management programs',
                    'created_by': 1
                },
                {
                    'name': 'College of Education',
                    'code': 'COED',
                    'description': 'Prepares future educators and teachers',
                    'created_by': 1
                },
                {
                    'name': 'College of Arts and Sciences',
                    'code': 'CAS',
                    'description': 'Liberal arts and sciences programs',
                    'created_by': 1
                }
            ]
            
            for dept_data in departments_data:
                department = Department(**dept_data)
                db.session.add(department)
            
            db.session.commit()
            print("✅ Sample departments added!")
            
            # Add sample courses
            print("📝 Adding sample courses...")
            
            # Get the created departments
            ccs = Department.query.filter_by(code='CCS').first()
            coe = Department.query.filter_by(code='COE').first()
            cba = Department.query.filter_by(code='CBA').first()
            coed = Department.query.filter_by(code='COED').first()
            cas = Department.query.filter_by(code='CAS').first()
            
            courses_data = [
                # CCS Courses
                {
                    'name': 'Bachelor of Science in Computer Science',
                    'code': 'BSCS',
                    'description': 'Four-year program focusing on computer programming, algorithms, and software development',
                    'department_id': ccs.id,
                    'created_by': 1
                },
                {
                    'name': 'Bachelor of Science in Information Technology',
                    'code': 'BSIT',
                    'description': 'Program focusing on information systems, networking, and technology management',
                    'department_id': ccs.id,
                    'created_by': 1
                },
                {
                    'name': 'Bachelor of Science in Information Systems',
                    'code': 'BSIS',
                    'description': 'Program combining business and technology for information management',
                    'department_id': ccs.id,
                    'created_by': 1
                },
                
                # COE Courses
                {
                    'name': 'Bachelor of Science in Civil Engineering',
                    'code': 'BSCE',
                    'description': 'Engineering program focusing on infrastructure and construction',
                    'department_id': coe.id,
                    'created_by': 1
                },
                {
                    'name': 'Bachelor of Science in Electrical Engineering',
                    'code': 'BSEE',
                    'description': 'Engineering program focusing on electrical systems and electronics',
                    'department_id': coe.id,
                    'created_by': 1
                },
                
                # CBA Courses
                {
                    'name': 'Bachelor of Science in Business Administration',
                    'code': 'BSBA',
                    'description': 'Comprehensive business program covering management, marketing, and finance',
                    'department_id': cba.id,
                    'created_by': 1
                },
                {
                    'name': 'Bachelor of Science in Accountancy',
                    'code': 'BSA',
                    'description': 'Professional accounting program preparing students for CPA certification',
                    'department_id': cba.id,
                    'created_by': 1
                },
                
                # COED Courses
                {
                    'name': 'Bachelor of Elementary Education',
                    'code': 'BEED',
                    'description': 'Teacher preparation program for elementary education',
                    'department_id': coed.id,
                    'created_by': 1
                },
                {
                    'name': 'Bachelor of Secondary Education',
                    'code': 'BSED',
                    'description': 'Teacher preparation program for secondary education',
                    'department_id': coed.id,
                    'created_by': 1
                },
                
                # CAS Courses
                {
                    'name': 'Bachelor of Arts in Psychology',
                    'code': 'AB-PSYC',
                    'description': 'Liberal arts program focusing on human behavior and mental processes',
                    'department_id': cas.id,
                    'created_by': 1
                },
                {
                    'name': 'Bachelor of Science in Biology',
                    'code': 'BS-BIO',
                    'description': 'Science program focusing on living organisms and biological processes',
                    'department_id': cas.id,
                    'created_by': 1
                }
            ]
            
            for course_data in courses_data:
                course = Course(**course_data)
                db.session.add(course)
            
            db.session.commit()
            print("✅ Sample courses added!")
            
        else:
            print("ℹ️  Departments already exist, skipping sample data")
            
    except Exception as e:
        print(f"⚠️  Warning: Could not add sample data: {str(e)}")
        print("   This is normal if admin user doesn't exist yet")

def main():
    """Main function"""
    print("🚀 Department and Course Management Setup")
    print("=" * 50)
    
    create_tables()
    
    print("\n✅ Setup completed successfully!")
    print("\nYou can now:")
    print("1. Access /admin/departments to manage departments")
    print("2. Access /admin/courses to manage courses")
    print("3. Use the admin dashboard navigation to access these features")
    print("\nNote: Make sure you're logged in as an admin user to access these features.")

if __name__ == '__main__':
    main()
