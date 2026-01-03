-- ============================================
-- Migration: Add is_admin column to users table
-- ============================================
-- This migration adds the is_admin column to existing databases
-- Run this if you have an existing database without the is_admin column
--
-- SAFE TO RUN: This will not delete any data
-- ============================================

-- Check if column already exists before adding
DO $$ 
BEGIN
    -- Add is_admin column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'users' 
        AND column_name = 'is_admin'
    ) THEN
        ALTER TABLE public.users 
        ADD COLUMN is_admin BOOLEAN DEFAULT FALSE NOT NULL;
        
        RAISE NOTICE 'Added is_admin column to users table';
    ELSE
        RAISE NOTICE 'is_admin column already exists';
    END IF;
END $$;

-- Create index on is_admin for faster admin queries
CREATE INDEX IF NOT EXISTS idx_users_is_admin ON public.users(is_admin);

-- ============================================
-- Verification Query
-- ============================================
-- Run this to verify the column was added:
SELECT 
    column_name,
    data_type,
    column_default,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'users'
AND column_name = 'is_admin';

