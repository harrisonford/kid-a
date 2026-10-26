import { svelte } from '@sveltejs/vite-plugin-svelte'
import { defineConfig } from 'vite'

// the build is served by ../server.py from ../static; `npm run dev` proxies the API to it
export default defineConfig({
  plugins: [svelte()],
  build: { outDir: '../static', emptyOutDir: true },
  server: { proxy: { '/api': 'http://127.0.0.1:8787' } },
})
