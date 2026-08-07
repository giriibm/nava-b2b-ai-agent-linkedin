import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        navy: "#1F2937",
        accent: "#2563EB",
      },
    },
  },
  plugins: [],
};
export default config;
