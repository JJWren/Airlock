/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}", // Scans all subfolders including components and views
  ],
  theme: {
    extend: {
      colors: {
        // Your specific Tactical Theme colors
        primary: "#3B82F6",
        secondary: "#71717A",
        tertiary: "#EF4444",
        neutral: "#09090B",
        surface: "#18181B", // Darker zinc for card backgrounds
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
        headline: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}