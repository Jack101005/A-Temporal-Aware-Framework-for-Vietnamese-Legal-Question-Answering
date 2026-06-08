"""
temporal_rag.py
===============
The conductor. Wires every stage together into the full pipeline.

THE FLOW (matches Figure 2 in the proposal):
    question
      -> query_parser.parse_query_date()      # 1. what date?
      -> hybrid_retriever.retrieve()          # 2. find candidates
      -> temporal_filter.filter_by_date()     # 3a. drop invalid laws  (NOVEL)
      -> citation_graph.expand()              # 3b. follow references   (NOVEL)
      -> llm_client.generate()                # 4. write the answer
      -> grounded answer

WHY A SEPARATE ORCHESTRATOR:
Each stage stays small and testable on its own. This file is the only place
that knows the full order of operations, so the pipeline is easy to read and
easy to compare against the "standard RAG" baseline (which simply skips
stages 3a and 3b).

WHAT IT WILL DO LATER:
- answer(question, mode): mode in {"no_rag", "standard_rag", "temporal_rag"}
  so the same class can run all three experimental configurations.
"""


class TemporalRAG:
    """End-to-end temporal-aware RAG pipeline."""

    def answer(self, question: str, mode: str = "temporal_rag") -> str:
        """TODO: run the pipeline for the chosen mode and return the answer.
        - no_rag        : LLM alone, no retrieval
        - standard_rag  : retrieve + generate (no temporal filter)
        - temporal_rag  : retrieve + temporal filter + graph + generate
        Having all three here is what makes RQ1/RQ3 measurable."""
        ...
