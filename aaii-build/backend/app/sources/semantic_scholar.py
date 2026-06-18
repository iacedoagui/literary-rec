"""Semantic Scholar Graph API search.

Works without an API key (a shared, aggressively rate-limited pool). Set
SEMANTIC_SCHOLAR_API_KEY for much higher limits and reliability.
"""
import asyncio

import httpx

from ..config import settings
from ..models import Paper

S2_SEARCH = "https://api.semanticscholar.org/graph/v1/paper/search"
FIELDS = "title,abstract,year,authors,url,externalIds,openAccessPdf"


async def search_semantic_scholar(query: str, limit: int) -> list[Paper]:
    headers = {"User-Agent": "literary-rec/0.1"}
    if settings.semantic_scholar_api_key:
        headers["x-api-key"] = settings.semantic_scholar_api_key

    params = {"query": query, "limit": limit, "fields": FIELDS}
    data: dict | None = None
    async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
        # The keyless pool frequently returns 429; retry with backoff before
        # giving up (returning empty so the other source can still succeed).
        for attempt in range(4):
            resp = await client.get(S2_SEARCH, params=params)
            if resp.status_code == 429:
                retry_after = resp.headers.get("retry-after")
                delay = float(retry_after) if retry_after else 2 ** attempt
                await asyncio.sleep(delay)
                continue
            resp.raise_for_status()
            data = resp.json()
            break
    if data is None:
        return []

    papers: list[Paper] = []
    for item in data.get("data") or []:
        paper_id = item.get("paperId", "")
        open_access = item.get("openAccessPdf") or {}
        papers.append(
            Paper(
                id=f"s2:{paper_id}",
                title=" ".join((item.get("title") or "").split()),
                authors=[a.get("name", "") for a in (item.get("authors") or [])],
                year=item.get("year"),
                abstract=item.get("abstract"),
                url=item.get("url"),
                pdf_url=open_access.get("url"),
                source="Semantic Scholar",
            )
        )
    return papers
