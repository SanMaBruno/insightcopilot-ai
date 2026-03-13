// ── Dataset ──────────────────────────────────────────────

export interface Dataset {
  id: string;
  name: string;
  file_path: string;
  source_type: string;
  created_at: string;
}

// ── Profile ──────────────────────────────────────────────

export interface ColumnProfile {
  name: string;
  dtype: string;
  null_count: number;
  unique_count: number;
}

export interface DatasetProfile {
  dataset_id: string;
  row_count: number;
  column_count: number;
  columns: ColumnProfile[];
}

// ── Insights ─────────────────────────────────────────────

export interface Insight {
  category: string;
  message: string;
}

export interface DatasetInsightReport {
  dataset_id: string;
  summary: string;
  insights: Insight[];
  warnings: string[];
}

// ── Visualizations ───────────────────────────────────────

export interface ChartResult {
  chart_type: string;
  title: string;
  columns: string[];
  image_base64: string;
}

export interface DatasetVisualization {
  dataset_id: string;
  charts: ChartResult[];
}

// ── Analytical Query ─────────────────────────────────────

export interface AnalyticalAnswer {
  dataset_id: string;
  intent: string;
  question: string;
  answer: string;
  supporting_data: string[];
}

// ── Executive Summary ────────────────────────────────────

export interface ExecutiveSummaryRequest {
  audience?: string;
  tone?: string;
  max_paragraphs?: number;
}

export interface ExecutiveSummary {
  dataset_id: string;
  audience: string;
  tone: string;
  content: string;
}

// ── RAG ──────────────────────────────────────────────────

export interface DocumentChunk {
  source: string;
  content: string;
  chunk_index: number;
}

export interface RagQueryResponse {
  dataset_id: string;
  question: string;
  answer: string;
  sources: DocumentChunk[];
}
