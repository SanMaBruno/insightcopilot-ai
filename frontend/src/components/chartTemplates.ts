export interface ChartVisualTemplate {
  eyebrow: string;
  description: string;
  subtitleFallback: string;
  accentColor: string;
  accentSoft: string;
  cardClassName: string;
  tooltipLabel: string;
  legendAlign: "left" | "right" | "center";
  legendVerticalAlign: "top" | "middle" | "bottom";
  legendLayout: "horizontal" | "vertical";
  xAxisLabelRotation: number;
  dataLabelColor: string;
}

const DEFAULT_TEMPLATE: ChartVisualTemplate = {
  eyebrow: "Chart",
  description: "Vista ejecutiva del dataset con foco en lectura rapida y comparacion visual.",
  subtitleFallback: "Resumen visual del comportamiento observado en la muestra.",
  accentColor: "#2563eb",
  accentSoft: "rgba(37, 99, 235, 0.10)",
  cardClassName:
    "border-slate-200 bg-[linear-gradient(180deg,rgba(255,255,255,0.98),rgba(248,250,252,0.96))]",
  tooltipLabel: "Valor",
  legendAlign: "right",
  legendVerticalAlign: "top",
  legendLayout: "horizontal",
  xAxisLabelRotation: 0,
  dataLabelColor: "#142033",
};

const TEMPLATES: Record<string, ChartVisualTemplate> = {
  nulls_per_column: {
    eyebrow: "Data Quality",
    description: "Identifica columnas con mayor impacto potencial por datos faltantes.",
    subtitleFallback: "Distribucion de registros faltantes por columna.",
    accentColor: "#dc4c3f",
    accentSoft: "rgba(220, 76, 63, 0.12)",
    cardClassName:
      "border-rose-100 bg-[linear-gradient(180deg,rgba(255,255,255,0.98),rgba(255,247,246,0.98))]",
    tooltipLabel: "Nulos",
    legendAlign: "left",
    legendVerticalAlign: "top",
    legendLayout: "horizontal",
    xAxisLabelRotation: -18,
    dataLabelColor: "#7f1d1d",
  },
  dtype_distribution: {
    eyebrow: "Schema Mix",
    description: "Resume la composicion estructural del dataset por tipo de dato.",
    subtitleFallback: "Balance estructural de columnas por tipologia.",
    accentColor: "#305eea",
    accentSoft: "rgba(48, 94, 234, 0.12)",
    cardClassName:
      "border-blue-100 bg-[linear-gradient(180deg,rgba(255,255,255,0.98),rgba(244,248,255,0.98))]",
    tooltipLabel: "Columnas",
    legendAlign: "left",
    legendVerticalAlign: "top",
    legendLayout: "horizontal",
    xAxisLabelRotation: 0,
    dataLabelColor: "#1d4ed8",
  },
  histogram: {
    eyebrow: "Distribution",
    description: "Describe la distribucion de la variable numerica y su concentracion por rango.",
    subtitleFallback: "Frecuencia por intervalo para detectar dispersion o sesgo.",
    accentColor: "#15936b",
    accentSoft: "rgba(21, 147, 107, 0.12)",
    cardClassName:
      "border-emerald-100 bg-[linear-gradient(180deg,rgba(255,255,255,0.98),rgba(243,252,248,0.98))]",
    tooltipLabel: "Frecuencia",
    legendAlign: "right",
    legendVerticalAlign: "top",
    legendLayout: "horizontal",
    xAxisLabelRotation: -32,
    dataLabelColor: "#166534",
  },
  top_values: {
    eyebrow: "Category Leaders",
    description: "Muestra las categorias con mayor presencia para una lectura comparativa inmediata.",
    subtitleFallback: "Ranking de categorias con mayor peso relativo en la muestra.",
    accentColor: "#a855f7",
    accentSoft: "rgba(168, 85, 247, 0.12)",
    cardClassName:
      "border-fuchsia-100 bg-[linear-gradient(180deg,rgba(255,255,255,0.98),rgba(252,246,255,0.98))]",
    tooltipLabel: "Frecuencia",
    legendAlign: "right",
    legendVerticalAlign: "middle",
    legendLayout: "vertical",
    xAxisLabelRotation: 0,
    dataLabelColor: "#86198f",
  },
};

export function getChartTemplate(chartType: string): ChartVisualTemplate {
  return TEMPLATES[chartType] ?? DEFAULT_TEMPLATE;
}
