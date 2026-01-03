# 🚀 Quick Start: Database Setup

## ⚡ 3-Step Setup (5 minutes)

### Step 1: Create Schema
1. Open **Supabase Dashboard** → **SQL Editor**
2. Copy entire contents of `01_complete_schema.sql`
3. Paste and click **Run**
4. ✅ Tables created!

### Step 2: Enable Security
1. In SQL Editor, copy `02_enable_rls.sql`
2. Paste and click **Run**
3. ✅ Security enabled!

### Step 3: Verify
1. Copy `03_verify_setup.sql`
2. Paste and click **Run**
3. ✅ Check all items show ✅

## 🎯 That's It!

Your database is now ready. Your Flask app will work automatically because:
- Tables match your SQLAlchemy models exactly
- RLS policies allow service role (your Flask app) full access
- All indexes are created for fast queries

## 🔍 What Each File Does

| File | What It Does | When to Run |
|------|-------------|-------------|
| `01_complete_schema.sql` | Creates tables, indexes, triggers | First time setup |
| `02_enable_rls.sql` | Enables security policies | After schema |
| `03_verify_setup.sql` | Checks everything is correct | After both |

## ⚠️ Important Notes

1. **DATABASE_URL**: Make sure your Flask app's `DATABASE_URL` uses the **service role** connection string (not anon key)

2. **Fresh Start**: The schema file drops existing tables. If you have data you want to keep, export it first!

3. **Flask App**: Your Flask app will automatically work because:
   - Tables already exist (no need for `db.create_all()`)
   - Service role has full access via RLS policies

## 🐛 Troubleshooting

**Error: "Table already exists"**
- The schema file includes `DROP TABLE IF EXISTS`, so it's safe to re-run
- It will drop and recreate everything

**Error: "Permission denied"**
- Check your `DATABASE_URL` uses service role credentials
- Service role connection string looks like: `postgresql://postgres:[PASSWORD]@[HOST]/postgres`

**Flask app can't access data**
- Verify RLS policies exist (run verification query)
- Check `DATABASE_URL` environment variable
- Make sure you ran both SQL files

## 📚 Learn More

See `README.md` for detailed explanations of:
- How tables work
- Why indexes matter
- How RLS security works
- Database concepts explained





