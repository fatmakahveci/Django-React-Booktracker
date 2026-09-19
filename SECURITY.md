# Security Policy

This policy covers security vulnerabilities in Django React Book Tracker, including its Django API, React client, authentication flow, dependencies, and repository workflows.

## Supported versions

Security fixes target the latest code on the default branch (`main`). Older releases, forks, and development branches are not guaranteed to receive backported fixes. Deployments should track security updates and review migration instructions before upgrading.

## Report a vulnerability privately

Please report suspected vulnerabilities through [GitHub private vulnerability reporting](https://github.com/fatmakahveci/Django-React-Booktracker/security/advisories/new).

Do not publish exploit details, credentials, tokens, or personal data in public issues, discussions, or pull requests. If private reporting is unavailable, check the [maintainer's GitHub profile](https://github.com/fatmakahveci) for a published private contact method. If none is available, open an issue asking only for a private reporting channel, without describing the vulnerability.

A useful report includes:

- The affected component, commit or release, and relevant dependency versions.
- A description of the issue and its potential impact.
- Required permissions, configuration, and other conditions needed to reproduce it.
- Minimal reproduction steps or a proof of concept using synthetic data.
- Expected behavior and actual behavior.
- Redacted logs or screenshots, and any suggested mitigation.

Never include real passwords, signing keys, access or refresh tokens, or another person's records. Share only the information needed to reproduce the issue.

## Investigation and disclosure

Reports will be reviewed as promptly as possible. This project does not promise a fixed response or resolution time.

Maintainers may request more information, reproduce the issue, assess affected versions, and develop a fix with regression coverage. Please coordinate public disclosure through the private report so affected users can receive a fix or mitigation first. Reporter attribution can be discussed during that process.

## Areas of particular interest

- Authentication bypass, account takeover, and JWT refresh-token handling.
- Access to another user's books or unauthorized changes to book ownership.
- Injection vulnerabilities, including cross-site scripting in the frontend.
- Exposure of secrets, private records, or sensitive files.
- Dependency or workflow vulnerabilities that affect this repository.
- Deployment configuration that unexpectedly bypasses documented protections.

Use the normal issue tracker for non-sensitive bugs and feature requests. Automated dependency reports are useful when they identify the affected version and how the vulnerable component is used.

## Safe reproduction

Use a local checkout, an isolated database, test accounts, and synthetic book records. Only test systems you own or have explicit permission to assess. Avoid accessing other users' data, disrupting shared services, or sending unsolicited traffic to deployed instances. If you encounter sensitive data, stop testing and describe the exposure privately without copying the data into the report.

## Deployment considerations

- Keep `DJANGO_DEBUG=false` in production. Configure explicit allowed hosts and trusted frontend origins.
- Provide a unique, persistent `DJANGO_SECRET_KEY` through your deployment's secret store. Never reuse historical development credentials from repository history. If a signing key was exposed, rotate it and invalidate affected sessions and tokens.
- Use HTTPS and review reverse-proxy trust settings. Run `python manage.py check --deploy` with the actual production configuration.
- Local SQLite databases must not be committed or included in source releases. Removing a database from the current tree does not remove it from Git history; treat any credentials previously included as exposed.
- Back up databases before upgrades and review migration history before applying migrations.
- The browser uses HttpOnly, SameSite=Lax cookies, with Secure required outside debug. Unsafe requests require CSRF, including login/refresh/logout. Tokens are never written to local or session storage. Ordinary logout revokes refresh and clears cookies; copied access tokens can remain valid for up to five minutes. Failed server logout is surfaced in the UI and can be retried.
- Password changes and all-session revocation invalidate access and refresh tokens. Account deletion cascades to its private books. Sensitive account changes require the current password.
- Email verification is required. Reset and verification links are single-use and expire after one hour. Existing addresses require verification after upgrading.
- Production requires Redis for atomic per-IP authentication limits across workers. Redis failures fail closed. Only explicitly trusted gateways can set the original client address. Additional gateway limits complement application controls.
- Refresh tokens rotate after successful refresh, and old refresh tokens are blacklisted. Custom clients must retain the newly returned token pair.
- Install frontend dependencies from the committed lockfile with `npm ci`, review dependency alerts, and run the documented checks after upgrading.

See the [deployment guide](docs/operations/environments.md) for configuration and the [contributing guide](.github/CONTRIBUTING.md) for the development workflow.
