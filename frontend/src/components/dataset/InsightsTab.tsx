import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import { Lightbulb, AlertTriangle } from "lucide-react";
import { LoadingState } from "@/components/ui/loading-state";
import { EmptyState } from "@/components/ui/empty-state";
import { StaggerContainer, StaggerItem } from "@/components/ui/animated-section";

export default function InsightsTab({ datasetId }: { datasetId: string }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["insights", datasetId],
    queryFn: () => api.getInsights(datasetId),
  });

  if (isLoading) return <LoadingState message="Generando insights…" size="sm" />;
  if (error) return <p className="text-sm text-destructive">Error al cargar insights.</p>;
  if (!data || data.insights.length === 0) return <EmptyState icon={Lightbulb} title="Aún no hay insights" description="Los insights aparecerán una vez que el dataset sea procesado completamente." />;

  return (
    <div className="space-y-4">
      {data.summary && (
        <div className="rounded-lg border border-border/30 bg-muted/20 p-4">
          <p className="text-sm text-foreground/90 leading-relaxed">{data.summary}</p>
        </div>
      )}

      <StaggerContainer className="grid gap-3">
        {data.insights.map((insight, i) => (
          <StaggerItem key={i}>
            <div className="flex items-start gap-3 p-4 rounded-lg bg-muted/30 border border-border/30 hover:border-primary/20 transition-colors">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-accent/10 mt-0.5">
                <Lightbulb className="h-4 w-4 text-accent" />
              </div>
              <div className="min-w-0">
                <span className="text-[10px] font-semibold uppercase tracking-wider text-primary">{insight.category}</span>
                <p className="text-sm text-foreground mt-0.5 leading-relaxed">{insight.message}</p>
              </div>
            </div>
          </StaggerItem>
        ))}
      </StaggerContainer>

      {data.warnings.length > 0 && (
        <div className="space-y-2 mt-4">
          <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Advertencias</p>
          {data.warnings.map((w, i) => (
            <div key={i} className="flex items-start gap-2 p-3 rounded-lg bg-destructive/5 border border-destructive/20">
              <AlertTriangle className="h-3.5 w-3.5 text-destructive mt-0.5 shrink-0" />
              <p className="text-xs text-destructive">{w}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
