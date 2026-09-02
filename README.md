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

- Python 3.11 or newer
- Node.js 20 or newer
- pip and npm

### Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install Django djangorestframework djangorestframework-simplejwt django-cors-headers
python manage.py migrate
python manage.py runserver

# In a second terminal
cd frontend
npm install
npm run dev
```

The API runs on http://127.0.0.1:8000 and the Vite client reports its local URL in the terminal.

## Quality Checks

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
