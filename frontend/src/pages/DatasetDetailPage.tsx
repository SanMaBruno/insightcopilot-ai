import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getDataset } from "../api/datasets";
import type { Dataset } from "../types/api";
import ProfileSection from "../components/ProfileSection";
import InsightsSection from "../components/InsightsSection";
import VisualizationsSection from "../components/VisualizationsSection";
import QuerySection from "../components/QuerySection";
import ExecutiveSummarySection from "../components/ExecutiveSummarySection";
import RagQuerySection from "../components/RagQuerySection";

const TABS = ["profile", "insights", "visualizations", "query", "executive-summary", "rag"] as const;
type Tab = (typeof TABS)[number];

const TAB_LABELS: Record<Tab, string> = {
  profile: "Profile",
  insights: "Insights",
  visualizations: "Visualizations",
  query: "Analytical Query",
  "executive-summary": "Executive Summary",
  rag: "RAG Query",
};

export default function DatasetDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [dataset, setDataset] = useState<Dataset | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>("profile");

  useEffect(() => {
    if (!id) return;
    getDataset(id)
      .then(setDataset)
      .catch((err) => setError(err instanceof Error ? err.message : "Error"));
  }, [id]);

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
        {error}
      </div>
    );
  }

  if (!dataset) {
    return <p className="text-gray-500 text-sm">Cargando…</p>;
  }

  return (
    <div>
      {/* Breadcrumb + title */}
      <div className="mb-6">
        <Link to="/" className="text-sm text-blue-600 hover:underline">
          ← Datasets
        </Link>
        <h1 className="text-2xl font-bold text-gray-900 mt-2">{dataset.name}</h1>
        <p className="text-sm text-gray-500">
          {dataset.source_type} · {new Date(dataset.created_at).toLocaleDateString()}
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6 flex gap-1 overflow-x-auto">
        {TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium whitespace-nowrap border-b-2 transition ${
              activeTab === tab
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            {TAB_LABELS[tab]}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {activeTab === "profile" && <ProfileSection datasetId={dataset.id} />}
      {activeTab === "insights" && <InsightsSection datasetId={dataset.id} />}
      {activeTab === "visualizations" && <VisualizationsSection datasetId={dataset.id} />}
      {activeTab === "query" && <QuerySection datasetId={dataset.id} />}
      {activeTab === "executive-summary" && <ExecutiveSummarySection datasetId={dataset.id} />}
      {activeTab === "rag" && <RagQuerySection datasetId={dataset.id} />}
    </div>
  );
}
