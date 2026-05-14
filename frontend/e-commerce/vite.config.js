import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],

  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      include: ['src/**/*.{js,jsx}'],
      exclude: [
        'src/main.jsx',
        'src/test/**',
        'src/**/*.test.{js,jsx}',
        'src/assets/**',
        // Pages statiques sans logique métier → couvertes par les tests E2E (ÉTAPE 5)
        'src/App.jsx',
        'src/pages/about.jsx',
        'src/pages/contact.jsx',
        'src/pages/legal.jsx',
        'src/pages/notfound.jsx',
        'src/pages/productdetail.jsx',
        'src/components/scrollToTop.jsx',
      ],
      thresholds: {
        lines: 70,
        functions: 64,
        branches: 60,
      },
    },
  },
})
