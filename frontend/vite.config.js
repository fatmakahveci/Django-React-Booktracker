import { defineConfig, transformWithEsbuild } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  optimizeDeps: { esbuildOptions: { loader: { ".js": "jsx" } } },
  server: {
    proxy: {
      "/api": {
        target: process.env.E2E_BACKEND_URL || "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
  plugins: [
    {
      name: "treat-js-files-as-jsx",
      enforce: "pre",
      async transform(code, id) {
        if (/\/src\/.*\.js$/.test(id)) {
          return transformWithEsbuild(code, id, { loader: "jsx", jsx: "automatic" });
        }
      },
    },
    react(),
  ],
  test: {
    exclude: ["e2e/**", "node_modules/**"],
    environment: "jsdom",
    globals: true,
  },
});
