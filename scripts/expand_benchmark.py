"""
expand_benchmark.py
====================
Expands the evaluation benchmark from 20 to ~100+ questions by systematically
sampling articles across all 13 documents, asking the local LLM (Ollama) to
draft one question and answer per article (grounded strictly in that
article's own text), and auto-verifying numeric answers against the source.

This directly answers the supervisor's feedback that a 20-question benchmark
is too small. All new questions are generated FROM real article text, not
invented, and every question is tagged verified=true only if a numeric
answer was programmatically confirmed in the source, or needs_review=true
otherwise (mirroring the same honesty standard as the original benchmark).

Run with:
    cd ~/Desktop/vn-legal-rag
    source .venv/bin/activate
    export DATABASE_URL="postgresql://jacktrinh@localhost/vn_legal"
    export OLLAMA_MODELS="/Volumes/Jack/ollama-models"   # if using SSD models
    python scripts/expand_benchmark.py --target 100
"""

import os
import re
import json
import random
import argparse
import urllib.request
from pathlib import Path

import psycopg2

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BENCH_FILE = PROJECT_ROOT / "data" / "benchmark" / "labor_law_benchmark.json"
OUT_FILE = PROJECT_ROOT / "data" / "benchmark" / "labor_law_benchmark_expanded.json"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jacktrinh@localhost/vn_legal")
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:3b"
MIN_ARTICLE_CHARS = 200      # skip trivial/administrative articles
DEFAULT_QUERY_DATE = "2026-06-08"

# Documents belonging to the temporal chains already covered by the
# original 20 questions; the new questions default to static coverage of
# other topics so we do not duplicate what is already well tested.
TEMPORAL_CHAIN_DOCS = {"ND_90_2019", "ND_38_2022", "ND_74_2024",
                       "ND_152_2020", "ND_70_2023"}


def fetch_articles(conn):
    """Reassemble full article text (across sub-chunks) grouped by
    (document_id, article_label), so long articles split for embedding
    are still treated as one question-generation unit."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT c.document_id, c.article_label, d.title, d.document_type,
                   d.effective_from, d.effective_to,
                   string_agg(c.content, ' ' ORDER BY c.chunk_index) AS full_text
            FROM document_chunks c
            JOIN legal_documents d ON c.document_id = d.document_id
            WHERE c.article_label IS NOT NULL
            GROUP BY c.document_id, c.article_label, d.title, d.document_type,
                     d.effective_from, d.effective_to
            HAVING length(string_agg(c.content, ' ')) >= %s
            ORDER BY c.document_id, c.article_label;
            """,
            (MIN_ARTICLE_CHARS,),
        )
        return cur.fetchall()


def already_covered(existing_questions):
    """(document_id, article_label) pairs already used as gold in the
    original benchmark, so we do not generate near-duplicate questions."""
    return {(q["gold_document_id"], q["gold_article"]) for q in existing_questions}


PROMPT_TEMPLATE = """Bạn là một chuyên gia soạn câu hỏi trắc nghiệm pháp luật lao động Việt Nam.

Dưới đây là toàn văn một Điều luật. Hãy soạn ĐÚNG MỘT câu hỏi tự nhiên mà người dân có thể hỏi, sao cho câu trả lời nằm HOÀN TOÀN trong nội dung Điều luật này, và một câu trả lời ngắn gọn dựa đúng theo Điều luật.

Nếu Điều luật không chứa thông tin nào đủ cụ thể để hỏi (ví dụ chỉ là điều khoản thi hành, hiệu lực), hãy trả lời với "question": null.

CHỈ trả lời bằng JSON hợp lệ, không thêm chữ nào khác, theo đúng định dạng:
{{"question": "...", "expected_answer": "..."}}

VĂN BẢN: {title}
ĐIỀU LUẬT: {article}
NỘI DUNG:
{content}
"""


