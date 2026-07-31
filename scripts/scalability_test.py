"""
scalability_test.py
====================
Synthetic scalability experiment for the supervisor's question: "how would
the system perform at 100,000 legal documents, and would pgvector still be
fast enough?"

We cannot obtain 100,000 real annotated legal documents in a few days, so
instead we run a SYNTHETIC scaling test: we populate a temporary pgvector
table with synthetic vectors (derived from real embeddings plus small
random noise, so they retain realistic geometry) at increasing scale, and
measure real query latency at each scale, both for plain semantic search
and for semantic search combined with the temporal WHERE filter, with and
without an HNSW approximate index.

This produces a real, reproducible latency table to cite in the paper's
scalability discussion, clearly labeled as a synthetic experiment.

Run with:
    cd ~/Desktop/vn-legal-rag
    source .venv/bin/activate
    export DATABASE_URL="postgresql://jacktrinh@localhost/vn_legal"
    python scripts/scalability_test.py
"""

import os
import time
import random
import json
from pathlib import Path

import psycopg2

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_FILE = PROJECT_ROOT / "data" / "benchmark" / "scalability_results.json"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jacktrinh@localhost/vn_legal")
DIM = 768
SCALES = [1_000, 10_000, 50_000, 100_000]
N_QUERY_TRIALS = 15
TEMP_TABLE = "scalability_test_chunks"


