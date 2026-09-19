# Professionalization: 20-item delivery ledger

Scope agreed on 2026-09-19: prepare portable hosting/SMTP configuration; assess historical SQLite exposure without rewriting Git history. Each item below records implementation and reviewable evidence. Public hosting, external SMTP delivery and history erasure are not claimed.

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Historical secrets/data assessment | Complete within report-only scope | [Assessment](security/history-assessment.md): 4 accounts, 6 books, no Django sessions; old commit/tag/archive exposure identified; no force-push |
| 2 | Production environments, HTTPS, server/proxy | Implemented | Split settings, Gunicorn, Nginx, optional Caddy; [environment guide](operations/environments.md); production Django checks |
| 3 | PostgreSQL and data migration | Implemented and tested | Compose PostgreSQL 18; 49-test PostgreSQL run; schema migrations and [migration runbook](operations/recovery.md) |
| 4 | Shared cache and proxy rate limits | Implemented and tested | Redis atomic sliding window, fail-closed outage behavior, trusted gateway headers; concurrency admits exactly the configured number |
| 5 | HttpOnly authentication and CSRF | Implemented and tested | Browser cookie flow, Secure flags in production, no JWT browser storage, CSRF enforced on login/refresh/logout/writes |
| 6 | Password reset | Implemented and tested | Generic request responses, one-hour single-use links, password validation, prior-token invalidation; backend and browser email tests |
| 7 | Email verification | Implemented and tested | Verification required before login, resend flow and explicit confirmation; local mailbox integration |
| 8 | Profile and account security | Implemented and tested | Profile, password change, all-device revoke, password-confirmed cascading deletion |
| 9 | Responsive interface | Implemented and reviewed | Reading-room design, desktop/mobile [screenshots](demo), loading/empty/error states |
| 10 | Accessibility | Implemented and tested | Semantic labels, native dialogs, focus restore, skip link, live regions; axe WCAG A/AA checks on desktop/mobile; no detected violations in tested pages |
| 11 | Search, filter, ordering, pagination | Implemented and tested | Server-owned queries, stable ordering with null ratings last, 12-item pages and 100-item cap, URL state |
| 12 | Extended book records | Implemented and tested | ISBN checksums, HTTPS covers, notes, rating and reading dates; validation/ownership tests |
| 13 | OpenAPI, validation and error contract | Implemented and tested | [Schema](openapi.yaml) validates without warnings; self-hosted Swagger verified in Docker; typed client displays field errors |
| 14 | Routing and separation of responsibilities | Implemented | Router pages, auth provider, API client, shared dialog components; [architecture](ARCHITECTURE.md) |
| 15 | TypeScript | Implemented and checked | Strict application type checking; React 19/Router 7/Vite 8; TypeScript 6 matches ESLint peer support |
| 16 | Lint, format and unused code cleanup | Implemented and checked | Ruff, ESLint, Prettier; legacy JS/Babel, duplicate root dependencies and unused Bootstrap/Axios/JWT decoder removed |
| 17 | Expanded automated coverage | Implemented and tested | 49 backend tests, 3 API-client unit tests, 12 desktop/mobile browser cases against production assets; CI Python 3.12/13/14 and Node 22/24/26 |
| 18 | Health, structured logs and error reporting | Implemented and tested | Dependency readiness, request IDs and timings, sanitized logs, optional scrubbed Sentry; [operations guide](operations/observability.md) |
| 19 | Deployment, release, rollback and recovery | Implemented and rehearsed | Docker build/start/health, release workflow and script, guarded backup/restore; synthetic 1-account/8-book recovery verified |
| 20 | Demo, screenshots and project narrative | Updated | [README](../README.md), recorded GIF, desktop/mobile/welcome captures, architecture and operational documentation |

## Validation record

- PostgreSQL 18.6 + Redis: 49 backend tests passed, including competing refresh requests and atomic rate-limit admission.
- Frontend: strict TypeScript build, ESLint, formatting and 3 unit tests passed; 12 Playwright cases passed on desktop and mobile Chromium. Axe scans cover the landing page, populated library and book editor.
- Docker: API/web images built; PostgreSQL, Redis, Mailpit, API and web started; readiness returned 200. Interactive API docs rendered 28 operations without JavaScript errors.
- Backup/restore: generated private custom-format backup with SHA-256; restored to a fresh PostgreSQL database with matching counts. Original data was untouched.
- Security dependency checks: npm audit reported 0 vulnerabilities; pip-audit reported no known vulnerabilities in the resolved runtime requirements.
- Production settings: Django deployment checks pass with explicit HTTPS, allowed hosts and opted-in domain-wide HSTS settings. Operators must review HSTS for their own domain.

Automated tests and dependency scans do not prove absence of every vulnerability or full accessibility conformance. Public certificate issuance, a live SMTP provider and external monitoring remain deployment-time checks because no provider/domain has been selected.
