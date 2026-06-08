"""
vbpl_scraper.py
===============
Concrete scraper for vbpl.vn (the Ministry of Justice official portal).

WHY START HERE:
vbpl.vn is a government source, so the documents are public-domain and the
ethics are clean. It also exposes effective dates and document relationships
fairly explicitly, which is exactly the temporal metadata we need.

WHAT IT WILL DO LATER:
- Walk the labor-law category pages to collect document URLs
- For each document, extract: title, type (Law/Decree/Circular), issuing
  agency, issue_date, effective_from, effective_to, the body text, and any
  "superseded by / amends" relationships shown on the page.
- Hand each parsed document back as a RawDocument (see models.py).
"""

from src.scraper.base_scraper import BaseScraper


class VbplScraper(BaseScraper):
    """Scraper for vbpl.vn labor-law documents."""

    BASE_URL = "https://vbpl.vn"

    def fetch_document_list(self) -> list[str]:
        """TODO: paginate through the labor-law category, return doc URLs."""
        ...

    def fetch_document(self, url: str):
        """TODO: fetch one document page, parse fields + temporal metadata."""
        ...
