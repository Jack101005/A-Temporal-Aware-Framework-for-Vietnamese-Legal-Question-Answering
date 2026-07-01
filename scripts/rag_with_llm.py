"""
rag_with_llm.py
===============
Full RAG pipeline: retrieve chunks with the temporal filter, then ask a local
Ollama model to answer the question using only those chunks as context.

Requires Ollama running (either via `ollama serve` in another terminal, or the
Ollama menu-bar app). The default endpoint is http://localhost:11434.

Run with:
    cd ~/Desktop/vn-legal-rag
    source .venv/bin/activate
    export DATABASE_URL="postgresql://jacktrinh@localhost/vn_legal"
    export OLLAMA_MODELS="/Volumes/Jack/ollama-models"    # if using SSD models
    python scripts/rag_with_llm.py
"""

import os
import json
import urllib.request
import urllib.error

import psycopg2
from sentence_transformers import SentenceTransformer

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jacktrinh@localhost/vn_legal")
EMBED_MODEL = "bkai-foundation-models/vietnamese-bi-encoder"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:3b"
TOP_K = 4


def retrieve(conn, vec, query_date, k=TOP_K):
    """Temporal-aware retrieval: only chunks from documents valid on query_date."""
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


def build_prompt(question, query_date, chunks):
    ctx = "\n\n".join(
        f"[{doc_id} - {label}]\n{content}"
        for doc_id, label, content, title in chunks
    )
    return f"""Bạn là trợ lý pháp lý. Hãy trả lời câu hỏi CHỈ dựa trên nội dung các văn bản luật được cung cấp bên dưới. Nếu thông tin không có trong các văn bản đó, trả lời "Tôi không có đủ thông tin để trả lời". Luôn trích dẫn văn bản và Điều mà bạn dựa vào.

NGÀY ÁP DỤNG: {query_date}

CÁC VĂN BẢN LIÊN QUAN (đã lọc theo hiệu lực trên ngày trên):
{ctx}

CÂU HỎI: {question}

TRẢ LỜI:"""


def ask_ollama(prompt):
    data = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1},
    }).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL, data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read()).get("response", "").strip()


def main():
    conn = psycopg2.connect(DATABASE_URL)
    print("Connected. Loading embedding model...")
    model = SentenceTransformer(EMBED_MODEL)
    print(f"Ready. Using LLM: {OLLAMA_MODEL}\n")

    tests = [
        ("Mức lương tối thiểu vùng 1 là bao nhiêu?", "2025-06-01"),
        ("Mức lương tối thiểu vùng 1 là bao nhiêu?", "2023-03-01"),
        ("Thời giờ làm việc tối đa một ngày là bao nhiêu?", "2025-06-01"),
    ]

    for question, date in tests:
        print("=" * 72)
        print(f"Q: {question}")
        print(f"Ngày: {date}")
        print("-" * 72)

        emb = model.encode([question], normalize_embeddings=True)[0]
        vec = "[" + ",".join(f"{x:.6f}" for x in emb) + "]"
        chunks = retrieve(conn, vec, date)
        print(f"Retrieved {len(chunks)} chunks. Asking LLM...\n")

        prompt = build_prompt(question, date, chunks)
        try:
            answer = ask_ollama(prompt)
        except urllib.error.URLError as e:
            print(f"⚠️  Ollama not reachable: {e}")
            print("   Make sure Ollama is running (menu-bar app or `ollama serve`)")
            break
        print(f"A: {answer}\n")

    conn.close()


if __name__ == "__main__":
    main()
