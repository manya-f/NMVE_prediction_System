import React from "react";
import { Link, useLocation } from "react-router-dom";
import { BarChart3, Server, Zap, Lightbulb, Cpu } from "lucide-react";

function Sidebar() {
  const location = useLocation();

  const navItems = [
    { path: "/", label: "Dashboard", icon: BarChart3 },
    { path: "/drives", label: "Drives", icon: Server },
    { path: "/predictions", label: "Predictions", icon: Zap },
    { path: "/predict-single", label: "Single Drive", icon: Cpu },
    { path: "/insights", label: "Insights", icon: Lightbulb },
  ];

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-dark-700 border-r border-dark-600 flex flex-col overflow-y-auto">
      <div className="p-6 border-b border-dark-600">
        <h1 className="text-xl font-bold bg-gradient-to-r from-purple-400 to-purple-600 bg-clip-text text-transparent">
          NVMe Predictor
        </h1>
      </div>

      <nav className="flex-1 p-4">
        {navItems.map(({ path, label, icon: Icon }) => {
          const isActive = location.pathname === path;
          return (
            <Link
              key={path}
              to={path}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition-all duration-200 ${
                isActive
                  ? "bg-purple-600/20 text-purple-400 border border-purple-600/50"
                  : "text-slate-400 hover:bg-dark-600 hover:text-slate-300"
              }`}
            >
              <Icon size={20} />
              <span className="font-medium">{label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-dark-600 text-xs text-slate-500">
        <div className="flex items-center gap-2">
          <Zap size={14} className="text-purple-400" />
          <span>Predictive Maintenance</span>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
