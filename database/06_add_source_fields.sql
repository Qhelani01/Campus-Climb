-- ============================================
-- Migration: Add source tracking fields to opportunities table
-- ============================================
-- This migration adds fields to track where opportunities came from
-- for automated fetching and deduplication
--
-- SAFE TO RUN: This will not delete any data
-- ============================================

-- Add source field
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'opportunities' 
        AND column_name = 'source'
    ) THEN
        ALTER TABLE public.opportunities 
        ADD COLUMN source VARCHAR(50);
        
        CREATE INDEX IF NOT EXISTS idx_opportunities_source ON public.opportunities(source);
        
        RAISE NOTICE 'Added source column to opportunities table';
    ELSE
        RAISE NOTICE 'source column already exists';
    END IF;
END $$;

-- Add source_id field
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'opportunities' 
        AND column_name = 'source_id'
    ) THEN
        ALTER TABLE public.opportunities 
        ADD COLUMN source_id VARCHAR(200);
        
        CREATE INDEX IF NOT EXISTS idx_opportunities_source_id ON public.opportunities(source_id);
        
        RAISE NOTICE 'Added source_id column to opportunities table';
    ELSE
        RAISE NOTICE 'source_id column already exists';
    END IF;
END $$;

-- Add source_url field
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'opportunities' 
        AND column_name = 'source_url'
    ) THEN
        ALTER TABLE public.opportunities 
        ADD COLUMN source_url VARCHAR(500);
        
        RAISE NOTICE 'Added source_url column to opportunities table';
    ELSE
        RAISE NOTICE 'source_url column already exists';
    END IF;
END $$;

-- Add last_fetched field
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'opportunities' 
        AND column_name = 'last_fetched'
    ) THEN
        ALTER TABLE public.opportunities 
        ADD COLUMN last_fetched TIMESTAMP;
        
        RAISE NOTICE 'Added last_fetched column to opportunities table';
    ELSE
        RAISE NOTICE 'last_fetched column already exists';
    END IF;
END $$;

-- Add auto_fetched field
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'opportunities' 
        AND column_name = 'auto_fetched'
    ) THEN
        ALTER TABLE public.opportunities 
        ADD COLUMN auto_fetched BOOLEAN DEFAULT FALSE;
        
        CREATE INDEX IF NOT EXISTS idx_opportunities_auto_fetched ON public.opportunities(auto_fetched);
        
        RAISE NOTICE 'Added auto_fetched column to opportunities table';
    ELSE
        RAISE NOTICE 'auto_fetched column already exists';
    END IF;
END $$;

-- Create composite index for source + source_id lookups
CREATE INDEX IF NOT EXISTS idx_opportunities_source_lookup ON public.opportunities(source, source_id);

-- ============================================
-- Verification Query
-- ============================================
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'opportunities'
AND column_name IN ('source', 'source_id', 'source_url', 'last_fetched', 'auto_fetched')
ORDER BY column_name;

