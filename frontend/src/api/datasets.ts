import { request, uploadFile } from "./client";
import type {
  AnalyticalAnswer,
  Dataset,
  DatasetInsightReport,
  DatasetProfile,
  DatasetVisualization,
  ExecutiveSummary,
  ExecutiveSummaryRequest,
  RagQueryResponse,
} from "../types/api";

// ── Datasets ─────────────────────────────────────────────

export function listDatasets(): Promise<Dataset[]> {
  return request<Dataset[]>("/datasets");
}

export function getDataset(id: string): Promise<Dataset> {
  return request<Dataset>(`/datasets/${id}`);
}

export function uploadDataset(file: File): Promise<Dataset> {
  return uploadFile<Dataset>("/datasets/upload", file);
}

// ── Analysis ─────────────────────────────────────────────

export function getProfile(id: string): Promise<DatasetProfile> {
  return request<DatasetProfile>(`/datasets/${id}/profile`);
}

export function getInsights(id: string): Promise<DatasetInsightReport> {
  return request<DatasetInsightReport>(`/datasets/${id}/insights`);
}

export function getVisualizations(id: string): Promise<DatasetVisualization> {
  return request<DatasetVisualization>(`/datasets/${id}/visualizations`);
}

export function postQuery(id: string, question: string): Promise<AnalyticalAnswer> {
  return request<AnalyticalAnswer>(`/datasets/${id}/query`, {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}

// ── LLM ──────────────────────────────────────────────────

export function postExecutiveSummary(
  id: string,
  params?: ExecutiveSummaryRequest,
): Promise<ExecutiveSummary> {
  return request<ExecutiveSummary>(`/datasets/${id}/executive-summary`, {
    method: "POST",
    body: JSON.stringify(params ?? {}),
  });
}

export function postRagQuery(
  id: string,
  question: string,
  topK = 5,
): Promise<RagQueryResponse> {
  return request<RagQueryResponse>(`/datasets/${id}/rag-query`, {
    method: "POST",
    body: JSON.stringify({ question, top_k: topK }),
  });
}
