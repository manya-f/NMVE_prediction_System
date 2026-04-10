import React, { useState, useEffect, useMemo } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import "./index.css";
import Sidebar from "./components/Sidebar";
import Navbar from "./components/Navbar";
import { AlertTriangle, Zap } from "lucide-react";

import Dashboard from "./pages/Dashboard";
import DrivesList from "./pages/DrivesList";
import Predictions from "./pages/Predictions";
import SingleDrivePredictor from "./pages/SingleDrivePredictor";
import Insights from "./pages/Insights";

// Shared data and utilities
export const failureModeLabels = {
  0: "Healthy",
  1: "Wear-Out",
  2: "Thermal",
  3: "Power-Related",
  4: "Controller / Firmware",
  5: "Rapid Error Accumulation",
};

export function parseCsvFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const text = reader.result;
        if (typeof text !== "string") throw new Error("Unable to read file");

        const lines = text.trim().split(/\r\n|\n/).filter(line => line.trim());
        if (lines.length < 2) throw new Error("CSV must have header and at least one data row");

        const headers = lines[0].split(",").map(h => h.trim());
        const rows = lines.slice(1).map(row => {
          const cells = row.split(",").map(v => v.trim());
          const record = {};
          headers.forEach((header, index) => {
            const val = cells[index] ?? "";
            const num = Number(val);
            record[header] = Number.isFinite(num) && val !== "" ? num : val || null;
          });
          return record;
        });
        resolve(rows);
      } catch (err) {
        reject(err);
      }
    };
    reader.onerror = () => reject(new Error("Failed to read file"));
    reader.readAsText(file);
  });
}

export function buildSummary(rows) {
  const failureCounts = {};
  rows.forEach(row => {
    const mode = Number(row.Failure_Mode) || 0;
    failureCounts[mode] = (failureCounts[mode] || 0) + 1;
  });

  const chartData = Object.entries(failureCounts).map(([mode, count]) => ({
    mode: failureModeLabels[mode] || `Mode ${mode}`,
    count,
  }));

  const patternCounts = {
    "Wear-Out": 0,
    "Thermal": 0,
    "Power-Related": 0,
    "Firmware": 0,
    "Early-Life Failure": 0,
  };

  rows.forEach(row => {
    const percentLife = Number(row.Percent_Life_Used) || 0;
    const tbw = Number(row.Total_TBW_TB) || 0;
    const temp = Number(row.Temperature_C) || 0;
    const unsafe = Number(row.Unsafe_Shutdowns) || 0;
    const crc = Number(row.CRC_Errors) || 0;
    const readRate = Number(row.Read_Error_Rate) || 0;
    const writeRate = Number(row.Write_Error_Rate) || 0;
    const hours = Number(row.Power_On_Hours) || 0;
    const errors = Number(row.Media_Errors) || 0;

    if (percentLife >= 80 || tbw >= 300) patternCounts["Wear-Out"]++;
    if (temp >= 70) patternCounts["Thermal"]++;
    if (unsafe >= 4 || crc >= 3) patternCounts["Power-Related"]++;
    if (row.Firmware_Version) patternCounts["Firmware"]++;
    if (hours <= 3000 && readRate + writeRate >= 20) patternCounts["Early-Life Failure"]++;
  });

  const patterns = Object.entries(patternCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([name, count]) => ({ name, count }));

  return {
    rows,
    total: rows.length,
    healthy: failureCounts[0] || 0,
    failing: rows.filter(r => Number(r.Failure_Flag) === 1).length,
    failureModeData: chartData,
    topPatterns: patterns,
  };
}

// Header component with API status
function Header() {
  const [apiStatus, setApiStatus] = useState(null);

  useEffect(() => {
    fetch("http://localhost:5000/api/health")
      .then(r => setApiStatus(r.ok ? "connected" : "error"))
      .catch(() => setApiStatus("error"));
  }, []);

  return (
    <div className="header">
      <div className="title-block flex items-center gap-3">
        <Zap size={24} className="text-purple-400" />
        <div>
          <h1>NVMe Drive Failure Predictor</h1>
          <p>Real-time health analysis and predictive maintenance powered by machine learning</p>
        </div>
      </div>
      <div className="header-actions">
        {apiStatus && (
          <div className="status-badge">
            <span className="status-dot"></span>
            {apiStatus === "connected" ? "API Connected" : "API Offline"}
          </div>
        )}
      </div>
    </div>
  );
}

// App Provider to share state across pages
export const AppContext = React.createContext({
  uploadedRows: [],
  setUploadedRows: () => {},
  summary: null,
  setSummary: () => {},
  error: null,
  setError: () => {},
});

// Main App component
function AppRouterContent() {
  const [uploadedRows, setUploadedRows] = useState([]);
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);

  const onFileChange = async event => {
    setError(null);
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const rows = await parseCsvFile(file);
      const newSummary = buildSummary(rows);
      setUploadedRows(rows);
      setSummary(newSummary);
    } catch (err) {
      setError(err.message);
      setUploadedRows([]);
      setSummary(null);
    }
  };

  return (
    <AppContext.Provider value={{ uploadedRows, setUploadedRows, summary, setSummary, error, setError }}>
      <div className="min-h-screen bg-dark-800">
        <Sidebar />
        <Navbar onUpload={onFileChange} />
        
        <main className="ml-64 pt-32 pb-8">
          <div className="px-8">
            {error && (
              <div className="mb-6 p-4 bg-red-900/20 border border-red-800 rounded-lg text-red-400 flex items-center gap-2">
                <AlertTriangle size={18} className="text-red-400" />
                <span>{error}</span>
              </div>
            )}
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/drives" element={<DrivesList />} />
              <Route path="/predictions" element={<Predictions />} />
              <Route path="/predict-single" element={<SingleDrivePredictor />} />
              <Route path="/insights" element={<Insights />} />
            </Routes>
          </div>
        </main>
      </div>
    </AppContext.Provider>
  );
}

function App() {
  return (
    <Router>
      <AppRouterContent />
    </Router>
  );
}

function getSelectedRowDisplay(row) {
  if (!row) {
    return [];
  }
  return Object.entries(row).map(([key, value]) => ({
    key,
    value: value === null || value === undefined ? "—" : String(value),
  }));
}

export default App;
