"""arXiv pre-print search via the public Atom API (no key required)."""
import asyncio

import feedparser
import httpx

from ..models import Paper

# arXiv redirects http -> https and throttles clients without a descriptive
# User-Agent; both are handled here.
ARXIV_API = "https://export.arxiv.org/api/query"
HEADERS = {"User-Agent": "literary-rec/0.1 (research paper recommender)"}


async def search_arxiv(query: str, limit: int) -> list[Paper]:
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": limit,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    text: str | None = None
    # arXiv can be slow (tens of seconds) and intermittently returns 429/503;
    # use a generous timeout and retry transient statuses with backoff.
    async with httpx.AsyncClient(
        timeout=90.0, follow_redirects=True, headers=HEADERS
    ) as client:
        for attempt in range(4):
            try:
                resp = await client.get(ARXIV_API, params=params)
            except httpx.TimeoutException:
                continue
            if resp.status_code in (429, 503):
                await asyncio.sleep(3 * (attempt + 1))
                continue
            resp.raise_for_status()
            text = resp.text
            break
    if text is None:
        return []

    feed = feedparser.parse(text)
    papers: list[Paper] = []
    for entry in feed.entries:
        # entry.id looks like http://arxiv.org/abs/2401.12345v1
        arxiv_id = entry.id.rsplit("/abs/", 1)[-1] if "/abs/" in entry.id else entry.id
        pdf_url = next(
            (link.href for link in entry.get("links", []) if link.get("type") == "application/pdf"),
            None,
        )
        year = None
        if getattr(entry, "published_parsed", None):
            year = entry.published_parsed.tm_year

        papers.append(
            Paper(
                id=f"arxiv:{arxiv_id}",
                title=" ".join(entry.title.split()),
                authors=[a.name for a in entry.get("authors", [])],
                year=year,
                abstract=" ".join(entry.summary.split()) if entry.get("summary") else None,
                url=entry.id,
                pdf_url=pdf_url,
                source="arXiv",
            )
        )
    return papers
