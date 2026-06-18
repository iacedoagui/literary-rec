import { useState } from "react";
import type { Paper } from "../types";
import { summarize } from "../api";

export function PaperCard({ paper }: { paper: Paper }) {
  const [open, setOpen] = useState(false);
  const [summary, setSummary] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function toggle() {
    const next = !open;
    setOpen(next);
    // Lazily fetch the summary the first time the card is expanded.
    if (next && summary === null && !loading) {
      setLoading(true);
      setError(null);
      try {
        setSummary(await summarize(paper));
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load summary");
      } finally {
        setLoading(false);
      }
    }
  }

  const authors =
    paper.authors.length > 3
      ? `${paper.authors.slice(0, 3).join(", ")} et al.`
      : paper.authors.join(", ");

  return (
    <div className="paper-card">
      <div className="paper-head">
        <a href={paper.url ?? "#"} target="_blank" rel="noreferrer" className="paper-title">
          {paper.title}
        </a>
        <span className={`source-badge ${paper.source === "arXiv" ? "arxiv" : "s2"}`}>
          {paper.source}
        </span>
      </div>

      <div className="paper-meta">
        {authors}
        {paper.year ? ` · ${paper.year}` : ""}
        {paper.pdf_url ? (
          <>
            {" · "}
            <a href={paper.pdf_url} target="_blank" rel="noreferrer">
              PDF
            </a>
          </>
        ) : null}
      </div>

      <button className="toggle-btn" onClick={toggle}>
        {open ? "▾ Hide summary" : "▸ Show summary"}
      </button>

      {open && (
        <div className="summary">
          {loading && <p className="muted">Summarizing with Claude…</p>}
          {error && <p className="error">{error}</p>}
          {summary && <p>{summary}</p>}
        </div>
      )}
    </div>
  );
}
