-- Migration: Enable Row Level Security (RLS) on Campus Climb tables
-- This fixes the Supabase security issues by enabling RLS on public tables
-- 
-- IMPORTANT: Run these files in order:
-- 1. STEP1_check_tables.sql - Check what tables exist
-- 2. STEP2_create_tables_if_needed.sql - Create tables if missing (only if needed)
-- 3. enable_rls.sql - Enable RLS (this file)
--
-- Run this in your Supabase SQL Editor

-- ============================================
-- 1. Enable RLS on users table
-- ============================================
-- Only enable if table exists (will fail silently if table doesn't exist)
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'users') THEN
        ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'RLS enabled on public.users';
    ELSE
        RAISE NOTICE 'Table public.users does not exist. Run STEP2_create_tables_if_needed.sql first.';
    END IF;
END $$;

-- ============================================
-- 2. Enable RLS on opportunities table
-- ============================================
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'opportunities') THEN
        ALTER TABLE public.opportunities ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'RLS enabled on public.opportunities';
    ELSE
        RAISE NOTICE 'Table public.opportunities does not exist. Run STEP2_create_tables_if_needed.sql first.';
    END IF;
END $$;

-- ============================================
-- 3. Drop existing policies if they exist (for re-running)
-- ============================================
DROP POLICY IF EXISTS "Service role can manage users" ON public.users;
DROP POLICY IF EXISTS "Users can read own profile" ON public.users;
DROP POLICY IF EXISTS "Users can update own profile" ON public.users;
DROP POLICY IF EXISTS "Service role can manage opportunities" ON public.opportunities;
DROP POLICY IF EXISTS "Public can read active opportunities" ON public.opportunities;

-- ============================================
-- 4. Create RLS Policies for users table
-- ============================================

-- Policy: Allow service role (Flask backend) full access to users
-- This allows your Flask app to read/write users using the service role key
CREATE POLICY "Service role can manage users"
ON public.users
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- Policy: Allow authenticated users to read their own profile
-- This allows users to read their own data if using Supabase Auth
CREATE POLICY "Users can read own profile"
ON public.users
FOR SELECT
TO authenticated
USING (auth.uid()::text = id::text);

-- Policy: Allow authenticated users to update their own profile
CREATE POLICY "Users can update own profile"
ON public.users
FOR UPDATE
TO authenticated
USING (auth.uid()::text = id::text)
WITH CHECK (auth.uid()::text = id::text);

-- ============================================
-- 5. Create RLS Policies for opportunities table
-- ============================================

-- Policy: Allow service role (Flask backend) full access to opportunities
-- This allows your Flask app to read/write opportunities using the service role key
CREATE POLICY "Service role can manage opportunities"
ON public.opportunities
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- Policy: Allow public read access to non-deleted opportunities
-- This allows anyone to view active opportunities (for your public-facing app)
CREATE POLICY "Public can read active opportunities"
ON public.opportunities
FOR SELECT
TO anon, authenticated
USING (is_deleted = false OR is_deleted IS NULL);

-- ============================================
-- Verification queries (run these to verify RLS is enabled)
-- ============================================
-- SELECT tablename, rowsecurity 
-- FROM pg_tables 
-- WHERE schemaname = 'public' 
-- AND tablename IN ('users', 'user', 'opportunities', 'opportunity');

-- SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
-- FROM pg_policies 
-- WHERE schemaname = 'public' 
-- AND tablename IN ('users', 'opportunities');
