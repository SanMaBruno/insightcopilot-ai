import { useState } from "react";
import { postExecutiveSummary } from "../api/datasets";
import type { ExecutiveSummary } from "../types/api";

export default function ExecutiveSummarySection({ datasetId }: { datasetId: string }) {
  const [summary, setSummary] = useState<ExecutiveSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [audience, setAudience] = useState("equipo técnico");
  const [tone, setTone] = useState("profesional");

  const handleGenerate = async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await postExecutiveSummary(datasetId, {
        audience,
        tone,
        max_paragraphs: 3,
      });
      setSummary(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="flex gap-3 items-end mb-6">
        <div>
          <label className="block text-xs text-gray-500 mb-1">Audiencia</label>
          <input
            type="text"
            value={audience}
            onChange={(e) => setAudience(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">Tono</label>
          <input
            type="text"
            value={tone}
            onChange={(e) => setTone(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition"
        >
          {loading ? "Generando…" : "Generar resumen"}
        </button>
      </div>

      {error && <p className="text-sm text-red-600 mb-4">{error}</p>}

      {summary && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <p className="text-xs text-gray-500 mb-3">
            Para: {summary.audience} · Tono: {summary.tone}
          </p>
          <div className="prose prose-sm max-w-none text-gray-800 whitespace-pre-line">
            {summary.content}
          </div>
        </div>
      )}
    </div>
  );
}
