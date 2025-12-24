# Quick Start: Fix Supabase Security Issues

## 🚨 Issues to Fix
1. ✅ Table `public.opportunity` - RLS not enabled
2. ✅ Table `public.user` - RLS not enabled  
3. ⚠️ PostgreSQL version (optional - usually auto-updated by Supabase)

## ⚡ Quick Fix (5-10 minutes)

### IMPORTANT: If you got "table does not exist" error
The tables might not be created in Supabase yet. Follow these steps:

### Step 1: Check What Tables Exist
1. Open Supabase SQL Editor
2. Run `STEP1_check_tables.sql`
3. Check if `users` and `opportunities` tables exist

### Step 2: Create Tables (If Needed)
**Only if tables don't exist:**
1. Run `STEP2_create_tables_if_needed.sql`
2. This safely creates the tables with correct structure

**OR** - Let Flask create them:
- Deploy your app and make an API call
- Tables will be created automatically

### Step 3: Enable RLS
1. Run `enable_rls.sql` (updated version)
2. This enables RLS and creates security policies

### Step 4: Verify It Worked
1. Go to **Database** → **Tables**
2. Click on `users` table
3. Check that **"Row Level Security"** shows as **Enabled** ✅
4. Repeat for `opportunities` table

### Step 5: Test Your App
- Your Flask app should continue working normally
- The service role policies allow your backend full access
- Public users can only read active opportunities

## ✅ Done!

After running all steps, the 3 security issues should be resolved. The Supabase dashboard should update within a few minutes.

## 🔍 Troubleshooting

**If you get "policy already exists" error:**
- The migration includes DROP statements, so you can safely re-run it

**If your API stops working:**
- Verify your `DATABASE_URL` uses the **service role** connection string
- Check Supabase logs for any RLS violations

**If tables are named differently:**
- The migration handles both `users`/`user` and `opportunities`/`opportunity`
- If you have different names, update the SQL accordingly

