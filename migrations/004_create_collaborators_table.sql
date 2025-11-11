-- Migration: Create Collaborators Table for Google Sheets Sync
-- Date: 2025-11-10
-- Purpose: Store members/collaborators from Google Sheets

-- Create app schema (separate from Evolution data)
CREATE SCHEMA IF NOT EXISTS app;

-- Collaborators table
CREATE TABLE IF NOT EXISTS app.collaborators (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    role VARCHAR(100),           -- "Desenvolvedor", "Founder", "PM", etc
    status VARCHAR(20) NOT NULL DEFAULT 'ativo',  -- "ativo", "inativo", "saída"
    entry_date DATE,
    last_synced TIMESTAMP DEFAULT NOW(),
    sheets_row_id INTEGER,       -- Reference to Google Sheets row
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_collaborators_status ON app.collaborators(status);
CREATE INDEX IF NOT EXISTS idx_collaborators_name ON app.collaborators(name);
CREATE INDEX IF NOT EXISTS idx_collaborators_email ON app.collaborators(email);
CREATE INDEX IF NOT EXISTS idx_collaborators_sheets_id ON app.collaborators(sheets_row_id);
CREATE INDEX IF NOT EXISTS idx_collaborators_role ON app.collaborators(role);

-- Sync logs table (track synchronization history)
CREATE TABLE IF NOT EXISTS app.sync_logs (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    records_created INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    records_deleted INTEGER DEFAULT 0,
    status VARCHAR(20) NOT NULL,        -- "success", "error", "partial"
    error_message TEXT,
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP,
    duration_seconds INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Index for sync logs
CREATE INDEX IF NOT EXISTS idx_sync_logs_table_name ON app.sync_logs(table_name);
CREATE INDEX IF NOT EXISTS idx_sync_logs_created_at ON app.sync_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sync_logs_status ON app.sync_logs(status);

-- Add comments for documentation
COMMENT ON SCHEMA app IS 'Application data (separate from Evolution)';
COMMENT ON TABLE app.collaborators IS 'Members/collaborators synced from Google Sheets';
COMMENT ON COLUMN app.collaborators.status IS 'Status: ativo (active), inativo (inactive), saída (departed)';
COMMENT ON COLUMN app.collaborators.last_synced IS 'Last synchronization timestamp from Google Sheets';
COMMENT ON COLUMN app.collaborators.sheets_row_id IS 'Reference to row ID in Google Sheets for tracking updates';
COMMENT ON TABLE app.sync_logs IS 'Log of all synchronization operations from Google Sheets';
COMMENT ON COLUMN app.sync_logs.duration_seconds IS 'How long the sync took in seconds';