def ask_ollama_json(prompt, retries=2):
    data = json.dumps({
        "model": OLLAMA_MODEL, "prompt": prompt, "stream": False,
        "format": "json", "options": {"temperature": 0.2},
    }).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL, data=data, headers={"Content-Type": "application/json"})
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                raw = json.loads(resp.read()).get("response", "").strip()
                return json.loads(raw)
        except Exception:
            if attempt == retries:
                return None
    return None


NUM_RE = re.compile(r"\d+(?:[.,]\d+)*")            # for display (expected_figure)
NUM_RE_STRICT = re.compile(r"\d{2,}(?:[.,]\d+)*")   # for auto verification (avoids
                                                     # single-digit false positives,
                                                     # e.g. a lone "3" matching almost
                                                     # anywhere in a long article)


def verify_numeric(expected_answer, source_text):
    """If the drafted answer contains a number with at least two digits,
    require that exact number string to appear in the source text before
    marking verified. Single-digit numbers are deliberately excluded from
    auto-verification (too likely to match incidentally) and fall back to
    needs-manual-review instead."""
    nums = NUM_RE_STRICT.findall(expected_answer or "")
    if not nums:
        return False   # no reliable number to check mechanically -> needs manual review
    return any(n in source_text for n in nums)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=100,
                     help="Target TOTAL question count including the existing 20")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    with open(BENCH_FILE, encoding="utf-8") as f:
        existing = json.load(f)["questions"]
    covered = already_covered(existing)
    n_new_needed = max(0, args.target - len(existing))
    print(f"Existing verified questions: {len(existing)}")
    print(f"New questions to draft: {n_new_needed}\n")

    conn = psycopg2.connect(DATABASE_URL)
    articles = fetch_articles(conn)
    print(f"Candidate articles available (>= {MIN_ARTICLE_CHARS} chars): {len(articles)}")

    candidates = [a for a in articles if (a[0], a[1]) not in covered]
    random.seed(args.seed)
    random.shuffle(candidates)

    new_questions = []
    next_id = len(existing) + 1
    verified_count = 0

    for doc_id, article, title, doc_type, eff_from, eff_to, content in candidates:
        if len(new_questions) >= n_new_needed:
            break

        result = ask_ollama_json(
            PROMPT_TEMPLATE.format(title=title, article=article, content=content[:3000])
        )
        if not result or not result.get("question"):
            continue   # article not question-worthy (e.g. procedural clause), skip

        q_text = result["question"].strip()
        a_text = result.get("expected_answer", "").strip()
        if not q_text or not a_text:
            continue

        verified = verify_numeric(a_text, content)
        if verified:
            verified_count += 1

        new_questions.append({
            "id": f"Q{next_id:03d}",
            "question": q_text,
            "query_date": DEFAULT_QUERY_DATE,
            "category": "temporal" if doc_id in TEMPORAL_CHAIN_DOCS else "static",
            "topic": doc_type.lower() if doc_type else "general",
            "gold_document_id": doc_id,
            "gold_article": article,
            "expected_answer": a_text,
            "expected_figure": (NUM_RE.findall(a_text) or [None])[0],
            "verified": verified,
            "notes": "auto-generated from article text; " +
                     ("numeric figure confirmed in source" if verified
                      else "needs manual review (no numeric anchor to auto-check)"),
        })
        next_id += 1
        if len(new_questions) % 10 == 0:
            print(f"  drafted {len(new_questions)} / {n_new_needed} "
                  f"({verified_count} auto-verified so far)")

    conn.close()

    combined = existing + new_questions
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump({"questions": combined}, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"TOTAL questions: {len(combined)}  "
          f"({len(existing)} original + {len(new_questions)} new)")
    print(f"New questions auto-verified (numeric match): {verified_count}")
    print(f"New questions needing manual review: {len(new_questions) - verified_count}")
    print(f"Saved to: {OUT_FILE}")
    print("\nNext steps:")
    print("  1. Open the file and skim the 'needs manual review' items.")
    print("  2. Run scripts/run_experiments.py against the new file to get")
    print("     updated Standard vs Temporal RAG numbers at the larger n.")


if __name__ == "__main__":
    main()
