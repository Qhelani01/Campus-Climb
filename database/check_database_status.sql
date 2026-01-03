-- ============================================
-- Quick Database Health Check
-- ============================================
-- Run this in Supabase SQL Editor to check your database status
-- This will tell you what's set up and what's missing
-- ============================================

-- Check 1: Do tables exist?
SELECT 
    CASE 
        WHEN COUNT(*) = 2 THEN '✅ Both tables exist'
        WHEN COUNT(*) = 1 THEN '⚠️ Only one table exists'
        ELSE '❌ Tables are missing - Run 01_complete_schema.sql'
    END as table_status,
    COUNT(*) as tables_found,
    STRING_AGG(tablename, ', ') as existing_tables
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'opportunities');

-- Check 2: Is RLS enabled?
-- First, get overall RLS status
SELECT 
    CASE 
        WHEN COUNT(*) = 2 AND COUNT(*) FILTER (WHERE c.relrowsecurity = true) = 2 THEN '✅ RLS enabled on both tables'
        WHEN COUNT(*) = 2 AND COUNT(*) FILTER (WHERE c.relrowsecurity = true) = 1 THEN '⚠️ RLS enabled on only one table - Run 02_enable_rls.sql'
        WHEN COUNT(*) = 2 THEN '❌ RLS not enabled - Run 02_enable_rls.sql'
        ELSE '❌ Tables missing - Run 01_complete_schema.sql first'
    END as rls_status
FROM pg_tables t
JOIN pg_class c ON c.relname = t.tablename
JOIN pg_namespace n ON n.oid = c.relnamespace AND n.nspname = t.schemaname
WHERE t.schemaname = 'public' 
AND t.tablename IN ('users', 'opportunities');

-- Then, get per-table RLS status
SELECT 
    t.tablename,
    CASE 
        WHEN c.relrowsecurity = true THEN '✅ Enabled'
        ELSE '❌ Disabled'
    END as rls_state
FROM pg_tables t
JOIN pg_class c ON c.relname = t.tablename
JOIN pg_namespace n ON n.oid = c.relnamespace AND n.nspname = t.schemaname
WHERE t.schemaname = 'public' 
AND t.tablename IN ('users', 'opportunities')
ORDER BY t.tablename;

-- Check 3: Do policies exist?
SELECT 
    CASE 
        WHEN COUNT(*) >= 5 THEN '✅ All policies exist'
        WHEN COUNT(*) > 0 THEN '⚠️ Some policies missing - Run 02_enable_rls.sql'
        ELSE '❌ No policies found - Run 02_enable_rls.sql'
    END as policy_status,
    COUNT(*) as policies_found,
    STRING_AGG(policyname, ', ') as existing_policies
FROM pg_policies 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'opportunities');

-- Check 4: Do indexes exist?
SELECT 
    CASE 
        WHEN COUNT(*) >= 8 THEN '✅ All indexes exist'
        WHEN COUNT(*) > 0 THEN '⚠️ Some indexes missing - Run 01_complete_schema.sql'
        ELSE '❌ No indexes found - Run 01_complete_schema.sql'
    END as index_status,
    COUNT(*) as indexes_found
FROM pg_indexes 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'opportunities');

-- Check 5: Overall Status Summary
SELECT 
    '📊 DATABASE STATUS SUMMARY' as summary,
    (SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public' AND tablename IN ('users', 'opportunities')) as tables_exist,
    (SELECT COUNT(*) 
     FROM pg_tables t
     JOIN pg_class c ON c.relname = t.tablename
     JOIN pg_namespace n ON n.oid = c.relnamespace AND n.nspname = t.schemaname
     WHERE t.schemaname = 'public' 
     AND t.tablename IN ('users', 'opportunities')
     AND c.relrowsecurity = true) as rls_enabled,
    (SELECT COUNT(*) FROM pg_policies WHERE schemaname = 'public' AND tablename IN ('users', 'opportunities')) as policies_exist,
    (SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public' AND tablename IN ('users', 'opportunities')) as indexes_exist,
    CASE 
        WHEN (SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public' AND tablename IN ('users', 'opportunities')) = 2
         AND (SELECT COUNT(*) 
              FROM pg_tables t
              JOIN pg_class c ON c.relname = t.tablename
              JOIN pg_namespace n ON n.oid = c.relnamespace AND n.nspname = t.schemaname
              WHERE t.schemaname = 'public' 
              AND t.tablename IN ('users', 'opportunities')
              AND c.relrowsecurity = true) = 2
         AND (SELECT COUNT(*) FROM pg_policies WHERE schemaname = 'public' AND tablename IN ('users', 'opportunities')) >= 5
        THEN '✅ Everything looks good!'
        ELSE '⚠️ Some setup steps may be missing'
    END as overall_status;

