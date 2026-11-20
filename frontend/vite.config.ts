/// <reference types="vitest/config" />
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  server: {
    // En développement, Vite relaie /api vers l'API FastAPI : le navigateur ne voit
    // qu'une seule origine, comme en production derrière Caddy.
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
  test: {
    environment: 'jsdom', // simule un navigateur (DOM) dans Node
    setupFiles: ['./src/tests/configuration.ts'],
  },
})
