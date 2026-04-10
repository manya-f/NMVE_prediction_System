import React, { useContext, useMemo } from "react";
import { AppContext } from "../App";
import { AlertTriangle, TrendingUp, Lightbulb, Thermometer, Settings, Zap, AlertCircle, CheckCircle2, ClipboardList } from "lucide-react";

function Insights() {
  const { uploadedRows, summary } = useContext(AppContext);

  const insights = useMemo(() => {
    if (!uploadedRows || uploadedRows.length === 0) return [];

    const result = [];

    const hotDrives = uploadedRows.filter((d) => Number(d.Temperature_C) >= 70);
    if (hotDrives.length > 0) {
      result.push({
        id: "temp",
        icon: "temp",
        title: "Thermal Issues",
        severity: "warning",
        desc: `${hotDrives.length} drives overheating (>70°C)`,
        count: hotDrives.length,
      });
    }

    const wornDrives = uploadedRows.filter((d) => Number(d.Percent_Life_Used) >= 80);
    if (wornDrives.length > 0) {
      result.push({
        id: "wear",
        icon: "wear",
        title: "Wear-Out Risk",
        severity: "warning",
        desc: `${wornDrives.length} drives nearing end-of-life`,
        count: wornDrives.length,
      });
    }

    const errorProne = uploadedRows.filter(
      (d) => Number(d.Read_Error_Rate) + Number(d.Write_Error_Rate) > 20
    );
    if (errorProne.length > 0) {
      result.push({
        id: "errors",
        icon: "errors",
        title: "High Error Rates",
        severity: "critical",
        desc: `${errorProne.length} drives with elevated errors`,
        count: errorProne.length,
      });
    }

    const powerIssues = uploadedRows.filter((d) => Number(d.Unsafe_Shutdowns) >= 4);
    if (powerIssues.length > 0) {
      result.push({
        id: "power",
        icon: "power",
        title: "Power Issues",
        severity: "warning",
        desc: `${powerIssues.length} drives with unsafe shutdowns`,
        count: powerIssues.length,
      });
    }

    const failingDrives = uploadedRows.filter((d) => Number(d.Failure_Flag) === 1);
    if (failingDrives.length > 0) {
      result.push({
        id: "failing",
        icon: "failing",
        title: "Critical Drives",
        severity: "critical",
        desc: `${failingDrives.length} drives showing failure indicators`,
        count: failingDrives.length,
      });
    } else {
      result.push({
        id: "healthy",
        icon: "healthy",
        title: "Fleet Healthy",
        severity: "success",
        desc: "All drives operating normally",
        count: uploadedRows.length,
      });
    }

    return result;
  }, [uploadedRows]);

  const atRiskDrives = useMemo(() => {
    if (!uploadedRows) return [];
    return uploadedRows
      .filter(
        (d) =>
          Number(d.Failure_Flag) === 1 ||
          Number(d.Temperature_C) >= 70 ||
          Number(d.Percent_Life_Used) >= 80
      )
      .slice(0, 10);
  }, [uploadedRows]);

  if (!summary) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-slate-50 mb-2">Insights</h2>
          <p className="text-slate-400">Upload a CSV file to view AI insights</p>
        </div>
      </div>
    );
  }

  const insightIcons = {
    temp: Thermometer,
    wear: Settings,
    errors: AlertCircle,
    power: Zap,
    failing: AlertTriangle,
    healthy: CheckCircle2,
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-50">Fleet Insights</h1>
        <p className="text-slate-400 mt-2">AI-powered recommendations and analysis</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {insights.map((insight) => {
          const borderColors = {
            critical: "border-red-600",
            warning: "border-yellow-600",
            success: "border-green-600",
          };

          const bgColors = {
            critical: "bg-red-900/10",
            warning: "bg-yellow-900/10",
            success: "bg-green-900/10",
          };

          const Icon = insightIcons[insight.icon] || AlertCircle;

          return (
            <div
              key={insight.id}
              className={`card border-l-4 ${borderColors[insight.severity]} ${bgColors[insight.severity]}`}
            >
              <div className="flex items-start gap-3">
                <Icon size={28} className="text-purple-400 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <h4 className="font-semibold text-slate-50 truncate">
                    {insight.title}
                  </h4>
                  <p className="text-sm text-slate-400 mt-1">{insight.desc}</p>
                  <div className="text-2xl font-bold text-purple-400 mt-2">
                    {insight.count}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {atRiskDrives.length > 0 && (
        <div className="card overflow-x-auto">
          <h3 className="text-lg font-semibold text-slate-50 mb-4">At-Risk Drives</h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-dark-600">
                <th className="px-4 py-3 text-left text-slate-400 font-semibold">Risk</th>
                <th className="px-4 py-3 text-left text-slate-400 font-semibold">Drive ID</th>
                <th className="px-4 py-3 text-left text-slate-400 font-semibold">Temp</th>
                <th className="px-4 py-3 text-left text-slate-400 font-semibold">Life %</th>
                <th className="px-4 py-3 text-left text-slate-400 font-semibold">Action</th>
              </tr>
            </thead>
            <tbody>
              {atRiskDrives.map((drive, idx) => {
                const temp = Number(drive.Temperature_C);
                const life = Number(drive.Percent_Life_Used);
                const isFailing = Number(drive.Failure_Flag) === 1;

                let riskLevel = "Low";
                let riskColor = "text-green-400";
                if (isFailing) {
                  riskLevel = "Critical";
                  riskColor = "text-red-400";
                } else if (temp >= 70 || life >= 80) {
                  riskLevel = "High";
                  riskColor = "text-yellow-400";
                }

                return (
                  <tr key={idx} className="border-b border-dark-600 hover:bg-dark-600/50">
                    <td className={`px-4 py-3 font-semibold ${riskColor}`}>
                      {riskLevel}
                    </td>
                    <td className="px-4 py-3 text-slate-300 font-medium">
                      {drive.Drive_ID}
                    </td>
                    <td className="px-4 py-3 text-slate-400">{temp.toFixed(1)}°C</td>
                    <td className="px-4 py-3 text-slate-400">{life.toFixed(1)}%</td>
                    <td className="px-4 py-3 text-xs text-slate-400">
                      {isFailing && (
                        <span className="inline-flex items-center gap-2 text-red-400">
                          <AlertCircle size={14} /> Replace
                        </span>
                      )}
                      {temp >= 70 && !isFailing && (
                        <span className="inline-flex items-center gap-2 text-yellow-400">
                          <Thermometer size={14} /> Cool
                        </span>
                      )}
                      {life >= 80 && !isFailing && temp < 70 && (
                        <span className="inline-flex items-center gap-2 text-purple-400">
                          <ClipboardList size={14} /> Plan
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <div className="card">
        <h3 className="text-lg font-semibold text-slate-50 mb-4 flex items-center gap-2">
          <Lightbulb size={20} />
          Recommendations
        </h3>
        <div className="space-y-3">
          {insights.some((i) => i.id === "temp") && (
            <div className="p-3 bg-yellow-900/10 border border-yellow-700/30 rounded-lg">
              <p className="text-yellow-400 font-semibold text-sm">Improve Cooling</p>
              <p className="text-sm text-slate-400 mt-1">
                Optimize airflow and consider underclocking hot drives
              </p>
            </div>
          )}
          {insights.some((i) => i.id === "wear") && (
            <div className="p-3 bg-yellow-900/10 border border-yellow-700/30 rounded-lg">
              <p className="text-yellow-400 font-semibold text-sm">Schedule Replacements</p>
              <p className="text-sm text-slate-400 mt-1">
                Plan drive replacement before reaching 90% wear
              </p>
            </div>
          )}
          {insights.some((i) => i.id === "errors") && (
            <div className="p-3 bg-red-900/10 border border-red-700/30 rounded-lg">
              <p className="text-red-400 font-semibold text-sm">Investigate Errors</p>
              <p className="text-sm text-slate-400 mt-1">
                High error rates are predictors of imminent failure
              </p>
            </div>
          )}
          {insights.some((i) => i.id === "healthy") && (
            <div className="p-3 bg-green-900/10 border border-green-700/30 rounded-lg">
              <p className="text-green-400 font-semibold text-sm">Continue Monitoring</p>
              <p className="text-sm text-slate-400 mt-1">
                Fleet is healthy. Maintain regular monitoring
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Insights;
