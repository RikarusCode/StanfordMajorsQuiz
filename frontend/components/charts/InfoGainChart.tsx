"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function InfoGainChart({
  infoGainHistory,
}: {
  infoGainHistory: number[];
}) {
  const data = infoGainHistory.map((ig, i) => ({
    step: i + 1,
    ig,
  }));

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid stroke="rgba(255,255,255,0.08)" strokeDasharray="3 3" />
          <XAxis
            dataKey="step"
            stroke="rgba(255,255,255,0.5)"
            tick={{ fill: "rgba(255,255,255,0.6)", fontSize: 12 }}
          />
          <YAxis
            stroke="rgba(255,255,255,0.5)"
            tick={{ fill: "rgba(255,255,255,0.6)", fontSize: 12 }}
            tickFormatter={(v) => v.toFixed(2)}
          />
          <Tooltip
            contentStyle={{
              background: "rgba(15, 23, 42, 0.9)",
              border: "1px solid rgba(255,255,255,0.12)",
              borderRadius: 12,
              color: "white",
            }}
            labelStyle={{ color: "rgba(255,255,255,0.8)" }}
            formatter={(value: any) => [
              typeof value === "number" ? value.toFixed(3) : value,
              "Information Gain (bits)",
            ]}
          />
          <Bar dataKey="ig" fill="#3b82f6" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

