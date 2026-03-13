import { Link } from "react-router-dom";

const CAPABILITIES = [
  {
    title: "Perfilado automático",
    description: "Carga un CSV y obtén estadísticas descriptivas por columna: tipos, nulos, valores únicos.",
    icon: "📊",
  },
  {
    title: "Generación de insights",
    description: "Detecta patrones, outliers y correlaciones automáticamente, clasificados por severidad.",
    icon: "💡",
  },
  {
    title: "Visualizaciones",
    description: "Genera gráficos (histogramas, barras, correlación) directamente desde los datos.",
    icon: "📈",
  },
  {
    title: "Consulta analítica",
    description: "Responde preguntas en lenguaje natural sobre tus datos: filtros, agrupaciones, métricas.",
    icon: "🔍",
  },
  {
    title: "Executive summary (LLM)",
    description: "Genera resúmenes ejecutivos con GPT a partir del perfil e insights del dataset.",
    icon: "📝",
  },
  {
    title: "RAG documental",
    description: "Indexa documentos, genera embeddings y responde preguntas combinando datos y documentos.",
    icon: "📚",
  },
] as const;

const STEPS = [
  { step: "1", label: "Sube un CSV", detail: "Carga tu dataset desde la sección Datasets." },
  { step: "2", label: "Explora el perfil", detail: "Revisa estadísticas, insights y visualizaciones." },
  { step: "3", label: "Haz preguntas", detail: "Consulta tus datos en lenguaje natural." },
  { step: "4", label: "Genera resúmenes", detail: "Obtén executive summaries con IA." },
] as const;

export default function HomePage() {
  return (
    <div>
      {/* Hero */}
      <section className="text-center py-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          InsightCopilot AI
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto mb-8">
          Plataforma analítica con inteligencia artificial para exploración de datos,
          comprensión documental y generación de insights.
        </p>
        <Link
          to="/datasets"
          className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition"
        >
          Comenzar →
        </Link>
      </section>

      {/* Capabilities */}
      <section className="py-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-6 text-center">
          Capacidades
        </h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {CAPABILITIES.map((cap) => (
            <div
              key={cap.title}
              className="bg-white border border-gray-200 rounded-lg p-5 hover:border-blue-200 transition"
            >
              <span className="text-2xl">{cap.icon}</span>
              <h3 className="font-semibold text-gray-900 mt-3 mb-1">{cap.title}</h3>
              <p className="text-sm text-gray-600">{cap.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How to use */}
      <section className="py-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-6 text-center">
          Flujo de uso
        </h2>
        <div className="grid gap-4 md:grid-cols-4">
          {STEPS.map((s) => (
            <div key={s.step} className="text-center">
              <div className="w-10 h-10 rounded-full bg-blue-600 text-white font-bold flex items-center justify-center mx-auto mb-3">
                {s.step}
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">{s.label}</h3>
              <p className="text-sm text-gray-500">{s.detail}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Tech stack summary */}
      <section className="py-8 text-center">
        <p className="text-sm text-gray-400">
          Python · FastAPI · React · TypeScript · Pandas · OpenAI · Clean Architecture
        </p>
      </section>
    </div>
  );
}
