import React, { useContext, useState } from "react";
import { AppContext } from "../App";
import { Zap, Loader, CheckCircle2, AlertTriangle } from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
} from "recharts";

const MODE_SUGGESTIONS = {
  Healthy:
    "No immediate action required. Continue routine SMART monitoring and keep firmware maintenance on schedule.",
  "Wear-Out Failure":
    "Schedule drive replacement soon, reduce write-heavy workloads, and verify backup coverage before endurance is exhausted.",
  "Thermal Failure":
    "Improve airflow, inspect heatsinks and fan curves, and avoid sustained high-temperature workloads until temperatures stabilize.",
  "Power-Related Failure":
    "Check PSU stability, inspect cabling, review unsafe shutdown history, and move the drive behind protected power if possible.",
  "Controller/Firmware Failure":
    "Review firmware version, apply vendor-approved updates, and run vendor diagnostics to rule out controller instability.",
  "Rapid Error Accumulation (Early-Life Failure)":
    "Back up data immediately, isolate the drive from critical workloads, and plan replacement because the error trend suggests early degradation.",
};

const MODE_COLORS = {
  Healthy: "#22c55e",
  "Wear-Out Failure": "#f59e0b",
  "Thermal Failure": "#ef4444",
  "Power-Related Failure": "#fb923c",
  "Controller/Firmware Failure": "#8b5cf6",
  "Rapid Error Accumulation (Early-Life Failure)": "#06b6d4",
};

function getModeSuggestion(modeName) {
  return (
    MODE_SUGGESTIONS[modeName] ||
    "Review drive telemetry, validate backups, and monitor this failure pattern more closely."
  );
}

function getBarColor(modeName, isPrimary) {
  if (isPrimary) {
    return modeName === "Healthy" ? "#22c55e" : "#ef4444";
  }

  return MODE_COLORS[modeName] || "#64748b";
}

function getDisplayValue(row, key, fallbackKey) {
  return row?.[key] ?? row?.[fallbackKey] ?? "-";
}

function buildPredictionPayload(row) {
  return {
    Vendor: row.Vendor ?? row.vendor ?? "Samsung",
    Model: row.Model ?? row.model ?? "980 Pro",
    Firmware_Version: row.Firmware_Version ?? row.firmware_version ?? "1.0.0",
    Temperature_C: Number(row.Temperature_C ?? row.temperature ?? 0),
    Total_TBW_TB: Number(row.Total_TBW_TB ?? 0),
    Total_TBR_TB: Number(row.Total_TBR_TB ?? 0),
    Power_On_Hours: Number(row.Power_On_Hours ?? row.power_on_hours ?? 0),
    Unsafe_Shutdowns: Number(row.Unsafe_Shutdowns ?? row.unsafe_shutdowns ?? 0),
    Media_Errors: Number(row.Media_Errors ?? row.media_errors ?? row.error_count ?? 0),
    Percent_Life_Used: Number(row.Percent_Life_Used ?? row.life_used ?? 0),
    Available_Spare: Number(row.Available_Spare ?? 100),
    SMART_Warning_Flag: Number(row.SMART_Warning_Flag ?? 0),
  };
}

