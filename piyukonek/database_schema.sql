-- =====================================================
-- PIYUKONEK DATABASE SCHEMA
-- Complete database structure with all columns
-- =====================================================

-- =====================================================
-- TABLE: user
-- =====================================================
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    password VARCHAR(120) NOT NULL,
    user_type VARCHAR(20) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- TABLE: students
-- =====================================================
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fullname VARCHAR(30) NOT NULL,
    username VARCHAR(20) UNIQUE NOT NULL,
    student_id_number VARCHAR(20) NOT NULL,
    email_address VARCHAR(30) UNIQUE NOT NULL,
    course VARCHAR(50) NOT NULL,
    college_dept VARCHAR(70) NOT NULL,
    year_lvl VARCHAR(20) NOT NULL,
    cert_of_registration VARCHAR(100) NOT NULL,
    student_id VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    status VARCHAR(10) DEFAULT 'active',
    profile_image VARCHAR(255),
    is_online BOOLEAN DEFAULT FALSE,
    last_seen DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- TABLE: ssc
-- =====================================================
CREATE TABLE ssc (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fullname VARCHAR(50) NOT NULL,
    username VARCHAR(30) UNIQUE NOT NULL,
    email_address VARCHAR(50) UNIQUE NOT NULL,
    position VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    profile_image VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_online BOOLEAN DEFAULT FALSE,
    last_seen DATETIME,
    status VARCHAR(10) DEFAULT 'active'
);

-- =====================================================
-- TABLE: admin
-- =====================================================
CREATE TABLE admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fullname VARCHAR(50) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    email_address VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    profile_image VARCHAR(255)
);

-- =====================================================
-- TABLE: concerns
-- =====================================================
CREATE TABLE concerns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    concern_type VARCHAR(50) NOT NULL,
    priority_level VARCHAR(20) NOT NULL,
    docs VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending',
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME,
    resolved_by INTEGER,
    resolution_notes TEXT,
    response_attachment VARCHAR(255),
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (resolved_by) REFERENCES ssc(id)
);

-- =====================================================
-- TABLE: notifications
-- =====================================================
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    user_type VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    concern_id INTEGER,
    FOREIGN KEY (concern_id) REFERENCES concerns(id)
);

-- =====================================================
-- TABLE: messages
-- =====================================================
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    sender_type VARCHAR(20) NOT NULL,
    recipient_id INTEGER NOT NULL,
    recipient_type VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    attachment_path VARCHAR(255),
    attachment_name VARCHAR(255),
    attachment_type VARCHAR(50),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    concern_id INTEGER,
    FOREIGN KEY (concern_id) REFERENCES concerns(id)
);

-- =====================================================
-- TABLE: concern_history
-- =====================================================
CREATE TABLE concern_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    concern_id INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL,
    action VARCHAR(255) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (concern_id) REFERENCES concerns(id)
);

-- =====================================================
-- INDEXES FOR BETTER PERFORMANCE
-- =====================================================

-- User table indexes
CREATE INDEX idx_user_username ON user(username);
CREATE INDEX idx_user_email ON user(email);
CREATE INDEX idx_user_type ON user(user_type);

-- Students table indexes
CREATE INDEX idx_students_username ON students(username);
CREATE INDEX idx_students_email ON students(email_address);
CREATE INDEX idx_students_status ON students(status);
CREATE INDEX idx_students_online ON students(is_online);

-- SSC table indexes
CREATE INDEX idx_ssc_username ON ssc(username);
CREATE INDEX idx_ssc_email ON ssc(email_address);
CREATE INDEX idx_ssc_status ON ssc(status);
CREATE INDEX idx_ssc_online ON ssc(is_online);

-- Admin table indexes
CREATE INDEX idx_admin_username ON admin(username);
CREATE INDEX idx_admin_email ON admin(email_address);

-- Concerns table indexes
CREATE INDEX idx_concerns_student_id ON concerns(student_id);
CREATE INDEX idx_concerns_status ON concerns(status);
CREATE INDEX idx_concerns_type ON concerns(concern_type);
CREATE INDEX idx_concerns_priority ON concerns(priority_level);
CREATE INDEX idx_concerns_submitted_at ON concerns(submitted_at);
CREATE INDEX idx_concerns_resolved_by ON concerns(resolved_by);

-- Notifications table indexes
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_user_type ON notifications(user_type);
CREATE INDEX idx_notifications_concern_id ON notifications(concern_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);

-- Messages table indexes
CREATE INDEX idx_messages_sender_id ON messages(sender_id);
CREATE INDEX idx_messages_recipient_id ON messages(recipient_id);
CREATE INDEX idx_messages_concern_id ON messages(concern_id);
CREATE INDEX idx_messages_timestamp ON messages(timestamp);

