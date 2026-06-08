"""
document_parser.py
==================
Cleaning + structuring helpers shared by all scrapers.

WHY SEPARATE FROM THE SCRAPER:
Fetching (network) and parsing (text cleanup) are different jobs. Keeping
parsing here means we can unit-test it on saved HTML without hitting the
network, and reuse the same cleanup logic across all sources.

WHAT IT WILL DO LATER:
- normalize_whitespace(): collapse weird spacing from copy-pasted legal text
- extract_dates(): pull issue/effective dates from Vietnamese date formats
  (e.g. "có hiệu lực từ ngày 01/07/2024")
- extract_citations(): find references to other documents
  (e.g. "Nghị định 38/2022/NĐ-CP", "Điều 90 Bộ luật Lao động")
- split_articles(): break a document into its Điều / Khoản / Điểm structure
"""


def normalize_whitespace(text: str) -> str:
    """TODO: clean spacing, remove noise characters."""
    ...


def extract_dates(text: str) -> dict:
    """TODO: parse Vietnamese effective/issue dates into ISO format."""
    ...


def extract_citations(text: str) -> list[str]:
    """TODO: detect references to other legal documents."""
    ...


def split_articles(text: str) -> list[dict]:
    """TODO: split into Điều/Khoản/Điểm units for finer retrieval."""
    ...
