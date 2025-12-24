# 🔧 Fixed Instructions: Enable RLS on Supabase

## The Problem
You got an error: `relation "public.users" does not exist`

This means the tables haven't been created in Supabase yet. Your Flask app creates them automatically when it runs, but we need to create them manually in Supabase first.

## ✅ Solution: Run These Files in Order

### Step 1: Check What Tables Exist
1. Open Supabase SQL Editor
2. Run `STEP1_check_tables.sql`
3. **Check the results** - Do you see `users` and `opportunities` tables?

### Step 2A: If Tables DON'T Exist
- Run `STEP2_create_tables_if_needed.sql` to create them
- This creates the tables with the correct structure

### Step 2B: If Tables DO Exist
- Skip to Step 3

### Step 3: Enable RLS
- Run `enable_rls.sql` (updated version that checks if tables exist first)
- This will enable RLS and create the security policies

## 🚀 Quick Fix (All-in-One)

If you want to do it all at once, run this in order:

1. **STEP1_check_tables.sql** - See what exists
2. **STEP2_create_tables_if_needed.sql** - Create tables (safe to run even if they exist)
3. **enable_rls.sql** - Enable RLS

## 📝 Alternative: Let Flask Create Tables

If you prefer, you can also:
1. Deploy your Flask app to Vercel (if not already)
2. Make a request to any API endpoint
3. The `@app.before_request` hook will create the tables automatically
4. Then run `enable_rls.sql` to enable RLS

## ✅ Verification

After running all steps, verify:
```sql
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'opportunities');
```

Both tables should show `rowsecurity = true`

