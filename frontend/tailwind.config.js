/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // 8-bucket diverging scale used by the map and table
        dem5: "#0b3d91",
        dem4: "#1f6fdc",
        dem3: "#5aa1ec",
        dem2: "#fde68a",
        tossup: "#e5e7eb",
        rep2: "#fbbf24",
        rep3: "#ea6f6f",
        rep4: "#d33b3b",
        rep5: "#8c1d1d",
        // Grey scale for Independents (caucus-with-D for majority purposes).
        ind2: "#d4d4d4",
        ind3: "#a3a3a3",
        ind4: "#525252",
        ind5: "#374151",
      },
    },
  },
  plugins: [],
};
