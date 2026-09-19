# Booktracker frontend

React 19 + TypeScript 6 + React Router 7, built by Vite 8. Node 22.22.2+, 24.15.0+, or 26 is required. TypeScript stays on 6.0.3 because the installed typescript-eslint release supports `<6.1.0`.

```sh
npm ci --strict-peer-deps --engine-strict
npm run dev
npm run lint
npm run format:check
npm test
npm run build
npx playwright install chromium
npm run test:e2e
```

The development server proxies `/api/` to localhost:8000. E2E tests create an isolated database and local file mailbox, and test the production build with desktop and mobile Chromium. Activate the Python environment before starting them. Never use a real account or live database for tests.

See the root [README](../README.md), [architecture](../docs/ARCHITECTURE.md), and [API schema](../docs/openapi.yaml). Application pages, shared dialogs, authentication state and network handling have separate directories under `src`. Auth cookies are not readable by JavaScript.
