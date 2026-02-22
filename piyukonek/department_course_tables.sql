-- SQL script to create departments and courses tables for PIYUKONEK system
-- Run this in your MySQL database

-- Drop existing tables if they exist (to avoid conflicts)
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS departments;

-- Create departments table
CREATE TABLE departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(20) NOT NULL UNIQUE,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT NOT NULL DEFAULT 1
);

-- Create courses table
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
);

-- Insert sample departments
INSERT INTO departments (name, code, description, created_by) VALUES
('College of Computer Studies', 'CCS', 'Offers programs in computer science, information technology, and related fields', 1),
('College of Engineering', 'COE', 'Provides engineering programs including civil, mechanical, and electrical engineering', 1),
('College of Business Administration', 'CBA', 'Offers business and management programs', 1),
('College of Education', 'COED', 'Prepares future educators and teachers', 1),
('College of Arts and Sciences', 'CAS', 'Liberal arts and sciences programs', 1);

-- Insert sample courses
INSERT INTO courses (name, code, description, department_id, created_by) VALUES
-- CCS Courses (department_id = 1)
('Bachelor of Science in Computer Science', 'BSCS', 'Four-year program focusing on computer programming, algorithms, and software development', 1, 1),
('Bachelor of Science in Information Technology', 'BSIT', 'Program focusing on information systems, networking, and technology management', 1, 1),
('Bachelor of Science in Information Systems', 'BSIS', 'Program combining business and technology for information management', 1, 1),

-- COE Courses (department_id = 2)
('Bachelor of Science in Civil Engineering', 'BSCE', 'Engineering program focusing on infrastructure and construction', 2, 1),
('Bachelor of Science in Electrical Engineering', 'BSEE', 'Engineering program focusing on electrical systems and electronics', 2, 1),
('Bachelor of Science in Mechanical Engineering', 'BSME', 'Engineering program focusing on mechanical systems and manufacturing', 2, 1),

-- CBA Courses (department_id = 3)
('Bachelor of Science in Business Administration', 'BSBA', 'Comprehensive business program covering management, marketing, and finance', 3, 1),
('Bachelor of Science in Accountancy', 'BSA', 'Professional accounting program preparing students for CPA certification', 3, 1),
('Bachelor of Science in Entrepreneurship', 'BSE', 'Program focusing on business creation and innovation', 3, 1),

-- COED Courses (department_id = 4)
('Bachelor of Elementary Education', 'BEED', 'Teacher preparation program for elementary education', 4, 1),
('Bachelor of Secondary Education', 'BSED', 'Teacher preparation program for secondary education', 4, 1),
('Bachelor of Physical Education', 'BPED', 'Program for physical education and sports instruction', 4, 1),

-- CAS Courses (department_id = 5)
('Bachelor of Arts in Psychology', 'AB-PSYC', 'Liberal arts program focusing on human behavior and mental processes', 5, 1),
('Bachelor of Science in Biology', 'BS-BIO', 'Science program focusing on living organisms and biological processes', 5, 1),
('Bachelor of Arts in English', 'AB-ENG', 'Liberal arts program focusing on English language and literature', 5, 1),
('Bachelor of Science in Mathematics', 'BS-MATH', 'Science program focusing on mathematical concepts and applications', 5, 1);

-- Verify the data was inserted correctly
SELECT 'Departments created:' as info, COUNT(*) as count FROM departments
UNION ALL
SELECT 'Courses created:' as info, COUNT(*) as count FROM courses;

-- Show the departments with their course counts
SELECT 
    d.name as department_name,
    d.code as department_code,
    COUNT(c.id) as course_count
FROM departments d
LEFT JOIN courses c ON d.id = c.department_id
GROUP BY d.id, d.name, d.code
ORDER BY d.name;
