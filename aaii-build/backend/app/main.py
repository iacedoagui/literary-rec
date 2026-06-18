"""FastAPI entrypoint for the literary-rec dashboard."""
import asyncio
import logging
from collections import defaultdict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("literary-rec")

from .config import settings
from .models import (
    Cluster,
    Paper,
    RecommendRequest,
    RecommendResponse,
    SummarizeRequest,
    SummarizeResponse,
)
from .services.cluster import cluster_embeddings
from .services.embed import embed_texts
from .services.fetch import fetch_papers
from .services.summarize import label_clusters, summarize_paper

app = FastAPI(title="literary-rec", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "claude_configured": bool(settings.anthropic_api_key)}


def _build_clusters(
    papers: list[Paper],
    per_topic_limit: int | None = None,
    max_clusters: int | None = None,
) -> list[Cluster]:
    """Embed, cluster, and label. Runs synchronously (called via a thread)."""
    texts = [f"{p.title}. {p.abstract or ''}".strip() for p in papers]
    embeddings = embed_texts(texts)
    labels = cluster_embeddings(embeddings, max_clusters)

    grouped: dict[int, list[Paper]] = defaultdict(list)
    for paper, label in zip(papers, labels):
        grouped[label].append(paper)

    title_groups = {cid: [p.title for p in ps] for cid, ps in grouped.items()}
    cluster_labels = label_clusters(title_groups)

    clusters = [
        Cluster(
            id=cid,
            label=cluster_labels.get(cid, f"Sub-topic {cid + 1}"),
            # Papers keep arXiv's relevance order, so the head is the most relevant.
            papers=ps[:per_topic_limit] if per_topic_limit else ps,
        )
        for cid, ps in grouped.items()
    ]
    # Largest clusters first.
    clusters.sort(key=lambda c: len(c.papers), reverse=True)
    return clusters


@app.post("/api/recommend", response_model=RecommendResponse)
async def recommend(req: RecommendRequest) -> RecommendResponse:
    papers = await fetch_papers(req.query, settings.max_results_per_source)
    papers = papers[: req.limit]

    if not papers:
        return RecommendResponse(query=req.query, total=0, clusters=[])

    # The pipeline is CPU/IO blocking (embeddings + Claude); keep the event loop free.
    try:
        clusters = await asyncio.to_thread(
            _build_clusters, papers, req.per_topic_limit, req.max_clusters
        )
    except Exception as exc:
        logger.exception("recommend pipeline failed")
        raise HTTPException(
            status_code=502, detail=f"{type(exc).__name__}: {exc}"
        ) from exc
    return RecommendResponse(query=req.query, total=len(papers), clusters=clusters)


@app.post("/api/summarize", response_model=SummarizeResponse)
def summarize(req: SummarizeRequest) -> SummarizeResponse:
    try:
        summary = summarize_paper(req.title, req.abstract)
    except Exception as exc:  # surface a clean error to the UI
        raise HTTPException(status_code=502, detail=f"Summary failed: {exc}") from exc
    return SummarizeResponse(summary=summary)
