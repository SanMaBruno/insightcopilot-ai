import { useEffect, useState } from "react";
import { getProfile } from "../api/datasets";
import type { DatasetProfile } from "../types/api";

export default function ProfileSection({ datasetId }: { datasetId: string }) {
  const [profile, setProfile] = useState<DatasetProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    getProfile(datasetId)
      .then(setProfile)
      .catch((err) => setError(err instanceof Error ? err.message : "Error"))
      .finally(() => setLoading(false));
  }, [datasetId]);

  if (loading) return <p className="text-sm text-gray-500">Cargando perfil…</p>;
  if (error) return <p className="text-sm text-red-600">{error}</p>;
  if (!profile) return null;

  return (
    <div>
      <div className="flex gap-6 mb-6">
        <Stat label="Filas" value={profile.row_count.toLocaleString()} />
        <Stat label="Columnas" value={profile.column_count.toLocaleString()} />
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 text-left text-gray-500">
              <th className="pb-2 font-medium">Columna</th>
              <th className="pb-2 font-medium">Tipo</th>
              <th className="pb-2 font-medium text-right">Nulos</th>
              <th className="pb-2 font-medium text-right">Únicos</th>
            </tr>
          </thead>
          <tbody>
            {profile.columns.map((col) => (
              <tr key={col.name} className="border-b border-gray-100">
                <td className="py-2 font-mono text-gray-900">{col.name}</td>
                <td className="py-2 text-gray-600">{col.dtype}</td>
                <td className="py-2 text-right text-gray-600">{col.null_count}</td>
                <td className="py-2 text-right text-gray-600">{col.unique_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg px-4 py-3">
      <p className="text-xs text-gray-500 uppercase tracking-wide">{label}</p>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  );
}
