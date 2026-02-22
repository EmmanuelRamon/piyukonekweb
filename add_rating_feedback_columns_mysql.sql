-- Migration: Add rating and feedback columns to concerns (MySQL)
-- Usage: Run this in your MySQL database used by the app

ALTER TABLE `concerns`
  ADD COLUMN IF NOT EXISTS `rating` INT NULL AFTER `closed_by`,
  ADD COLUMN IF NOT EXISTS `feedback` TEXT NULL AFTER `rating`,
  ADD COLUMN IF NOT EXISTS `feedback_submitted_at` DATETIME NULL AFTER `feedback`,
  ADD COLUMN IF NOT EXISTS `is_feedback_submitted` TINYINT(1) NOT NULL DEFAULT 0 AFTER `feedback_submitted_at`;



