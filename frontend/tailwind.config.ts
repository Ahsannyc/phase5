import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#22d3ee', // cyan-400
          glow: 'rgba(34, 211, 238, 0.3)',
        },
        secondary: '#a855f7',
        success: '#34d399',
        danger: '#f43f5e',
      },
      boxShadow: {
        glow: '0 0 20px rgba(34, 211, 238, 0.2)',
        'glow-lg': '0 0 30px rgba(34, 211, 238, 0.4)',
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
export default config