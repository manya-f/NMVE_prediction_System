import React from "react";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts";

const COLORS = ["#8b5cf6", "#ec4899", "#f59e0b", "#10b981", "#06b6d4"];

function FailureModeChart({ data }) {
  return (
    <div className="card h-full">
      <h3 className="text-lg font-semibold text-slate-50 mb-6">
        Failure Mode Distribution
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="mode" stroke="#64748b" />
          <YAxis stroke="#64748b" />
          <Tooltip
            contentStyle={{
              backgroundColor: "#1e293b",
              border: "1px solid #475569",
              borderRadius: "8px",
            }}
            labelStyle={{ color: "#e2e8f0" }}
          />
          <Bar dataKey="count" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function FleetHealthChart({ healthy, failing, total }) {
  const data = [
    { name: "Healthy", value: healthy },
    { name: "Failing", value: failing },
    { name: "Unknown", value: total - healthy - failing },
  ];

  return (
    <div className="card h-full">
      <h3 className="text-lg font-semibold text-slate-50 mb-6">
        Fleet Health Overview
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            paddingAngle={2}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: "#1e293b",
              border: "1px solid #475569",
              borderRadius: "8px",
            }}
            labelStyle={{ color: "#e2e8f0" }}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

function TopPatternsChart({ patterns }) {
  const data = patterns.slice(0, 5);

  return (
    <div className="card h-full">
      <h3 className="text-lg font-semibold text-slate-50 mb-6">
        Top Failure Patterns
      </h3>
      <div className="space-y-4">
        {data.map((pattern, index) => (
          <div key={index} className="flex items-center justify-between">
            <div className="flex items-center gap-3 flex-1">
              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: COLORS[index] }} />
              <span className="text-slate-300">{pattern.name}</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-32 h-2 bg-dark-600 rounded-full overflow-hidden">
                <div
                  className="h-full"
                  style={{
                    width: `${(pattern.count / data[0].count) * 100}%`,
                    backgroundColor: COLORS[index],
                  }}
                />
              </div>
              <span className="text-slate-400 text-sm font-medium w-10 text-right">
                {pattern.count}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export { FailureModeChart, FleetHealthChart, TopPatternsChart };
