export interface Paper {
  id: string;
  title: string;
  authors: string[];
  year: number | null;
  abstract: string | null;
  url: string | null;
  pdf_url: string | null;
  source: string;
}

export interface Cluster {
  id: number;
  label: string;
  papers: Paper[];
}

export interface RecommendResponse {
  query: string;
  total: number;
  clusters: Cluster[];
}
