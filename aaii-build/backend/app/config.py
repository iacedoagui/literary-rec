"""Runtime configuration, read from the environment (see .env.example)."""
import os

from dotenv import load_dotenv

load_dotenv()


def _read_api_key() -> str:
    """Read the Anthropic key, treating the .env.example placeholder as unset."""
    key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if key in ("", "sk-ant-...", "sk-ant-api03-..."):
        return ""
    return key


class Settings:
    # Claude
    anthropic_api_key: str = _read_api_key()
    # Default to Opus 4.8 for quality. Switch to claude-haiku-4-5 for cheaper,
    # faster summaries at scale by setting SUMMARY_MODEL / LABEL_MODEL.
    summary_model: str = os.getenv("SUMMARY_MODEL", "claude-opus-4-8")
    label_model: str = os.getenv("LABEL_MODEL", "claude-opus-4-8")

    # Embeddings / clustering
    embedding_model: str = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    max_clusters: int = int(os.getenv("MAX_CLUSTERS", "8"))

    # Sources
    max_results_per_source: int = int(os.getenv("MAX_RESULTS_PER_SOURCE", "25"))
    semantic_scholar_api_key: str = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")

    # CORS
    allowed_origins: list[str] = os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:5173"
    ).split(",")


settings = Settings()
