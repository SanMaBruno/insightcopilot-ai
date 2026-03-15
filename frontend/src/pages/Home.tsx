import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Upload, Database, BarChart3, BrainCircuit, Search,
  FileText, ArrowRight, Sparkles, Zap, TrendingUp,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { AnimatedSection, StaggerContainer, StaggerItem } from "@/components/ui/animated-section";

const capabilities = [
  {
    icon: Database,
    title: "Perfilado de Datos",
    description: "Detección automática de esquemas, resúmenes estadísticos y análisis de calidad de datos.",
    color: "text-primary",
    bg: "bg-primary/10",
  },
  {
    icon: Sparkles,
    title: "Insights con IA",
    description: "Insights generados por IA que revelan patrones, anomalías y oportunidades.",
    color: "text-accent",
    bg: "bg-accent/10",
  },
  {
    icon: BarChart3,
    title: "Visualizaciones Inteligentes",
    description: "Gráficos y análisis visuales generados automáticamente para tus datos.",
    color: "text-cyan",
    bg: "bg-cyan/10",
  },
  {
    icon: Search,
    title: "Consultas en Lenguaje Natural",
    description: "Haz preguntas en español. Obtén respuestas analíticas respaldadas por SQL.",
    color: "text-primary",
    bg: "bg-primary/10",
  },
  {
    icon: FileText,
    title: "Resúmenes Ejecutivos",
    description: "Resúmenes generados por LLM que sintetizan hallazgos clave para la toma de decisiones.",
    color: "text-accent",
    bg: "bg-accent/10",
  },
  {
    icon: BrainCircuit,
    title: "Consultas RAG",
    description: "Generación aumentada por recuperación para Q&A contextual y profundo.",
    color: "text-cyan",
    bg: "bg-cyan/10",
  },
];

const steps = [
  { step: "01", title: "Subir", description: "Arrastra tu dataset CSV" },
  { step: "02", title: "Analizar", description: "La IA procesa y perfila" },
  { step: "03", title: "Explorar", description: "Consulta, visualiza, decide" },
];

export default function Home() {
  return (
    <div className="relative max-w-5xl mx-auto space-y-20 pb-16">
      {/* Hero */}
      <section className="relative pt-8 pb-4">
        <div className="absolute inset-0 mesh-gradient pointer-events-none" />
        <AnimatedSection className="relative text-center space-y-6 max-w-2xl mx-auto">
          <div className="inline-flex items-center gap-2 rounded-full border border-border/50 bg-card/80 backdrop-blur-sm px-4 py-1.5 text-xs font-medium text-muted-foreground">
            <Zap className="h-3 w-3 text-accent" />
            Plataforma de Inteligencia de Datos con IA
          </div>

          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight leading-[1.1]">
            <span className="text-foreground">Transforma datos crudos en</span>
            <br />
            <span className="gradient-text">inteligencia accionable</span>
          </h1>

          <p className="text-muted-foreground text-base sm:text-lg max-w-lg mx-auto leading-relaxed">
            Sube datasets, obtén perfilado instantáneo con IA, insights, visualizaciones y consultas en lenguaje natural — todo en una plataforma.
          </p>

          <div className="flex items-center justify-center gap-3 pt-2">
            <Link to="/upload">
              <Button size="lg" className="gap-2 shadow-lg shadow-primary/20 hover:shadow-primary/30 transition-shadow">
                <Upload className="h-4 w-4" />
                Subir Dataset
              </Button>
            </Link>
            <Link to="/datasets">
              <Button variant="outline" size="lg" className="gap-2">
                Ver Datasets
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>
        </AnimatedSection>
      </section>

      {/* How it works */}
      <AnimatedSection delay={0.2} className="space-y-8">
        <div className="text-center">
          <p className="text-xs font-semibold uppercase tracking-widest text-primary mb-2">Cómo funciona</p>
          <h2 className="text-2xl font-bold text-foreground">Tres pasos hacia la inteligencia</h2>
        </div>
        <div className="grid grid-cols-3 gap-6">
          {steps.map((s, i) => (
            <motion.div
              key={s.step}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + i * 0.1, duration: 0.4 }}
              className="relative text-center group"
            >
              <span className="text-5xl font-extrabold gradient-text opacity-20 group-hover:opacity-40 transition-opacity">
                {s.step}
              </span>
              <h3 className="text-sm font-semibold text-foreground -mt-2">{s.title}</h3>
              <p className="text-xs text-muted-foreground mt-1">{s.description}</p>
            </motion.div>
          ))}
        </div>
      </AnimatedSection>

      {/* Capabilities */}
      <div className="space-y-8">
        <AnimatedSection delay={0.1} className="text-center">
          <p className="text-xs font-semibold uppercase tracking-widest text-primary mb-2">Capacidades</p>
          <h2 className="text-2xl font-bold text-foreground">Todo lo que necesitas para explorar datos</h2>
        </AnimatedSection>

        <StaggerContainer className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {capabilities.map((cap) => (
            <StaggerItem key={cap.title}>
              <div className="glass-card p-5 h-full card-hover group">
                <div className={`inline-flex h-9 w-9 items-center justify-center rounded-lg ${cap.bg} mb-3`}>
                  <cap.icon className={`h-4.5 w-4.5 ${cap.color}`} />
                </div>
                <h3 className="text-sm font-semibold text-foreground group-hover:text-primary transition-colors">
                  {cap.title}
                </h3>
                <p className="text-xs text-muted-foreground mt-1.5 leading-relaxed">
                  {cap.description}
                </p>
              </div>
            </StaggerItem>
          ))}
        </StaggerContainer>
      </div>

      {/* CTA */}
      <AnimatedSection delay={0.2} className="text-center space-y-4">
        <div className="glass-card max-w-xl mx-auto p-8 glow">
          <TrendingUp className="h-8 w-8 text-primary mx-auto mb-3" />
          <h3 className="text-lg font-bold text-foreground">¿Listo para explorar tus datos?</h3>
          <p className="text-sm text-muted-foreground mt-1.5 mb-4">
            Sube un CSV y deja que la IA haga el trabajo pesado.
          </p>
          <Link to="/upload">
            <Button className="gap-2">
              <Upload className="h-4 w-4" />
              Comenzar
            </Button>
          </Link>
        </div>
      </AnimatedSection>
    </div>
  );
}
