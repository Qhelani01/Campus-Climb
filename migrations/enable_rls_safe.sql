-- Migration: Enable Row Level Security (RLS) on Campus Climb tables
-- SAFE VERSION: Only enables RLS if tables exist
-- Run this AFTER checking what tables exist with check_tables.sql

-- ============================================
-- STEP 1: First, check what tables exist
-- ============================================
-- Run check_tables.sql first to see your actual table names
-- Then update the table names below to match your database

-- ============================================
-- STEP 2: Enable RLS on users table
-- ============================================
-- Try different possible table names (uncomment the one that matches your database)
-- ALTER TABLE IF EXISTS public.users ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE IF EXISTS public.user ENABLE ROW LEVEL SECURITY;

-- ============================================
-- STEP 3: Enable RLS on opportunities table
-- ============================================
-- Try different possible table names (uncomment the one that matches your database)
-- ALTER TABLE IF EXISTS public.opportunities ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE IF EXISTS public.opportunity ENABLE ROW LEVEL SECURITY;

-- ============================================
-- STEP 4: Drop existing policies if they exist
-- ============================================
-- Uncomment and update table names based on what exists
-- DROP POLICY IF EXISTS "Service role can manage users" ON public.users;
-- DROP POLICY IF EXISTS "Users can read own profile" ON public.users;
-- DROP POLICY IF EXISTS "Users can update own profile" ON public.users;
-- DROP POLICY IF EXISTS "Service role can manage opportunities" ON public.opportunities;
-- DROP POLICY IF EXISTS "Public can read active opportunities" ON public.opportunities;

-- ============================================
-- STEP 5: Create RLS Policies
-- ============================================
-- Uncomment and update table names based on what exists

-- Users table policies:
-- CREATE POLICY "Service role can manage users"
-- ON public.users  -- Update table name
-- FOR ALL
-- TO service_role
-- USING (true)
-- WITH CHECK (true);

-- CREATE POLICY "Users can read own profile"
-- ON public.users  -- Update table name
-- FOR SELECT
-- TO authenticated
-- USING (auth.uid()::text = id::text);

-- CREATE POLICY "Users can update own profile"
-- ON public.users  -- Update table name
-- FOR UPDATE
-- TO authenticated
-- USING (auth.uid()::text = id::text)
-- WITH CHECK (auth.uid()::text = id::text);

-- Opportunities table policies:
-- CREATE POLICY "Service role can manage opportunities"
-- ON public.opportunities  -- Update table name
-- FOR ALL
-- TO service_role
-- USING (true)
-- WITH CHECK (true);

-- CREATE POLICY "Public can read active opportunities"
-- ON public.opportunities  -- Update table name
-- FOR SELECT
-- TO anon, authenticated
-- USING (is_deleted = false OR is_deleted IS NULL);

