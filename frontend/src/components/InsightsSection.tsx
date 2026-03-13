import { useEffect, useState } from "react";
import { getInsights } from "../api/datasets";
import type { DatasetInsightReport } from "../types/api";

const CATEGORY_COLORS: Record<string, string> = {
  info: "bg-blue-50 text-blue-700 border-blue-200",
  warning: "bg-yellow-50 text-yellow-700 border-yellow-200",
  critical: "bg-red-50 text-red-700 border-red-200",
};

export default function InsightsSection({ datasetId }: { datasetId: string }) {
  const [report, setReport] = useState<DatasetInsightReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    getInsights(datasetId)
      .then(setReport)
      .catch((err) => setError(err instanceof Error ? err.message : "Error"))
      .finally(() => setLoading(false));
  }, [datasetId]);

  if (loading) return <p className="text-sm text-gray-500">Generando insights…</p>;
  if (error) return <p className="text-sm text-red-600">{error}</p>;
  if (!report) return null;

  return (
    <div>
      <p className="text-gray-700 mb-4">{report.summary}</p>

      {report.insights.length > 0 && (
        <div className="grid gap-3 mb-4">
          {report.insights.map((insight, i) => (
            <div
              key={i}
              className={`border rounded-lg px-4 py-3 text-sm ${
                CATEGORY_COLORS[insight.category] ?? "bg-gray-50 text-gray-700 border-gray-200"
              }`}
            >
              <span className="font-medium uppercase text-xs tracking-wide">
                {insight.category}
              </span>
              <p className="mt-1">{insight.message}</p>
            </div>
          ))}
        </div>
      )}

      {report.warnings.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-yellow-800 mb-2">Advertencias</h3>
          <ul className="list-disc list-inside text-sm text-yellow-700 space-y-1">
            {report.warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
