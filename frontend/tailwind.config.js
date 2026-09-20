/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ocean: {
          950: '#030b14',
          900: '#071626',
          850: '#0a1f36',
          800: '#0f2b48',
          700: '#153b63',
          600: '#1d5187',
          500: '#0284c7',
          400: '#38bdf8',
          300: '#7dd3fc',
          200: '#bae6fd',
          100: '#e0f2fe',
        },
        marine: {
          safe: '#10b981',
          caution: '#f59e0b',
          unsafe: '#ef4444',
          neutral: '#64748b'
        }
      }
    },
  },
  plugins: [],
}
