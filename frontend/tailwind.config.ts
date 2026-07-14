import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eff7ff",
          100: "#dcedff",
          200: "#b3dcff",
          300: "#74c0ff",
          400: "#37a1ff",
          500: "#0f81ff",
          600: "#0064e3",
          700: "#0050b4",
          800: "#054594",
          900: "#0b3b78",
        },
        mint: {
          50: "#effdf8",
          100: "#d8f8eb",
          200: "#b5f0d6",
          300: "#7be2b9",
          400: "#41ce98",
          500: "#1fb27d",
          600: "#149063",
          700: "#137352",
          800: "#145b43",
          900: "#134b39",
        },
      },
      boxShadow: {
        soft: "0 18px 40px -24px rgba(15, 23, 42, 0.28)",
        card: "0 18px 36px -28px rgba(14, 116, 144, 0.24)",
      },
      borderRadius: {
        "4xl": "2rem",
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', '"Segoe UI"', "Candara", "sans-serif"],
      },
      backgroundImage: {
        "health-grid":
          "radial-gradient(circle at top left, rgba(15,129,255,0.08), transparent 28%), radial-gradient(circle at right top, rgba(31,178,125,0.08), transparent 22%)",
      },
    },
  },
  plugins: [],
};

export default config;
