-- schema_chunks.sql
-- Adds the document_chunks table for semantic search.
CREATE TABLE IF NOT EXISTS document_chunks (
    chunk_id      SERIAL PRIMARY KEY,
    document_id   TEXT REFERENCES legal_documents(document_id) ON DELETE CASCADE,
    chunk_index   INTEGER,
    article_label TEXT,
    content       TEXT,
    embedding     vector(768)
);
CREATE INDEX IF NOT EXISTS idx_chunks_doc ON document_chunks(document_id);
