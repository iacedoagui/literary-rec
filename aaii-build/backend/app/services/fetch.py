"""Fetch from all sources concurrently and de-duplicate the merged set."""
import asyncio
import re

from ..models import Paper
from ..sources.arxiv import search_arxiv
from ..sources.semantic_scholar import search_semantic_scholar


def _normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]", "", title.lower())


async def fetch_papers(query: str, limit_per_source: int) -> list[Paper]:
    # Run both sources concurrently; tolerate one failing.
    results = await asyncio.gather(
        search_arxiv(query, limit_per_source),
        search_semantic_scholar(query, limit_per_source),
        return_exceptions=True,
    )

    papers: list[Paper] = []
    for result in results:
        if isinstance(result, Exception):
            continue
        papers.extend(result)

    # De-dupe by normalized title; prefer the copy that has an abstract.
    by_title: dict[str, Paper] = {}
    for paper in papers:
        if not paper.title:
            continue
        key = _normalize_title(paper.title)
        existing = by_title.get(key)
        if existing is None:
            by_title[key] = paper
        elif not existing.abstract and paper.abstract:
            by_title[key] = paper

    return list(by_title.values())
