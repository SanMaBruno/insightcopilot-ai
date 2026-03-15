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
