/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'game-dark': '#1a1a2e',
        'game-darker': '#16213e',
        'game-accent': '#00d4ff',
        'game-purple': '#7000ff',
      },
      animation: {
        'fadeIn': 'fadeIn 0.3s ease-out',
        'slideInRight': 'slideInRight 0.3s ease-out',
      },
    },
  },
  plugins: [],
}
