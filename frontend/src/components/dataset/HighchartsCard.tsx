import { useMemo } from "react";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";
import type { InteractiveChartSpec } from "@/types/dataset";

interface HighchartsCardProps {
  spec: InteractiveChartSpec;
  title: string;
}

const CHART_COLORS = [
  "#6366f1", // indigo
  "#f43f5e", // rose
  "#10b981", // emerald
  "#f59e0b", // amber
  "#8b5cf6", // violet
  "#06b6d4", // cyan
  "#ec4899", // pink
  "#84cc16", // lime
];

export default function HighchartsCard({ spec, title }: HighchartsCardProps) {
  const options = useMemo<Highcharts.Options>(() => {
    const isHorizontalBar = spec.chart_kind === "bar";

    return {
      chart: {
        type: isHorizontalBar ? "bar" : "column",
        backgroundColor: "transparent",
        style: { fontFamily: "inherit" },
      },
      title: {
        text: title,
        style: { fontSize: "14px", fontWeight: "600" },
      },
      subtitle: {
        text: spec.subtitle || undefined,
        style: { fontSize: "11px", color: "#94a3b8" },
      },
      xAxis: {
        categories: spec.categories,
        crosshair: true,
        title: {
          text: isHorizontalBar ? spec.y_axis_label : spec.x_axis_label,
          style: { fontSize: "11px" },
        },
        labels: {
          style: { fontSize: "10px" },
          rotation: !isHorizontalBar && spec.categories.length > 8 ? -45 : 0,
        },
      },
      yAxis: {
        min: 0,
        title: {
          text: isHorizontalBar ? spec.x_axis_label : spec.y_axis_label,
          style: { fontSize: "11px" },
        },
        labels: { style: { fontSize: "10px" } },
      },
      tooltip: {
        valueSuffix: spec.tooltip_suffix || "",
        shared: true,
        backgroundColor: "rgba(0,0,0,0.8)",
        borderColor: "transparent",
        style: { color: "#fff", fontSize: "12px" },
      },
      plotOptions: {
        column: {
          pointPadding: 0.15,
          borderWidth: 0,
          borderRadius: 3,
        },
        bar: {
          pointPadding: 0.15,
          borderWidth: 0,
          borderRadius: 3,
        },
      },
      colors: CHART_COLORS,
      series: spec.series.map((s, i) => ({
        type: isHorizontalBar ? ("bar" as const) : ("column" as const),
        name: s.name,
        data: s.data,
        color: s.color || CHART_COLORS[i % CHART_COLORS.length],
      })),
      legend: {
        enabled: spec.series.length > 1,
        itemStyle: { fontSize: "11px", fontWeight: "normal" },
      },
      credits: {
        enabled: !!spec.source_label,
        text: spec.source_label || "",
      },
    };
  }, [spec, title]);

  return (
    <HighchartsReact
      highcharts={Highcharts}
      options={options}
      containerProps={{ style: { width: "100%", minHeight: "280px" } }}
    />
  );
}
