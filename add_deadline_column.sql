-- Add deadline column to concerns table
ALTER TABLE concerns ADD COLUMN deadline DATETIME NULL;

-- Update existing concerns to have deadline set to 3 days from their submission date
UPDATE concerns 
SET deadline = datetime(submitted_at, '+3 days')
WHERE deadline IS NULL;

-- Verify the column was added
PRAGMA table_info(concerns);
