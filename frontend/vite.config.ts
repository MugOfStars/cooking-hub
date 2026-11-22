import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Forward /api/* to FastAPI so the browser sees a single origin: no CORS setup
    // needed in development, matching a production setup behind one domain.
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
