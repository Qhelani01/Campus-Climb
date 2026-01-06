-- ============================================
-- Migration: Add user profile fields for AI Assistant
-- ============================================
-- This migration adds resume_summary, skills, and career_goals columns
-- to the users table for the AI application assistant feature
--
-- SAFE TO RUN: This will not delete any data
-- ============================================

-- Add resume_summary column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'users' 
        AND column_name = 'resume_summary'
    ) THEN
        ALTER TABLE public.users 
        ADD COLUMN resume_summary TEXT;
        
        RAISE NOTICE 'Added resume_summary column to users table';
    ELSE
        RAISE NOTICE 'resume_summary column already exists';
    END IF;
END $$;

-- Add skills column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'users' 
        AND column_name = 'skills'
    ) THEN
        ALTER TABLE public.users 
        ADD COLUMN skills TEXT;
        
        RAISE NOTICE 'Added skills column to users table';
    ELSE
        RAISE NOTICE 'skills column already exists';
    END IF;
END $$;

-- Add career_goals column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'users' 
        AND column_name = 'career_goals'
    ) THEN
        ALTER TABLE public.users 
        ADD COLUMN career_goals TEXT;
        
        RAISE NOTICE 'Added career_goals column to users table';
    ELSE
        RAISE NOTICE 'career_goals column already exists';
    END IF;
END $$;

-- ============================================
-- Verification Query
-- ============================================
-- Run this to verify the columns were added:
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'users'
AND column_name IN ('resume_summary', 'skills', 'career_goals')
ORDER BY column_name;

