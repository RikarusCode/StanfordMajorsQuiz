"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function EntropyChart({
  entropyHistory,
  linearEntropyHistory,
}: {
  entropyHistory: number[];
  linearEntropyHistory?: number[];
}) {
  const n = Math.max(entropyHistory.length, linearEntropyHistory?.length ?? 0);
  const data = Array.from({ length: n }, (_, i) => ({
    step: i,
    adaptive: entropyHistory[i] ?? entropyHistory[entropyHistory.length - 1],
    linear: linearEntropyHistory
      ? linearEntropyHistory[i] ?? linearEntropyHistory[linearEntropyHistory.length - 1]
      : undefined,
  }));

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
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
            formatter={(value: any, name: any) => [
              typeof value === "number" ? value.toFixed(3) : value,
              name === "adaptive" ? "Adaptive" : "Linear",
            ]}
          />
          <Line
            type="monotone"
            dataKey="adaptive"
            stroke="#3b82f6"
            strokeWidth={3}
            dot={false}
            isAnimationActive={false}
            name="adaptive"
          />
          {linearEntropyHistory && (
            <Line
              type="monotone"
              dataKey="linear"
              stroke="rgba(255,255,255,0.45)"
              strokeWidth={2}
              dot={false}
              strokeDasharray="6 6"
              isAnimationActive={false}
              name="linear"
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

