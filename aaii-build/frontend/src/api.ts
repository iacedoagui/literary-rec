import type { Paper, RecommendResponse } from "./types";

export async function recommend(
  query: string,
  limit = 40,
  perTopicLimit: number | null = null,
  maxClusters: number | null = null
): Promise<RecommendResponse> {
  const resp = await fetch("/api/recommend", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      limit,
      per_topic_limit: perTopicLimit,
      max_clusters: maxClusters,
    }),
  });
  if (!resp.ok) {
    const detail = await resp.text();
    throw new Error(`Search failed (${resp.status}): ${detail}`);
  }
  return resp.json();
}

export async function summarize(paper: Paper): Promise<string> {
  const resp = await fetch("/api/summarize", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title: paper.title, abstract: paper.abstract }),
  });
  if (!resp.ok) {
    const detail = await resp.text();
    throw new Error(`Summary failed (${resp.status}): ${detail}`);
  }
  const data = (await resp.json()) as { summary: string };
  return data.summary;
}
