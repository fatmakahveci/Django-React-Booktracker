# Django React Book Tracker

A personal reading tracker built with Django REST Framework and React. Add books to your shelf, separate finished and unfinished reads, and update your reading progress through a browser interface.

[![Backend quality](https://github.com/fatmakahveci/Django-React-Booktracker/actions/workflows/backend.yml/badge.svg)](https://github.com/fatmakahveci/Django-React-Booktracker/actions/workflows/backend.yml)
[![Frontend quality](https://github.com/fatmakahveci/Django-React-Booktracker/actions/workflows/frontend.yml/badge.svg)](https://github.com/fatmakahveci/Django-React-Booktracker/actions/workflows/frontend.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE.md)

## Demo

![Book Tracker demo: add a book, mark it as finished, and organize finished and unfinished shelves.](docs/demo/booktracker-demo.gif)

Captured from the local application with sample data: add a book, move it to the finished shelf, and add another book to the reading list.

[View the bookshelf screenshot](docs/demo/bookshelf.png) · [Run the app locally](#local-setup)

## Features

- Register an account and sign in with email and password.
- Add books with a title, author, publication year, and reading status.
- Browse finished and unfinished shelves, move books between them, and delete entries.
- Edit a book’s title, author, and publication year from either shelf.
- Retry failed operations with visible error messages and preserved form input.
- Access a REST API for creating, retrieving, updating, and deleting books.
- Keep each user's books private through server-side ownership checks.
- Refresh expired access tokens automatically and persist rotated refresh tokens.

## Technology

| Layer | Tools |
| --- | --- |
| Backend | Python 3.12–3.14, Django 6.1.1, Django REST Framework 3.18.1 |
| Authentication | Simple JWT 5.5.1, refresh-token rotation, blacklisting, password-change revocation |
| Database | SQLite |
| Frontend | React 19.3, JavaScript, Vite 8.3, Axios 1.20 |
| Interface | Bootstrap, React Bootstrap, Font Awesome |
| Testing | Django test runner, Vitest 5, jsdom 30, Playwright 1.63 |
| CI | GitHub Actions |

Backend versions are pinned in [requirements.txt](requirements.txt). Frontend dependencies and scripts are defined in [frontend/package.json](frontend/package.json), with resolved versions in [frontend/package-lock.json](frontend/package-lock.json). The Vite configuration uses Oxc/Rolldown to support the existing JSX components stored in `.js` files.

## Local setup

The commands below use a macOS/Linux shell. Use Python 3.12, 3.13, or 3.14, and Node.js 22.22.2+, 24.15.0+, or 26+ with npm. CI tests the backend on all three Python versions and the frontend on Node.js 22, 24, and 26. Node.js 20 is no longer supported by the test tooling.

### 1. Clone the repository

```bash
git clone https://github.com/fatmakahveci/Django-React-Booktracker.git
cd Django-React-Booktracker
```

### 2. Start the API

From the repository root:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

export DJANGO_DEBUG=true
export DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(64))')"
export DJANGO_DB_PATH="$PWD/local.sqlite3"

python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

Substitute `python3.12` or `python3.14` if needed. The commands create a separate local database and leave any existing `db.sqlite3` untouched. Re-export the environment variables when opening a new backend shell; Django does not load `.env` files automatically. Keep the same local signing key between sessions if you want existing tokens to remain valid.

### 3. Start the frontend

In a second terminal, from the repository root:

```bash
cd frontend
npm ci --strict-peer-deps --engine-strict
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

Open **http://127.0.0.1:5173**, register an account, sign in, and open your books page. The API is available at **http://127.0.0.1:8000**. Install frontend dependencies inside `frontend/`.

Registration also enforces Django’s configured password validators, including similarity and common-password checks. Registration passwords must contain 8–24 characters, including an uppercase letter, a lowercase letter, a digit, and at least one of `! @ # $ % .`.

## Using the app

1. Register and sign in with your email address.
2. Add a title, author, and publication year. Select **Finished?** if you have already read the book.
3. Use **Finish** or **Unfinish** to move a book between shelves.
4. Select **Edit** on either shelf to update its details, then **Save changes** or **Cancel**.
5. Use **Delete** to remove an entry.

Failed saves retain your input, and failed updates or deletions leave the shelf unchanged. If the bookshelf fails to load, use **Retry loading books**. Buttons are disabled while a book operation is pending to prevent overlapping submissions.

## Configuration

| Variable | Purpose / default |
| --- | --- |
| `DJANGO_SECRET_KEY` | Required: a unique random value of at least 50 characters; cannot start with `django-insecure-`. |
| `DJANGO_DEBUG` | Defaults to `false`. Set to `true` for local development. |
| `DJANGO_DB_PATH` | SQLite path; defaults to the repository's `db.sqlite3`. Use `local.sqlite3` for development. |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hosts. In debug mode, defaults to `localhost,127.0.0.1`; otherwise empty. |
| `DJANGO_CORS_ALLOWED_ORIGINS` | Comma-separated origins. In debug mode, permits localhost and 127.0.0.1 on port 5173; otherwise empty. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Comma-separated trusted origins; empty by default. |
| `DJANGO_HSTS_INCLUDE_SUBDOMAINS` | Defaults to `false`. Enable only if every subdomain supports HTTPS. |
| `DJANGO_HSTS_PRELOAD` | Defaults to `false`. Enable only when the domain meets HSTS preload requirements. |
| `VITE_API_URL` | Frontend API base URL; defaults to `http://localhost:8000/`. Set before starting Vite or building. |

For example, build the frontend for a separately hosted API:

```bash
cd frontend
VITE_API_URL=https://api.example.com/ npm run build
```

The build is written to `frontend/dist/`. The API must permit the deployed frontend origin. Configure the frontend host to serve `index.html` for application routes such as `/login/`, `/register/`, and `/books/`.

## REST API

All paths are relative to the API host. Book endpoints require an `Authorization: Bearer <access-token>` header.

| Method | Endpoint | Action |
| --- | --- | --- |
| `POST` | `/register/` | Register with `email`, `user_name`, and `password`. |
| `POST` | `/token/` | Sign in with `email` and `password`; receive access and refresh tokens. |
| `POST` | `/token/refresh/` | Send `refresh`; receive a new token pair. |
| `GET`, `POST` | `/books/` | List your books or create a book. |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/books/<id>/` | Retrieve, update, or delete one of your books. |
| `GET` | `/books/finished/` | List your finished books. |
| `GET` | `/books/unfinished/` | List your unfinished books. |

Example book creation body:

```json
{
  "title": "The Left Hand of Darkness",
  "author": "Ursula K. Le Guin",
  "year": 1969,
  "finished": false
}
```

The server assigns the authenticated user as the owner; client-provided `user` values are read-only. Books are returned in descending publication-year order.

### Authentication behavior

Access tokens expire after five minutes and refresh tokens after seven days. Refreshing rotates the refresh token and blacklists the old one, so API clients must save the returned token pair. The React client handles this automatically.

Changing an account’s password invalidates its existing access and refresh tokens. Refresh attempts for deleted or inactive accounts are rejected. Deploying these password-revocation checks also invalidates previously issued tokens without the revocation claim; users must sign in again.

The client stores tokens in browser local storage. Logout clears local credentials; it does not revoke every previously issued token on the server. See the [security policy](SECURITY.md) for reporting vulnerabilities and deployment considerations.

## Tests and quality checks

### Backend

From the repository root, with the virtual environment active and the development environment variables set:

```bash
python -m pip check
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

Backend tests cover account registration and password-policy enforcement, authentication, token rotation, password-change revocation, deleted-account refresh rejection, book operations, ownership isolation, and Django compatibility.

### Frontend

```bash
cd frontend
npm test
npm run build
npm ls --all
npm audit
```

### Browser integration

From the repository root, after installing both backend and frontend dependencies:

```bash
source .venv/bin/activate
cd frontend
npx playwright install chromium
npx playwright test
```

Playwright starts a Django API on port 8191 and a Vite server on port 5191 with a temporary SQLite database. Keep those ports available. The browser flow covers registration, login, book creation, token rotation, rejection of the old refresh token, persistence after reload, and logout. Additional browser tests cover editing and cancelling changes, preserving reading status, failed mutations, and retrying failed shelf loads.

GitHub Actions runs backend checks on Python 3.12, 3.13, and 3.14. On Node.js 22, 24, and 26 it verifies strict dependency installation, unit tests, the production build, npm audits, and browser integration with a real Django API. Both the root and frontend npm manifests are audited.

## Deployment notes

Production settings disable debug mode and enable HTTPS redirects, secure session/CSRF cookies, and one-year HSTS. Configure TLS, allowed hosts, frontend origins, and a trusted reverse proxy for your hosting environment. Only trust forwarded headers from a proxy you control.

Provide a persistent signing key through your deployment's secret store. Never reuse the historical development key from repository history. If that key was used in a deployment, rotate it and invalidate existing sessions and JWTs.

SQLite databases are local data and are excluded from version control. Earlier repository history contains a development database; removing it from the current tree does not erase historical copies. If its accounts were used outside local testing, change the affected passwords and invalidate their sessions.

Back up existing databases and reconcile migration history before adopting the initial migrations. Do not blindly use `--fake` or overwrite existing data.

Run the deployment check with your actual production environment:

```bash
python manage.py check --deploy
```

HSTS subdomain and preload warnings require deployment-specific decisions; only enable those settings when appropriate for your domain. Django's development server and the Vite development server are for local use.

## Repository structure

```text
Django-React-Booktracker/
├── accounts/          # Custom user model, registration, JWT endpoints, tests
├── backend/           # Django settings and root URL configuration
├── books/             # Book model, serializers, API, migrations, tests
├── frontend/
│   ├── src/           # React pages, components, authentication, API client
│   ├── e2e/           # Playwright browser integration tests
│   ├── vite.config.mjs # Vite, JSX transformation, and Vitest configuration
│   └── package.json   # Frontend dependencies and scripts
├── .github/           # CI workflows and contributor policies
├── docs/demo/         # Recorded GIF and bookshelf screenshot
├── SECURITY.md        # Security policy and private reporting instructions
├── manage.py          # Django management entry point
└── requirements.txt   # Backend dependencies
```

## Contributing and license

See the [contributing guide](.github/CONTRIBUTING.md) for development guidelines, the [security policy](SECURITY.md) for vulnerability reporting, and the [changelog](CHANGELOG.md) for project history.

Licensed under the [Apache License 2.0](LICENSE.md).
