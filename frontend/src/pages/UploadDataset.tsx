import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import { Upload, FileUp, Loader2, CheckCircle2, File } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { AnimatedSection } from "@/components/ui/animated-section";
import { SectionHeader } from "@/components/ui/section-header";

export default function UploadDataset() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const mutation = useMutation({
    mutationFn: (file: File) => api.uploadDataset(file),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["datasets"] });
      toast.success("Dataset subido exitosamente");
      navigate(`/datasets/${data.id}`);
    },
    onError: () => {
      toast.error("Error al subir. Por favor, inténtalo de nuevo.");
    },
  });

  const handleFile = useCallback((file: File) => {
    if (!file.name.endsWith(".csv")) {
      toast.error("Solo se admiten archivos CSV.");
      return;
    }
    setSelectedFile(file);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile],
  );

  return (
    <div className="max-w-lg mx-auto space-y-6">
      <AnimatedSection>
        <SectionHeader icon={Upload} title="Subir Dataset" description="Sube un archivo CSV para iniciar el análisis con IA." />
      </AnimatedSection>

      <AnimatedSection delay={0.1}>
        <div className="glass-card overflow-hidden">
          <div className="p-6">
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setDragOver(true);
              }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              className={`
                relative border-2 border-dashed rounded-xl p-10 text-center transition-all duration-300
                ${dragOver
                  ? "border-primary bg-primary/5 scale-[1.01]"
                  : "border-border/50 hover:border-primary/30 hover:bg-muted/30"
                }
              `}
            >
              {selectedFile ? (
                <div className="space-y-3">
                  <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-accent/10">
                    <CheckCircle2 className="h-7 w-7 text-accent" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-foreground">{selectedFile.name}</p>
                    <p className="text-xs text-muted-foreground mt-0.5 font-mono">
                      {(selectedFile.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedFile(null);
                    }}
                    className="text-xs text-primary hover:underline"
                  >
                    Elegir otro archivo
                  </button>
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-muted/50">
                    <FileUp className="h-7 w-7 text-muted-foreground" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-foreground">
                      Arrastra tu archivo CSV aquí
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      o haz clic para buscar · Solo archivos CSV
                    </p>
                  </div>
                </div>
              )}

              <input
                type="file"
                accept=".csv"
                className="absolute inset-0 opacity-0 cursor-pointer"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleFile(file);
                }}
              />
            </div>

            <Button
              className="w-full mt-5 gap-2"
              size="lg"
              disabled={!selectedFile || mutation.isPending}
              onClick={() => selectedFile && mutation.mutate(selectedFile)}
            >
              {mutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Analizando…
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4" />
                  Subir y Analizar
                </>
              )}
            </Button>
          </div>
        </div>
      </AnimatedSection>
    </div>
  );
}
