import { defineConfig, transformWithOxc } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  optimizeDeps: { rolldownOptions: { moduleTypes: { ".js": "jsx" } } },
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
          // Existing React components use .js filenames; parse their contents as JSX.
          return transformWithOxc(code, id.replace(/\.js$/, ".jsx"), { jsx: { runtime: "automatic" } });
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