-- Concern history table indexes
CREATE INDEX idx_concern_history_concern_id ON concern_history(concern_id);
CREATE INDEX idx_concern_history_status ON concern_history(status);
CREATE INDEX idx_concern_history_timestamp ON concern_history(timestamp);

-- =====================================================
-- SAMPLE DATA INSERTION QUERIES
-- =====================================================

-- Insert sample admin user
INSERT INTO admin (fullname, username, email_address, password) 
VALUES ('System Administrator', 'admin', 'admin@lspu.edu.ph', 'hashed_password_here');

-- Insert sample SSC staff
INSERT INTO ssc (fullname, username, email_address, position, password, status) 
VALUES ('SSC Staff Member', 'ssc_staff', 'ssc@lspu.edu.ph', 'Student Support Coordinator', 'hashed_password_here', 'active');

-- Insert sample student
INSERT INTO students (fullname, username, student_id_number, email_address, course, college_dept, year_lvl, cert_of_registration, student_id, password, status) 
VALUES ('Sample Student', 'student1', '2021-0001', 'student@lspu.edu.ph', 'BSIT', 'College of Engineering', '3rd Year', 'cert_file.pdf', 'STUDENT001', 'hashed_password_here', 'active');

-- =====================================================
-- USEFUL QUERY EXAMPLES
-- =====================================================

-- Get all students with their concern counts
SELECT 
    s.id,
    s.fullname,
    s.email_address,
    s.course,
    COUNT(c.id) as total_concerns,
    COUNT(CASE WHEN c.status = 'pending' THEN 1 END) as pending_concerns,
    COUNT(CASE WHEN c.status = 'resolved' THEN 1 END) as resolved_concerns
FROM students s
LEFT JOIN concerns c ON s.id = c.student_id
GROUP BY s.id, s.fullname, s.email_address, s.course;

-- Get all concerns with student and resolver information
SELECT 
    c.id,
    c.title,
    c.description,
    c.concern_type,
    c.priority_level,
    c.status,
    c.submitted_at,
    s.fullname as student_name,
    ssc.fullname as resolver_name
FROM concerns c
JOIN students s ON c.student_id = s.id
LEFT JOIN ssc ON c.resolved_by = ssc.id
ORDER BY c.submitted_at DESC;

-- Get unread notifications for a specific user
SELECT 
    n.id,
    n.title,
    n.message,
    n.notification_type,
    n.created_at
FROM notifications n
WHERE n.user_id = ? AND n.user_type = ? AND n.is_read = FALSE
ORDER BY n.created_at DESC;

-- Get recent messages for a conversation
SELECT 
    m.id,
    m.content,
    m.sender_type,
    m.sender_id,
    m.timestamp,
    m.attachment_name
FROM messages m
WHERE (m.sender_id = ? AND m.recipient_id = ?) 
   OR (m.sender_id = ? AND m.recipient_id = ?)
ORDER BY m.timestamp ASC;

-- Get concern history for a specific concern
SELECT 
    ch.status,
    ch.action,
    ch.timestamp
FROM concern_history ch
WHERE ch.concern_id = ?
ORDER BY ch.timestamp ASC;

-- =====================================================
-- CLEANUP QUERIES (USE WITH CAUTION!)
-- =====================================================

-- Delete all data from all tables (in correct order due to foreign keys)
DELETE FROM concern_history;
DELETE FROM messages;
DELETE FROM notifications;
DELETE FROM concerns;
DELETE FROM students;
DELETE FROM ssc;
DELETE FROM admin;
DELETE FROM user;

-- Reset auto-increment counters (SQLite specific)
DELETE FROM sqlite_sequence WHERE name IN ('user', 'students', 'ssc', 'admin', 'concerns', 'notifications', 'messages', 'concern_history');

-- =====================================================
-- DATABASE STATISTICS QUERIES
-- =====================================================

-- Get total counts for each table
SELECT 'user' as table_name, COUNT(*) as count FROM user
UNION ALL
SELECT 'students', COUNT(*) FROM students
UNION ALL
SELECT 'ssc', COUNT(*) FROM ssc
UNION ALL
SELECT 'admin', COUNT(*) FROM admin
UNION ALL
SELECT 'concerns', COUNT(*) FROM concerns
UNION ALL
SELECT 'notifications', COUNT(*) FROM notifications
UNION ALL
SELECT 'messages', COUNT(*) FROM messages
UNION ALL
SELECT 'concern_history', COUNT(*) FROM concern_history;

-- Get concern statistics by status
SELECT 
    status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM concerns), 2) as percentage
FROM concerns
GROUP BY status;

-- Get concern statistics by type
SELECT 
    concern_type,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM concerns), 2) as percentage
FROM concerns
GROUP BY concern_type;

-- Get concern statistics by priority
SELECT 
    priority_level,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM concerns), 2) as percentage
FROM concerns
GROUP BY priority_level; 