"""
base_scraper.py
================
Abstract base class for all legal-document scrapers.

WHY THIS EXISTS:
We will scrape from more than one source (vbpl.vn, thuvienphapluat.vn,
congbao.chinhphu.vn). Each site has a different HTML layout, but they all
need to do the same THINGS: fetch a page politely, parse it into a common
shape, and respect rate limits / robots.txt. This base class defines that
shared contract so every concrete scraper looks the same to the rest of
the system.

WHAT TO IMPLEMENT LATER:
- fetch_document_list(): get the list of labor-law document URLs
- fetch_document(url): download and parse one document into a RawDocument
- The polite-fetch helper (rate limiting, retries, User-Agent) lives here.
"""

from abc import ABC, abstractmethod


class BaseScraper(ABC):
    """Common contract + polite-fetching utilities for all scrapers."""

    def __init__(self, rate_limit_seconds: float = 3.0, user_agent: str = ""):
        # rate_limit_seconds: minimum wait between requests (politeness)
        # user_agent: identifiable academic UA string
        ...

    def polite_get(self, url: str):
        """Fetch a URL while respecting rate limits, retries, and robots.txt.
        TODO: implement requests + sleep + retry logic here."""
        ...

    @abstractmethod
    def fetch_document_list(self) -> list[str]:
        """Return a list of document URLs in the labor-law domain."""
        ...

    @abstractmethod
    def fetch_document(self, url: str):
        """Download + parse one document into a RawDocument object."""
        ...
