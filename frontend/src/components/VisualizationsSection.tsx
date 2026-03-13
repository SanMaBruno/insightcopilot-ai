import { useEffect, useState } from "react";
import { getVisualizations } from "../api/datasets";
import type { DatasetVisualization } from "../types/api";
import { Spinner, ErrorBox, EmptyState } from "./ui";

export default function VisualizationsSection({ datasetId }: { datasetId: string }) {
  const [viz, setViz] = useState<DatasetVisualization | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    getVisualizations(datasetId)
      .then(setViz)
      .catch((err) => setError(err instanceof Error ? err.message : "Error"))
      .finally(() => setLoading(false));
  }, [datasetId]);

  if (loading) return <Spinner text="Generando visualizaciones…" />;
  if (error) return <ErrorBox message={error} onRetry={() => { setError(null); setLoading(true); getVisualizations(datasetId).then(setViz).catch((e) => setError(e instanceof Error ? e.message : "Error")).finally(() => setLoading(false)); }} />;
  if (!viz || viz.charts.length === 0) return <EmptyState icon="📊" title="Sin gráficos disponibles" description="No se pudieron generar visualizaciones para este dataset" />;

  return (
    <div className="grid gap-6 md:grid-cols-2">
      {viz.charts.map((chart, i) => (
        <div key={i} className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-2">{chart.title}</h3>
          <p className="text-xs text-gray-500 mb-3">
            {chart.chart_type} · {chart.columns.join(", ")}
          </p>
          <img
            src={`data:image/png;base64,${chart.image_base64}`}
            alt={chart.title}
            className="w-full rounded"
          />
        </div>
      ))}
    </div>
  );
}
