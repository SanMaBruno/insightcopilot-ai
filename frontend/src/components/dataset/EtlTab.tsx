import { useState, useEffect } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { api } from "@/api/client";
import { Workflow, ShieldCheck, ClipboardList, ChevronRight, Play, Download, CheckCircle2, SkipForward, Zap } from "lucide-react";
import { LoadingState } from "@/components/ui/loading-state";
import { EmptyState } from "@/components/ui/empty-state";
import { StaggerContainer, StaggerItem } from "@/components/ui/animated-section";
import type { QualityAssessment, TransformationPlan, CuratedResult } from "@/types/etl";

const ROLE_CONFIG: Record<string, { label: string; color: string; icon: string }> = {
  valuable_numeric: { label: "Numérica valiosa", color: "text-emerald-400", icon: "🟢" },
  valuable_categorical: { label: "Categórica valiosa", color: "text-emerald-400", icon: "🟢" },
  date_candidate: { label: "Candidata a fecha", color: "text-blue-400", icon: "🔵" },
  low_variance: { label: "Baja variabilidad", color: "text-yellow-400", icon: "🟡" },
  identifier: { label: "Identificador", color: "text-yellow-400", icon: "🟡" },
  high_null: { label: "Nulos altos", color: "text-orange-400", icon: "🟠" },
  noise: { label: "Ruido", color: "text-red-400", icon: "🔴" },
  constant: { label: "Constante", color: "text-red-400", icon: "🔴" },
  empty: { label: "Vacía", color: "text-red-400", icon: "🔴" },
};

const ACTION_LABELS: Record<string, string> = {
  normalize_names: "Normalizar nombres",
  drop_column: "Eliminar columna",
  fill_nulls_median: "Rellenar con mediana",
  fill_nulls_mode: "Rellenar con moda",
  fill_nulls_unknown: "Rellenar con 'Desconocido'",
  cast_type: "Convertir tipo",
  remove_duplicates: "Eliminar duplicados",
  strip_whitespace: "Limpiar espacios",
  keep: "Conservar",
};

function ScoreBar({ label, value }: { label: string; value: number }) {
  const pct = Math.round(value * 100);
  const barColor =
    pct >= 80 ? "bg-emerald-500" : pct >= 60 ? "bg-yellow-500" : "bg-red-500";
  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-muted-foreground w-28 shrink-0">{label}</span>
      <div className="flex-1 h-2 rounded-full bg-muted/40 overflow-hidden">
        <div className={`h-full rounded-full ${barColor} transition-all duration-700`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-mono text-foreground w-10 text-right">{pct}%</span>
    </div>
  );
}

