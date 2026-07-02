"""
main.py  (FastAPI)
==================
The bridge between the UI and the PostgreSQL database.

Two endpoints:
  /ask   — original structured minimum-wage answer (keyword-routed)
  /chat  — full RAG + local LLM (Ollama): answers ANY labor-law question,
           grounded in temporally-filtered retrieved chunks.

Run with:
    uvicorn src.api.main:app --reload --port 8000
"""

from __future__ import annotations

import json
import urllib.request
import urllib.error
from datetime import date

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2

from configs.settings import DATABASE_URL

app = FastAPI(title="Vietnamese Legal Temporal RAG")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Original /ask endpoint (unchanged)
# ============================================================================

class AskRequest(BaseModel):
    question: str
    date: str
    region: str = "1"


def _fmt_vnd(n) -> str:
    return f"{n:,}".replace(",", ".")


def _connect():
    return psycopg2.connect(DATABASE_URL)


def _build_wage_answer(query_date: str, region: str = "1") -> dict:
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT document_id, title, effective_from, effective_to,
                       content, structured_data
                FROM legal_documents
                WHERE document_type = 'Decree'
                  AND effective_from <= %s
                  AND (effective_to >= %s OR effective_to IS NULL)
                LIMIT 1;
                """,
                (query_date, query_date),
            )
            row = cur.fetchone()
    finally:
        conn.close()

    if not row:
        return {
            "notFound": True,
            "lede": "Tại thời điểm đã chọn, chưa có dữ liệu văn bản trong hệ thống. "
                    "Vui lòng chọn mốc thời gian từ ngày 01/01/2020 trở đi.",
        }

    doc_id, title, eff_from, eff_to, content, sdata = row
    sd = sdata if isinstance(sdata, dict) else json.loads(sdata)
    v = sd["regions"][region]
    h = sd["hourly"][region]

    return {
        "lede": f"Theo {title}, mức lương tối thiểu vùng I là",
        "value": f"{_fmt_vnd(v)} ₫",
        "valueLabel": "/ tháng" + (f"  ·  {_fmt_vnd(h)} ₫ / giờ" if h else ""),
        "body": "Đây là mức sàn áp dụng cho người lao động làm việc theo hợp đồng "
                "lao động tại các doanh nghiệp thuộc vùng I. Người sử dụng lao động "
                "không được trả thấp hơn mức này.",
        "regions": sd["regions"],
        "sources": [
            {"title": title, "kind": "Nghị định", "subject": sd.get("subject", ""),
             "from": str(eff_from), "to": (str(eff_to) if eff_to else None)},
            {"title": "Bộ luật Lao động (Luật 45/2019/QH14)", "kind": "Luật",
             "subject": "Điều 91 — Mức lương tối thiểu", "from": "2021-01-01", "to": None},
        ],
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask(req: AskRequest):
    q = req.question.lower()
    wage_kw = ["lương tối thiểu", "luong toi thieu", "lương vùng", "mức lương",
               "minimum wage", "vùng 1", "vung 1", "lương cơ bản"]
    if any(kw in q for kw in wage_kw):
        answer = _build_wage_answer(req.date, req.region)
        return {"topic": "min-wage", "query_date": req.date, "answer": answer}
    return {"topic": "unknown", "query_date": req.date,
            "answer": {"notFound": True,
                       "lede": "Chủ đề này chưa được kết nối với cơ sở dữ liệu thật. "
                               "Hiện tại hệ thống đã hỗ trợ câu hỏi về lương tối thiểu vùng."}}


# ============================================================================
# NEW /chat endpoint — full RAG + local LLM (Ollama)
# ============================================================================

EMBED_MODEL_NAME = "bkai-foundation-models/vietnamese-bi-encoder"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:3b"
TOP_K = 4

_embed_model = None   # lazy-loaded on first /chat call


def _get_model():
    """Load the embedding model once, on first use."""
    global _embed_model
    if _embed_model is None:
        from sentence_transformers import SentenceTransformer
        _embed_model = SentenceTransformer(EMBED_MODEL_NAME)
    return _embed_model


class ChatRequest(BaseModel):
    question: str
    date: str                       # "YYYY-MM-DD"


def _retrieve_chunks(query_date: str, vec: str, k: int = TOP_K):
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT c.document_id, c.article_label, c.content, d.title
                FROM document_chunks c
                JOIN legal_documents d ON c.document_id = d.document_id
                WHERE d.effective_from <= %s
                  AND (d.effective_to >= %s OR d.effective_to IS NULL)
                ORDER BY c.embedding <=> %s::vector
                LIMIT %s;
                """,
                (query_date, query_date, vec, k),
            )
            return cur.fetchall()
    finally:
        conn.close()


def _build_prompt(question: str, query_date: str, chunks) -> str:
    ctx = "\n\n".join(
        f"[{doc_id} - {label}]\n{content}"
        for doc_id, label, content, title in chunks
    )
    return f"""Bạn là trợ lý pháp lý về luật lao động Việt Nam. Hãy trả lời câu hỏi CHỈ dựa trên nội dung các văn bản luật được cung cấp bên dưới. Nếu thông tin không có trong các văn bản đó, hãy trả lời "Tôi không có đủ thông tin trong cơ sở dữ liệu để trả lời câu hỏi này". Luôn trích dẫn tên văn bản và Điều mà bạn dựa vào.

NGÀY ÁP DỤNG: {query_date}

CÁC VĂN BẢN LIÊN QUAN (đã lọc theo hiệu lực trên ngày trên):
{ctx}

CÂU HỎI: {question}

TRẢ LỜI (ngắn gọn, chính xác, có trích dẫn):"""


def _ask_ollama(prompt: str) -> str:
    data = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1},
    }).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read()).get("response", "").strip()


@app.post("/chat")
def chat(req: ChatRequest):
    """Full RAG: temporal retrieval + local LLM answer."""
    model = _get_model()
    emb = model.encode([req.question], normalize_embeddings=True)[0]
    vec = "[" + ",".join(f"{x:.6f}" for x in emb) + "]"

    chunks = _retrieve_chunks(req.date, vec)
    if not chunks:
        return {"answer": "Tại ngày đã chọn, hệ thống không tìm thấy văn bản luật "
                          "nào còn hiệu lực. Vui lòng chọn mốc từ 01/01/2020 trở đi.",
                "sources": [], "query_date": req.date}

    prompt = _build_prompt(req.question, req.date, chunks)
    try:
        answer = _ask_ollama(prompt)
    except urllib.error.URLError:
        return {"answer": "Không kết nối được với mô hình ngôn ngữ (Ollama). "
                          "Hãy đảm bảo Ollama đang chạy.",
                "sources": [], "query_date": req.date, "error": "ollama_unreachable"}

    # dedupe sources by (document, article)
    seen, sources = set(), []
    for doc_id, label, content, title in chunks:
        key = (doc_id, label)
        if key in seen:
            continue
        seen.add(key)
        sources.append({"document_id": doc_id, "article": label, "title": title})

    return {"answer": answer, "sources": sources, "query_date": req.date}
