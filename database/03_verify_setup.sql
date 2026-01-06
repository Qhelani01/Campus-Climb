-- ============================================
-- Campus Climb Database - Setup Verification
-- ============================================
-- Run this after completing steps 1 and 2
-- It checks that everything is set up correctly
-- ============================================

-- ============================================
-- CHECK 1: Tables Exist
-- ============================================
SELECT 
    '✅ Tables Check' as check_name,
    tablename,
    CASE 
        WHEN tablename IN ('users', 'opportunities') THEN '✅ Exists'
        ELSE '❌ Missing'
    END as status
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'opportunities')
ORDER BY tablename;

-- ============================================
-- CHECK 2: RLS is Enabled
-- ============================================
SELECT 
    '✅ RLS Check' as check_name,
    tablename,
    CASE 
        WHEN rowsecurity = true THEN '✅ RLS Enabled'
        ELSE '❌ RLS Disabled'
    END as status
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'opportunities')
ORDER BY tablename;

-- ============================================
-- CHECK 3: Indexes Exist
-- ============================================
SELECT 
    '✅ Indexes Check' as check_name,
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'opportunities')
ORDER BY tablename, indexname;

-- ============================================
-- CHECK 4: RLS Policies Exist
-- ============================================
SELECT 
    '✅ Policies Check' as check_name,
    tablename,
    policyname,
    permissive,
    roles,
    cmd as operation
FROM pg_policies 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'opportunities')
ORDER BY tablename, policyname;

-- ============================================
-- CHECK 5: Triggers Exist (for auto-update)
-- ============================================
SELECT 
    '✅ Triggers Check' as check_name,
    trigger_name,
    event_manipulation,
    event_object_table,
    action_statement
FROM information_schema.triggers
WHERE trigger_schema = 'public'
AND event_object_table IN ('users', 'opportunities')
ORDER BY event_object_table, trigger_name;

-- ============================================
-- SUMMARY: All Checks
-- ============================================
SELECT 
    '📊 SETUP SUMMARY' as summary,
    (SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public' AND tablename IN ('users', 'opportunities')) as tables_count,
    (SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public' AND tablename IN ('users', 'opportunities') AND rowsecurity = true) as rls_enabled_count,
    (SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public' AND tablename IN ('users', 'opportunities')) as indexes_count,
    (SELECT COUNT(*) FROM pg_policies WHERE schemaname = 'public' AND tablename IN ('users', 'opportunities')) as policies_count;






