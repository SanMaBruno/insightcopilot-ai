import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "@/api/client";
import { Database, ArrowRight, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { LoadingState } from "@/components/ui/loading-state";
import { SectionHeader } from "@/components/ui/section-header";
import { AnimatedSection, StaggerContainer, StaggerItem } from "@/components/ui/animated-section";

export default function Datasets() {
  const { data: datasets, isLoading, error } = useQuery({
    queryKey: ["datasets"],
    queryFn: api.getDatasets,
  });

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <AnimatedSection>
        <SectionHeader
          icon={Database}
          title="Datasets"
          description="Administra y explora tus datasets subidos."
          action={
            <Link to="/upload">
              <Button size="sm" className="gap-1.5">
                <Plus className="h-3.5 w-3.5" />
                Subir
              </Button>
            </Link>
          }
        />
      </AnimatedSection>

      {isLoading && <LoadingState message="Cargando datasets…" />}

      {error && (
        <AnimatedSection className="glass-card p-4">
          <p className="text-sm text-destructive">
            Error al cargar los datasets. Asegúrate de que el backend esté ejecutándose.
          </p>
        </AnimatedSection>
      )}

      {datasets && datasets.length === 0 && (
        <EmptyState
          icon={Database}
          title="Aún no hay datasets"
          description="Sube un archivo CSV para comenzar a analizar tus datos con IA."
          action={
            <Link to="/upload">
              <Button size="sm" className="gap-1.5">
                <Plus className="h-3.5 w-3.5" />
                Sube tu primer dataset
              </Button>
            </Link>
          }
        />
      )}

      {datasets && datasets.length > 0 && (
        <StaggerContainer className="grid gap-3">
          {datasets.map((ds) => (
            <StaggerItem key={ds.id}>
              <Link to={`/datasets/${ds.id}`}>
                <div className="glass-card card-hover flex items-center justify-between p-4 group cursor-pointer">
                  <div className="flex items-center gap-4 min-w-0">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                      <Database className="h-4 w-4 text-primary" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-foreground truncate">{ds.name}</p>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {ds.source_type}
                        <span className="mx-1.5 opacity-40">·</span>
                        {new Date(ds.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <ArrowRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 group-hover:translate-x-0.5 transition-all" />
                  </div>
                </div>
              </Link>
            </StaggerItem>
          ))}
        </StaggerContainer>
      )}
    </div>
  );
}
