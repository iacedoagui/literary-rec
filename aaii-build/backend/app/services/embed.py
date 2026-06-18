"""Sentence-embedding of paper abstracts. The model is loaded lazily and cached."""
from functools import lru_cache

import numpy as np

from ..config import settings


@lru_cache(maxsize=1)
def _get_model():
    # Imported lazily so the (heavy) model only loads on first use.
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: list[str]) -> np.ndarray:
    model = _get_model()
    return model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
        convert_to_numpy=True,
    )
