/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        bis: {
          blue: '#1E3A8A',
          gold: '#D97706',
          dark: '#0F172A',
        }
      }
    },
  },
  plugins: [],
}
