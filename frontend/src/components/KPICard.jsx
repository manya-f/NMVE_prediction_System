import React from "react";
import { TrendingUp, CheckCircle2, AlertTriangle } from "lucide-react";

function KPICard({ icon: Icon, label, value, percentage, color = "purple" }) {
  const colorMap = {
    purple: "from-purple-600/20 to-purple-900/20 text-purple-400",
    green: "from-green-600/20 to-green-900/20 text-green-400",
    red: "from-red-600/20 to-red-900/20 text-red-400",
  };

  return (
    <div className={`card bg-gradient-to-br ${colorMap[color]} border-${color}-600/30`}>
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-slate-400 text-sm font-medium">{label}</p>
          <p className="text-4xl font-bold text-slate-50 mt-2">{value}</p>
        </div>
        {Icon && <Icon size={32} className="opacity-40" />}
      </div>
      {percentage !== undefined && (
        <div className="text-sm text-slate-400">
          <span className="text-green-400 font-semibold">{percentage}%</span> of fleet
        </div>
      )}
    </div>
  );
}

function KPIGrid({ summary }) {
  const healthPercent = ((summary.healthy / summary.total) * 100).toFixed(1);
  const failPercent = ((summary.failing / summary.total) * 100).toFixed(1);

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <KPICard
        icon={TrendingUp}
        label="Total Drives"
        value={summary.total}
        color="purple"
      />
      <KPICard
        icon={CheckCircle2}
        label="Healthy Fleet"
        value={`${healthPercent}%`}
        percentage={healthPercent}
        color="green"
      />
      <KPICard
        icon={AlertTriangle}
        label="At Risk"
        value={`${failPercent}%`}
        percentage={failPercent}
        color="red"
      />
    </div>
  );
}

export default KPIGrid;
export { KPICard };
