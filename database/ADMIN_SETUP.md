# 🔐 Admin Authentication Setup Guide

This guide explains how to set up admin authentication for Campus Climb after the security improvements.

## ✅ What Changed

1. **Removed hardcoded credentials** - No more passwords in code
2. **Added `is_admin` field** - Database column to track admin status
3. **Proper authentication** - All admin endpoints now require authentication
4. **Secure decorator** - `@admin_required` checks user authentication and admin status

## 🚀 Initial Setup

### Step 1: Run Database Migration

If you have an existing database, run the migration to add the `is_admin` column:

1. Open **Supabase Dashboard** → **SQL Editor**
2. Copy and paste `04_add_admin_column.sql`
3. Click **Run**

This will:
- Add `is_admin` column to `users` table (defaults to `FALSE`)
- Create an index for faster admin queries
- Verify the column was added

### Step 2: Set Admin Secret Key

Set the `ADMIN_SECRET_KEY` environment variable in your Vercel project:

1. Go to **Vercel Dashboard** → Your Project → **Settings** → **Environment Variables**
2. Add new variable:
   - **Name**: `ADMIN_SECRET_KEY`
   - **Value**: Generate a strong random string (e.g., use `openssl rand -hex 32`)
   - **Environment**: Production, Preview, Development (as needed)

**Important**: Keep this secret key secure! It's only used for initial admin promotion.

### Step 3: Create First Admin User

#### Option A: Using the API Endpoint

1. Register a user normally (or use existing account)
2. Make a POST request to `/api/admin/promote`:

```bash
curl -X POST https://your-domain.vercel.app/api/admin/promote \
  -H "Content-Type: application/json" \
  -d '{
    "secret_key": "your-admin-secret-key",
    "email": "admin@wvstateu.edu"
  }'
```

#### Option B: Using SQL (Direct Database Access)

If you have direct database access:

```sql
-- Update user to admin
UPDATE public.users 
SET is_admin = TRUE 
WHERE email = 'admin@wvstateu.edu';
```

### Step 4: Verify Admin Access

1. Login with the admin account
2. Try accessing an admin endpoint (e.g., `/api/admin/dashboard`)
3. You should receive admin data, not an error

## 🔒 How It Works

### Authentication Flow

1. **User logs in** → Session created with `user_id` and `email`
2. **Admin endpoint called** → `@admin_required` decorator checks:
   - Is user authenticated? (session or email parameter)
   - Does user have `is_admin = TRUE`?
3. **Access granted/denied** → Returns data or 403 error

### Security Features

- ✅ **No hardcoded credentials** - All passwords stored as hashes
- ✅ **Session-based auth** - Secure session management
- ✅ **Database-backed admin status** - Can be changed without code deployment
- ✅ **Protected endpoints** - All admin routes require authentication
- ✅ **Serverless-compatible** - Works with email parameter fallback

## 📝 Admin Endpoints

All these endpoints now require admin authentication:

- `GET /api/admin/opportunities` - List all opportunities
- `POST /api/admin/opportunities` - Create opportunity
- `PUT /api/admin/opportunities/<id>` - Update opportunity
- `DELETE /api/admin/opportunities/<id>` - Delete opportunity
- `GET /api/admin/users` - List all users
- `GET /api/admin/dashboard` - Admin dashboard stats

## 🛠️ Managing Admins

### Promote User to Admin

Use the `/api/admin/promote` endpoint (requires `ADMIN_SECRET_KEY`):

```json
POST /api/admin/promote
{
  "secret_key": "your-secret-key",
  "email": "newadmin@wvstateu.edu"
}
```

### Remove Admin Status

Direct SQL (if you have database access):

```sql
UPDATE public.users 
SET is_admin = FALSE 
WHERE email = 'user@wvstateu.edu';
```

Or create a new admin endpoint (recommended):

```python
@app.route('/api/admin/users/<int:user_id>/admin', methods=['DELETE'])
@admin_required
def remove_admin(user_id):
    # Implementation here
    pass
```

## 🔐 Best Practices

1. **Limit admin promotion** - Only use `ADMIN_SECRET_KEY` for initial setup
2. **Rotate secrets** - Change `ADMIN_SECRET_KEY` periodically
3. **Monitor admin access** - Log admin actions for security
4. **Use strong passwords** - Admin accounts should have strong passwords
5. **Regular audits** - Review admin users periodically

## 🚨 Troubleshooting

### "Authentication required" error
- User is not logged in
- Session expired
- Solution: Login again

### "Admin access required" error
- User is logged in but not an admin
- Solution: Promote user to admin using steps above

### "Admin promotion not configured" error
- `ADMIN_SECRET_KEY` environment variable not set
- Solution: Set the environment variable in Vercel

### Migration fails
- Column might already exist
- Solution: Check if column exists first, or drop and recreate

## 📚 Related Files

- `api/index.py` - Main Flask application with admin endpoints
- `database/01_complete_schema.sql` - Complete schema with `is_admin` column
- `database/04_add_admin_column.sql` - Migration script for existing databases

---

**Security Note**: After setting up your first admin, consider disabling or further securing the `/api/admin/promote` endpoint to prevent unauthorized admin creation.

