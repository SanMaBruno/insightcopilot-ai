import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/api/client";
import { Send, Loader2, Search, Terminal, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { AnimatedSection } from "@/components/ui/animated-section";

function isOpenAIError(error: unknown): boolean {
  const msg = String(error);
  return msg.includes("429") || msg.includes("insufficient_quota") || msg.includes("openai") || msg.includes("OpenAI");
}

export default function AnalyticalQueryTab({ datasetId }: { datasetId: string }) {
  const [query, setQuery] = useState("");

  const mutation = useMutation({
    mutationFn: (q: string) => api.analyticalQuery(datasetId, q),
    retry: false,
  });

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-2 mb-1">
        <Search className="h-4 w-4 text-primary" />
        <p className="text-sm font-medium text-foreground">Consulta en Lenguaje Natural</p>
      </div>
      <p className="text-xs text-muted-foreground -mt-3">Haz preguntas sobre tus datos en español. La IA generará SQL y devolverá resultados.</p>

      <div className="flex gap-3">
        <Textarea
          placeholder="Ej: ¿Cuáles son las 5 categorías principales por ingresos?"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="min-h-[80px] bg-muted/30 border-border/50 focus:border-primary/50 resize-none"
        />
        <Button
          size="icon"
          className="shrink-0 self-end h-10 w-10"
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
          {mutation.data.supporting_data && mutation.data.supporting_data.length > 0 && (
            <div className="rounded-lg border border-border/30 bg-card p-4">
              <div className="flex items-center gap-1.5 mb-2">
                <Terminal className="h-3 w-3 text-muted-foreground" />
                <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Datos de Soporte</span>
              </div>
              <ul className="space-y-1">
                {mutation.data.supporting_data.map((item, i) => (
                  <li key={i} className="text-xs font-mono text-foreground/80">{item}</li>
                ))}
              </ul>
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
                  <p className="text-xs text-destructive/80 mt-1">Esta funcionalidad requiere créditos de OpenAI que actualmente no están disponibles. Configura una API key con saldo activo para utilizar consultas analíticas con IA.</p>
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
