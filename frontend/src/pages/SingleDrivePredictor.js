import React, { useState } from "react";
import { AlertCircle, CheckCircle2, TrendingUp, Zap } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const PIE_COLORS = [
  "#38bdf8",
  "#22c55e",
  "#f59e0b",
  "#ef4444",
  "#8b5cf6",
  "#06b6d4",
  "#fb7185",
  "#84cc16",
  "#f97316",
];

const INPUT_FIELDS = [
  {
    key: "Vendor",
    label: "Vendor",
    type: "select",
    options: ["Crucial", "Intel", "Samsung", "Seagate", "Western Digital"],
  },
  {
    key: "Model",
    label: "Model",
    type: "select",
    options: ["670p", "980 Pro", "FireCuda 530", "P5 Plus", "SN850"],
  },
  {
    key: "Firmware_Version",
    label: "Firmware_Version",
    type: "select",
    options: ["1.0.0", "1.1.2", "2.0.1", "2.1.0", "3.0.5"],
  },
  { key: "Temperature_C", label: "Temperature_C", type: "number", step: "any" },
  { key: "Total_TBW_TB", label: "Total_TBW_TB", type: "number", step: "any" },
  { key: "Total_TBR_TB", label: "Total_TBR_TB", type: "number", step: "any" },
  { key: "Power_On_Hours", label: "Power_On_Hours", type: "number", step: "1" },
  { key: "Unsafe_Shutdowns", label: "Unsafe_Shutdowns", type: "number", step: "1" },
  { key: "Media_Errors", label: "Media_Errors", type: "number", step: "1" },
  { key: "Percent_Life_Used", label: "Percent_Life_Used", type: "number", step: "any", min: 0, max: 100 },
  { key: "Available_Spare", label: "Available_Spare", type: "number", step: "any", min: 0, max: 100 },
  { key: "SMART_Warning_Flag", label: "SMART_Warning_Flag", type: "number", step: "1", min: 0, max: 1 },
];

const FACTOR_RULES = {
  Temperature_C: {
    threshold: 70,
    description: "Higher temperature increases thermal stress and instability.",
    recommendation: "Improve airflow or cooling around the NVMe drive.",
  },
  Total_TBW_TB: {
    threshold: 300,
    description: "Higher written bytes can indicate wear progression.",
    recommendation: "Reduce write-heavy workloads and review replacement planning.",
  },
  Total_TBR_TB: {
    threshold: 600,
    description: "Heavy read activity can reflect sustained device load.",
    recommendation: "Review workload balance and observe read-intensive usage periods.",
  },
  Power_On_Hours: {
    threshold: 30000,
    description: "Longer operating lifetime can correlate with age-related degradation.",
    recommendation: "Track aging drives and compare lifetime against replacement policy.",
  },
  Unsafe_Shutdowns: {
    threshold: 10,
    description: "Frequent unsafe shutdowns increase corruption and power-related risk.",
    recommendation: "Check PSU stability, shutdown handling, and cable integrity.",
  },
  Media_Errors: {
    threshold: 20,
    description: "Media errors are a direct sign of storage reliability issues.",
    recommendation: "Back up data and run diagnostics if media errors continue rising.",
  },
  Percent_Life_Used: {
    threshold: 80,
    description: "Higher life used indicates the drive is nearing endurance limits.",
    recommendation: "Prepare replacement when endurance usage becomes consistently high.",
  },
  Available_Spare: {
    threshold: 100,
    invert: true,
    description: "Lower available spare reduces the drive's margin for handling degradation.",
    recommendation: "Monitor spare capacity decline and replace the drive if it drops sharply.",
  },
  SMART_Warning_Flag: {
    threshold: 1,
    description: "SMART warnings indicate the controller has detected a health concern.",
    recommendation: "Treat SMART warnings as immediate maintenance signals.",
  },
};

function clamp01(value) {
  return Math.max(0, Math.min(1, value));
}

