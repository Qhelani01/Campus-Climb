# Database Migrations

This directory contains SQL migration files for the Campus Climb database.

## 🔒 Security Fixes

### Issue: Row Level Security (RLS) Not Enabled

Supabase detected that your tables are public but RLS is not enabled. This is a security concern.

## 📋 How to Apply Migrations

### Option 1: Using Supabase Dashboard (Recommended)

1. **Open Supabase Dashboard**
   - Go to your Supabase project dashboard
   - Navigate to **SQL Editor** (left sidebar)

2. **Run the Migration**
   - Click **New Query**
   - Copy and paste the contents of `enable_rls.sql`
   - Click **Run** (or press `Cmd/Ctrl + Enter`)

3. **Verify RLS is Enabled**
   - Go to **Database** → **Tables**
   - Click on `users` table
   - Check that "Row Level Security" shows as **Enabled**
   - Repeat for `opportunities` table

### Option 2: Using Supabase CLI

```bash
# Install Supabase CLI (if not already installed)
npm install -g supabase

# Login to Supabase
supabase login

# Link your project
supabase link --project-ref your-project-ref

# Run migration
supabase db push
```

## 🔐 Understanding RLS Policies

The migration creates the following policies:

### Users Table Policies:
- **Service Role Access**: Your Flask backend (using service role key) has full access
- **User Self-Access**: Authenticated users can read/update their own profile

### Opportunities Table Policies:
- **Service Role Access**: Your Flask backend has full access for CRUD operations
- **Public Read Access**: Anyone can read active (non-deleted) opportunities

## ⚠️ Important Notes

1. **Service Role Key**: Your Flask app should use the **service role key** (not the anon key) to bypass RLS restrictions. This is safe because:
   - The service role key is only used server-side
   - It's never exposed to the frontend
   - Your Flask app handles authentication separately

2. **Database URL**: Make sure your `DATABASE_URL` environment variable in Vercel uses the connection string with service role credentials.

3. **Testing**: After applying migrations, test your API endpoints to ensure they still work correctly.

## 🐛 Troubleshooting

### Issue: "Policy already exists"
- The migration includes `DROP POLICY IF EXISTS` statements
- Re-run the migration - it will drop and recreate policies

### Issue: "Table does not exist"
- Make sure your tables are named `users` and `opportunities` (or `user` and `opportunity`)
- The migration handles both naming conventions

### Issue: API endpoints not working after migration
- Verify your `DATABASE_URL` uses the service role connection string
- Check that RLS policies allow service role access
- Review Supabase logs for any RLS policy violations

## 📚 Additional Resources

- [Supabase RLS Documentation](https://supabase.com/docs/guides/auth/row-level-security)
- [RLS Policy Examples](https://supabase.com/docs/guides/auth/row-level-security#policy-examples)

