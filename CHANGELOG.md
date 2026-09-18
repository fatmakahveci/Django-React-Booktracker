# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
where applicable.

## [Unreleased]

### Changed

- Upgraded Django to 6.1.1 and aligned the documented Python requirement with 3.12–3.14.
- Validate backend checks, migrations, deployment settings, and tests on all three supported Python versions.

### Added

- Edit book titles, authors, and publication years from either reading shelf.
- Show actionable book-operation errors and retry failed shelf loading.
- Cover editing, cancellation, persistence, and failed operations with browser tests.

- Regression coverage for pre-upgrade password hashes and custom-user admin pages.
- Added an initial changelog to track future project changes.

### Fixed

- Preserve form input after failed saves and update shelves only after successful API requests.
- Prevent overlapping book mutations while a request is pending.

<!--
When preparing a release, move relevant entries from Unreleased into a dated
version section. Use Added, Changed, Deprecated, Removed, Fixed, and Security
headings as appropriate.
-->