function Predictions() {
  const { uploadedRows } = useContext(AppContext);
  const [selectedDriveIdx, setSelectedDriveIdx] = useState(0);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const selectedDrive = uploadedRows[selectedDriveIdx] || null;

  const handlePredict = async () => {
    if (!selectedDrive) return;

    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const predictionData = buildPredictionPayload(selectedDrive);

      const response = await fetch("http://localhost:5000/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(predictionData),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Prediction failed");

      const modeProbabilities = (data.mode_probabilities || []).map((mode) => ({
        ...mode,
        name: mode.label,
        suggestion: getModeSuggestion(mode.label),
      }));

      const predictedMode = data.predicted_mode ?? 0;
      const predictedEntry =
        modeProbabilities.find((mode) => mode.mode === predictedMode) || null;
      const topRiskMode =
        modeProbabilities
          .filter((mode) => mode.mode !== predictedMode)
          .sort((a, b) => b.percentage - a.percentage)[0] || null;

      setPrediction({
        health: data.health,
        predicted_mode: predictedMode,
        mode_name: data.failure_mode_label || data.failure_mode || "Unknown",
        mode_description: data.failure_mode_description || "",
        confidence: Number(data.confidence_percent ?? 0) / 100,
        label: predictedMode === 0 ? "SAFE" : "ATTENTION",
        prob_safe:
          Number(
            (data.binary_probabilities || []).find((item) => item.mode === "SAFE")
              ?.percentage ?? 0
          ) / 100,
        prob_fail:
          Number(
            (data.binary_probabilities || []).find((item) => item.mode === "FAIL")
              ?.percentage ?? 0
          ) / 100,
        failure_modes: modeProbabilities,
        top_risk_mode: topRiskMode,
        primary_suggestion:
          predictedEntry?.suggestion || getModeSuggestion(data.failure_mode_label),
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!uploadedRows || uploadedRows.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-slate-50 mb-2">Predictions</h2>
          <p className="text-slate-400">Upload a CSV file to make predictions</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-50">ML Predictions</h1>
        <p className="text-slate-400 mt-2">
          Predict drive failure with per-mode percentages and action suggestions
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-slate-50 mb-4">Select Drive</h3>
          <div className="space-y-4">
            <div>
              <label className="text-sm text-slate-400 mb-2 block">
                Drive {selectedDriveIdx + 1} / {uploadedRows.length}
              </label>
              <input
                type="range"
                min="0"
                max={Math.max(0, uploadedRows.length - 1)}
                value={selectedDriveIdx}
                onChange={(e) => setSelectedDriveIdx(Number(e.target.value))}
                className="w-full accent-purple-600"
              />
            </div>

            {selectedDrive && (
              <div className="bg-dark-600/50 p-4 rounded-lg space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">ID:</span>
                  <span className="text-slate-300 font-medium">
                    {getDisplayValue(selectedDrive, "Drive_ID", "drive_id")}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Model:</span>
                  <span className="text-slate-300 font-medium">
                    {getDisplayValue(selectedDrive, "Model", "model")}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Vendor:</span>
                  <span className="text-slate-300 font-medium">
                    {getDisplayValue(selectedDrive, "Vendor", "vendor")}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Firmware:</span>
                  <span className="text-slate-300 font-medium">
                    {getDisplayValue(selectedDrive, "Firmware_Version", "firmware_version")}
                  </span>
                </div>
              </div>
            )}

            <button
              onClick={handlePredict}
              disabled={loading || !selectedDrive}
              className="btn-primary w-full"
            >
              {loading ? (
                <>
                  <Loader size={18} className="animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Zap size={18} />
                  Predict
                </>
              )}
            </button>

            {error && (
              <div className="text-red-400 text-sm bg-red-900/20 p-3 rounded-lg">
                {error}
              </div>
            )}
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-slate-50 mb-4">Prediction Result</h3>
          {prediction ? (
            <div className="space-y-4">
              <div
                className={`p-4 rounded-lg border-2 text-center ${
                  prediction.predicted_mode === 0
                    ? "bg-green-900/20 border-green-600 text-green-400"
                    : "bg-red-900/20 border-red-600 text-red-400"
                }`}
              >
                <div className="text-3xl font-bold flex justify-center">
                  {prediction.predicted_mode === 0 ? (
                    <CheckCircle2 className="text-green-400" size={40} />
                  ) : (
                    <AlertTriangle className="text-red-400" size={40} />
                  )}
                </div>
                <div className="text-xl font-bold mt-2">{prediction.label}</div>
                <div className="text-sm text-slate-300 mt-1">{prediction.mode_name}</div>
              </div>

              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-slate-300">P(SAFE)</span>
                  <span className="text-green-400 font-bold">
                    {(prediction.prob_safe * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="w-full h-3 bg-dark-600 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-green-500 to-green-600"
                    style={{ width: `${prediction.prob_safe * 100}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-slate-300">P(FAIL)</span>
                  <span className="text-red-400 font-bold">
                    {(prediction.prob_fail * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="w-full h-3 bg-dark-600 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-red-500 to-red-600"
                    style={{ width: `${prediction.prob_fail * 100}%` }}
                  />
                </div>
              </div>

              <div className="bg-sky-950/30 border border-sky-700/40 rounded-lg p-4">
                <p className="text-slate-400 text-sm">Primary Failure Pattern</p>
                <div className="text-sky-400 font-semibold text-lg mt-1">
                  {prediction.mode_name}
                </div>
                <p className="text-slate-300 text-sm mt-2">
                  {prediction.mode_description}
                </p>
                <p className="text-slate-200 text-sm mt-3">
                  {prediction.primary_suggestion}
                </p>
              </div>

              {prediction.top_risk_mode && (
                <div className="bg-amber-950/30 border border-amber-700/40 rounded-lg p-4">
                  <p className="text-slate-400 text-sm">Secondary Risk To Watch</p>
                  <div className="text-amber-400 font-semibold mt-1">
                    {prediction.top_risk_mode.name}
                  </div>
                  <p className="text-slate-300 text-sm mt-2">
                    {getModeSuggestion(prediction.top_risk_mode.name)}
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12 text-slate-400">
              <p>Select a drive and click Predict</p>
            </div>
          )}
        </div>
      </div>

      {selectedDrive && (
        <div className="card">
          <h3 className="text-lg font-semibold text-slate-50 mb-4">Drive Attributes</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: "Temperature", key: "Temperature_C", unit: "C" },
              { label: "Power Hours", key: "Power_On_Hours" },
              { label: "Life Used", key: "Percent_Life_Used", unit: "%" },
              { label: "Total TBW", key: "Total_TBW_TB", unit: "TB" },
              { label: "Total TBR", key: "Total_TBR_TB", unit: "TB" },
              { label: "Media Errors", key: "Media_Errors" },
              { label: "Unsafe Shutdowns", key: "Unsafe_Shutdowns" },
              { label: "Available Spare", key: "Available_Spare", unit: "%" },
            ].map((attr) => (
              <div key={attr.key} className="bg-dark-600/50 p-3 rounded-lg">
                <p className="text-slate-400 text-xs mb-1">{attr.label}</p>
                <p className="text-slate-50 font-bold text-lg">
                  {selectedDrive[attr.key] ?? "-"}
                  {attr.unit && (
                    <span className="text-xs text-slate-400 ml-1">{attr.unit}</span>
                  )}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {prediction?.failure_modes?.length > 0 && (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <div className="card">
            <h3 className="text-lg font-semibold text-slate-50 mb-4">
              Failure Probability Graph
            </h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={prediction.failure_modes}
                  layout="vertical"
                  margin={{ top: 8, right: 24, left: 16, bottom: 8 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis
                    type="number"
                    stroke="#94a3b8"
                    domain={[0, 100]}
                    tickFormatter={(value) => `${value}%`}
                  />
                  <YAxis
                    type="category"
                    dataKey="name"
                    stroke="#94a3b8"
                    width={180}
                  />
                  <Tooltip
                    formatter={(value) => [`${Number(value).toFixed(1)}%`, "Probability"]}
                    contentStyle={{
                      backgroundColor: "#0f172a",
                      border: "1px solid #334155",
                      borderRadius: "8px",
                      color: "#f8fafc",
                    }}
                    labelStyle={{ color: "#f8fafc" }}
                    itemStyle={{ color: "#f8fafc" }}
                  />
                  <Bar dataKey="percentage" radius={[0, 8, 8, 0]}>
                    {prediction.failure_modes.map((mode) => (
                      <Cell
                        key={mode.mode}
                        fill={getBarColor(
                          mode.name,
                          mode.mode === prediction.predicted_mode
                        )}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold text-slate-50 mb-4">
              Suggestions For Every Error
            </h3>
            <div className="space-y-3">
              {prediction.failure_modes.map((mode) => (
                <div
                  key={mode.mode}
                  className="rounded-lg border border-dark-500 bg-dark-600/40 p-4"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="text-slate-50 font-semibold">{mode.name}</p>
                    </div>
                    <span className="text-sky-400 font-bold whitespace-nowrap">
                      {mode.percentage}%
                    </span>
                  </div>
                  <p className="text-slate-200 text-sm mt-3">{mode.suggestion}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Predictions;
