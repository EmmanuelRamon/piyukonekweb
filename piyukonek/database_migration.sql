-- Database migration to add online status tracking to students table
-- Run this script to update your existing database

-- Add online status columns to students table
ALTER TABLE students ADD COLUMN is_online BOOLEAN DEFAULT FALSE;
ALTER TABLE students ADD COLUMN last_seen DATETIME;

-- Update existing students to have offline status
UPDATE students SET is_online = FALSE WHERE is_online IS NULL;

-- Create index for better performance on online status queries
CREATE INDEX idx_students_online_status ON students(is_online, last_seen); 