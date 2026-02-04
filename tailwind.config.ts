import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: [
          'Inter',
          'SF Pro Display',
          '-apple-system',
          'BlinkMacSystemFont',
          'sans-serif',
        ],
      },
      fontSize: {
        display: [
          'clamp(2.5rem, 5vw, 4rem)',
          { lineHeight: '1.1', letterSpacing: '-0.02em' },
        ],
        title: [
          'clamp(1.5rem, 3vw, 2rem)',
          { lineHeight: '1.2', letterSpacing: '-0.01em' },
        ],
        body: ['1.0625rem', { lineHeight: '1.6' }],
      },
      transitionTimingFunction: {
        apple: 'cubic-bezier(0.4, 0, 0.2, 1)',
        'apple-spring': 'cubic-bezier(0.34, 1.56, 0.64, 1)',
      },
      transitionDuration: {
        '400': '400ms',
        '600': '600ms',
      },
      keyframes: {
        'fade-up': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
      animation: {
        'fade-up': 'fade-up 600ms cubic-bezier(0.4, 0, 0.2, 1) forwards',
        'fade-in': 'fade-in 400ms cubic-bezier(0.4, 0, 0.2, 1) forwards',
      },
      colors: {
        surface: {
          DEFAULT: '#ffffff',
          dark: '#0a0a0a',
        },
        muted: {
          DEFAULT: '#6b7280',
          dark: '#9ca3af',
        },
      },
    },
  },
  plugins: [],
};

export default config;
