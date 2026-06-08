"""
hybrid_retriever.py
===================
The Phase 1 baseline: dense (PhoBERT) + sparse (BM25) retrieval combined.

WHY HYBRID:
Dense search understands meaning ("what is the minimum wage") but can miss
exact legal references. Sparse BM25 nails exact tokens like
"Điều 90" or "Nghị định 74/2024". Combining both (Reciprocal Rank Fusion)
gives the best of each. This is the BASELINE we compare the temporal system
against.

WHAT IT WILL DO LATER:
- dense_search(query): vector search via the DB
- sparse_search(query): BM25 over the corpus
- retrieve(query, k): fuse both rankings, return top-k documents
NOTE: this baseline does NOT know about time. That is intentional --
the temporal layer is added separately so we can measure its effect.
"""


class HybridRetriever:
    """Dense + sparse retrieval with rank fusion (no temporal awareness)."""

    def dense_search(self, query: str, k: int = 10):
        """TODO: embed query, vector_search via DB."""
        ...

    def sparse_search(self, query: str, k: int = 10):
        """TODO: BM25 keyword search."""
        ...

    def retrieve(self, query: str, k: int = 10):
        """TODO: combine dense + sparse with Reciprocal Rank Fusion."""
        ...
