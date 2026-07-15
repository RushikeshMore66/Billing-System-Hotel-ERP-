import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./features/**/*.{js,ts,jsx,tsx,mdx}",
    "./layouts/**/*.{js,ts,jsx,tsx,mdx}",
    "./shell/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
      },
      colors: {
        // NDL Color Palette — Niralay Design Language
        primary: {
          DEFAULT: "#155E4B",
          50: "#EDF7F3",
          100: "#D0EDE5",
          200: "#A2DBCB",
          300: "#73C9B1",
          400: "#45B797",
          500: "#155E4B",
          600: "#124F3F",
          700: "#0F4033",
          800: "#0B3127",
          900: "#07221B",
        },
        secondary: {
          DEFAULT: "#49617A",
          50: "#EEF1F5",
          100: "#D5DCE7",
          200: "#ABB9CF",
          300: "#8196B7",
          400: "#57739F",
          500: "#49617A",
          600: "#3D5267",
          700: "#314354",
          800: "#253441",
          900: "#19252E",
        },
        accent: {
          DEFAULT: "#D4AF37",
          50: "#FDF9EC",
          100: "#FAF1C8",
          200: "#F5E391",
          300: "#EFD55A",
          400: "#E9C723",
          500: "#D4AF37",
          600: "#B8952C",
          700: "#9C7B21",
          800: "#806116",
          900: "#64470B",
        },
        background: "#F7F8FA",
        surface: "#FFFFFF",
        border: "#E5E7EB",
        "text-primary": "#1F2937",
        "text-secondary": "#6B7280",
        success: {
          DEFAULT: "#16A34A",
          50: "#F0FDF4",
          100: "#DCFCE7",
          500: "#16A34A",
          600: "#15803D",
        },
        warning: {
          DEFAULT: "#F59E0B",
          50: "#FFFBEB",
          100: "#FEF3C7",
          500: "#F59E0B",
          600: "#D97706",
        },
        danger: {
          DEFAULT: "#DC2626",
          50: "#FEF2F2",
          100: "#FEE2E2",
          500: "#DC2626",
          600: "#B91C1C",
        },
      },
      borderRadius: {
        "2xl": "18px",
        xl: "14px",
        lg: "10px",
        md: "8px",
        sm: "6px",
      },
      boxShadow: {
        card: "0 1px 3px 0 rgba(0,0,0,0.06), 0 1px 2px -1px rgba(0,0,0,0.04)",
        "card-hover":
          "0 4px 12px 0 rgba(0,0,0,0.08), 0 2px 4px -2px rgba(0,0,0,0.04)",
        modal:
          "0 20px 60px -10px rgba(0,0,0,0.15), 0 8px 20px -6px rgba(0,0,0,0.08)",
        sidebar:
          "1px 0 0 0 #E5E7EB",
        topbar:
          "0 1px 0 0 #E5E7EB",
        input:
          "0 0 0 3px rgba(21,94,75,0.12)",
        sm: "0 1px 2px 0 rgba(0,0,0,0.05)",
        md: "0 4px 6px -1px rgba(0,0,0,0.06), 0 2px 4px -2px rgba(0,0,0,0.04)",
        lg: "0 10px 15px -3px rgba(0,0,0,0.07), 0 4px 6px -4px rgba(0,0,0,0.04)",
      },
      transitionDuration: {
        fast: "150ms",
        normal: "200ms",
      },
      animation: {
        "fade-in": "fadeIn 200ms ease-out",
        "slide-in-left": "slideInLeft 200ms ease-out",
        "slide-up": "slideUp 200ms ease-out",
        "scale-in": "scaleIn 150ms ease-out",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideInLeft: {
          "0%": { opacity: "0", transform: "translateX(-8px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        scaleIn: {
          "0%": { opacity: "0", transform: "scale(0.96)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
      },
    },
  },
  plugins: [],
};
export default config;
