import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import { Table2 } from "lucide-react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { LoadingState } from "@/components/ui/loading-state";
import { EmptyState } from "@/components/ui/empty-state";

export default function ProfileTab({ datasetId }: { datasetId: string }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["profile", datasetId],
    queryFn: () => api.getProfile(datasetId),
  });

  if (isLoading) return <LoadingState message="Perfilando datos…" size="sm" />;
  if (error) return <p className="text-sm text-destructive">Error al cargar el perfil.</p>;
  if (!data) return <EmptyState icon={Table2} title="Sin datos de perfil" />;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <div className="rounded-lg bg-primary/10 px-3 py-1.5">
          <span className="text-xs font-medium text-primary font-mono">{data.row_count.toLocaleString()} filas</span>
        </div>
        <div className="rounded-lg bg-accent/10 px-3 py-1.5">
          <span className="text-xs font-medium text-accent font-mono">{data.column_count} columnas</span>
        </div>
      </div>
      <div className="rounded-lg border border-border/50 overflow-auto">
        <Table>
          <TableHeader>
            <TableRow className="border-border/50 hover:bg-transparent">
              <TableHead className="text-xs font-semibold uppercase tracking-wider text-muted-foreground/70">Columna</TableHead>
              <TableHead className="text-xs font-semibold uppercase tracking-wider text-muted-foreground/70">Tipo</TableHead>
              <TableHead className="text-right text-xs font-semibold uppercase tracking-wider text-muted-foreground/70">Nulos</TableHead>
              <TableHead className="text-right text-xs font-semibold uppercase tracking-wider text-muted-foreground/70">Únicos</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.columns.map((col) => (
              <TableRow key={col.name} className="border-border/30 hover:bg-muted/30 transition-colors">
                <TableCell className="font-medium text-sm">{col.name}</TableCell>
                <TableCell className="text-muted-foreground font-mono text-xs">{col.dtype}</TableCell>
                <TableCell className="text-right font-mono text-xs">{col.null_count.toLocaleString()}</TableCell>
                <TableCell className="text-right font-mono text-xs">{col.unique_count.toLocaleString()}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
