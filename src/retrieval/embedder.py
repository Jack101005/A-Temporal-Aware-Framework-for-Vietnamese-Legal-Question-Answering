"""
embedder.py
===========
Turns Vietnamese text into vectors using PhoBERT.

IMPORTANT: this does NOT train anything. It loads an already-trained
PhoBERT model and uses it to convert text into numbers (a vector) so we
can compare documents by meaning. This is the "indexing" step, not training.
"""

import torch
from transformers import AutoModel, AutoTokenizer

from configs.settings import EMBEDDING_MODEL


class Embedder:
    """Wraps PhoBERT to produce sentence embeddings."""

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        # Load the pre-trained model + tokenizer ONCE (slow to load).
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()   # inference mode, no training

    def embed_text(self, text: str) -> list[float]:
        """Convert one piece of text into a single vector."""
        inputs = self.tokenizer(
            text, return_tensors="pt", truncation=True,
            max_length=256, padding=True,
        )
        with torch.no_grad():                      # no gradients = no training
            outputs = self.model(**inputs)
        # Mean-pool the token embeddings into one sentence vector
        vec = outputs.last_hidden_state.mean(dim=1).squeeze()
        return vec.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed many texts (simple loop; optimize later if needed)."""
        return [self.embed_text(t) for t in texts]