export default function EtlTab({ datasetId }: { datasetId: string }) {
  const [assessment, setAssessment] = useState<QualityAssessment | null>(null);
  const [plan, setPlan] = useState<TransformationPlan | null>(null);
  const [curatedResult, setCuratedResult] = useState<CuratedResult | null>(null);
  const [strategy, setStrategy] = useState<string>("conservative");

  // Phase 3: detect existing curated result on mount
  const latestQuery = useQuery({
    queryKey: ["etl-latest", datasetId],
    queryFn: () => api.getLatestCuratedResult(datasetId),
    retry: false,
  });

  useEffect(() => {
    if (latestQuery.data) {
      setCuratedResult(latestQuery.data);
    }
  }, [latestQuery.data]);

  const qualityQuery = useQuery({
    queryKey: ["quality", datasetId],
    queryFn: () => api.assessQuality(datasetId),
    enabled: false,
  });

  const planMutation = useMutation({
    mutationFn: () =>
      api.generateTransformPlan(datasetId, assessment!.etl_run_id, assessment!.id, strategy),
    onSuccess: (data) => { setPlan(data); setCuratedResult(null); },
  });

  const executeMutation = useMutation({
    mutationFn: () =>
      api.executeEtl(datasetId, assessment!.etl_run_id, assessment!.id, strategy),
    onSuccess: (data) => setCuratedResult(data),
  });

  const handleAssess = async () => {
    const result = await qualityQuery.refetch();
    if (result.data) {
      setAssessment(result.data);
      setPlan(null);
      setCuratedResult(null);
    }
  };

  // Step 0: initial state — check for auto-curated first
  if (!assessment && !curatedResult) {
    if (latestQuery.isLoading) {
      return <LoadingState message="Verificando ETL previo…" />;
    }
    return (
      <div className="space-y-4">
        <EmptyState
          icon={Workflow}
          title="ETL Inteligente"
          description="Evalúa la calidad de tu dataset, clasifica cada columna y genera un plan de transformación automatizado."
        />
        <div className="flex justify-center">
          <button
            onClick={handleAssess}
            disabled={qualityQuery.isFetching}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
          >
            <ShieldCheck className="h-4 w-4" />
            {qualityQuery.isFetching ? "Evaluando…" : "Evaluar Calidad"}
          </button>
        </div>
        {qualityQuery.isError && (
          <p className="text-sm text-destructive text-center">Error al evaluar calidad del dataset.</p>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <StaggerContainer className="space-y-4">
      {/* Step 1: Quality Assessment (only if manual flow started) */}
      {assessment && (
        <StaggerItem>
          <div className="rounded-lg border border-border/30 bg-muted/20 p-4 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-primary" />
                <h3 className="text-sm font-semibold text-foreground">Evaluación de Calidad</h3>
              </div>
              <span className="text-[10px] font-mono text-muted-foreground">
                {assessment.row_count} filas · {assessment.column_count} columnas · {assessment.duplicate_row_count} duplicadas
              </span>
            </div>

            {/* Score bars */}
            <div className="space-y-2">
              <ScoreBar label="General" value={assessment.score.overall} />
              <ScoreBar label="Completitud" value={assessment.score.completeness} />
              <ScoreBar label="Consistencia" value={assessment.score.consistency} />
              <ScoreBar label="Unicidad" value={assessment.score.uniqueness} />
              <ScoreBar label="Validez" value={assessment.score.validity} />
            </div>

            {/* Column table */}
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-border/30">
                    <th className="text-left py-2 px-2 text-muted-foreground font-medium">Columna</th>
                    <th className="text-left py-2 px-2 text-muted-foreground font-medium">Tipo</th>
                    <th className="text-left py-2 px-2 text-muted-foreground font-medium">Clasificación</th>
                    <th className="text-right py-2 px-2 text-muted-foreground font-medium">Nulos</th>
                    <th className="text-right py-2 px-2 text-muted-foreground font-medium">Únicos</th>
                    <th className="text-left py-2 px-2 text-muted-foreground font-medium">Razón</th>
                  </tr>
                </thead>
                <tbody>
                  {assessment.column_assessments.map((col) => {
                    const cfg = ROLE_CONFIG[col.role] ?? { label: col.role, color: "text-muted-foreground", icon: "⚪" };
                    return (
                      <tr key={col.column_name} className="border-b border-border/10 hover:bg-muted/30 transition-colors">
                        <td className="py-1.5 px-2 font-mono text-foreground">{col.column_name}</td>
                        <td className="py-1.5 px-2 text-muted-foreground">{col.dtype}</td>
                        <td className="py-1.5 px-2">
                          <span className={`${cfg.color} font-medium`}>{cfg.icon} {cfg.label}</span>
                        </td>
                        <td className="py-1.5 px-2 text-right font-mono text-muted-foreground">{Math.round(col.null_ratio * 100)}%</td>
                        <td className="py-1.5 px-2 text-right font-mono text-muted-foreground">{Math.round(col.unique_ratio * 100)}%</td>
                        <td className="py-1.5 px-2 text-muted-foreground max-w-[200px] truncate" title={col.reason}>{col.reason}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </StaggerItem>
      )}

        {/* Step 2: Plan generation (only if manual flow started) */}
        {assessment && (
        <StaggerItem>
          <div className="rounded-lg border border-border/30 bg-muted/20 p-4 space-y-4">
            <div className="flex items-center gap-2">
              <ClipboardList className="h-4 w-4 text-primary" />
              <h3 className="text-sm font-semibold text-foreground">Plan de Transformación</h3>
            </div>

            {!plan ? (
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <label className="text-xs text-muted-foreground">Estrategia:</label>
                  <select
                    value={strategy}
                    onChange={(e) => setStrategy(e.target.value)}
                    className="text-xs bg-muted/40 border border-border/30 rounded-md px-2 py-1 text-foreground"
                  >
                    <option value="conservative">Conservadora</option>
                    <option value="aggressive">Agresiva</option>
                  </select>
                </div>
                <button
                  onClick={() => planMutation.mutate()}
                  disabled={planMutation.isPending}
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
                >
                  <ChevronRight className="h-4 w-4" />
                  {planMutation.isPending ? "Generando…" : "Generar Plan"}
                </button>
                {planMutation.isError && (
                  <p className="text-sm text-destructive">Error al generar plan de transformación.</p>
                )}
              </div>
            ) : (
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-primary/10 text-primary font-medium uppercase tracking-wider">
                    {plan.strategy === "conservative" ? "Conservadora" : "Agresiva"}
                  </span>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-muted text-muted-foreground font-medium uppercase tracking-wider">
                    {plan.status}
                  </span>
                  <span className="text-[10px] text-muted-foreground font-mono">
                    {plan.steps.length} acción(es)
                  </span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="border-b border-border/30">
                        <th className="text-left py-2 px-2 text-muted-foreground font-medium">#</th>
                        <th className="text-left py-2 px-2 text-muted-foreground font-medium">Columna</th>
                        <th className="text-left py-2 px-2 text-muted-foreground font-medium">Acción</th>
                        <th className="text-left py-2 px-2 text-muted-foreground font-medium">Razón</th>
                      </tr>
                    </thead>
                    <tbody>
                      {plan.steps.map((step) => (
                        <tr key={step.priority} className="border-b border-border/10 hover:bg-muted/30 transition-colors">
                          <td className="py-1.5 px-2 font-mono text-muted-foreground">{step.priority}</td>
                          <td className="py-1.5 px-2 font-mono text-foreground">
                            {step.column_name ?? <span className="text-muted-foreground italic">filas</span>}
                          </td>
                          <td className="py-1.5 px-2">
                            <span className={
                              step.action === "drop_column" ? "text-red-400 font-medium"
                              : step.action === "keep" ? "text-muted-foreground"
                              : "text-blue-400 font-medium"
                            }>
                              {ACTION_LABELS[step.action] ?? step.action}
                            </span>
                          </td>
                          <td className="py-1.5 px-2 text-muted-foreground max-w-[250px] truncate" title={step.reason}>
                            {step.reason}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <button
                  onClick={() => { setPlan(null); setCuratedResult(null); }}
                  className="text-xs text-muted-foreground hover:text-foreground transition-colors"
                >
                  ← Cambiar estrategia
                </button>

                {/* Execute button */}
                {!curatedResult && (
                  <div className="pt-2 border-t border-border/20">
                    <button
                      onClick={() => executeMutation.mutate()}
                      disabled={executeMutation.isPending}
                      className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-700 transition-colors disabled:opacity-50"
                    >
                      <Play className="h-4 w-4" />
                      {executeMutation.isPending ? "Ejecutando…" : "Aplicar Plan"}
                    </button>
                    {executeMutation.isError && (
                      <p className="text-sm text-destructive mt-2">Error al ejecutar el plan ETL.</p>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </StaggerItem>
        )}

        {/* Step 3: Execution result */}
        {curatedResult && (
          <StaggerItem>
            <div className="rounded-lg border border-border/30 bg-muted/20 p-4 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                  <h3 className="text-sm font-semibold text-foreground">Resultado de Ejecución</h3>
                  {curatedResult.execution_mode === "auto_safe" && (
                    <span className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-500 font-medium uppercase tracking-wider">
                      <Zap className="h-3 w-3" />
                      ETL Automático
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-500 font-medium uppercase tracking-wider">
                    {curatedResult.strategy === "conservative" ? "Conservadora" : "Agresiva"}
                  </span>
                  <span className="text-[10px] font-mono text-muted-foreground">
                    {curatedResult.execution_time_ms}ms
                  </span>
                </div>
              </div>

              {/* Before / After comparison */}
              <div className="grid grid-cols-3 gap-4">
                <ComparisonCard label="Filas" before={curatedResult.original_row_count} after={curatedResult.curated_row_count} />
                <ComparisonCard label="Columnas" before={curatedResult.original_column_count} after={curatedResult.curated_column_count} />
                <ComparisonCard label="Nulos" before={curatedResult.original_null_count} after={curatedResult.curated_null_count} />
              </div>

              {/* Step summary */}
              {(() => {
                const successSteps = curatedResult.executed_steps.filter((s) => s.success);
                const skippedSteps = curatedResult.executed_steps.filter((s) => !s.success);
                return (
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <CheckCircle2 className="h-3 w-3 text-emerald-500" />
                      {successSteps.length} ejecutado(s)
                    </span>
                    <span className="flex items-center gap-1">
                      <SkipForward className="h-3 w-3 text-yellow-500" />
                      {skippedSteps.length} omitido(s)
                    </span>
                  </div>
                );
              })()}

              {/* Executed steps table */}
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-border/30">
                      <th className="text-left py-2 px-2 text-muted-foreground font-medium">Estado</th>
                      <th className="text-left py-2 px-2 text-muted-foreground font-medium">Columna</th>
                      <th className="text-left py-2 px-2 text-muted-foreground font-medium">Acción</th>
                      <th className="text-left py-2 px-2 text-muted-foreground font-medium">Detalle</th>
                    </tr>
                  </thead>
                  <tbody>
                    {curatedResult.executed_steps.map((step, idx) => (
                      <tr key={idx} className="border-b border-border/10 hover:bg-muted/30 transition-colors">
                        <td className="py-1.5 px-2">
                          {step.success ? (
                            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                          ) : (
                            <SkipForward className="h-3.5 w-3.5 text-yellow-500" />
                          )}
                        </td>
                        <td className="py-1.5 px-2 font-mono text-foreground">
                          {step.column_name ?? <span className="text-muted-foreground italic">global</span>}
                        </td>
                        <td className="py-1.5 px-2">
                          <span className={step.success ? "text-blue-400 font-medium" : "text-muted-foreground"}>
                            {ACTION_LABELS[step.action] ?? step.action}
                          </span>
                        </td>
                        <td className="py-1.5 px-2 text-muted-foreground max-w-[280px] truncate" title={step.detail}>
                          {step.detail}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Download */}
              <div className="flex justify-between items-center">
                {curatedResult.execution_mode === "auto_safe" && !assessment && (
                  <button
                    onClick={handleAssess}
                    disabled={qualityQuery.isFetching}
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-border/30 text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-muted/30 transition-colors disabled:opacity-50"
                  >
                    <ShieldCheck className="h-4 w-4" />
                    {qualityQuery.isFetching ? "Evaluando…" : "Iniciar flujo manual"}
                  </button>
                )}
                <div className="ml-auto">
                  <a
                    href={api.getCuratedDownloadUrl(datasetId, curatedResult.etl_run_id)}
                    download
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors"
                  >
                    <Download className="h-4 w-4" />
                    Descargar CSV Curado
                  </a>
                </div>
              </div>
            </div>
          </StaggerItem>
        )}
      </StaggerContainer>
    </div>
  );
}

function ComparisonCard({ label, before, after }: { label: string; before: number; after: number }) {
  const diff = after - before;
  const diffLabel = diff === 0 ? "sin cambio" : diff > 0 ? `+${diff}` : `${diff}`;
  const diffColor = diff === 0 ? "text-muted-foreground" : diff < 0 ? "text-emerald-400" : "text-yellow-400";
  return (
    <div className="rounded-md border border-border/20 bg-background/50 p-3 text-center space-y-1">
      <p className="text-[10px] text-muted-foreground uppercase tracking-wider">{label}</p>
      <div className="flex items-center justify-center gap-2">
        <span className="text-sm font-mono text-muted-foreground">{before.toLocaleString()}</span>
        <span className="text-muted-foreground">→</span>
        <span className="text-sm font-mono text-foreground font-semibold">{after.toLocaleString()}</span>
      </div>
      <p className={`text-[10px] font-mono ${diffColor}`}>{diffLabel}</p>
    </div>
  );
}
