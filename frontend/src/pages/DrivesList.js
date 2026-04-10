import React, { useContext, useState, useMemo } from "react";
import { AppContext } from "../App";
import { Search, ArrowUpDown } from "lucide-react";

function DrivesList() {
  const { uploadedRows, summary } = useContext(AppContext);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sortColumn, setSortColumn] = useState("Power_On_Hours");
  const [sortAsc, setSortAsc] = useState(false);

  if (!summary) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-slate-50 mb-2">Drives List</h2>
          <p className="text-slate-400">Upload a CSV file to view all drives</p>
        </div>
      </div>
    );
  }

  const filteredDrives = useMemo(() => {
    let drives = [...uploadedRows];

    if (searchTerm) {
      const lower = searchTerm.toLowerCase();
      drives = drives.filter(
        (drive) =>
          (drive.Drive_ID && String(drive.Drive_ID).toLowerCase().includes(lower)) ||
          (drive.Model && String(drive.Model).toLowerCase().includes(lower)) ||
          (drive.Vendor && String(drive.Vendor).toLowerCase().includes(lower))
      );
    }

    if (statusFilter !== "all") {
      if (statusFilter === "healthy") {
        drives = drives.filter((d) => Number(d.Failure_Flag) === 0);
      } else if (statusFilter === "failing") {
        drives = drives.filter((d) => Number(d.Failure_Flag) === 1);
      } else if (statusFilter === "warning") {
        drives = drives.filter(
          (d) => Number(d.Temperature_C) >= 70 || Number(d.Percent_Life_Used) >= 80
        );
      }
    }

    drives.sort((a, b) => {
      const aVal = Number(a[sortColumn]) || 0;
      const bVal = Number(b[sortColumn]) || 0;
      return sortAsc ? aVal - bVal : bVal - aVal;
    });

    return drives;
  }, [uploadedRows, searchTerm, statusFilter, sortColumn, sortAsc]);

  const getStatusBadge = (drive) => {
    const isFailing = Number(drive.Failure_Flag) === 1;
    const temp = Number(drive.Temperature_C);
    const lifeUsed = Number(drive.Percent_Life_Used);

    if (isFailing)
      return { text: "FAIL", class: "badge-danger" };
    if (temp >= 70 || lifeUsed >= 80)
      return { text: "WARN", class: "badge-warning" };
    return { text: "OK", class: "badge-success" };
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-50">Drives List</h1>
        <p className="text-slate-400 mt-2">Manage and monitor all drives in your fleet</p>
      </div>

      <div className="card space-y-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3 text-slate-400" size={18} />
            <input
              type="text"
              placeholder="Search by Drive ID, Model, or Vendor..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-dark-600 border border-dark-500 rounded-lg text-slate-50 placeholder-slate-500 focus:border-purple-600 focus:outline-none transition"
            />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 bg-dark-600 border border-dark-500 rounded-lg text-slate-50 focus:border-purple-600 focus:outline-none"
          >
            <option value="all">All Drives</option>
            <option value="healthy">Healthy</option>
            <option value="warning">Warning</option>
            <option value="failing">Failing</option>
          </select>

          <select
            value={sortColumn}
            onChange={(e) => setSortColumn(e.target.value)}
            className="px-4 py-2 bg-dark-600 border border-dark-500 rounded-lg text-slate-50 focus:border-purple-600 focus:outline-none"
          >
            <option value="Power_On_Hours">Sort: Power Hours</option>
            <option value="Temperature_C">Sort: Temperature</option>
            <option value="Percent_Life_Used">Sort: Life Used %</option>
            <option value="Media_Errors">Sort: Errors</option>
          </select>

          <button
            onClick={() => setSortAsc(!sortAsc)}
            className="btn-secondary px-4"
          >
            <ArrowUpDown size={18} />
          </button>
        </div>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-dark-600">
              <th className="px-6 py-3 text-left text-slate-400 font-semibold">Status</th>
              <th className="px-6 py-3 text-left text-slate-400 font-semibold">Drive ID</th>
              <th className="px-6 py-3 text-left text-slate-400 font-semibold">Model</th>
              <th className="px-6 py-3 text-left text-slate-400 font-semibold">Temp</th>
              <th className="px-6 py-3 text-left text-slate-400 font-semibold">Life %</th>
              <th className="px-6 py-3 text-left text-slate-400 font-semibold">Power Hrs</th>
              <th className="px-6 py-3 text-left text-slate-400 font-semibold">Errors</th>
            </tr>
          </thead>
          <tbody>
            {filteredDrives.slice(0, 50).map((drive, idx) => {
              const status = getStatusBadge(drive);
              return (
                <tr key={idx} className="border-b border-dark-600 hover:bg-dark-600/50 transition">
                  <td className="px-6 py-4">
                    <span className={`badge ${status.class}`}>{status.text}</span>
                  </td>
                  <td className="px-6 py-4 text-slate-300 font-medium">{drive.Drive_ID || "—"}</td>
                  <td className="px-6 py-4 text-slate-400">{drive.Model || "—"}</td>
                  <td className="px-6 py-4 text-slate-400">
                    {Number(drive.Temperature_C).toFixed(1)}°C
                  </td>
                  <td className="px-6 py-4 text-slate-400">
                    {Number(drive.Percent_Life_Used).toFixed(1)}%
                  </td>
                  <td className="px-6 py-4 text-slate-400">
                    {Number(drive.Power_On_Hours).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-slate-400">{Number(drive.Media_Errors)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default DrivesList;
