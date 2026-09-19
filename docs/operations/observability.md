# Operations and observability

- `GET /api/health/live/` checks process availability; `GET /api/health/ready/` checks PostgreSQL and Redis. Dependency failure returns 503 without internal addresses. Health routes are unauthenticated and contain no user data.
- Every API response carries a generated `X-Request-ID`. Application JSON logs contain method, route template, status and duration in milliseconds. They omit request bodies, query strings, cookies and authorization headers. Nginx logs use `$uri`, not `$request_uri`, so reset and verification query tokens stay out of access logs.
- Aggregate request duration and status by route in the eventual log platform. Start with alerts for three consecutive failed readiness probes, 5xx over 1% for five minutes, sustained authentication 503s, p95 API latency over one second, PostgreSQL disk under 20%, or Redis memory over 80%. Tune these against measured usage.
- `SENTRY_DSN` optionally enables exception reporting; `APP_VERSION` and `DJANGO_ENV` label releases. User identity, request data, cookies, headers, URLs, stack local variables, exception messages and breadcrumbs are stripped by `backend/observability.py`. Tracing is disabled; request timing remains in local JSON logs. No external error-reporting account is configured or claimed as tested.
- Redis uses atomic admission across workers and fails closed for authentication on outages. The local memory fallback is development only. Redis memory uses `noeviction`; monitor capacity to prevent authentication unavailability.
- Run `python manage.py flushexpiredtokens` daily from the scheduler chosen for deployment. It removes expired JWT bookkeeping, not account or book data.
- `docker compose logs --tail 100 api web` supports local diagnosis. Treat logs and Mailpit storage as private; production disables Mailpit.

If readiness fails, check dependency health before restarting the API. If only login fails, inspect Redis health, trusted gateway configuration and SMTP status. Use the response request ID when correlating a failure. Follow [recovery.md](recovery.md) for restores and rollback.
