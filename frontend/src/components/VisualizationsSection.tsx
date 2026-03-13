import { Suspense, lazy, useEffect, useState } from "react";
import { getVisualizations } from "../api/datasets";
import type { ChartResult, DatasetVisualization } from "../types/api";
import { Spinner, ErrorBox, EmptyState } from "./ui";
import { getChartTemplate } from "./chartTemplates";

const InteractiveChart = lazy(() => import("./InteractiveChart"));

function canRenderInteractiveChart(chart: ChartResult): boolean {
  const spec = chart.interactive_spec;
  if (!spec) {
    return false;
  }
  if (spec.categories.length === 0 || spec.series.length === 0) {
    return false;
  }
  return spec.series.every((series) => series.data.length === spec.categories.length);
}

function ChartSkeleton() {
  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50/80 p-6">
      <div className="h-4 w-32 animate-pulse rounded bg-slate-200" />
      <div className="mt-3 h-56 animate-pulse rounded-2xl bg-slate-100" />
    </div>
  );
}

function ChartsLoadingState() {
  return (
    <div className="space-y-5">
      <div className="rounded-2xl border border-slate-200 bg-[radial-gradient(circle_at_top_left,_rgba(59,130,246,0.10),_transparent_40%),linear-gradient(180deg,#ffffff_0%,#f8fafc_100%)] p-5 shadow-[0_20px_40px_-30px_rgba(15,23,42,0.35)]">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">
          Charts
        </p>
        <h2 className="mt-2 text-xl font-semibold text-slate-900">
          Preparando visualizaciones del dataset
        </h2>
        <p className="mt-2 max-w-2xl text-sm text-slate-600">
          Estamos organizando la vista analitica para mostrar los graficos con el mejor formato disponible.
        </p>
      </div>

      <Spinner text="Cargando visualizaciones y preparando el render interactivo..." />

      <div className="grid gap-6 xl:grid-cols-2">
        <ChartSkeleton />
        <ChartSkeleton />
      </div>
    </div>
  );
}

function ChartsErrorState({
  message,
  onRetry,
}: {
  message: string;
  onRetry: () => void;
}) {
  return (
    <div className="space-y-5">
      <div className="rounded-2xl border border-slate-200 bg-[radial-gradient(circle_at_top_left,_rgba(59,130,246,0.10),_transparent_40%),linear-gradient(180deg,#ffffff_0%,#f8fafc_100%)] p-5 shadow-[0_20px_40px_-30px_rgba(15,23,42,0.35)]">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">
          Charts
        </p>
        <h2 className="mt-2 text-xl font-semibold text-slate-900">
          No fue posible cargar las visualizaciones
        </h2>
        <p className="mt-2 max-w-2xl text-sm text-slate-600">
          La seccion de charts no pudo completarse en este momento. Puedes reintentar sin afectar el resto del dataset.
        </p>
      </div>
      <ErrorBox message={message} onRetry={onRetry} />
    </div>
  );
}

function ChartsEmptyState() {
  return (
    <div className="space-y-5">
      <div className="rounded-2xl border border-slate-200 bg-[radial-gradient(circle_at_top_left,_rgba(59,130,246,0.10),_transparent_40%),linear-gradient(180deg,#ffffff_0%,#f8fafc_100%)] p-5 shadow-[0_20px_40px_-30px_rgba(15,23,42,0.35)]">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">
          Charts
        </p>
        <h2 className="mt-2 text-xl font-semibold text-slate-900">
          Aun no hay visualizaciones disponibles
        </h2>
        <p className="mt-2 max-w-2xl text-sm text-slate-600">
          Este dataset no produjo graficos renderizables con la configuracion actual. Puedes continuar con profile, insights y query analitico.
        </p>
      </div>
      <EmptyState
        icon="📊"
        title="Sin charts para mostrar"
        description="Cuando haya informacion suficiente, esta seccion mostrara las visualizaciones automaticamente."
      />
    </div>
  );
}

export default function VisualizationsSection({ datasetId }: { datasetId: string }) {
  const [viz, setViz] = useState<DatasetVisualization | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    getVisualizations(datasetId)
      .then((data) => {
        if (!active) return;
        setViz(data);
        setError(null);
      })
      .catch((err) => {
        if (!active) return;
        setError(err instanceof Error ? err.message : "Error");
      })
      .finally(() => {
        if (!active) return;
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [datasetId]);

  if (loading) return <ChartsLoadingState />;
  if (error) return <ChartsErrorState message={error} onRetry={() => window.location.reload()} />;
  if (!viz || viz.charts.length === 0) return <ChartsEmptyState />;

  return (
    <div className="space-y-5">
      <div className="rounded-2xl border border-slate-200 bg-[radial-gradient(circle_at_top_left,_rgba(59,130,246,0.12),_transparent_40%),linear-gradient(180deg,#ffffff_0%,#f8fafc_100%)] p-5 shadow-[0_20px_40px_-30px_rgba(15,23,42,0.35)]">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">
          Charts
        </p>
        <h2 className="mt-2 text-xl font-semibold text-slate-900">
          Visualizaciones analiticas del dataset
        </h2>
        <p className="mt-2 max-w-2xl text-sm text-slate-600">
          La vista prioriza charts interactivos cuando hay estructura suficiente y mantiene una representacion visual de respaldo cuando corresponde.
        </p>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
      {viz.charts.map((chart, i) => {
        const template = getChartTemplate(chart.chart_type);
        const showInteractive = canRenderInteractiveChart(chart);

        return (
        <div
          key={`${chart.chart_type}-${i}`}
          className={`overflow-hidden rounded-2xl border bg-white shadow-[0_18px_40px_-32px_rgba(15,23,42,0.42)] ${template.cardClassName}`}
        >
          <div className="flex items-start justify-between gap-3 border-b border-slate-100 px-5 py-4">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">
                {template.eyebrow}
              </p>
              <h3 className="text-sm font-semibold text-slate-900">{chart.title}</h3>
              <p className="mt-1 max-w-lg text-xs leading-5 text-slate-500">
                {template.description}
              </p>
              <p className="mt-2 text-[11px] uppercase tracking-[0.14em] text-slate-400">
                {chart.chart_type} · {chart.columns.join(", ")}
              </p>
            </div>
            <span
              className="rounded-full px-2.5 py-1 text-[11px] font-medium uppercase tracking-[0.16em] text-slate-600"
              style={{ backgroundColor: template.accentSoft }}
            >
              {showInteractive ? "Interactive" : "Fallback"}
            </span>
          </div>

          <div className="p-4">
            {showInteractive && chart.interactive_spec ? (
              <Suspense fallback={<ChartSkeleton />}>
                <InteractiveChart
                  chartType={chart.chart_type}
                  title={chart.title}
                  spec={chart.interactive_spec}
                />
              </Suspense>
            ) : (
              <div className="space-y-3">
                <div className="rounded-xl border border-amber-100 bg-amber-50/90 px-3 py-2 text-xs text-amber-800">
                  Esta vista usa una imagen generada por el backend como respaldo visual. El chart interactivo no estaba disponible para esta configuracion.
                </div>
                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-3">
                <img
                  src={`data:image/png;base64,${chart.image_base64}`}
                  alt={chart.title}
                  className="w-full rounded-xl"
                />
                </div>
              </div>
            )}
          </div>
        </div>
      )})}
      </div>
    </div>
  );
}
