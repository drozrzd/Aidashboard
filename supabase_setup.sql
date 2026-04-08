-- ─────────────────────────────────────────────────────────────────────────────
-- AI E-Commerce Decision Dashboard — Supabase Schema Setup
-- Run this in Supabase SQL Editor (Dashboard > SQL Editor > New query)
-- ─────────────────────────────────────────────────────────────────────────────

-- 1. Create the inventory table
CREATE TABLE IF NOT EXISTS public.sku_inventory (
    id                   SERIAL PRIMARY KEY,
    sku_id               VARCHAR(10)  UNIQUE NOT NULL,
    product_name         VARCHAR(100) NOT NULL,
    category             VARCHAR(20)  NOT NULL CHECK (category IN ('Sun', 'Optical', 'Blue Light')),
    current_stock        INTEGER      NOT NULL CHECK (current_stock >= 0),
    daily_sales_velocity FLOAT        NOT NULL CHECK (daily_sales_velocity >= 0),
    unit_cost            FLOAT        NOT NULL CHECK (unit_cost > 0),
    selling_price        FLOAT        NOT NULL CHECK (selling_price > 0),
    profit_margin        FLOAT        NOT NULL CHECK (profit_margin BETWEEN 0 AND 1),
    seasonality_score    FLOAT        NOT NULL CHECK (seasonality_score BETWEEN 0 AND 1),
    created_at           TIMESTAMPTZ  DEFAULT NOW()
);

-- 2. Enable Row Level Security (always on for production)
ALTER TABLE public.sku_inventory ENABLE ROW LEVEL SECURITY;

-- 3. Allow the anon key to SELECT (read-only for the dashboard)
CREATE POLICY "anon_read"
    ON public.sku_inventory
    FOR SELECT
    TO anon
    USING (true);

-- 4. Allow the anon key to INSERT (needed for first-run synthetic data seeding)
--    REMOVE this policy after initial seed if you want to lock down writes.
CREATE POLICY "anon_insert"
    ON public.sku_inventory
    FOR INSERT
    TO anon
    WITH CHECK (true);

-- 5. Useful indexes for dashboard queries
CREATE INDEX IF NOT EXISTS idx_sku_category    ON public.sku_inventory (category);
CREATE INDEX IF NOT EXISTS idx_sku_velocity    ON public.sku_inventory (daily_sales_velocity DESC);
CREATE INDEX IF NOT EXISTS idx_sku_margin      ON public.sku_inventory (profit_margin DESC);

-- ─────────────────────────────────────────────────────────────────────────────
-- AFTER INITIAL SEED: drop the insert policy to prevent unauthorized writes
-- Uncomment and run once synthetic data is loaded:
-- DROP POLICY "anon_insert" ON public.sku_inventory;
-- ─────────────────────────────────────────────────────────────────────────────
