"""
chunker.py
==========
Splits a Vietnamese legal document into article-based chunks.

Vietnamese laws are structured as "Điều 1.", "Điều 2.", ... Each article is a
natural, self-contained unit and is exactly how laws are cited ("theo Điều 91").
We split on these boundaries. Very long articles are further split into
sub-chunks so they fit the embedding model's input limit.
"""

import re

MAX_CHARS = 1500          # ~250-300 Vietnamese words; keeps chunks embeddable
OVERLAP_CHARS = 150       # small overlap so context isn't lost at boundaries


def _split_long(text: str, max_chars: int = MAX_CHARS, overlap: int = OVERLAP_CHARS):
    """Split an over-long article into smaller overlapping windows."""
    if len(text) <= max_chars:
        return [text]
    pieces = []
    start = 0
    while start < len(text):
        end = start + max_chars
        pieces.append(text[start:end])
        if end >= len(text):
            break
        start = end - overlap
    return pieces


def chunk_document(text: str, document_id: str):
    """Return a list of chunk dicts for one document.
    Each: {document_id, chunk_index, article_label, content}."""
    # Split right before each "Điều N." at the start of a line
    parts = re.split(r'(?=^Điều \d+\.)', text, flags=re.MULTILINE)

    chunks = []
    idx = 0
    for part in parts:
        part = part.strip()
        if not part:
            continue
        m = re.match(r'^(Điều \d+)\.', part)
        label = m.group(1) if m else "Phần mở đầu"

        # sub-split long articles
        for piece in _split_long(part):
            piece = piece.strip()
            if not piece:
                continue
            chunks.append({
                "document_id": document_id,
                "chunk_index": idx,
                "article_label": label,
                "content": piece,
            })
            idx += 1
    return chunks
