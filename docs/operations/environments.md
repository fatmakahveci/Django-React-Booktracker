# Environments and production boundary

`DJANGO_ENV=production` requires PostgreSQL, Redis, an HTTPS public URL, explicit allowed hosts, and debug disabled. Development can use SQLite and process-local cache. `DJANGO_ENV=test` uses the in-memory email backend for test assertions.

Run `python scripts/init-local.py`, then `docker compose up -d postgres redis mailpit`, `docker compose run --rm api python manage.py migrate`, and `docker compose up --build -d api web`. Open http://localhost:8080 and read local emails at http://localhost:8025. No application or database port is published beyond loopback.

For a production host with a trusted HTTPS gateway, use `docker compose -f compose.yaml -f deploy/compose.production.yaml`. Set real SMTP credentials, `DJANGO_PUBLIC_URL`, allowed hosts (including localhost for health checks), and CSRF trusted origins in the deployment secret store. Mailpit is disabled by the production overlay. The loopback web listener must only be accessible through the gateway. Pass real client IPs from the trusted gateway through a reviewed Nginx `real_ip` configuration; do not trust forwarded IPs from arbitrary networks.

Redis admission uses an atomic sliding window shared by API workers. Admin and API sign-in share `DJANGO_LOGIN_RATE` (default `30/min`); browser and bearer refresh share `DJANGO_REFRESH_RATE` (default `60/min`). Redis failures reject these requests with 503 instead of silently disabling limits. Nginx applies an additional authentication request limit. The development fallback is process-local and is not suitable for a distributed deployment.

Cookies are HttpOnly, SameSite=Lax and Secure outside debug. Browser writes, login, refresh and logout require CSRF. Serve frontend and API from one origin (`/api/`) in production. Bearer endpoints are retained for non-browser clients; the web app never stores JWTs in local/session storage.

## Self-hosted HTTPS option

A portable Caddy gateway is provided for hosts without an existing TLS ingress:

```sh
# In the secret environment: SITE_ADDRESS=books.example.com, ACME_EMAIL=operator@example.com
# Set DJANGO_PUBLIC_URL=https://books.example.com and matching hosts/CSRF origins in .env.
docker compose -f compose.yaml -f deploy/compose.production.yaml -f deploy/compose.tls.yaml up -d
```

Point DNS at the host and allow inbound 80/443. The dedicated gateway has a fixed private address; Nginx trusts forwarding headers only from that address. Adapt the private subnet if it conflicts with the host network. For a different ingress, replace the trusted-gateway configuration with the exact ingress addresses after reviewing its header sanitization. Never trust `0.0.0.0/0`.

For local development, Mailpit catches all mail without contacting external recipients. In production, configure `DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`, host, port, `DJANGO_EMAIL_USER`, `DJANGO_EMAIL_PASSWORD`, TLS and a verified sender. SMTP delivery, DNS, certificate issuance and public hosting must be tested when a provider/domain is chosen. They are not prerequisites for the tested local Docker environment.

Python settings are split into base, test and production modules. Production rejects debug mode, missing database/cache configuration, non-HTTPS public URLs, and console/file/in-memory/dummy email backends. Configure the real email backend before upgrading a production service. Static administration assets and Swagger UI assets are self-hosted; no CDN is required for API documentation. Cookies and CSRF follow [Django's documented AJAX pattern](https://docs.djangoproject.com/en/6.0/howto/csrf/).
