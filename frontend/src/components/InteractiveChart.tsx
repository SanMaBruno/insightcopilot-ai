import Highcharts from "highcharts";
import { Chart, setHighcharts } from "@highcharts/react";
import type { InteractiveChartSpec } from "../types/api";
import { getChartTemplate } from "./chartTemplates";

setHighcharts(Highcharts);

const CHART_FONT = `"Segoe UI", "Helvetica Neue", Arial, sans-serif`;

function buildSeries(spec: InteractiveChartSpec): Highcharts.SeriesOptionsType[] {
  if (spec.chart_kind === "bar") {
    return spec.series.map((series) => ({
      type: "bar",
      name: series.name,
      data: series.data,
      color: series.color ?? undefined,
    }));
  }

  return spec.series.map((series) => ({
    type: "column",
    name: series.name,
    data: series.data,
    color: series.color ?? undefined,
  }));
}

export default function InteractiveChart({
  chartType,
  title,
  spec,
}: {
  chartType: string;
  title: string;
  spec: InteractiveChartSpec;
}) {
  const template = getChartTemplate(chartType);
  const options: Highcharts.Options = {
    chart: {
      type: spec.chart_kind as "bar" | "column",
      backgroundColor: "transparent",
      spacingTop: 16,
      spacingRight: 16,
      spacingBottom: 16,
      spacingLeft: 16,
      style: {
        fontFamily: CHART_FONT,
      },
    },
    title: {
      text: title,
      align: "left",
      style: {
        color: "#142033",
        fontSize: "16px",
        fontWeight: "700",
      },
    },
    subtitle: {
      text: spec.subtitle || template.subtitleFallback,
      align: "left",
      style: {
        color: "#60708a",
        fontSize: "12px",
      },
    },
    xAxis: {
      categories: spec.categories,
      title: {
        text: spec.x_axis_label || undefined,
        style: {
          color: "#60708a",
          fontWeight: "600",
        },
      },
      labels: {
        style: {
          color: "#475569",
          fontSize: "11px",
        },
        rotation: template.xAxisLabelRotation,
      },
      lineColor: "#d7dfeb",
      tickColor: "#d7dfeb",
    },
    yAxis: {
      min: 0,
      title: {
        text: spec.y_axis_label || undefined,
        style: {
          color: "#60708a",
          fontWeight: "600",
        },
      },
      labels: {
        style: {
          color: "#475569",
          fontSize: "11px",
        },
      },
      gridLineColor: "#e7edf5",
    },
    legend: {
      enabled: true,
      align: template.legendAlign,
      verticalAlign: template.legendVerticalAlign,
      layout: template.legendLayout,
      floating: false,
      itemDistance: 12,
      itemMarginBottom: 4,
      itemStyle: {
        color: "#334155",
        fontWeight: "500",
        fontSize: "11px",
      },
    },
    tooltip: {
      shared: true,
      useHTML: true,
      backgroundColor: "#0f172a",
      borderColor: "#0f172a",
      borderRadius: 12,
      style: {
        color: "#f8fafc",
      },
      headerFormat:
        '<span style="font-size:11px;color:#cbd5e1">{point.key}</span><br/>',
      pointFormat:
        `<span style="color:{series.color}">\u25CF</span> ${template.tooltipLabel}: <b>{point.y}</b>${spec.tooltip_suffix || ""}<br/>`,
    },
    credits: {
      enabled: false,
    },
    plotOptions: {
      series: {
        animation: false,
        borderWidth: 0,
        dataLabels: {
          enabled: true,
          crop: false,
          overflow: "allow",
          style: {
            color: template.dataLabelColor,
            fontSize: "11px",
            fontWeight: "600",
            textOutline: "none",
          },
        },
        states: {
          inactive: {
            opacity: 1,
          },
        },
      },
      column: {
        borderRadius: 10,
        minPointLength: 3,
        groupPadding: 0.12,
        pointPadding: 0.06,
      },
      bar: {
        borderRadius: 10,
        minPointLength: 3,
        groupPadding: 0.12,
        pointPadding: 0.1,
      },
    },
    responsive: {
      rules: [
        {
          condition: {
            maxWidth: 640,
          },
          chartOptions: {
            legend: {
              align: "left",
              verticalAlign: "bottom",
              layout: "horizontal",
            },
            xAxis: {
              labels: {
                rotation: spec.chart_kind === "column" ? -35 : 0,
                style: {
                  fontSize: "10px",
                },
              },
            },
          },
        },
      ],
    },
    series: buildSeries(spec),
  };

  return (
    <div
      className="rounded-2xl border p-2 shadow-[0_18px_45px_-30px_rgba(15,23,42,0.45)]"
      style={{
        borderColor: template.accentSoft,
        background: `linear-gradient(180deg, rgba(255,255,255,0.99), rgba(248,250,252,0.97)), radial-gradient(circle at top left, ${template.accentSoft}, transparent 42%)`,
      }}
    >
      <Chart options={options} />
      {spec.source_label && (
        <p className="px-4 pb-3 text-[11px] uppercase tracking-[0.18em] text-slate-400">
          {spec.source_label}
        </p>
      )}
    </div>
  );
}
