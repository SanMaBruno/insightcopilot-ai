import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowLeft, Table2, Lightbulb, BarChart3, Search,
  FileText, BrainCircuit,
} from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { LoadingState } from "@/components/ui/loading-state";
import { AnimatedSection } from "@/components/ui/animated-section";
import ProfileTab from "@/components/dataset/ProfileTab";
import InsightsTab from "@/components/dataset/InsightsTab";
import VisualizationsTab from "@/components/dataset/VisualizationsTab";
import AnalyticalQueryTab from "@/components/dataset/AnalyticalQueryTab";
import ExecutiveSummaryTab from "@/components/dataset/ExecutiveSummaryTab";
import RagQueryTab from "@/components/dataset/RagQueryTab";

const tabs = [
  { value: "profile", label: "Perfil", icon: Table2 },
  { value: "insights", label: "Insights", icon: Lightbulb },
  { value: "visualizations", label: "Gráficos", icon: BarChart3 },
  { value: "analytical", label: "Consulta", icon: Search },
  { value: "summary", label: "Resumen", icon: FileText },
  { value: "rag", label: "RAG", icon: BrainCircuit },
];

export default function DatasetDetail() {
  const { id } = useParams<{ id: string }>();
  const { data: dataset, isLoading } = useQuery({
    queryKey: ["dataset", id],
    queryFn: () => api.getDataset(id!),
    enabled: !!id,
  });

  if (isLoading) return <LoadingState message="Cargando dataset…" size="lg" />;

  if (!dataset) {
    return (
      <div className="text-center py-16">
        <p className="text-muted-foreground">Dataset no encontrado.</p>
        <Link to="/datasets" className="text-primary text-sm hover:underline mt-2 inline-block">
          ← Volver a datasets
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <AnimatedSection className="space-y-3">
        <Link
          to="/datasets"
          className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="h-3 w-3" />
          Datasets
        </Link>

        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0">
            <div className="flex items-center gap-3">
              <h1 className="text-xl font-bold text-foreground truncate">{dataset.name}</h1>
            </div>
            <p className="text-xs text-muted-foreground mt-1 font-mono">
              {dataset.source_type}
              <span className="mx-1.5 opacity-40">·</span>
              Subido el {new Date(dataset.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>
      </AnimatedSection>

      {/* Tabs */}
      <AnimatedSection delay={0.1}>
        <Tabs defaultValue="profile" className="space-y-5">
          <TabsList className="bg-muted/50 p-1 rounded-xl h-auto flex-wrap gap-0.5">
            {tabs.map((tab) => (
              <TabsTrigger
                key={tab.value}
                value={tab.value}
                className="gap-1.5 rounded-lg text-xs data-[state=active]:bg-card data-[state=active]:shadow-sm data-[state=active]:text-foreground px-3 py-2 transition-all"
              >
                <tab.icon className="h-3.5 w-3.5" />
                {tab.label}
              </TabsTrigger>
            ))}
          </TabsList>

          {tabs.map((tab) => (
            <TabsContent key={tab.value} value={tab.value}>
              <AnimatePresence mode="wait">
                <motion.div
                  key={tab.value}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.25 }}
                >
                  <div className="glass-card p-5">
                    {tab.value === "profile" && <ProfileTab datasetId={id!} />}
                    {tab.value === "insights" && <InsightsTab datasetId={id!} />}
                    {tab.value === "visualizations" && <VisualizationsTab datasetId={id!} />}
                    {tab.value === "analytical" && <AnalyticalQueryTab datasetId={id!} />}
                    {tab.value === "summary" && <ExecutiveSummaryTab datasetId={id!} />}
                    {tab.value === "rag" && <RagQueryTab datasetId={id!} />}
                  </div>
                </motion.div>
              </AnimatePresence>
            </TabsContent>
          ))}
        </Tabs>
      </AnimatedSection>
    </div>
  );
}
