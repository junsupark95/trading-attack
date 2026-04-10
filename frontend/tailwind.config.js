/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'brand-dark': '#0f172a',
        'brand-card': '#1e293b',
        'brand-accent': '#38bdf8',
        'brand-success': '#10b981',
        'brand-danger': '#ef4444',
      },
      backdropBlur: {
        xs: '2px',
      }
    },
  },
  plugins: [],
}
