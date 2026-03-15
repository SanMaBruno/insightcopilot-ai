import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";
import type { InteractiveChartSpec } from "@/types/dataset";

interface InteractiveChartProps {
  title: string;
  spec: InteractiveChartSpec;
}

export default function InteractiveChart({ title, spec }: InteractiveChartProps) {
  const isPie = spec.chart_kind === "pie";

  const options: Highcharts.Options = {
    chart: {
      type: isPie ? "pie" : spec.chart_kind,
      backgroundColor: "transparent",
      style: { fontFamily: "inherit" },
    },
    title: { text: undefined },
    subtitle: {
      text: spec.subtitle,
      style: { color: "var(--muted-foreground, #888)", fontSize: "11px" },
    },
    xAxis: isPie
      ? undefined
      : {
          categories: spec.categories,
          title: { text: spec.x_axis_label, style: { color: "var(--muted-foreground, #888)" } },
          labels: {
            style: { color: "var(--muted-foreground, #888)", fontSize: "10px" },
            rotation: spec.categories.length > 8 ? -45 : 0,
          },
        },
    yAxis: isPie
      ? undefined
      : {
          title: { text: spec.y_axis_label, style: { color: "var(--muted-foreground, #888)" } },
          labels: { style: { color: "var(--muted-foreground, #888)", fontSize: "10px" } },
          gridLineColor: "var(--border, #333)",
        },
    tooltip: {
      valueSuffix: spec.tooltip_suffix,
      backgroundColor: "var(--popover, #1a1a2e)",
      borderColor: "var(--border, #333)",
      style: { color: "var(--popover-foreground, #fff)" },
    },
    legend: {
      itemStyle: { color: "var(--muted-foreground, #aaa)", fontSize: "11px" },
      itemHoverStyle: { color: "var(--foreground, #fff)" },
    },
    plotOptions: {
      column: {
        borderRadius: 4,
        dataLabels: { enabled: spec.categories.length <= 10, style: { fontSize: "10px" } },
      },
      bar: {
        borderRadius: 4,
        dataLabels: { enabled: spec.categories.length <= 10, style: { fontSize: "10px" } },
      },
      pie: {
        allowPointSelect: true,
        cursor: "pointer",
        dataLabels: { enabled: true, format: "<b>{point.name}</b>: {point.percentage:.1f} %" },
      },
    },
    series: isPie
      ? [
          {
            type: "pie",
            name: spec.series[0]?.name ?? title,
            data: spec.categories.map((cat, idx) => ({
              name: cat,
              y: spec.series[0]?.data[idx] ?? 0,
              color: spec.series[0]?.color,
            })),
          },
        ]
      : spec.series.map((s) => ({
          type: spec.chart_kind as "column" | "bar",
          name: s.name,
          data: s.data,
          color: s.color ?? undefined,
        })),
    credits: { enabled: false },
  };

  return <HighchartsReact highcharts={Highcharts} options={options} />;
}
