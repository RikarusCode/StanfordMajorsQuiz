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

export default function TopMajorsEvolutionChart({
  data,
  series,
}: {
  data: Array<Record<string, number | string>>;
  series: { name: string; key: string; color: string }[];
}) {
  return (
    <div className="h-72 w-full">
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
            tickFormatter={(v) => `${Number(v).toFixed(0)}%`}
            domain={[0, 100]}
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
              typeof value === "number" ? `${value.toFixed(2)}%` : value,
              name,
            ]}
          />
          {series.map((s) => (
            <Line
              key={s.key}
              type="monotone"
              dataKey={s.key}
              stroke={s.color}
              strokeWidth={2.5}
              dot={false}
              isAnimationActive={false}
              name={s.name}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

