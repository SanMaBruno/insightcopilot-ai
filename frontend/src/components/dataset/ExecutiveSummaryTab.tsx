import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import { FileText, AlertCircle } from "lucide-react";
import { LoadingState } from "@/components/ui/loading-state";
import { EmptyState } from "@/components/ui/empty-state";
import { AnimatedSection } from "@/components/ui/animated-section";

function isOpenAIError(error: unknown): boolean {
  const msg = String(error);
  return msg.includes("429") || msg.includes("insufficient_quota") || msg.includes("openai") || msg.includes("OpenAI");
}

export default function ExecutiveSummaryTab({ datasetId }: { datasetId: string }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["executive-summary", datasetId],
    queryFn: () => api.getExecutiveSummary(datasetId),
    retry: false,
    staleTime: Infinity,
  });

  if (isLoading) return <LoadingState message="Generando resumen ejecutivo…" size="sm" />;

  if (error) {
    return (
      <div className="rounded-lg border border-destructive/30 bg-destructive/5 p-4">
        <div className="flex items-start gap-2">
          <AlertCircle className="h-4 w-4 text-destructive mt-0.5 shrink-0" />
          <div>
            {isOpenAIError(error) ? (
              <>
                <p className="text-sm font-medium text-destructive">Créditos de OpenAI no disponibles</p>
                <p className="text-xs text-destructive/80 mt-1">Esta funcionalidad requiere créditos de OpenAI que actualmente no están disponibles. Configura una API key con saldo activo para generar resúmenes ejecutivos.</p>
              </>
            ) : (
              <p className="text-sm text-destructive">Error al cargar el resumen.</p>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (!data) return <EmptyState icon={FileText} title="Sin resumen disponible" />;

  return (
    <AnimatedSection>
      <div className="flex items-center gap-2 mb-4">
        <FileText className="h-4 w-4 text-primary" />
        <h3 className="text-sm font-medium text-foreground">Resumen Ejecutivo</h3>
        <span className="text-[10px] rounded-full bg-primary/10 px-2 py-0.5 text-primary font-medium">Generado por IA</span>
      </div>
      <div className="rounded-lg border border-border/30 bg-muted/20 p-5">
        <p className="text-sm text-foreground/90 whitespace-pre-wrap leading-relaxed">{data.content}</p>
      </div>
    </AnimatedSection>
  );
}