function buildLiveFactorAnalysis(formData, predictedMode) {
  const modeBoosts = {
    0: {
      Temperature_C: 0.8,
      Total_TBW_TB: 0.8,
      Total_TBR_TB: 0.9,
      Power_On_Hours: 0.85,
      Unsafe_Shutdowns: 0.7,
      Media_Errors: 0.65,
      Percent_Life_Used: 0.75,
      Available_Spare: 0.95,
      SMART_Warning_Flag: 0.5,
    },
    1: {
      Total_TBW_TB: 1.35,
      Percent_Life_Used: 1.45,
      Power_On_Hours: 1.1,
      Available_Spare: 1.2,
    },
    2: {
      Temperature_C: 1.6,
      SMART_Warning_Flag: 1.15,
      Media_Errors: 1.05,
    },
    3: {
      Unsafe_Shutdowns: 1.7,
      SMART_Warning_Flag: 1.2,
      Media_Errors: 1.05,
    },
    4: {
      Media_Errors: 1.35,
      SMART_Warning_Flag: 1.2,
      Total_TBR_TB: 1.05,
    },
    5: {
      Media_Errors: 1.55,
      Power_On_Hours: 0.65,
      SMART_Warning_Flag: 1.15,
      Temperature_C: 1.05,
    },
  };

  const activeBoosts = modeBoosts[predictedMode ?? 1] || {};

  const factors = Object.entries(FACTOR_RULES).map(([key, config]) => {
    const rawValue = Number(formData[key] ?? 0);
    const baseScore = config.invert
      ? clamp01((config.threshold - rawValue) / config.threshold)
      : clamp01(rawValue / config.threshold);
    const weightedScore = Math.max(baseScore * (activeBoosts[key] || 1), 0.01);

    return {
      factor: key,
      label: key,
      value: rawValue,
      description: config.description,
      recommendation: config.recommendation,
      score: weightedScore,
    };
  });

  const total = factors.reduce((sum, factor) => sum + factor.score, 0) || 1;
  const chartData = factors
    .map((factor) => ({
      ...factor,
      percentage: Number(((factor.score / total) * 100).toFixed(1)),
    }))
    .sort((a, b) => b.percentage - a.percentage);

  const recommendations = chartData
    .filter((factor) => factor.score >= 0.15)
    .slice(0, 4)
    .map((factor) => ({
      factor: factor.label,
      text: factor.recommendation,
    }));

  if (recommendations.length === 0) {
    recommendations.push({
      factor: "General",
      text: "Current inputs do not indicate a strong risk driver. Continue monitoring the drive regularly.",
    });
  }

  return { chartData, recommendations };
}

