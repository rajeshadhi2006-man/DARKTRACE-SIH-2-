/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#05070A',
        primary: '#00FF88',
        secondary: '#00D9FF',
        warning: '#FFB020',
        danger: '#FF4D6D',
        card: 'rgba(10, 15, 26, 0.75)',
        'card-border': 'rgba(0, 217, 255, 0.15)',
        'card-border-glow': 'rgba(0, 255, 136, 0.35)',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      boxShadow: {
        'glow-primary': '0 0 20px rgba(0, 255, 136, 0.25)',
        'glow-secondary': '0 0 20px rgba(0, 217, 255, 0.25)',
      }
    },
  },
  plugins: [],
}
