import { useState } from "react";
import { postRagQuery } from "../api/datasets";
import type { RagQueryResponse } from "../types/api";
import { ErrorBox, InfoBanner } from "./ui";

export default function RagQuerySection({ datasetId }: { datasetId: string }) {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<RagQueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    try {
      setLoading(true);
      setError(null);
      const data = await postRagQuery(datasetId, question);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <InfoBanner>
        Requiere OPENAI_API_KEY y documentos indexados. Combina datos del dataset con documentos para responder preguntas.
      </InfoBanner>

      <form onSubmit={handleSubmit} className="flex gap-3 mb-6">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Pregunta sobre los documentos indexados…"
          className="flex-1 border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition"
        >
          {loading ? "Buscando…" : "Preguntar"}
        </button>
      </form>

      {error && <ErrorBox message={error} />}

      {result && (
        <div className="space-y-4">
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <p className="text-gray-900">{result.answer}</p>
          </div>

          {result.sources.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Fuentes</h3>
              <div className="grid gap-2">
                {result.sources.map((src, i) => (
                  <div
                    key={i}
                    className="bg-gray-50 border border-gray-200 rounded-lg px-4 py-3 text-sm"
                  >
                    <p className="text-xs text-gray-500 mb-1">
                      {src.source} · chunk {src.chunk_index}
                    </p>
                    <p className="text-gray-700 line-clamp-3">{src.content}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
