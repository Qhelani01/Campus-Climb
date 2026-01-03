# 🗄️ Campus Climb Database Setup Guide

This directory contains the complete database setup for Campus Climb. We'll build it step-by-step and explain everything as we go.

## 📚 What You'll Learn

1. **Database Schema Design** - How to structure your data
2. **Indexes** - Making queries fast
3. **Row Level Security (RLS)** - Protecting your data
4. **PostgreSQL Features** - Triggers, functions, and more

## 🏗️ Architecture Overview

```
┌─────────────────┐
│   Flask App     │  ← Your Python backend
│  (SQLAlchemy)   │
└────────┬────────┘
         │
         │ Uses DATABASE_URL
         │
         ▼
┌─────────────────┐
│   Supabase      │  ← PostgreSQL database
│   PostgreSQL    │
└─────────────────┘
```

**How it works:**
- Flask app uses SQLAlchemy ORM (Object-Relational Mapping)
- SQLAlchemy converts Python code to SQL queries
- Queries go to Supabase PostgreSQL database
- RLS policies control who can access what

## 📁 Files in This Directory

### `01_complete_schema.sql`
**What it does:** Creates all tables, indexes, and triggers from scratch

**Key concepts:**
- **Tables**: Where data is stored (like spreadsheets)
- **Indexes**: Speed up queries (like book indexes)
- **Triggers**: Auto-update timestamps
- **Constraints**: Rules for data (unique emails, required fields)

### `02_enable_rls.sql`
**What it does:** Enables security (Row Level Security) on all tables

**Key concepts:**
- **RLS**: Controls who can see/modify which rows
- **Policies**: Rules that define access permissions
- **Service Role**: Special role for your Flask app (full access)
- **Public Access**: Rules for public users (read-only)

## 🚀 Setup Instructions

### Step 1: Create the Schema

1. Open Supabase Dashboard → **SQL Editor**
2. Click **New Query**
3. Copy and paste the entire contents of `01_complete_schema.sql`
4. Click **Run** (or `Cmd/Ctrl + Enter`)

**What happens:**
- Drops any existing tables (fresh start)
- Creates `users` and `opportunities` tables
- Creates all indexes for performance
- Sets up auto-update triggers

**Expected output:**
- Should see "Success" message
- Tables appear in Database → Tables

### Step 2: Enable Security (RLS)

1. In the same SQL Editor (or new query)
2. Copy and paste `02_enable_rls.sql`
3. Click **Run**

**What happens:**
- Enables RLS on both tables
- Creates security policies
- Your Flask app can still access everything (service role)
- Public users can only read active opportunities

**Expected output:**
- Should see "Success" message
- In Database → Tables, RLS should show as "Enabled"

### Step 3: Verify Everything Works

Run these verification queries in SQL Editor:

```sql
-- Check tables exist
SELECT tablename FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'opportunities');

-- Check RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'opportunities');

-- Check policies exist
SELECT tablename, policyname 
FROM pg_policies 
WHERE schemaname = 'public';
```

## 🔐 Understanding Security (RLS)

### What is Row Level Security?

Think of RLS like a bouncer at a club:
- **Without RLS**: Anyone with the address can enter and do anything
- **With RLS**: Bouncer checks your ID and enforces rules

### How It Works in Your App

```
User Request → Flask App → Database
                      ↓
              Service Role Key
                      ↓
              RLS Policy Check
                      ↓
              ✅ Allowed (service role has full access)
```

### Your Security Policies

1. **Service Role (Flask App)**: Full access to everything
   - Can create, read, update delete users
   - Can create, read, update, delete opportunities
   - Uses service role key from `DATABASE_URL`

2. **Public Users**: Read-only access to active opportunities
   - Can only see opportunities where `is_deleted = false`
   - Cannot see deleted opportunities
   - Cannot modify anything

3. **Authenticated Users** (if using Supabase Auth):
   - Can read/update their own profile
   - Can read active opportunities

## 🎓 Key Database Concepts Explained

### 1. Tables vs Models

**Table (Database):**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL
);
```

**Model (Python/SQLAlchemy):**
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
```

**They're the same thing!** SQLAlchemy converts models to tables.

### 2. Indexes - Why They Matter

**Without Index:**
```
Query: "Find user with email john@wvstateu.edu"
Database: Scans all 10,000 rows one by one ❌ Slow
```

**With Index:**
```
Query: "Find user with email john@wvstateu.edu"
Database: Looks up in index, jumps directly to row ✅ Fast
```

**Rule:** Index columns you frequently search/filter by.

### 3. Soft Delete vs Hard Delete

**Hard Delete:**
```sql
DELETE FROM opportunities WHERE id = 1;
-- Data is gone forever ❌
```

**Soft Delete:**
```sql
UPDATE opportunities SET is_deleted = true WHERE id = 1;
-- Data still exists, just hidden ✅
```

**Why soft delete?**
- Can "undelete" if needed
- Preserves history
- Better for analytics

### 4. Triggers - Auto-Update Timestamps

**Problem:** Need to manually update `updated_at` every time?

**Solution:** Trigger automatically updates it:
```sql
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

Now `updated_at` updates automatically! 🎉

## 🔧 Troubleshooting

### Issue: "Table already exists"
**Solution:** The schema file includes `DROP TABLE IF EXISTS`, so it's safe to run. It will drop and recreate.

### Issue: "Permission denied"
**Solution:** Make sure you're using the service role connection string in your `DATABASE_URL`.

### Issue: "RLS policy violation"
**Solution:** Check that your `DATABASE_URL` uses service role credentials, not anon key.

### Issue: Flask app can't access data
**Solution:** 
1. Verify RLS policies allow `service_role`
2. Check `DATABASE_URL` uses service role connection string
3. Verify tables exist (run verification queries)

## 📊 Database Structure

```
users
├── id (Primary Key)
├── email (Unique, Indexed)
├── password_hash
├── first_name
├── last_name
├── created_at (Indexed)
└── updated_at (Auto-updated)

opportunities
├── id (Primary Key)
├── title (Indexed)
├── company
├── location
├── type (Indexed)
├── category (Indexed)
├── description
├── requirements
├── salary
├── deadline (Indexed)
├── application_url
├── created_at (Indexed)
├── updated_at (Auto-updated)
└── is_deleted (Indexed, for soft delete)
```

## 🎯 Next Steps

1. ✅ Run `01_complete_schema.sql` to create tables
2. ✅ Run `02_enable_rls.sql` to enable security
3. ✅ Verify with verification queries
4. ✅ Test your Flask app - it should work perfectly!

## 📚 Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Supabase RLS Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

---

**Questions?** Check the comments in the SQL files - they explain each step!





