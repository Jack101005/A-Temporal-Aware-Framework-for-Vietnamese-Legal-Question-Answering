"""
main.py  (FastAPI)
==================
A thin web API so the system can be demoed in a browser / Postman.

WHY:
For the thesis defense and for showing Dr. Tam, it is much more convincing
to type a question into a /ask endpoint and watch a grounded answer come
back than to read code. This wraps TemporalRAG in one HTTP endpoint.

WHAT IT WILL DO LATER:
- POST /ask {question, mode} -> {answer, sources, query_date}
- GET  /health -> simple status check
Keep it tiny: it just calls TemporalRAG.answer().
"""

# from fastapi import FastAPI
# app = FastAPI(title="Vietnamese Legal Temporal RAG")

# @app.post("/ask")
# def ask(question: str, mode: str = "temporal_rag"):
#     """TODO: call TemporalRAG.answer() and return answer + sources."""
#     ...

# @app.get("/health")
# def health():
#     return {"status": "ok"}
