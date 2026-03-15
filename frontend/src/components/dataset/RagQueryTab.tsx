import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/api/client";
import { Send, Loader2, BrainCircuit, BookOpen, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { AnimatedSection } from "@/components/ui/animated-section";

function isOpenAIError(error: unknown): boolean {
  const msg = String(error);
  return msg.includes("429") || msg.includes("insufficient_quota") || msg.includes("openai") || msg.includes("OpenAI");
}

export default function RagQueryTab({ datasetId }: { datasetId: string }) {
  const [query, setQuery] = useState("");

  const mutation = useMutation({
    mutationFn: (q: string) => api.ragQuery(datasetId, q),
    retry: false,
  });

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-2 mb-1">
        <BrainCircuit className="h-4 w-4 text-accent" />
        <p className="text-sm font-medium text-foreground">Consulta RAG</p>
        <span className="text-[10px] rounded-full bg-accent/10 px-2 py-0.5 text-accent font-medium">Generación Aumentada</span>
      </div>
      <p className="text-xs text-muted-foreground -mt-3">Haz preguntas contextuales impulsadas por generación aumentada por recuperación.</p>

      <div className="flex gap-3">
        <Textarea
          placeholder="Ej: ¿Qué patrones existen en los datos de abandono de clientes?"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="min-h-[80px] bg-muted/30 border-border/50 focus:border-accent/50 resize-none"
        />
        <Button
          size="icon"
          className="shrink-0 self-end h-10 w-10 bg-accent text-accent-foreground hover:bg-accent/90"
          disabled={!query.trim() || mutation.isPending}
          onClick={() => mutation.mutate(query)}
        >
          {mutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
        </Button>
      </div>

      {mutation.data && (
        <AnimatedSection className="space-y-3">
          <div className="rounded-lg border border-border/30 bg-muted/20 p-4">
            <p className="text-sm text-foreground whitespace-pre-wrap leading-relaxed">{mutation.data.answer}</p>
          </div>
          {mutation.data.sources && mutation.data.sources.length > 0 && (
            <div className="rounded-lg border border-border/30 bg-card p-4">
              <div className="flex items-center gap-1.5 mb-2">
                <BookOpen className="h-3 w-3 text-muted-foreground" />
                <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Fuentes</span>
              </div>
              <div className="space-y-2">
                {mutation.data.sources.map((src, i) => (
                  <div key={i} className="text-xs bg-muted/50 rounded p-2 border border-border/20">
                    <span className="font-mono text-primary">{src.source}</span>
                    <span className="text-muted-foreground ml-2">(fragmento {src.chunk_index})</span>
                    <p className="text-foreground/80 mt-1 leading-relaxed">{src.content}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </AnimatedSection>
      )}

      {mutation.error && (
        <div className="rounded-lg border border-destructive/30 bg-destructive/5 p-4">
          <div className="flex items-start gap-2">
            <AlertCircle className="h-4 w-4 text-destructive mt-0.5 shrink-0" />
            <div>
              {isOpenAIError(mutation.error) ? (
                <>
                  <p className="text-sm font-medium text-destructive">Créditos de OpenAI no disponibles</p>
                  <p className="text-xs text-destructive/80 mt-1">Esta funcionalidad requiere créditos de OpenAI que actualmente no están disponibles. Configura una API key con saldo activo para utilizar consultas RAG.</p>
                </>
              ) : (
                <p className="text-sm text-destructive">La consulta falló. Por favor, inténtalo de nuevo.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
