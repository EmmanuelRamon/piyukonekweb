#!/usr/bin/env python3
"""
Quick fix script for database schema issues
This script will create the department and course tables with the correct schema
"""

import pymysql
from app import app
import sys

def fix_database():
    """Fix the database schema by creating tables manually"""
    
    # Database connection details from app config
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'piyukonek',
        'charset': 'utf8mb4'
    }
    
    try:
        print("🔧 Connecting to database...")
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        
        print("🗑️  Dropping existing tables if they exist...")
        cursor.execute("DROP TABLE IF EXISTS courses")
        cursor.execute("DROP TABLE IF EXISTS departments")
        
        print("✅ Creating departments table...")
        departments_sql = """
        CREATE TABLE departments (
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
        cursor.execute(departments_sql)
        
        print("✅ Creating courses table...")
        courses_sql = """
        CREATE TABLE courses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            code VARCHAR(20) NOT NULL,
            description TEXT,
            department_id INT NOT NULL,
            status VARCHAR(20) DEFAULT 'active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            created_by INT NOT NULL DEFAULT 1,
            FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE,
            UNIQUE KEY unique_course_per_dept (code, department_id)
        )
        """
        cursor.execute(courses_sql)
        
        print("📝 Adding sample departments...")
        departments_data = [
            ('College of Computer Studies', 'CCS', 'Offers programs in computer science, information technology, and related fields'),
            ('College of Engineering', 'COE', 'Provides engineering programs including civil, mechanical, and electrical engineering'),
            ('College of Business Administration', 'CBA', 'Offers business and management programs'),
            ('College of Education', 'COED', 'Prepares future educators and teachers'),
            ('College of Arts and Sciences', 'CAS', 'Liberal arts and sciences programs')
        ]
        
        for name, code, description in departments_data:
            cursor.execute(
                "INSERT INTO departments (name, code, description, created_by) VALUES (%s, %s, %s, %s)",
                (name, code, description, 1)
            )
        
        print("📚 Adding sample courses...")
        courses_data = [
            # CCS Courses
            ('Bachelor of Science in Computer Science', 'BSCS', 'Four-year program focusing on computer programming, algorithms, and software development', 1),
            ('Bachelor of Science in Information Technology', 'BSIT', 'Program focusing on information systems, networking, and technology management', 1),
            ('Bachelor of Science in Information Systems', 'BSIS', 'Program combining business and technology for information management', 1),
            
            # COE Courses
            ('Bachelor of Science in Civil Engineering', 'BSCE', 'Engineering program focusing on infrastructure and construction', 2),
            ('Bachelor of Science in Electrical Engineering', 'BSEE', 'Engineering program focusing on electrical systems and electronics', 2),
            
            # CBA Courses
            ('Bachelor of Science in Business Administration', 'BSBA', 'Comprehensive business program covering management, marketing, and finance', 3),
            ('Bachelor of Science in Accountancy', 'BSA', 'Professional accounting program preparing students for CPA certification', 3),
            
            # COED Courses
            ('Bachelor of Elementary Education', 'BEED', 'Teacher preparation program for elementary education', 4),
            ('Bachelor of Secondary Education', 'BSED', 'Teacher preparation program for secondary education', 4),
            
            # CAS Courses
            ('Bachelor of Arts in Psychology', 'AB-PSYC', 'Liberal arts program focusing on human behavior and mental processes', 5),
            ('Bachelor of Science in Biology', 'BS-BIO', 'Science program focusing on living organisms and biological processes', 5)
        ]
        
        for name, code, description, dept_id in courses_data:
            cursor.execute(
                "INSERT INTO courses (name, code, description, department_id, created_by) VALUES (%s, %s, %s, %s, %s)",
                (name, code, description, dept_id, 1)
            )
        
        connection.commit()
        print("✅ Database schema fixed successfully!")
        print("📊 Sample data added!")
        
        # Verify the tables
        cursor.execute("SELECT COUNT(*) FROM departments")
        dept_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM courses")
        course_count = cursor.fetchone()[0]
        
        print(f"📈 Created {dept_count} departments and {course_count} courses")
        
        cursor.close()
        connection.close()
        
        print("\n🎉 Database fix completed successfully!")
        print("You can now access:")
        print("- /admin/departments - Department management")
        print("- /admin/courses - Course management")
        
    except pymysql.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    print("🔧 Database Schema Fix Tool")
    print("=" * 40)
    
    response = input("This will recreate the departments and courses tables. Continue? (y/N): ")
    if response.lower() in ['y', 'yes']:
        fix_database()
    else:
        print("Operation cancelled.")
