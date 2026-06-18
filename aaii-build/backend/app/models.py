"""Pydantic request/response schemas shared across the API."""
from pydantic import BaseModel, Field


class Paper(BaseModel):
    id: str
    title: str
    authors: list[str] = []
    year: int | None = None
    abstract: str | None = None
    url: str | None = None
    pdf_url: str | None = None
    source: str  # "arXiv" | "Semantic Scholar"


class Cluster(BaseModel):
    id: int
    label: str
    papers: list[Paper]


class RecommendRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Topic or research idea")
    limit: int = Field(40, ge=4, le=100, description="Max papers to return")
    per_topic_limit: int | None = Field(
        None, ge=1, le=50, description="Max papers shown per sub-topic (null = all)"
    )
    max_clusters: int | None = Field(
        None, ge=2, le=20, description="Max number of sub-topics (null = server default)"
    )


class RecommendResponse(BaseModel):
    query: str
    total: int
    clusters: list[Cluster]


class SummarizeRequest(BaseModel):
    title: str
    abstract: str | None = None


class SummarizeResponse(BaseModel):
    summary: str
