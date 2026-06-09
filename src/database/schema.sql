-- schema.sql
-- ==========
-- PostgreSQL schema for the temporal-aware legal corpus.
--
-- WHY THIS DESIGN:
-- The whole thesis rests on being able to ask "which laws were valid on date X?".
-- That requires effective_from / effective_to on every document. The pgvector
-- column lets us do semantic search in the same database. The structured_data
-- JSONB column holds extra details (e.g. wage tables) that the UI displays.
--
-- RUN LATER WITH:  psql -d vn_legal -f schema.sql

-- Enable vector search (run once per database)
CREATE EXTENSION IF NOT EXISTS vector;

-- Main documents table
CREATE TABLE IF NOT EXISTS legal_documents (
    document_id     TEXT PRIMARY KEY,
    title           TEXT NOT NULL,
    document_type   TEXT,              -- 'Law' | 'Decree' | 'Circular'
    issuing_agency  TEXT,
    issue_date      DATE,
    effective_from  DATE,              -- when it starts being valid
    effective_to    DATE,              -- when it stops; NULL = still valid
    content         TEXT,
    structured_data JSONB,             -- extra details (wage tables, etc.) for the UI
    embedding       vector(768)        -- PhoBERT dim; adjust to model used
);

-- Citation / amendment graph (edges between documents)
CREATE TABLE IF NOT EXISTS document_relationships (
    id            SERIAL PRIMARY KEY,
    source_id     TEXT REFERENCES legal_documents(document_id),
    target_id     TEXT REFERENCES legal_documents(document_id),
    relation_type TEXT                 -- 'supersedes' | 'amends' | 'cites'
);

-- Evaluation benchmark questions
CREATE TABLE IF NOT EXISTS legal_questions (
    question_id      TEXT PRIMARY KEY,
    question_text    TEXT NOT NULL,
    answer_text      TEXT,
    cited_doc_ids    TEXT[],
    temporal_context TEXT,
    query_date       DATE,
    difficulty       TEXT
);