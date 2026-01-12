-- Reset password for admin user in Supabase
-- This will set the password hash for 'admin123' password
-- Run this in Supabase SQL Editor

-- First, generate the password hash using Python (run this locally):
-- python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('admin123'))"

-- Then update the user with the generated hash:
-- UPDATE users 
-- SET password_hash = 'GENERATED_HASH_HERE'
-- WHERE email = 'qhestoemoyo@gmail.com';

-- OR use this Python script approach (recommended):
-- The password hash for 'admin123' should start with 'scrypt:32768:8:1$'

-- Quick fix: Update password using a known hash format
-- Note: You'll need to generate this hash first using the Python script above

-- Alternative: Use the setup endpoint after deployment:
-- curl -X POST https://campus-climb.vercel.app/api/setup/admin \
--   -H "Content-Type: application/json" \
--   -H "X-Setup-Token: YOUR_SETUP_TOKEN" \
--   -d '{"email":"qhestoemoyo@gmail.com","password":"admin123","first_name":"Qhelani","last_name":"Moyo"}'
