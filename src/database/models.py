"""
models.py
=========
The data shapes used everywhere in the project.

These mirror the PostgreSQL tables in schema.sql. The scraper produces
these, the database stores them, and retrieval/temporal modules read them.
The date fields (effective_from, effective_to) are what make the whole
temporal thesis possible.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List


@dataclass
class LegalDocument:
    """A legal document row (mirrors the legal_documents table)."""
    document_id: str
    title: str
    document_type: str = ""        # "Law" | "Decree" | "Circular"
    issuing_agency: str = ""
    issue_date: Optional[date] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None   # None = still in effect
    content: str = ""
    embedding: Optional[List[float]] = None


@dataclass
class DocumentRelationship:
    """An edge in the citation / amendment graph."""
    source_id: str
    target_id: str
    relation_type: str             # "supersedes" | "amends" | "cites"


@dataclass
class LegalQuestion:
    """One benchmark question with its expected answer + temporal tag."""
    question_id: str
    question_text: str
    answer_text: str = ""
    cited_document_ids: List[str] = field(default_factory=list)
    temporal_context: str = ""     # "current" | "historical" | "version-specific"
    query_date: Optional[date] = None
    difficulty: str = ""