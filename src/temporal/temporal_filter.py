"""
temporal_filter.py
==================
THE CORE NOVEL CONTRIBUTION of the thesis.

Given retrieved documents and a query_date, keep only the documents that
were legally in force on that date. This is why the LLM never sees an
outdated decree, and therefore stops citing old laws.

THE RULE:
    keep a document IF
        effective_from <= query_date
        AND (effective_to >= query_date OR effective_to is None)
"""

from datetime import date
from src.database.models import LegalDocument


def filter_by_date(documents: list[LegalDocument], query_date: date) -> list[LegalDocument]:
    """Return only documents valid on query_date (the core temporal rule)."""
    kept = []
    for doc in documents:
        if doc.effective_from is None:
            continue  # cannot verify validity -> drop to be safe
        starts_ok = doc.effective_from <= query_date
        ends_ok = (doc.effective_to is None) or (doc.effective_to >= query_date)
        if starts_ok and ends_ok:
            kept.append(doc)
    return kept
