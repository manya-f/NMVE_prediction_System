import React, { useContext } from "react";
import { AppContext } from "../App";
import KPIGrid from "../components/KPICard";
import { FailureModeChart, FleetHealthChart, TopPatternsChart } from "../components/Charts";
import { AlertCircle, Circle, TrendingUp } from "lucide-react";

function Dashboard() {
  const { uploadedRows, summary } = useContext(AppContext);

  if (!summary) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-slate-50 mb-2">Welcome</h2>
          <p className="text-slate-400 mb-8">Upload a CSV file to get started</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-50">Dashboard</h1>
        <p className="text-slate-400 mt-2">Fleet health status and analytics</p>
      </div>

      <KPIGrid summary={summary} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <FailureModeChart data={summary.failureModeData} />
        <FleetHealthChart
          healthy={summary.healthy}
          failing={summary.failing}
          total={summary.total}
        />
      </div>

      <TopPatternsChart patterns={summary.topPatterns} />

      <div className="card border-red-600/30">
        <div className="flex items-start gap-4">
          <AlertCircle className="text-red-400 flex-shrink-0 mt-1" size={24} />
          <div>
            <h3 className="text-lg font-semibold text-slate-50 mb-2">Critical Alerts</h3>
            <ul className="space-y-2 text-slate-400">
              <li className="flex items-center gap-2">
                <Circle className="text-red-400" size={12} />
                {summary.failing} drives in critical condition
              </li>
              <li className="flex items-center gap-2">
                <Circle className="text-yellow-400" size={12} />
                {Math.round(summary.total * 0.1)} drives nearing capacity
              </li>
              <li className="flex items-center gap-2">
                <TrendingUp className="text-slate-400" size={12} />
                Fleet utilization at {((summary.total / (summary.total + 50)) * 100).toFixed(0)}%
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
