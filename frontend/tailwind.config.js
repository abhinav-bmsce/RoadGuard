/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0fdf4',
          100: '#dcfce7',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
        },
        asphalt: {
          800: '#1e293b',
          900: '#0f172a',
          950: '#020617',
        },
        hazard: {
          low: '#10b981',      // emerald
          medium: '#f59e0b',   // amber
          high: '#ef4444',     // crimson
          critical: '#991b1b', // dark red
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}

