"""
main.py  (FastAPI)
==================
The bridge between the UI and the PostgreSQL database.

The UI sends a question + a date. This API:
  1. figures out what the question is about (currently: minimum wage)
  2. runs the temporal query to find the decree valid on that date
  3. returns the answer in the exact shape the UI expects

Run with:
    uvicorn src.api.main:app --reload --port 8000
"""

from __future__ import annotations

import json
from datetime import date

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2

from configs.settings import DATABASE_URL

app = FastAPI(title="Vietnamese Legal Temporal RAG")

# Allow the UI (running on localhost:3000) to call this API (localhost:8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # demo only; tighten for production
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- request / response shapes ----
class AskRequest(BaseModel):
    question: str
    date: str                      # "YYYY-MM-DD"
    region: str = "1"


def _fmt_vnd(n) -> str:
    return f"{n:,}".replace(",", ".")


def _connect():
    return psycopg2.connect(DATABASE_URL)


def _build_wage_answer(query_date: str, region: str = "1") -> dict:
    """Find the minimum-wage decree valid on query_date, format for the UI."""
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
            {
                "title": title, "kind": "Nghị định",
                "subject": sd.get("subject", ""),
                "from": str(eff_from), "to": (str(eff_to) if eff_to else None),
            },
            {
                "title": "Bộ luật Lao động (Luật 45/2019/QH14)", "kind": "Luật",
                "subject": "Điều 91 — Mức lương tối thiểu",
                "from": "2021-01-01", "to": None,
            },
        ],
    }


# ---- endpoints ----
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask(req: AskRequest):
    """Main endpoint. For now it answers minimum-wage questions from the DB."""
    # Simple keyword routing (only minimum wage is wired to the DB for now)
    q = req.question.lower()
    wage_kw = ["lương tối thiểu", "luong toi thieu", "lương vùng", "mức lương",
               "minimum wage", "vùng 1", "vung 1", "lương cơ bản"]
    if any(kw in q for kw in wage_kw):
        answer = _build_wage_answer(req.date, req.region)
        return {"topic": "min-wage", "query_date": req.date, "answer": answer}

    # other topics not yet wired to the DB
    return {
        "topic": "unknown",
        "query_date": req.date,
        "answer": {
            "notFound": True,
            "lede": "Chủ đề này chưa được kết nối với cơ sở dữ liệu thật. "
                    "Hiện tại hệ thống đã hỗ trợ câu hỏi về lương tối thiểu vùng.",
        },
    }