function ProbabilityPieChart({ data, target }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-[220px_minmax(0,1fr)] gap-6 items-center">
      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="percentage"
              nameKey="label"
              innerRadius={55}
              outerRadius={82}
              paddingAngle={2}
              stroke="#0f172a"
              strokeWidth={2}
            >
              {data.map((entry, index) => (
                <Cell
                  key={entry.factor || entry.mode}
                  fill={PIE_COLORS[index % PIE_COLORS.length]}
                />
              ))}
            </Pie>
            <Tooltip
              formatter={(value) => [`${Number(value).toFixed(1)}%`, "Contribution"]}
              contentStyle={{
                backgroundColor: "#0f172a",
                border: "1px solid #334155",
                borderRadius: "8px",
              }}
              labelStyle={{ color: "#e2e8f0" }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="space-y-3">
        {data.map((entry, index) => (
          <div
            key={entry.factor || entry.mode}
            className="rounded-lg border border-dark-500 bg-dark-600/40 p-3"
          >
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <span
                  className="h-3 w-3 rounded-full"
                  style={{ backgroundColor: PIE_COLORS[index % PIE_COLORS.length] }}
                />
                <span className="text-slate-200 font-medium">{entry.label}</span>
              </div>
              <span className="text-sky-400 font-semibold">
                {entry.percentage.toFixed(1)}%
              </span>
            </div>
            <p className="text-slate-400 text-sm mt-2">
              {entry.description ||
                (target === "failure"
                  ? "Share of failure risk predicted from the current SMART metrics."
                  : "Share of healthy contribution based on the current SMART metrics.")}
            </p>
            {entry.value !== undefined && (
              <p className="text-slate-500 text-xs mt-2">Input value: {entry.value}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function FailureConfidenceChart({ data, predictedMode }) {
  const chartData = [...data].sort((a, b) => b.percentage - a.percentage);
  const predictedColor = predictedMode === 0 ? "#22c55e" : "#ef4444";

  return (
    <div className="space-y-4">
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 8, right: 24, left: 16, bottom: 8 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis
              type="number"
              domain={[0, 100]}
              stroke="#94a3b8"
              tickFormatter={(value) => `${value}%`}
            />
            <YAxis
              type="category"
              dataKey="label"
              stroke="#94a3b8"
              width={160}
            />
            <Tooltip
              formatter={(value) => [`${Number(value).toFixed(1)}%`, "Confidence"]}
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
              {chartData.map((entry) => (
                <Cell
                  key={entry.mode}
                  fill={entry.mode === predictedMode ? predictedColor : "#64748b"}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="space-y-2">
        {chartData.map((entry) => (
          <div
            key={entry.mode}
            className="flex items-center justify-between rounded-lg border border-dark-500 bg-dark-600/40 px-4 py-3"
          >
            <div className="flex items-center gap-3">
              <span
                className="h-3 w-3 rounded-full"
                style={{
                  backgroundColor:
                    entry.mode === predictedMode ? predictedColor : "#64748b",
                }}
              />
              <span className="text-slate-200">
                {entry.label}
                {entry.mode === predictedMode ? " (Predicted)" : ""}
              </span>
            </div>
            <span className="text-sky-400 font-semibold">{entry.percentage.toFixed(1)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function LiveFactorImpactCard({ analysis, predictedMode }) {
  const accent = predictedMode === 0 ? "#22c55e" : "#ef4444";

  return (
    <div className="card">
      <h4 className="text-lg font-semibold text-slate-50 mb-4">
        Input Factor Impact
      </h4>
      <div className="grid grid-cols-1 md:grid-cols-[240px_minmax(0,1fr)] gap-6 items-center">
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={analysis.chartData}
                dataKey="percentage"
                nameKey="label"
                innerRadius={52}
                outerRadius={88}
                paddingAngle={2}
                stroke="#0f172a"
                strokeWidth={2}
              >
                {analysis.chartData.map((entry, index) => (
                  <Cell
                    key={entry.factor}
                    fill={index === 0 ? accent : PIE_COLORS[index % PIE_COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip
                formatter={(value) => [`${Number(value).toFixed(1)}%`, "Factor impact"]}
                contentStyle={{
                  backgroundColor: "#0f172a",
                  border: "1px solid #334155",
                  borderRadius: "8px",
                  color: "#f8fafc",
                }}
                labelStyle={{ color: "#f8fafc" }}
                itemStyle={{ color: "#f8fafc" }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="space-y-2">
          {analysis.chartData.map((entry, index) => (
            <div
              key={entry.factor}
              className="flex items-center justify-between rounded-lg border border-dark-500 bg-dark-600/40 px-4 py-3"
            >
              <div className="flex items-center gap-3">
                <span
                  className="h-3 w-3 rounded-full"
                  style={{
                    backgroundColor:
                      index === 0 ? accent : PIE_COLORS[index % PIE_COLORS.length],
                  }}
                />
                <span className="text-slate-200">{entry.label}</span>
              </div>
              <span className="text-sky-400 font-semibold">{entry.percentage.toFixed(1)}%</span>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-5 space-y-3">
        <h5 className="text-sm font-semibold text-slate-200">Recommendations</h5>
        {analysis.recommendations.map((item) => (
          <div
            key={item.factor}
            className="rounded-lg border border-dark-500 bg-dark-600/40 px-4 py-3"
          >
            <p className="text-slate-100 font-medium">{item.factor}</p>
            <p className="text-slate-400 text-sm mt-1">{item.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function ManualDrivePredictor() {
  const [formData, setFormData] = useState({
    Vendor: "Samsung",
    Model: "980 Pro",
    Firmware_Version: "1.0.0",
    Temperature_C: 40,
    Total_TBW_TB: 0,
    Total_TBR_TB: 0,
    Power_On_Hours: 5000,
    Unsafe_Shutdowns: 1,
    Media_Errors: 0,
    Percent_Life_Used: 20,
    Available_Spare: 100,
    SMART_Warning_Flag: 0,
  });

  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const liveAnalysis = buildLiveFactorAnalysis(formData, prediction?.predicted_mode);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]:
        name === "Vendor" || name === "Model" || name === "Firmware_Version"
          ? value
          : value === ""
            ? ""
            : Number(value),
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const payload = {
        ...formData,
        temperature: formData.Temperature_C,
        power_on_hours: formData.Power_On_Hours,
        life_used: formData.Percent_Life_Used,
        unsafe_shutdowns: formData.Unsafe_Shutdowns,
        media_errors: formData.Media_Errors,
        error_count: formData.Media_Errors,
      };

      const response = await fetch("http://localhost:5000/api/predict/single", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Prediction failed");

      setPrediction(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case "LOW":
        return "text-green-400 bg-green-900/20 border-green-700/50";
      case "MEDIUM":
        return "text-yellow-400 bg-yellow-900/20 border-yellow-700/50";
      case "HIGH":
        return "text-red-400 bg-red-900/20 border-red-700/50";
      default:
        return "text-slate-400 bg-dark-600/50";
    }
  };

  const getPredictionAccent = (predictedMode) => {
    return predictedMode === 0 ? "text-green-400 bg-green-500" : "text-red-400 bg-red-500";
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-50">Single Drive Predictor</h1>
        <p className="text-slate-400 mt-2">Enter NVMe drive SMART metrics to get failure predictions</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-6">
          <div className="card">
            <form onSubmit={handleSubmit} className="space-y-4">
              <h3 className="text-lg font-semibold text-slate-50 mb-4">Drive Information</h3>
              <h3 className="text-lg font-semibold text-slate-50 mt-6 mb-3">SMART Metrics</h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {INPUT_FIELDS.map((field) => (
                  <div key={field.key}>
                    <label className="text-sm text-slate-400 block mb-1">{field.label}</label>
                    {field.type === "select" ? (
                      <select
                        name={field.key}
                        value={formData[field.key]}
                        onChange={handleChange}
                        className="w-full px-3 py-2 bg-dark-600 border border-dark-500 rounded-lg text-slate-50 focus:border-purple-600"
                      >
                        {field.options.map((option) => (
                          <option key={option} value={option}>
                            {option}
                          </option>
                        ))}
                      </select>
                    ) : (
                      <input
                        type={field.type}
                        name={field.key}
                        value={formData[field.key]}
                        step={field.step}
                        min={field.min}
                        max={field.max}
                        onChange={handleChange}
                        className="w-full px-3 py-2 bg-dark-600 border border-dark-500 rounded-lg text-slate-50 focus:border-purple-600"
                      />
                    )}
                  </div>
                ))}
              </div>

              {error && (
                <div className="mt-4 p-3 bg-red-900/20 border border-red-700 rounded-lg text-red-400">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full mt-6 btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? "Predicting..." : "Predict Drive Status"}
              </button>
            </form>
          </div>

          <LiveFactorImpactCard
            analysis={liveAnalysis}
            predictedMode={prediction?.predicted_mode}
          />
        </div>

        <div className="space-y-4">
          {prediction ? (
            <>
              <div className={`card border ${getRiskColor(prediction.risk_level)}`}>
                <div className="flex items-center gap-3 mb-3">
                  {prediction.risk_level === "LOW" && <CheckCircle2 className="text-green-400" size={24} />}
                  {prediction.risk_level === "MEDIUM" && <AlertCircle className="text-yellow-400" size={24} />}
                  {prediction.risk_level === "HIGH" && <AlertCircle className="text-red-400" size={24} />}
                  <div>
                    <p className="text-sm text-slate-400">Overall Risk Level</p>
                    <p className="text-2xl font-bold">{prediction.risk_level}</p>
                  </div>
                </div>
              </div>

              <div className="card">
                <h4 className="text-lg font-semibold text-slate-50 mb-4">Failure Mode Prediction</h4>
                <div className="space-y-3">
                  {(() => {
                    const accent = getPredictionAccent(prediction.predicted_mode);
                    const textColor = accent.split(" ")[0];
                    const barColor = accent.split(" ")[1];

                    return (
                  <div className="p-4 bg-dark-600/50 rounded-lg border border-dark-500">
                    <p className="text-sm text-slate-400 mb-2">Predicted Failure Mode</p>
                    <p className={`text-2xl font-bold mb-2 ${textColor}`}>
                      {prediction.failure_mode_label}
                    </p>
                    <p className="text-sm text-slate-300 mb-3">{prediction.failure_mode_description}</p>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-dark-500 h-2 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${barColor}`}
                          style={{ width: `${prediction.confidence_percent}%` }}
                        ></div>
                      </div>
                      <span className={`font-bold text-sm ${textColor}`}>{prediction.confidence_percent}%</span>
                    </div>
                  </div>
                    );
                  })()}
                </div>
              </div>

              {prediction.mode_probabilities && (
                <div className="card">
                  <h4 className="text-lg font-semibold text-slate-50 mb-4">
                    Failure Confidence Levels
                  </h4>
                  <FailureConfidenceChart
                    data={prediction.mode_probabilities}
                    predictedMode={prediction.predicted_mode}
                  />
                </div>
              )}

              {prediction.factor_contributions && (
                <div className="card">
                  <h4 className="text-lg font-semibold text-slate-50 mb-4">
                    Factor Contribution To {prediction.factor_contribution_target === "failure" ? "Failure Risk" : "Healthy Condition"}
                  </h4>
                  <ProbabilityPieChart
                    data={prediction.factor_contributions}
                    target={prediction.factor_contribution_target}
                  />
                </div>
              )}

              {prediction.warnings && prediction.warnings.length > 0 && (
                <div className="card border border-yellow-700/50 bg-yellow-900/10">
                  <h4 className="text-lg font-semibold text-yellow-400 mb-3 flex items-center gap-2">
                    <AlertCircle size={20} />
                    Warnings & Alerts
                  </h4>
                  <ul className="space-y-2">
                    {prediction.warnings.map((warning, idx) => (
                      <li key={idx} className="text-sm text-yellow-300 flex items-start gap-2">
                        <span className="text-yellow-400 mt-0.5">!</span>
                        <span>{warning}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="card bg-purple-900/20 border border-purple-700/50">
                <h4 className="text-lg font-semibold text-purple-400 mb-2 flex items-center gap-2">
                  <TrendingUp size={20} />
                  Recommendation
                </h4>
                <p className="text-slate-50 mb-3">{prediction.recommendation}</p>
                {prediction.recommendation_points && prediction.recommendation_points.length > 0 && (
                  <ul className="space-y-2">
                    {prediction.recommendation_points.map((point, idx) => (
                      <li key={idx} className="text-sm text-slate-200 flex items-start gap-2">
                        <span className="text-purple-300 mt-0.5">•</span>
                        <span>{point}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </>
          ) : (
            <div className="card text-center py-12">
              <Zap className="mx-auto mb-4 text-slate-500" size={32} />
              <p className="text-slate-400">Enter drive metrics and click "Predict Drive Status"</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ManualDrivePredictor;
