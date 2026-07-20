"use client";

import { useEffect, useRef } from "react";
import * as echarts from "echarts/core";
import { GaugeChart, PieChart } from "echarts/charts";
import { TooltipComponent } from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";
import type { ClaimVerdict, FactCheckClaim } from "@/lib/agentcore";
import { useI18n } from "@/lib/i18n-context";

echarts.use([GaugeChart, PieChart, TooltipComponent, CanvasRenderer]);

// CVD検証済みの状態色（teal/redはdeutan ΔE>=13で分離、全スライス直接ラベル付き）
const CLAIM_COLORS: Record<ClaimVerdict, string> = {
  supported: "#0d9488",
  unsupported: "#dc2626",
  unverified: "#6b7280",
};

function gaugeColor(score: number): string {
  if (score >= 70) return "#dc2626";
  if (score >= 40) return "#d97706";
  return "#0d9488";
}

function useEChart(build: (chart: echarts.ECharts) => void, deps: unknown[]) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!ref.current) return;
    const chart = echarts.init(ref.current);
    build(chart);
    const onResize = () => chart.resize();
    window.addEventListener("resize", onResize);
    return () => {
      window.removeEventListener("resize", onResize);
      chart.dispose();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  return ref;
}

export function ScoreGauge({ score }: { score: number }) {
  const ref = useEChart(
    (chart) => {
      chart.setOption({
        series: [
          {
            type: "gauge",
            startAngle: 210,
            endAngle: -30,
            min: 0,
            max: 100,
            progress: { show: true, width: 10, itemStyle: { color: gaugeColor(score) } },
            axisLine: { lineStyle: { width: 10, color: [[1, "#e5e7eb"]] } },
            axisTick: { show: false },
            splitLine: { show: false },
            axisLabel: { show: false },
            pointer: { show: false },
            detail: {
              valueAnimation: true,
              fontSize: 28,
              fontWeight: 700,
              offsetCenter: [0, 0],
              color: gaugeColor(score),
              formatter: "{value}",
            },
            data: [{ value: score }],
          },
        ],
      });
    },
    [score],
  );
  return <div ref={ref} className="h-28 w-36" />;
}

export function ClaimsDonut({ claims }: { claims: FactCheckClaim[] }) {
  const { t } = useI18n();
  const labels: Record<ClaimVerdict, string> = {
    supported: t.factSupported,
    unsupported: t.factUnsupported,
    unverified: t.factUnverified,
  };
  const donutData = (["supported", "unsupported", "unverified"] as const)
    .map((verdict) => ({
      name: labels[verdict],
      value: claims.filter((c) => c.verdict === verdict).length,
      itemStyle: { color: CLAIM_COLORS[verdict] },
    }))
    .filter((d) => d.value > 0);

  const ref = useEChart(
    (chart) => {
      if (donutData.length === 0) return;
      chart.setOption({
        tooltip: { trigger: "item", formatter: "{b}: {c}" },
        series: [
          {
            type: "pie",
            radius: ["42%", "68%"],
            itemStyle: { borderColor: "#ffffff", borderWidth: 2, borderRadius: 4 },
            label: { formatter: "{b} {c}", color: "#374151", fontSize: 12 },
            data: donutData,
          },
        ],
      });
    },
    [claims, t],
  );

  if (donutData.length === 0) return null;
  return <div ref={ref} className="h-44 w-full" />;
}
