"""Cluster abstract embeddings into sub-topics with KMeans.

The number of clusters is chosen automatically by maximizing the silhouette
score over a small candidate range.
"""
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from ..config import settings


def cluster_embeddings(
    embeddings: np.ndarray, max_clusters: int | None = None
) -> list[int]:
    """Return a cluster label per row of `embeddings`.

    The number of clusters is auto-selected between 2 and the cap (per-request
    `max_clusters`, falling back to the server default).
    """
    n = len(embeddings)
    if n <= 3:
        return [0] * n

    cap = max_clusters or settings.max_clusters
    max_k = min(cap, n - 1)
    best_labels: list[int] | None = None
    best_score = -1.0

    for k in range(2, max_k + 1):
        km = KMeans(n_clusters=k, n_init=10, random_state=42)
        labels = km.fit_predict(embeddings)
        if len(set(labels)) < 2:
            continue
        score = silhouette_score(embeddings, labels)
        if score > best_score:
            best_score = score
            best_labels = labels.tolist()

    return best_labels if best_labels is not None else [0] * n
