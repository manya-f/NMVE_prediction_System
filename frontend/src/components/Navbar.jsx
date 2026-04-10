import React, { useState, useEffect } from "react";
import { Upload, CheckCircle, AlertCircle } from "lucide-react";

function Navbar({ onUpload }) {
  const [apiStatus, setApiStatus] = useState("checking");

  useEffect(() => {
    fetch("http://localhost:5000/api/health")
      .then((r) => setApiStatus(r.ok ? "connected" : "error"))
      .catch(() => setApiStatus("error"));
  }, []);

  return (
    <nav className="fixed top-0 left-64 right-0 bg-dark-700 border-b border-dark-600 px-6 py-4 flex items-center justify-between z-40">
      <div>
        <h2 className="text-lg font-semibold text-slate-50">
          NVMe Drive Failure Predictor
        </h2>
        <p className="text-sm text-slate-400">
          Real-time health analysis and predictive maintenance
        </p>
      </div>

      <div className="flex items-center gap-4">
        <label className="btn-secondary cursor-pointer">
          <Upload size={18} />
          <span>Upload CSV</span>
          <input
            type="file"
            accept=".csv"
            onChange={onUpload}
            className="hidden"
          />
        </label>

        <div
          className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
            apiStatus === "connected"
              ? "bg-green-900/20 text-green-400"
              : "bg-red-900/20 text-red-400"
          }`}
        >
          {apiStatus === "connected" ? (
            <CheckCircle size={18} />
          ) : (
            <AlertCircle size={18} />
          )}
          <span className="text-sm font-medium">
            {apiStatus === "connected" ? "API Connected" : "API Offline"}
          </span>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
