-- STEP 1: Check what tables exist in your Supabase database
-- Run this FIRST to see what tables you actually have

-- Check all tables in public schema
SELECT 
    schemaname,
    tablename,
    tableowner,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- Check specifically for user/opportunity related tables
SELECT 
    schemaname,
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE schemaname = 'public'
AND (
    tablename ILIKE '%user%' 
    OR tablename ILIKE '%opportunit%'
)
ORDER BY tablename;