def get_real_embeddings(conn, limit=200):
    """Sample real embeddings from the production table to use as seeds,
    so synthetic vectors have realistic geometry rather than pure random
    noise (which would understate real-world nearest-neighbor cost)."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT embedding FROM document_chunks ORDER BY random() LIMIT {limit};")
        rows = cur.fetchall()
    seeds = []
    for (emb,) in rows:
        if isinstance(emb, str):
            vec = [float(x) for x in emb.strip("[]").split(",")]
        else:
            vec = list(emb)
        seeds.append(vec)
    return seeds


def make_synthetic_vector(seed, noise_scale=0.02):
    return [x + random.gauss(0, noise_scale) for x in seed]


def vec_to_pgvector_literal(vec):
    return "[" + ",".join(f"{x:.6f}" for x in vec) + "]"


def setup_temp_table(conn):
    with conn.cursor() as cur:
        cur.execute(f"DROP TABLE IF EXISTS {TEMP_TABLE};")
        cur.execute(f"""
            CREATE TABLE {TEMP_TABLE} (
                id SERIAL PRIMARY KEY,
                document_id TEXT,
                effective_from DATE,
                effective_to DATE,
                embedding vector({DIM})
            );
        """)
    conn.commit()


def populate_to_scale(conn, seeds, target_n, current_n, batch_size=2000):
    """Insert synthetic rows up to target_n, reusing seed vectors with noise.
    A subset of rows is given effective_to in the past (expired), to keep
    the temporal WHERE filter meaningful at scale."""
    to_insert = target_n - current_n
    if to_insert <= 0:
        return
    with conn.cursor() as cur:
        buf = []
        for i in range(to_insert):
            seed = random.choice(seeds)
            vec = make_synthetic_vector(seed)
            expired = random.random() < 0.3   # 30% synthetic docs are "expired"
            eff_from = "2015-01-01"
            eff_to = "2019-12-31" if expired else None
            buf.append((f"SYN_{current_n + i}", eff_from, eff_to,
                        vec_to_pgvector_literal(vec)))
            if len(buf) >= batch_size:
                cur.executemany(
                    f"INSERT INTO {TEMP_TABLE} (document_id, effective_from, effective_to, embedding) "
                    f"VALUES (%s, %s, %s, %s::vector);", buf)
                conn.commit()
                buf = []
        if buf:
            cur.executemany(
                f"INSERT INTO {TEMP_TABLE} (document_id, effective_from, effective_to, embedding) "
                f"VALUES (%s, %s, %s, %s::vector);", buf)
            conn.commit()


def time_queries(conn, query_vecs, use_temporal_filter, use_index):
    times = []
    with conn.cursor() as cur:
        for qv in query_vecs:
            qlit = vec_to_pgvector_literal(qv)
            if use_temporal_filter:
                sql = f"""
                    SELECT id FROM {TEMP_TABLE}
                    WHERE effective_from <= '2026-06-08'
                      AND (effective_to >= '2026-06-08' OR effective_to IS NULL)
                    ORDER BY embedding <=> %s::vector LIMIT 5;
                """
            else:
                sql = f"SELECT id FROM {TEMP_TABLE} ORDER BY embedding <=> %s::vector LIMIT 5;"
            t0 = time.perf_counter()
            cur.execute(sql, (qlit,))
            cur.fetchall()
            times.append((time.perf_counter() - t0) * 1000)  # ms
    times.sort()
    return {
        "mean_ms": round(sum(times) / len(times), 2),
        "p50_ms": round(times[len(times) // 2], 2),
        "p95_ms": round(times[int(len(times) * 0.95)], 2),
    }


def drop_index(conn):
    """Must be called before every 'no index' measurement. Without this,
    an HNSW index built in a PREVIOUS scale iteration would still be
    present on the table (we only add rows between iterations, we never
    drop the index automatically), and Postgres' query planner could
    silently use it, contaminating the no-index baseline at every scale
    after the first."""
    with conn.cursor() as cur:
        cur.execute(f"DROP INDEX IF EXISTS idx_{TEMP_TABLE}_hnsw;")
    conn.commit()


def build_hnsw_index(conn):
    with conn.cursor() as cur:
        cur.execute(f"DROP INDEX IF EXISTS idx_{TEMP_TABLE}_hnsw;")
        t0 = time.perf_counter()
        cur.execute(
            f"CREATE INDEX idx_{TEMP_TABLE}_hnsw ON {TEMP_TABLE} "
            f"USING hnsw (embedding vector_cosine_ops);"
        )
        conn.commit()
        build_time = time.perf_counter() - t0
    return round(build_time, 2)


def main():
    conn = psycopg2.connect(DATABASE_URL)
    print("Connected. Sampling real embeddings as synthesis seeds...")
    seeds = get_real_embeddings(conn)
    print(f"Loaded {len(seeds)} seed embeddings.\n")

    setup_temp_table(conn)
    query_vecs = [make_synthetic_vector(random.choice(seeds)) for _ in range(N_QUERY_TRIALS)]

    results = []
    current_n = 0
    for scale in SCALES:
        print(f"Populating to {scale:,} synthetic chunks...")
        populate_to_scale(conn, seeds, scale, current_n)
        current_n = scale

        drop_index(conn)   # ensure no stale index from the previous scale
        print(f"  [no index]  measuring semantic-only search...")
        no_idx_semantic = time_queries(conn, query_vecs, use_temporal_filter=False, use_index=False)
        print(f"  [no index]  measuring semantic + temporal filter...")
        no_idx_temporal = time_queries(conn, query_vecs, use_temporal_filter=True, use_index=False)

        print(f"  building HNSW index...")
        build_time = build_hnsw_index(conn)

        print(f"  [hnsw]      measuring semantic-only search...")
        idx_semantic = time_queries(conn, query_vecs, use_temporal_filter=False, use_index=True)
        print(f"  [hnsw]      measuring semantic + temporal filter...")
        idx_temporal = time_queries(conn, query_vecs, use_temporal_filter=True, use_index=True)

        row = {
            "scale": scale,
            "hnsw_build_seconds": build_time,
            "no_index_semantic_only_ms": no_idx_semantic,
            "no_index_with_temporal_filter_ms": no_idx_temporal,
            "hnsw_semantic_only_ms": idx_semantic,
            "hnsw_with_temporal_filter_ms": idx_temporal,
        }
        results.append(row)
        print(f"  -> semantic only (no index) mean {no_idx_semantic['mean_ms']} ms | "
              f"with HNSW mean {idx_semantic['mean_ms']} ms\n")

    with conn.cursor() as cur:
        cur.execute(f"DROP TABLE IF EXISTS {TEMP_TABLE};")
    conn.commit()
    conn.close()

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump({"dimension": DIM, "n_query_trials": N_QUERY_TRIALS,
                   "results": results}, f, indent=2)

    print("=" * 70)
    print(f"{'Scale':>10} | {'NoIdx Sem (ms)':>15} | {'NoIdx+Temp (ms)':>16} | "
          f"{'HNSW Sem (ms)':>14} | {'HNSW+Temp (ms)':>15}")
    for r in results:
        print(f"{r['scale']:>10,} | {r['no_index_semantic_only_ms']['mean_ms']:>15} | "
              f"{r['no_index_with_temporal_filter_ms']['mean_ms']:>16} | "
              f"{r['hnsw_semantic_only_ms']['mean_ms']:>14} | "
              f"{r['hnsw_with_temporal_filter_ms']['mean_ms']:>15}")
    print(f"\nSaved detailed results to {OUT_FILE}")
    print("Temporary test table was dropped; production data untouched.")


if __name__ == "__main__":
    main()
