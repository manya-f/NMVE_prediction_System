/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          50: "#f9fafb",
          100: "#f3f4f6",
          200: "#e5e7eb",
          300: "#d1d5db",
          400: "#9ca3af",
          500: "#6b7280",
          600: "#4b5563",
          700: "#1e293b",
          800: "#0f172a",
          900: "#020617",
        },
        slate: {
          400: "#94a3b8",
          500: "#64748b",
          600: "#475569",
          700: "#334155",
        },
      },
      boxShadow: {
        'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.2)',
        'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.3)',
        'glow': '0 0 20px rgba(139, 92, 246, 0.3)',
      },
    },
  },
  plugins: [],
}
