import { useState } from "react";
import type { Cluster } from "../types";
import { PaperCard } from "./PaperCard";

export function ClusterSection({
  cluster,
  onExplore,
}: {
  cluster: Cluster;
  onExplore: (label: string) => void;
}) {
  const [open, setOpen] = useState(false);

  return (
    <section className="cluster">
      <button
        className="cluster-header"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
      >
        <span className="chevron">{open ? "▾" : "▸"}</span>
        <span className="cluster-label">{cluster.label}</span>
        <span className="cluster-count">{cluster.papers.length}</span>
      </button>

      {open && (
        <div className="cluster-body">
          <div className="paper-list">
            {cluster.papers.map((p) => (
              <PaperCard key={p.id} paper={p} />
            ))}
          </div>
          <button
            className="explore-btn"
            title={`Refine the search with "${cluster.label}"`}
            onClick={() => onExplore(cluster.label)}
          >
            Explore this sub-topic ↳
          </button>
        </div>
      )}
    </section>
  );
}
