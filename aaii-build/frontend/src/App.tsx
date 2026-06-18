import { useState } from "react";
import { recommend } from "./api";
import type { RecommendResponse } from "./types";
import { ClusterSection } from "./components/ClusterSection";

export default function App() {
  const [query, setQuery] = useState("");
  const [perTopicLimit, setPerTopicLimit] = useState<number | null>(5);
  const [maxClusters, setMaxClusters] = useState<number>(8);
  const [data, setData] = useState<RecommendResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runSearch(q: string) {
    const trimmed = q.trim();
    if (trimmed.length < 2) return;
    setQuery(trimmed);
    setLoading(true);
    setError(null);
    setData(null);
    try {
      setData(await recommend(trimmed, 40, perTopicLimit, maxClusters));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    runSearch(query);
  }

  // Drill down: append the sub-topic label to the query that produced the
  // current results, then search again for more on that specific thing.
  function onExplore(label: string) {
    const base = data?.query ?? query;
    runSearch(`${base} ${label}`);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  return (
    <div className="app">
      <header className="hero">
        <h1>Literature Topic Look-up</h1>
        <p className="subtitle">
          Describe a topic or research idea. Get recommended literature from
          arXiv, grouped into sub-topics, each with an on-demand one-paragraph
          summary.
        </p>
        <form className="search" onSubmit={onSubmit}>
          <input
            type="text"
            value={query}
            placeholder="e.g. diffusion models for protein structure prediction"
            onChange={(e) => setQuery(e.target.value)}
          />
          <button type="submit" disabled={loading}>
            {loading ? "Searching…" : "Search"}
          </button>
        </form>
        <div className="controls">
          <label className="per-topic">
            Papers per sub-topic:
            <select
              value={perTopicLimit ?? "all"}
              onChange={(e) =>
                setPerTopicLimit(
                  e.target.value === "all" ? null : Number(e.target.value)
                )
              }
            >
              <option value="3">3</option>
              <option value="5">5</option>
              <option value="10">10</option>
              <option value="all">All</option>
            </select>
          </label>
          <label className="per-topic">
            Max sub-topics:
            <select
              value={maxClusters}
              onChange={(e) => setMaxClusters(Number(e.target.value))}
            >
              <option value="3">3</option>
              <option value="5">5</option>
              <option value="8">8</option>
              <option value="12">12</option>
            </select>
          </label>
        </div>
      </header>

      <main>
        {loading && (
          <p className="muted center">
            Fetching papers, embedding abstracts, and clustering sub-topics…
          </p>
        )}
        {error && <p className="error center">{error}</p>}
        {data && data.total === 0 && (
          <p className="muted center">No papers found for “{data.query}”.</p>
        )}
        {data && data.total > 0 && (
          <>
            <p className="result-meta">
              {data.total} papers across {data.clusters.length} sub-topics for “
              {data.query}”
            </p>
            {data.clusters.map((c) => (
              <ClusterSection key={c.id} cluster={c} onExplore={onExplore} />
            ))}
          </>
        )}
      </main>
    </div>
  );
}
