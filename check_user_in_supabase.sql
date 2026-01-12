-- Run this query in Supabase SQL Editor to check your admin user
-- This will help diagnose the login issue

-- Check if user exists and their admin status
SELECT 
    id,
    email,
    first_name,
    last_name,
    is_admin,
    CASE 
        WHEN is_admin IS NULL THEN 'NULL (needs to be TRUE)'
        WHEN is_admin = true THEN 'TRUE ✓'
        ELSE 'FALSE (needs to be TRUE)'
    END as admin_status,
    CASE 
        WHEN password_hash IS NULL THEN 'NULL (no password set)'
        WHEN LENGTH(password_hash) > 0 THEN 'SET ✓'
        ELSE 'EMPTY'
    END as password_status,
    created_at
FROM users
WHERE LOWER(email) = LOWER('qhestoemoyo@gmail.com');

-- If user doesn't exist or is_admin is not TRUE, run this to fix:
-- UPDATE users 
-- SET is_admin = TRUE 
-- WHERE LOWER(email) = LOWER('qhestoemoyo@gmail.com');

-- To check all users with admin status:
-- SELECT email, first_name, last_name, is_admin 
-- FROM users 
-- ORDER BY is_admin DESC, email;
