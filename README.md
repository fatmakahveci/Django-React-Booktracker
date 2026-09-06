# Django React Book Tracker

[![Django](https://img.shields.io/badge/Django-REST-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-TypeScript-149ECA?logo=react&logoColor=white)](https://react.dev/)
[![Last commit](https://img.shields.io/github/last-commit/fatmakahveci/Django-React-Booktracker)](https://github.com/fatmakahveci/Django-React-Booktracker/commits/main)
[![License](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE.md)

A full-stack reading tracker with a Django REST API, JWT authentication, and a Vite-powered React client.

## Highlights

- Register and authenticate users with JWT access and refresh tokens
- Create, update, delete, and organize books
- Filter finished and unfinished reading entries
- React context for authentication and Axios-based API access
- Frontend tests with Vitest and Testing Library

## Technology

- Python
- Django REST Framework
- Simple JWT
- React
- Vite
- Bootstrap
- SQLite

## Getting Started

### Prerequisites

- Python 3.12, 3.13, or 3.14 (Django 6.1 does not support Python 3.11)
- Node.js 20 or newer
- pip and npm

When upgrading an existing checkout, recreate the virtual environment with a
supported Python version before reinstalling `requirements.txt`. Back up your
SQLite database before running migrations. Backend CI verifies Python 3.12–3.14;
browser integration tests use Python 3.13.

### Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export DJANGO_DEBUG=true
export DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(64))')"
# Use a new local database; the historical tracked database is left untouched.
export DJANGO_DB_PATH="$PWD/local.sqlite3"
python manage.py migrate
python manage.py runserver

# In a second terminal
cd frontend
npm ci
npm run dev
```

The API runs on http://127.0.0.1:8000 and the Vite client reports its local URL in the terminal.

### Security and deployment

Debug mode is off by default. Set a unique `DJANGO_SECRET_KEY` (at least 50 random
characters) through your deployment's secret store, and set `DJANGO_ALLOWED_HOSTS`
to a comma-separated list of your hostnames. Set `DJANGO_CORS_ALLOWED_ORIGINS` and
`DJANGO_CSRF_TRUSTED_ORIGINS` to explicit HTTPS origins where needed; production
defaults allow no cross-origin clients. Development CORS permits Vite on port 5173.
Environment variables are read directly; `.env` files are not loaded automatically.

Production enables HTTPS redirects, secure session/CSRF cookies, and one-year HSTS.
Configure TLS and a trusted reverse proxy before deploying. Do not blindly trust
forwarded headers from clients. Run `python manage.py check --deploy` with your
actual deployment configuration.
Only enable `DJANGO_HSTS_INCLUDE_SUBDOMAINS=true` when every subdomain supports
HTTPS, and `DJANGO_HSTS_PRELOAD=true` when your domain meets preload requirements.
The deployment checker intentionally warns until those deployment-specific choices
are made; CI checks an HTTPS-only example configuration.

The old committed development signing key must never be reused. If it was used
in a deployment, rotate that deployment's secret and invalidate existing sessions
and JWTs. No production secret rotation or database migration is performed by CI.
Back up existing databases and reconcile their migration history before adopting
the initial migrations; do not blindly apply `--fake` or overwrite existing data.

Books are scoped to the authenticated user for list, detail, update, and delete.
The server assigns ownership; client-provided `user` fields are read-only.
JWT refresh tokens expire after seven days and are blacklisted after rotation.
Clients must store the newly returned refresh token after each refresh.

These defaults follow the [Django deployment checklist](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/)
and [DRF's user-scoped queryset pattern](https://www.django-rest-framework.org/api-guide/generic-views/#get_querysetself).

## Quality Checks

Browser integration tests start the real Django API with a fresh temporary SQLite
database. They cover registration, login, book creation, token rotation (including
rejection of the old refresh token), persistence after reload, and logout.
Install the Python requirements and run `npx playwright install chromium`, then
`npx playwright test` from `frontend/`. No production database or secret is used.
Set `VITE_API_URL` at build time to configure a deployment's API URL; it defaults
to the local Django server. Refresh tokens are persisted after rotation.

```bash
python manage.py check
python manage.py test
cd frontend && npm test
cd frontend && npm run build
```

## Repository Structure

- `accounts` — custom user model and JWT endpoints
- `books` — book model, serializer, and API view set
- `backend` — Django project configuration
- `frontend` — React application and tests

## Project Resources

- [Changelog](CHANGELOG.md)
- [Contributing guide](.github/CONTRIBUTING.md)
- [Security policy](.github/SECURITY.md)
- [License](LICENSE.md)
