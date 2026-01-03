-- ============================================
-- Campus Climb Database - Complete Schema
-- ============================================
-- This file creates the entire database from scratch
-- It matches your SQLAlchemy models exactly
--
-- WHAT THIS DOES:
-- 1. Drops existing tables (if any) - FRESH START
-- 2. Creates users and opportunities tables
-- 3. Adds all indexes for performance
-- 4. Sets up proper constraints
--
-- WHY WE DO THIS:
-- - Ensures database matches your Flask models exactly
-- - Creates indexes for fast queries
-- - Sets up proper data types and constraints
-- ============================================

-- ============================================
-- STEP 1: Clean Slate - Drop Existing Tables
-- ============================================
-- This removes any existing tables to start fresh
-- WARNING: This will delete all existing data!
-- Only run this if you want a completely fresh start

DROP TABLE IF EXISTS public.opportunities CASCADE;
DROP TABLE IF EXISTS public.users CASCADE;

-- ============================================
-- STEP 2: Create Users Table
-- ============================================
-- This table stores user accounts for authentication
--
-- KEY FIELDS:
-- - id: Auto-incrementing primary key (SERIAL = auto-increment integer)
-- - email: Unique identifier for users (must be @wvstateu.edu)
-- - password_hash: Encrypted password (never store plain passwords!)
-- - created_at/updated_at: Track when records are created/modified
--
-- CONSTRAINTS:
-- - email is UNIQUE (no duplicate emails)
-- - email is NOT NULL (required field)
-- - All name fields are NOT NULL (required)

CREATE TABLE public.users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- STEP 3: Create Opportunities Table
-- ============================================
-- This table stores job opportunities, internships, etc.
--
-- KEY FIELDS:
-- - id: Primary key
-- - title, company, location: Basic opportunity info
-- - type: job, internship, workshop, conference, competition
-- - category: Technology, Business, etc.
-- - description: Full text description (TEXT = unlimited length)
-- - is_deleted: Soft delete flag (don't actually delete, just mark as deleted)
--
-- WHY SOFT DELETE:
-- - Preserves data history
-- - Can "undelete" if needed
-- - Better for analytics

CREATE TABLE public.opportunities (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    company VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    requirements TEXT,
    salary VARCHAR(50),
    deadline DATE,
    application_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- ============================================
-- STEP 4: Create Indexes for Performance
-- ============================================
-- Indexes make queries faster by creating "lookup tables"
-- Think of it like an index in a book - you can find pages quickly
--
-- WHY INDEXES MATTER:
-- Without indexes: Database scans every row (slow)
-- With indexes: Database uses index to jump directly (fast)
--
-- RULE OF THUMB: Index columns you frequently:
-- - Filter by (WHERE clause)
-- - Sort by (ORDER BY)
-- - Join on (JOIN clause)

-- Users table indexes
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_users_created_at ON public.users(created_at);
CREATE INDEX idx_users_is_admin ON public.users(is_admin);

-- Opportunities table indexes
CREATE INDEX idx_opportunities_title ON public.opportunities(title);
CREATE INDEX idx_opportunities_type ON public.opportunities(type);
CREATE INDEX idx_opportunities_category ON public.opportunities(category);
CREATE INDEX idx_opportunities_deadline ON public.opportunities(deadline);
CREATE INDEX idx_opportunities_created_at ON public.opportunities(created_at);
CREATE INDEX idx_opportunities_is_deleted ON public.opportunities(is_deleted);

-- Composite index for common query pattern
-- This helps when filtering by: is_deleted AND type AND category
-- Example: "Get all active internships in Technology"
CREATE INDEX idx_opp_active ON public.opportunities(is_deleted, type, category);

-- ============================================
-- STEP 5: Create Function to Auto-Update Timestamps
-- ============================================
-- This function automatically updates the updated_at field
-- whenever a row is modified
--
-- HOW IT WORKS:
-- PostgreSQL triggers call this function before UPDATE
-- Function sets updated_at to current timestamp

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to users table
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to opportunities table
CREATE TRIGGER update_opportunities_updated_at 
    BEFORE UPDATE ON public.opportunities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Verification Query
-- ============================================
-- Run this to verify tables were created correctly
SELECT 
    tablename,
    schemaname
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'opportunities')
ORDER BY tablename;





