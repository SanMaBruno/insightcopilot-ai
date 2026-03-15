import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import { BarChart3 } from "lucide-react";
import { LoadingState } from "@/components/ui/loading-state";
import { EmptyState } from "@/components/ui/empty-state";
import { StaggerContainer, StaggerItem } from "@/components/ui/animated-section";

export default function VisualizationsTab({ datasetId }: { datasetId: string }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["visualizations", datasetId],
    queryFn: () => api.getVisualizations(datasetId),
  });

  if (isLoading) return <LoadingState message="Cargando gráficos…" size="sm" />;
  if (error) return <p className="text-sm text-destructive">Error al cargar visualizaciones.</p>;
  if (!data || data.charts.length === 0) return <EmptyState icon={BarChart3} title="Aún no hay visualizaciones" description="Los gráficos se generarán una vez que el dataset sea analizado." />;

  return (
    <StaggerContainer className="grid gap-4 sm:grid-cols-2">
      {data.charts.map((chart, i) => (
        <StaggerItem key={i}>
          <div className="rounded-lg border border-border/30 bg-muted/20 overflow-hidden card-hover">
            <div className="p-3 border-b border-border/30">
              <div className="flex items-center gap-2">
                <BarChart3 className="h-3.5 w-3.5 text-primary" />
                <h4 className="text-xs font-medium text-foreground">{chart.title}</h4>
              </div>
              <span className="text-[10px] font-mono text-muted-foreground mt-0.5 inline-block">{chart.chart_type}</span>
            </div>
            <div className="p-3">
              {chart.image_base64 ? (
                <img src={`data:image/png;base64,${chart.image_base64}`} alt={chart.title} className="w-full rounded-md" />
              ) : (
                <div className="h-44 rounded-md bg-muted/30 flex items-center justify-center dot-pattern">
                  <span className="text-xs text-muted-foreground">{chart.chart_type} chart</span>
                </div>
              )}
            </div>
          </div>
        </StaggerItem>
      ))}
    </StaggerContainer>
  );
}
