import { defineConfig } from "@playwright/test";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const database = join(mkdtempSync(join(tmpdir(), "booktracker-e2e-")), "test.sqlite3");
export default defineConfig({
  testDir: "./e2e",
  workers: 1,
  use: { baseURL: "http://127.0.0.1:5191", trace: "retain-on-failure" },
  webServer: [
    {
      command: "python manage.py migrate --noinput && python manage.py runserver 127.0.0.1:8191 --noreload",
      cwd: "..",
      url: "http://127.0.0.1:8191/",
      env: {
        DJANGO_DB_PATH: database,
        DJANGO_DEBUG: "true",
        DJANGO_SECRET_KEY: "isolated-e2e-only-not-a-deployment-secret-0123456789-abcdefgh",
        DJANGO_ALLOWED_HOSTS: "127.0.0.1,localhost",
      },
      reuseExistingServer: false,
    },
    {
      command: "npm run dev -- --host 127.0.0.1 --port 5191 --strictPort",
      url: "http://127.0.0.1:5191",
      env: { VITE_API_URL: "/api/", E2E_BACKEND_URL: "http://127.0.0.1:8191" },
      reuseExistingServer: false,
    },
  ],
});
