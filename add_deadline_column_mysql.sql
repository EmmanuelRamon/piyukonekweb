-- MySQL syntax for adding deadline column to concerns table
ALTER TABLE concerns ADD COLUMN deadline DATETIME NULL;

-- Update existing concerns to have deadline set to 3 days from their submission date
UPDATE concerns 
SET deadline = DATE_ADD(submitted_at, INTERVAL 3 DAY)
WHERE deadline IS NULL;

-- Verify the column was added
DESCRIBE concerns;
