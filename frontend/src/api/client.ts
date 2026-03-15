const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail ?? "API error");
  }
  return res.json();
}

export const api = {
  // Datasets
  getDatasets: () => request<import("@/types/dataset").Dataset[]>("/datasets"),
  getDataset: (id: string) => request<import("@/types/dataset").Dataset>(`/datasets/${id}`),
  uploadDataset: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return fetch(`${API_BASE}/datasets/upload`, { method: "POST", body: form }).then(async (r) => {
      if (!r.ok) throw new Error("Upload failed");
      return r.json() as Promise<import("@/types/dataset").Dataset>;
    });
  },

  // Analysis endpoints
  getProfile: (id: string) => request<import("@/types/dataset").DatasetProfile>(`/datasets/${id}/profile`),
  getInsights: (id: string) => request<import("@/types/dataset").DatasetInsightReport>(`/datasets/${id}/insights`),
  getVisualizations: (id: string) => request<import("@/types/dataset").DatasetVisualization>(`/datasets/${id}/visualizations`),
  getExecutiveSummary: (id: string) =>
    request<import("@/types/dataset").ExecutiveSummary>(`/datasets/${id}/executive-summary`, {
      method: "POST",
      body: JSON.stringify({}),
    }),

  // Query endpoints
  analyticalQuery: (id: string, query: string) =>
    request<import("@/types/dataset").AnalyticalAnswer>(`/datasets/${id}/query`, {
      method: "POST",
      body: JSON.stringify({ question: query }),
    }),
  ragQuery: (id: string, query: string) =>
    request<import("@/types/dataset").RagQueryResponse>(`/datasets/${id}/rag-query`, {
      method: "POST",
      body: JSON.stringify({ question: query }),
    }),

  // ETL endpoints
  assessQuality: (id: string) =>
    request<import("@/types/etl").QualityAssessment>(`/datasets/${id}/quality`),
  generateTransformPlan: (id: string, etlRunId: string, qualityAssessmentId: string, strategy: string = "conservative") =>
    request<import("@/types/etl").TransformationPlan>(`/datasets/${id}/etl/plan`, {
      method: "POST",
      body: JSON.stringify({ etl_run_id: etlRunId, quality_assessment_id: qualityAssessmentId, strategy }),
    }),

  // ETL Phase 2
  executeEtl: (id: string, etlRunId: string, qualityAssessmentId: string, strategy: string = "conservative") =>
    request<import("@/types/etl").CuratedResult>(`/datasets/${id}/etl/execute`, {
      method: "POST",
      body: JSON.stringify({ etl_run_id: etlRunId, quality_assessment_id: qualityAssessmentId, strategy }),
    }),
  getCuratedResult: (id: string, etlRunId: string) =>
    request<import("@/types/etl").CuratedResult>(`/datasets/${id}/etl/result?etl_run_id=${encodeURIComponent(etlRunId)}`),
  getLatestCuratedResult: (id: string) =>
    request<import("@/types/etl").CuratedResult>(`/datasets/${id}/etl/latest`),
  getCuratedDownloadUrl: (id: string, etlRunId: string) =>
    `${API_BASE}/datasets/${id}/etl/download?etl_run_id=${encodeURIComponent(etlRunId)}`,

  // ETL Phase 4
  generateEtlNarrative: (id: string, etlRunId: string) =>
    request<import("@/types/etl").EtlNarrative>(`/datasets/${id}/etl/narrative`, {
      method: "POST",
      body: JSON.stringify({ etl_run_id: etlRunId }),
    }),
};
