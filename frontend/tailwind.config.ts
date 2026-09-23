import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bis: {
          blue: "#0A3871",
          lightBlue: "#EBF3FB",
          accent: "#0B57D0",
          navy: "#062044",
          gold: "#D97706",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "-apple-system", "sans-serif"],
        display: ["var(--font-inter)", "system-ui", "sans-serif"],
        script: ["var(--font-cursive)", "Georgia", "serif"],
      },
    },
  },
  plugins: [],
};
export default config;
