-- schema.sql
-- ==========
-- PostgreSQL schema for the temporal-aware legal corpus.
--
-- WHY THIS DESIGN:
-- The whole thesis rests on being able to ask "which laws were valid on date X?".
-- That requires (a) effective_from / effective_to on every document, and
-- (b) a separate relationships table to model supersession + citation as a
-- graph. The pgvector column lets us do semantic search in the same database
-- instead of a separate vector store.
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
    cited_doc_ids    TEXT[],           -- expected supporting documents
    temporal_context TEXT,             -- 'current' | 'historical' | 'version-specific'
    query_date       DATE,
    difficulty       TEXT
);

-- Helpful indexes (add later when data grows)
-- CREATE INDEX ON legal_documents (effective_from, effective_to);
-- CREATE INDEX ON document_relationships (source_id);
