"""
citation_graph.py
=================
Follows references between documents (Circular -> Decree -> Law).

WHY:
Vietnamese legal questions are often multi-hop: a Circular implements a
Decree which implements a Law. If retrieval only finds the Circular, the
answer may be incomplete. This module expands the retrieved set by walking
citation edges -- but every newly-pulled document still passes through the
temporal filter, so we never add an outdated law.

WHAT IT WILL DO LATER:
- build_graph(relationships): construct an in-memory graph from DB edges
- expand(documents, query_date, depth): add cited documents up to `depth`
  hops, keeping only ones valid on query_date.
"""

from datetime import date


class CitationGraph:
    """Graph of document-to-document references."""

    def build_graph(self, relationships: list):
        """TODO: build adjacency structure from DocumentRelationship edges."""
        ...

    def expand(self, documents: list, query_date: date, depth: int = 1) -> list:
        """TODO: add referenced documents (still temporally filtered)."""
        ...
