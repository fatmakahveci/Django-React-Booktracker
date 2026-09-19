# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
where applicable.

## [Unreleased]

### Security

- Revalidate account writes under a row lock to prevent stale requests from restoring revoked credentials or deleted accounts.
- Serialize token issuance and rotation with account deletion; logout no longer recreates purged token records.
- Enforce email verification for existing access and refresh tokens as well as new sign-ins.
- Rate-limit admin sign-in and browser/bearer refresh requests, including fail-closed handling of Redis outages.
- Reject development email backends in production to avoid exposing verification/reset links in logs or discarding mail.

### Changed

- Upgrade to React 19.3, Vite 8.3, Vitest 5, jsdom 30, and Playwright 1.63.
- Consolidate Django settings and use `local.sqlite3` as the default development database.
- Calculate reading totals in one query and stream backup checksums with bounded memory.
- Extend frontend lint and formatting checks to browser tests and development scripts.
- Migrate JSX transformation and dependency optimization to Vite’s Oxc/Rolldown APIs.
- Validate frontend compatibility on Node.js 22, 24, and 26 and declare supported runtime versions.

- Upgraded Django to 6.1.1 and aligned the documented Python requirement with 3.12–3.14.
- Validate backend checks, migrations, deployment settings, and tests on all three supported Python versions.

### Added

- Per-IP login and registration limits with Retry-After feedback.
- Logout endpoint that blacklists the current refresh token; client waits for pending rotation and reports unconfirmed server logout.
- Regression coverage for throttling, spoofed forwarding headers, logout revocation, and logout failure recovery.

- Edit book titles, authors, and publication years from either reading shelf.
- Show actionable book-operation errors and retry failed shelf loading.
- Cover editing, cancellation, persistence, and failed operations with browser tests.

- Regression coverage for pre-upgrade password hashes and custom-user admin pages.
- Added an initial changelog to track future project changes.

### Fixed

- Use Django authentication forms for admin account creation, password changes and read-only password hashes.
- Apply consistent username validation to registration, profile editing and admin forms.
- Consume verification/reset links once under concurrent requests and avoid issuing tokens for unverified accounts.
- Reject malformed ISBN digits without server errors and clear finish dates before validating a reopened book.
- Recover unavailable library pages after edits and clear stale session errors after successful login.
- Exclude local email files and database dumps from Docker images; isolate browser tests from inherited deployment settings.
- Validate the public URL before stopping services during a release and bound the final health-check timeout.

- Revoke access and refresh tokens after password changes and reject refresh attempts for deleted accounts.
- Apply configured Django password validators during registration.
- Stop tracking the local SQLite database in source control.

- Preserve form input after failed saves and update shelves only after successful API requests.
- Prevent overlapping book mutations while a request is pending.

<!--
When preparing a release, move relevant entries from Unreleased into a dated
version section. Use Added, Changed, Deprecated, Removed, Fixed, and Security
headings as appropriate.
-->
