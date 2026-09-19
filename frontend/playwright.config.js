import { defineConfig, devices } from "@playwright/test";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
const temporary =
  process.env.E2E_ROOT || mkdtempSync(join(tmpdir(), "booktracker-e2e-"));
process.env.E2E_ROOT = temporary;
process.env.E2E_MAIL_DIR = join(temporary, "mail");
export default defineConfig({
  testDir: "./e2e",
  workers: 1,
  timeout: 30000,
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"] } },
    {
      name: "mobile",
      use: { ...devices["iPhone 13"], defaultBrowserType: "chromium" },
    },
  ],
  use: { baseURL: "http://127.0.0.1:5191", trace: "retain-on-failure" },
  webServer: [
    {
      command:
        "python manage.py migrate --noinput && python manage.py runserver 127.0.0.1:8191 --noreload",
      cwd: "..",
      url: "http://127.0.0.1:8191/health/live/",
      env: {
        // Never inherit deployment databases, mail settings or telemetry in browser tests.
        DATABASE_URL: "",
        REDIS_URL: "",
        SENTRY_DSN: "",
        DJANGO_ENV: "development",
        DJANGO_SCRIPT_NAME: "",
        DJANGO_TRUST_PROXY: "false",
        DJANGO_REQUIRE_EMAIL_VERIFICATION: "true",
        DJANGO_DB_PATH: join(temporary, "test.sqlite3"),
        DJANGO_DEBUG: "true",
        DJANGO_SECRET_KEY:
          "isolated-e2e-only-not-a-deployment-secret-0123456789-abcdefgh",
        DJANGO_ALLOWED_HOSTS: "127.0.0.1,localhost",
        DJANGO_CSRF_TRUSTED_ORIGINS: "http://127.0.0.1:5191",
        DJANGO_PUBLIC_URL: "http://127.0.0.1:5191",
        DJANGO_EMAIL_BACKEND:
          "django.core.mail.backends.filebased.EmailBackend",
        DJANGO_EMAIL_FILE_PATH: process.env.E2E_MAIL_DIR,
        DJANGO_LOGIN_RATE: "1000/min",
        DJANGO_REGISTRATION_RATE: "1000/hour",
        DJANGO_EMAIL_RATE: "1000/hour",
      },
      reuseExistingServer: false,
    },
    {
      command:
        "npm run build && npx vite preview --host 127.0.0.1 --port 5191 --strictPort",
      url: "http://127.0.0.1:5191",
      env: { VITE_API_URL: "/api/", E2E_BACKEND_URL: "http://127.0.0.1:8191" },
      reuseExistingServer: false,
    },
  ],
});
