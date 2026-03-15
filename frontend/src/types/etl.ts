export interface ColumnClassification {
  column_name: string;
  dtype: string;
  role: string;
  null_ratio: number;
  unique_ratio: number;
  reason: string;
  secondary_flags: string[];
}

export interface QualityScore {
  completeness: number;
  consistency: number;
  uniqueness: number;
  validity: number;
  overall: number;
}

export interface QualityAssessment {
  id: string;
  dataset_id: string;
  etl_run_id: string;
  score: QualityScore;
  column_assessments: ColumnClassification[];
  row_count: number;
  column_count: number;
  duplicate_row_count: number;
}

export interface TransformationStep {
  column_name: string | null;
  action: string;
  params: Record<string, string>;
  reason: string;
  priority: number;
}

export interface TransformationPlan {
  id: string;
  dataset_id: string;
  etl_run_id: string;
  quality_assessment_id: string;
  strategy: string;
  status: string;
  steps: TransformationStep[];
}

export interface ExecutedStep {
  action: string;
  column_name: string | null;
  success: boolean;
  rows_before: number;
  rows_after: number;
  columns_before: number;
  columns_after: number;
  detail: string;
}

export interface CuratedResult {
  id: string;
  dataset_id: string;
  etl_run_id: string;
  plan_id: string;
  strategy: string;
  status: string;
  curated_file_path: string;
  original_row_count: number;
  curated_row_count: number;
  original_column_count: number;
  curated_column_count: number;
  original_null_count: number;
  curated_null_count: number;
  executed_steps: ExecutedStep[];
  execution_time_ms: number;
}
}
