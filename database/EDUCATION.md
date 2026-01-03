# 🎓 Database Education Guide

This guide explains database concepts as they relate to your Campus Climb app.

## 📖 Table of Contents

1. [What is a Database?](#what-is-a-database)
2. [Tables and Rows](#tables-and-rows)
3. [Indexes - Making Queries Fast](#indexes)
4. [Row Level Security (RLS)](#row-level-security)
5. [How Flask Connects](#how-flask-connects)
6. [Common Patterns](#common-patterns)

---

## What is a Database?

Think of a database like a **filing cabinet**:

```
Filing Cabinet (Database)
├── Drawer 1: Users (Table)
│   ├── Folder: John Doe (Row)
│   ├── Folder: Jane Smith (Row)
│   └── ...
├── Drawer 2: Opportunities (Table)
│   ├── Folder: Software Engineer Job (Row)
│   ├── Folder: Internship Program (Row)
│   └── ...
```

**Why use a database?**
- **Persistent Storage**: Data survives app restarts
- **Fast Queries**: Find data quickly with indexes
- **Data Integrity**: Enforce rules (unique emails, required fields)
- **Concurrent Access**: Multiple users can access simultaneously
- **Security**: Control who can see/modify what

---

## Tables and Rows

### What is a Table?

A table is like a **spreadsheet** with columns and rows:

```
users table:
┌────┬─────────────────────┬─────────────┬───────────┐
│ id │ email               │ first_name  │ last_name  │
├────┼─────────────────────┼─────────────┼───────────┤
│ 1  │ john@wvstateu.edu   │ John        │ Doe       │
│ 2  │ jane@wvstateu.edu   │ Jane        │ Smith     │
└────┴─────────────────────┴─────────────┴───────────┘
```

### Columns = Fields

Each column has:
- **Name**: `email`, `first_name`, etc.
- **Type**: `VARCHAR(120)`, `INTEGER`, `TIMESTAMP`, etc.
- **Constraints**: `NOT NULL`, `UNIQUE`, etc.

### Rows = Records

Each row is one complete record (one user, one opportunity, etc.)

### Primary Key

The `id` column is the **primary key**:
- Unique identifier for each row
- Auto-increments (1, 2, 3, ...)
- Used to reference specific records

**Example:**
```sql
-- Get user with id = 1
SELECT * FROM users WHERE id = 1;
```

---

## Indexes

### What is an Index?

An index is like a **book index** - it helps you find pages quickly.

**Without Index:**
```
Query: "Find user with email john@wvstateu.edu"
Database: Scans all 10,000 rows one by one
Time: 100ms ❌
```

**With Index:**
```
Query: "Find user with email john@wvstateu.edu"
Database: Looks up email in index, jumps directly to row
Time: 1ms ✅
```

### When to Use Indexes

Index columns you frequently:
- **Filter by**: `WHERE email = '...'`
- **Sort by**: `ORDER BY created_at`
- **Join on**: `JOIN users ON ...`

### Your App's Indexes

```sql
-- Users table
CREATE INDEX idx_users_email ON users(email);        -- Fast email lookups
CREATE INDEX idx_users_created_at ON users(created_at); -- Fast sorting

-- Opportunities table
CREATE INDEX idx_opportunities_type ON opportunities(type); -- Fast filtering by type
CREATE INDEX idx_opportunities_category ON opportunities(category); -- Fast filtering by category
CREATE INDEX idx_opp_active ON opportunities(is_deleted, type, category); -- Fast combined queries
```

**Trade-off:**
- ✅ Faster queries
- ❌ Slightly slower inserts/updates (index must be updated)
- ✅ Worth it for read-heavy apps (like yours!)

---

## Row Level Security (RLS)

### What is RLS?

RLS is like a **bouncer at a club** - it checks who you are and what you're allowed to do.

**Without RLS:**
```
Anyone with database access → Can see/modify everything ❌
```

**With RLS:**
```
Request → Check Policy → Allow/Deny ✅
```

### How It Works

1. **Enable RLS** on a table
2. **Create Policies** that define who can do what
3. **PostgreSQL enforces** policies automatically

### Your App's Policies

#### Policy 1: Service Role (Flask App)
```sql
CREATE POLICY "Service role can manage users"
ON users
FOR ALL  -- All operations
TO service_role
USING (true);  -- Always allow
```

**Who:** Your Flask backend
**What:** Full access (create, read, update, delete)
**Why:** Your app needs to manage everything

#### Policy 2: Public Read (Opportunities)
```sql
CREATE POLICY "Public can read active opportunities"
ON opportunities
FOR SELECT  -- Read only
TO anon, authenticated
USING (is_deleted = false);  -- Only active ones
```

**Who:** Anyone (public users)
**What:** Read only, active opportunities
**Why:** Your app shows opportunities to everyone

### How Your Flask App Uses RLS

```
User Request
    ↓
Flask App (Python)
    ↓
SQLAlchemy (ORM)
    ↓
SQL Query
    ↓
PostgreSQL Database
    ↓
RLS Policy Check
    ↓
✅ Allowed (service role has full access)
    ↓
Return Data
```

**Key Point:** Your Flask app uses the **service role** connection string, which bypasses RLS restrictions (by design - your app is trusted).

---

## How Flask Connects

### The Connection Flow

```
Flask App
    ↓
DATABASE_URL environment variable
    ↓
postgresql://postgres:password@host/database
    ↓
Supabase PostgreSQL
```

### Environment Variables

Your Flask app needs:
```bash
DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]/postgres
SECRET_KEY=your-secret-key-here
```

**Where to set:**
- **Local**: `.env` file (not committed to git)
- **Vercel**: Environment variables in project settings

### SQLAlchemy ORM

**ORM = Object-Relational Mapping**

Converts Python code to SQL:

```python
# Python (SQLAlchemy)
user = User.query.filter_by(email='john@wvstateu.edu').first()
```

Becomes:

```sql
-- SQL (PostgreSQL)
SELECT * FROM users WHERE email = 'john@wvstateu.edu' LIMIT 1;
```

**Benefits:**
- Write Python instead of SQL
- Type-safe
- Database-agnostic (works with PostgreSQL, MySQL, SQLite, etc.)

---

## Common Patterns

### 1. Soft Delete

**Problem:** Want to "delete" but keep data for history

**Solution:** Use `is_deleted` flag

```sql
-- "Delete" (soft)
UPDATE opportunities SET is_deleted = true WHERE id = 1;

-- Query (exclude deleted)
SELECT * FROM opportunities WHERE is_deleted = false;
```

**Benefits:**
- Can "undelete" if needed
- Preserves history
- Better for analytics

### 2. Auto-Update Timestamps

**Problem:** Need to manually update `updated_at` every time?

**Solution:** Use triggers

```sql
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

Now `updated_at` updates automatically! 🎉

### 3. Composite Indexes

**Problem:** Frequently query by multiple columns

**Solution:** Composite index

```sql
-- Query pattern
SELECT * FROM opportunities 
WHERE is_deleted = false 
AND type = 'internship' 
AND category = 'Technology';

-- Composite index helps
CREATE INDEX idx_opp_active ON opportunities(is_deleted, type, category);
```

**How it works:**
- Index stores combinations of (is_deleted, type, category)
- Database can quickly find matching rows

---

## 🎯 Key Takeaways

1. **Tables** = Where data lives (like spreadsheets)
2. **Indexes** = Make queries fast (like book indexes)
3. **RLS** = Security (controls who can access what)
4. **ORM** = Write Python, get SQL (SQLAlchemy)
5. **Soft Delete** = Hide data, don't delete it
6. **Triggers** = Auto-update fields

---

## 📚 Next Steps

1. Run the database setup files
2. Read the SQL files - they have comments explaining each step
3. Experiment with queries in Supabase SQL Editor
4. Check out the verification queries to see how everything works

**Questions?** The SQL files have detailed comments explaining each concept!





