# Data migration, backup and recovery

## SQLite to PostgreSQL

Schedule a write freeze and take a private copy of the source first. Never import the historical Git database without establishing ownership of its records. The account migration intentionally leaves existing addresses unverified; owners use **Resend verification email** before their first sign-in.

For a reviewed local database, activate the Python environment, configure a signing key, and run:

```sh
umask 077
# Keep DATABASE_URL unset for this source export. Do not print the resulting fixture.
DJANGO_ENV=development DJANGO_DEBUG=true DJANGO_DB_PATH=/absolute/path/source.sqlite3 python manage.py migrate
DJANGO_ENV=development DJANGO_DEBUG=true DJANGO_DB_PATH=/absolute/path/source.sqlite3 python manage.py dumpdata accounts books --natural-foreign --natural-primary --output=/private/path/library.json
# Set DATABASE_URL to a NEW, empty PostgreSQL database in your secret environment.
python manage.py migrate
python manage.py loaddata /private/path/library.json
python manage.py check
```

Do not import sessions or JWT blacklist records. Ask users to sign in again. Validate account/book counts, owner relationships, dates, and several private samples before switching the application. Revert the connection to the untouched source copy if validation fails; do not accept writes on both databases. Remove the private fixture according to your retention policy after validation.

## PostgreSQL backup and restore

Install matching PostgreSQL 18 client tools and supply `DATABASE_URL` via a private environment. `scripts/database.py` passes credentials through the child process environment, never command arguments or output.

```sh
python scripts/database.py backup /private/backups/library-2026-09-19.dump
python scripts/database.py restore /private/backups/library-2026-09-19.dump --new-database booktracker_restore_20260919
```

Backups and checksums have mode 0600. The restore command verifies SHA-256 and creates a new database; it refuses the source database name and fails if the destination already exists. It never runs `DROP DATABASE` or `--clean`. A failed restore leaves the new database for inspection. Only restore trusted dumps: PostgreSQL backups can contain executable SQL.

Move successful dumps and their checksums to encrypted off-host storage with restricted access. Schedule daily backups and verify restore monthly; choose retention and recovery objectives with the eventual operator. A suggested starting target is RPO 24 hours and RTO 1 hour, to be measured against actual data size. These are operational targets, not availability guarantees. The checksum detects accidental corruption and does not authenticate a maliciously replaced backup.

## Deployment and rollback

From a reviewed version checkout, configure `.env`, export `DJANGO_PUBLIC_URL`, and run `scripts/release.sh deploy`. The script builds before maintenance, stops API/web writes, takes a PostgreSQL backup, runs migrations, starts the stack, and checks readiness. On a migration failure it leaves writes stopped so the operator can investigate rather than resuming a potentially incompatible application. The `backups/` directory must be on private persistent storage and copied off-host.

Record the previous commit/image digest and review backward compatibility of every migration. For a code-only rollback, check out the prior reviewed version and run `scripts/release.sh rollback-code` only when its code supports the current schema. This does not reverse migrations. For an incompatible schema change, restore the pre-deployment dump into a new database, validate it, and switch the application connection during maintenance. Preserve the old database for investigation and account for writes after the backup.

Published releases build API/web images tagged `sha-<full commit>` in GHCR after the container smoke job passes. The source-package workflow remains available. Provider credentials and automatic production rollout are deliberately absent until a host is selected.

## Rehearsal evidence

On 2026-09-19, PostgreSQL 18.6 on an isolated local port was migrated, seeded with one synthetic account and eight books, backed up to custom format, and restored into a new database. The restored counts were **1 account / 8 books**. Backend authorization and metadata tests also passed against PostgreSQL. No historical or user-owned SQLite records were used in this rehearsal.

Reference: [PostgreSQL 18 pg_dump](https://www.postgresql.org/docs/18/app-pgdump.html).
