/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,ts,scss}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Primária — Azul Hospitalar GuardIA
        primary: {
          50:  '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#2563EB',
          600: '#1d4ed8',
          700: '#1e40af',
          800: '#1e3a8a',
          900: '#172554',
        },
        // Secundária — Rosa/Fúcsia
        secondary: {
          400: '#f472b6',
          500: '#EC4899',
          600: '#DB2777',
        },
        // Superfícies dark mode
        bg:        '#0B0F19',
        surface:   '#1E293B',
        surface2:  '#334155',
        // Status
        success:   '#16A34A',
        warning:   '#EAB308',
        danger: {
          400: '#f87171',
          500: '#DC2626',
          600: '#b91c1c',
        },
        // IRA levels
        'ira-baixo':    '#16A34A',
        'ira-moderado': '#EAB308',
        'ira-critico':  '#DC2626',
        // Text
        'text-muted':  '#94A3B8',
        'text-subtle': '#64748B',
      },
      fontFamily: {
        sans: ['Outfit', 'Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'glow-primary': '0 0 20px rgba(37, 99, 235, 0.3)',
        'glow-danger':  '0 0 20px rgba(220, 38, 38, 0.3)',
        'glow-success': '0 0 20px rgba(22, 163, 74, 0.3)',
        'card':         '0 4px 24px rgba(0, 0, 0, 0.4)',
        'card-hover':   '0 8px 32px rgba(0, 0, 0, 0.5)',
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      animation: {
        'fade-in':       'fadeIn 0.3s ease-out',
        'slide-up':      'slideUp 0.4s ease-out',
        'pulse-slow':    'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow':     'spin 3s linear infinite',
        'processing':    'processingPulse 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%':   { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%':   { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        processingPulse: {
          '0%, 100%': { opacity: '1' },
          '50%':      { opacity: '0.4' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
};
