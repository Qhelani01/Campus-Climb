-- Diagnostic Query: Check what tables exist in your database
-- Run this FIRST to see what tables you actually have

-- Check all tables in public schema
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- Check if RLS is enabled on existing tables
SELECT 
    schemaname,
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- Check for tables with similar names (case-insensitive search)
SELECT 
    schemaname,
    tablename
FROM pg_tables 
WHERE schemaname = 'public'
AND (
    tablename ILIKE '%user%' 
    OR tablename ILIKE '%opportunit%'
)
ORDER BY tablename;

