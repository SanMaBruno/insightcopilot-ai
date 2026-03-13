import { useState } from "react";
import { postQuery } from "../api/datasets";
import type { AnalyticalAnswer } from "../types/api";
import { ErrorBox, InfoBanner } from "./ui";

export default function QuerySection({ datasetId }: { datasetId: string }) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<AnalyticalAnswer | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    try {
      setLoading(true);
      setError(null);
      const result = await postQuery(datasetId, question);
      setAnswer(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <InfoBanner>
        Consulta analítica local — no requiere API key. Prueba: "¿Cuántas filas tiene el dataset?", "resumen", "nulos".
      </InfoBanner>

      <form onSubmit={handleSubmit} className="flex gap-3 mb-6">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ej: ¿Cuántos nulos tiene el dataset?"
          className="flex-1 border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition"
        >
          {loading ? "Consultando…" : "Consultar"}
        </button>
      </form>

      {error && <ErrorBox message={error} />}

      {answer && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <p className="text-xs text-gray-500 mb-1">
            Intent: <span className="font-medium">{answer.intent}</span>
          </p>
          <p className="text-gray-900">{answer.answer}</p>

          {answer.supporting_data.length > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-100">
              <p className="text-xs text-gray-500 mb-1">Datos de soporte</p>
              <ul className="text-sm text-gray-700 space-y-1">
                {answer.supporting_data.map((d, i) => (
                  <li key={i} className="font-mono text-xs bg-gray-50 px-2 py-1 rounded">
                    {d}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
