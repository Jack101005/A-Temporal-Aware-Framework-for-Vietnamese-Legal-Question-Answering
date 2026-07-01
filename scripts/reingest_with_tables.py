"""
reingest_with_tables.py
Re-reads all .docx files WITH tables (preserving document order) and updates the
`content` column in legal_documents. This fixes the missing minimum-wage figures,
which live inside tables that the original paragraph-only ingestion skipped.
"""
import os
from pathlib import Path
import psycopg2
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jacktrinh@localhost/vn_legal")


def iter_block_items(parent):
    """Yield paragraphs and tables in the order they appear in the document."""
    parent_elm = parent.element.body
    for child in parent_elm.iterchildren():
        if child.tag.endswith('}p'):
            yield Paragraph(child, parent)
        elif child.tag.endswith('}tbl'):
            yield Table(child, parent)


def extract_with_tables(docpath):
    doc = Document(str(docpath))
    parts = []
    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            if block.text.strip():
                parts.append(block.text)
        else:  # Table
            for row in block.rows:
                cells = [c.text.strip() for c in row.cells]
                line = " | ".join(cells)
                if line.strip(" |"):
                    parts.append(line)
    return "\n".join(parts)


def main():
    conn = psycopg2.connect(DATABASE_URL)
    print("Connected to PostgreSQL.")
    files = sorted(RAW_DIR.glob("*.docx"))
    print(f"Found {len(files)} .docx files in {RAW_DIR}\n")

    updated = 0
    for f in files:
        doc_id = f.stem
        text = extract_with_tables(f)
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE legal_documents SET content = %s WHERE document_id = %s",
                (text, doc_id),
            )
            n = cur.rowcount
        conn.commit()
        status = "updated" if n else "NOT IN DB (skipped)"
        print(f"  {doc_id:15} {len(text):>9,} chars   {status}")
        updated += n

    print(f"\n✓ Updated {updated} documents (now including table content).")
    print("Next: re-run  python scripts/generate_embeddings.py")
    conn.close()


if __name__ == "__main__":
    main()
