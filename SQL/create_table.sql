
-- 1. Create the primary opportunities table
USE nys_postgesql_db;

CREATE TABLE public.contract_opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cr_number INTEGER UNIQUE NOT NULL,
    ad_type VARCHAR(30) NOT NULL, -- e.g., 'public_agency', 'subcontractor'
    title TEXT NOT NULL,
    description TEXT,
    issue_date DATE NOT NULL,
    due_date TIMESTAMPTZ,
    category VARCHAR(100),
    location VARCHAR(100),
    
    -- Semi-structured jdoc for type-specific attributes
    -- e.g., {"agency": "DOT", "division": "Highways"} OR {"company": "Acme Corp"}
    -- e.g. {"Ad end date":"07-15-2026"}
    jdoc JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 2. Indexes for fast operational queries
CREATE INDEX idx_opportunities_cr_number ON contract_opportunities (cr_number);
CREATE INDEX idx_opportunities_dates ON contract_opportunities (issue_date DESC, due_date ASC);
CREATE INDEX idx_opportunities_ad_type ON contract_opportunities (ad_type);

-- 3. GIN Index for fast querying inside the JSONB jdoc field
CREATE INDEX idx_opportunities_jdoc ON contract_opportunities USING gin (jdoc);

-- 4. Full-Text Search Index for searching title & description
CREATE INDEX idx_opportunities_fts ON contract_opportunities 
USING gin (to_tsvector('english', title || ' ' || COALESCE(description, '')));