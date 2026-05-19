const { join } = require('path');

module.exports = {
  content: [
    join(__dirname, '../../templates/**/*.html'),
    join(__dirname, '../../core/templates/**/*.html'),
    join(__dirname, '../../static/**/*.js'),
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          900: '#050d1a',
          800: '#0a1628',
          700: '#0f2040',
          600: '#1a3060',
        },
        sky: {
          400: '#38bdf8',
          500: '#00d4ff',
          600: '#0ea5e9',
        },
        gold: '#f59e0b',
        long: '#22c55e',
        short: '#ef4444',
      },
      fontFamily: {
        inter: ['Inter', 'sans-serif'],
        space: ['Space Grotesk', 'sans-serif'],
      },
      animation: {
        'glow': 'glow 2s ease-in-out infinite',
        'ticker': 'tickerScroll 30s linear infinite',
      },
      keyframes: {
        glow: {
          '0%, 100%': { boxShadow: '0 0 5px #ef4444, 0 0 10px #ef4444, 0 0 20px #ef4444' },
          '50%': { boxShadow: '0 0 10px #ef4444, 0 0 20px #ef4444, 0 0 40px #ef4444' },
        },
        tickerScroll: {
          '0%': { transform: 'translateX(0)' },
          '100%': { transform: 'translateX(-50%)' },
        },
      },
    },
  },
  plugins: [],
};
