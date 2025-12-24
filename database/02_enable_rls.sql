-- ============================================
-- Campus Climb Database - Enable Row Level Security
-- ============================================
-- This file enables RLS (Row Level Security) on all tables
-- and creates security policies
--
-- WHAT IS RLS?
-- Row Level Security is a PostgreSQL feature that lets you control
-- who can access which rows in a table. It's like having a bouncer
-- at a club checking IDs before letting people in.
--
-- WHY DO WE NEED IT?
-- Without RLS, anyone with database access can see/modify all data
-- With RLS, we can:
-- - Allow your Flask app (service role) full access
-- - Restrict public users to only read active opportunities
-- - Protect user data from unauthorized access
-- ============================================

-- ============================================
-- STEP 1: Enable RLS on Tables
-- ============================================
-- This turns on Row Level Security for each table
-- Once enabled, NO ONE can access rows unless a policy allows it
-- (This is why we need to create policies next)

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.opportunities ENABLE ROW LEVEL SECURITY;

-- ============================================
-- STEP 2: Drop Existing Policies (If Any)
-- ============================================
-- This ensures we start with a clean slate
-- Safe to run multiple times

DROP POLICY IF EXISTS "Service role can manage users" ON public.users;
DROP POLICY IF EXISTS "Users can read own profile" ON public.users;
DROP POLICY IF EXISTS "Users can update own profile" ON public.users;
DROP POLICY IF EXISTS "Service role can manage opportunities" ON public.opportunities;
DROP POLICY IF EXISTS "Public can read active opportunities" ON public.opportunities;

-- ============================================
-- STEP 3: Create RLS Policies for Users Table
-- ============================================

-- Policy 1: Service Role Full Access
-- WHO: Your Flask backend (using service role key)
-- WHAT: Can do everything (SELECT, INSERT, UPDATE, DELETE)
-- WHY: Your Flask app needs full access to manage users
--
-- HOW IT WORKS:
-- - service_role is a special PostgreSQL role
-- - Your DATABASE_URL uses service role credentials
-- - This policy allows all operations (USING true = always allow)

CREATE POLICY "Service role can manage users"
ON public.users
FOR ALL  -- All operations: SELECT, INSERT, UPDATE, DELETE
TO service_role
USING (true)  -- Always allow reading
WITH CHECK (true);  -- Always allow writing

-- Policy 2: Users Can Read Own Profile
-- WHO: Authenticated users (if using Supabase Auth)
-- WHAT: Can only read their own user record
-- WHY: Users should see their own profile
--
-- NOTE: This uses Supabase Auth's auth.uid() function
-- If you're not using Supabase Auth, this won't apply
-- Your Flask app handles auth separately

CREATE POLICY "Users can read own profile"
ON public.users
FOR SELECT  -- Read only
TO authenticated
USING (auth.uid()::text = id::text);  -- Only their own record

-- Policy 3: Users Can Update Own Profile
-- WHO: Authenticated users
-- WHAT: Can only update their own user record
-- WHY: Users should be able to update their own info

CREATE POLICY "Users can update own profile"
ON public.users
FOR UPDATE  -- Update only
TO authenticated
USING (auth.uid()::text = id::text)  -- Can only update their own
WITH CHECK (auth.uid()::text = id::text);  -- Must stay their own

-- ============================================
-- STEP 4: Create RLS Policies for Opportunities Table
-- ============================================

-- Policy 1: Service Role Full Access
-- WHO: Your Flask backend
-- WHAT: Can do everything with opportunities
-- WHY: Your Flask app manages all opportunities (CRUD operations)

CREATE POLICY "Service role can manage opportunities"
ON public.opportunities
FOR ALL  -- All operations
TO service_role
USING (true)
WITH CHECK (true);

-- Policy 2: Public Read Access (Active Opportunities Only)
-- WHO: Anyone (public users, authenticated users)
-- WHAT: Can only read opportunities where is_deleted = false
-- WHY: Your app shows opportunities to everyone, but hides deleted ones
--
-- HOW IT WORKS:
-- - anon = anonymous/public users
-- - authenticated = logged-in users (if using Supabase Auth)
-- - is_deleted = false OR is_deleted IS NULL = only active opportunities

CREATE POLICY "Public can read active opportunities"
ON public.opportunities
FOR SELECT  -- Read only
TO anon, authenticated  -- Both public and authenticated users
USING (is_deleted = false OR is_deleted IS NULL);  -- Only active ones

-- ============================================
-- Verification Queries
-- ============================================
-- Run these to verify RLS is enabled and policies exist

-- Check RLS is enabled
SELECT 
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'opportunities');

-- Check policies exist
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd
FROM pg_policies 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'opportunities')
ORDER BY tablename, policyname;

