export interface Dataset {
  id: string;
  name: string;
  file_path: string;
  source_type: string;
  created_at: string;
}

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

export interface ChartSeries {
  name: string;
  data: number[];
  color?: string;
}

export interface InteractiveChartSpec {
  chart_kind: string;
  subtitle: string;
  categories: string[];
  series: ChartSeries[];
  x_axis_label: string;
  y_axis_label: string;
  tooltip_suffix: string;
  source_label: string;
}

export interface ChartResult {
  chart_type: string;
  title: string;
  columns: string[];
  image_base64: string;
  interactive_spec?: InteractiveChartSpec;
}

export interface DatasetVisualization {
  dataset_id: string;
  charts: ChartResult[];
}

export interface ExecutiveSummary {
  dataset_id: string;
  audience: string;
  tone: string;
  content: string;
}

export interface AnalyticalAnswer {
  dataset_id: string;
  intent: string;
  question: string;
  answer: string;
  supporting_data: string[];
}

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
