"""Claude-powered paper summaries and cluster labels (Anthropic Python SDK)."""
import json
from functools import lru_cache

import anthropic

from ..config import settings

_SUMMARY_SYSTEM = (
    "You are a research assistant for academics. Given a paper's title and "
    "abstract, write a single tight paragraph (3-5 sentences) that explains what "
    "the paper does, its core method or contribution, and why it matters. Write "
    "for a researcher skimming the literature. Output only the paragraph, with no "
    "preamble, heading, or bullet points."
)

_LABEL_SYSTEM = (
    "You label clusters of academic papers. Given groups of paper titles, produce "
    "a concise, specific sub-topic label (2-5 words) for each group that captures "
    "what the papers share. Avoid generic labels like 'Machine Learning'."
)

_LABEL_SCHEMA = {
    "type": "object",
    "properties": {
        "labels": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "cluster_id": {"type": "integer"},
                    "label": {"type": "string"},
                },
                "required": ["cluster_id", "label"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["labels"],
    "additionalProperties": False,
}


@lru_cache(maxsize=1)
def _client() -> anthropic.Anthropic:
    if not settings.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def summarize_paper(title: str, abstract: str | None) -> str:
    content = f"Title: {title}\n\nAbstract: {abstract or '(no abstract available)'}"
    resp = _client().messages.create(
        model=settings.summary_model,
        max_tokens=512,
        system=_SUMMARY_SYSTEM,
        messages=[{"role": "user", "content": content}],
    )
    return "".join(b.text for b in resp.content if b.type == "text").strip()


def label_clusters(groups: dict[int, list[str]]) -> dict[int, str]:
    """Given {cluster_id: [titles]}, return {cluster_id: label}."""
    if not groups:
        return {}

    lines = []
    for cid, titles in groups.items():
        sample = titles[:8]
        joined = "\n".join(f"  - {t}" for t in sample)
        lines.append(f"Cluster {cid}:\n{joined}")
    user = "Label each cluster below.\n\n" + "\n\n".join(lines)

    resp = _client().messages.create(
        model=settings.label_model,
        max_tokens=1024,
        system=_LABEL_SYSTEM,
        messages=[{"role": "user", "content": user}],
        output_config={"format": {"type": "json_schema", "schema": _LABEL_SCHEMA}},
    )
    text = next(b.text for b in resp.content if b.type == "text")
    data = json.loads(text)
    labels = {item["cluster_id"]: item["label"] for item in data.get("labels", [])}
    # Fallback for any cluster the model skipped.
    return {cid: labels.get(cid, f"Sub-topic {cid + 1}") for cid in groups}
