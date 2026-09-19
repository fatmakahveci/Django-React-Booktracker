# Historical data assessment

Reviewed 2026-09-19. Only aggregate findings are recorded here; no individual emails, password hashes, tokens, or book contents are included.

- In the original history, `db.sqlite3` was introduced in commit `2377775` and removed in `d1767b9`. These are pre-cleanup commit IDs.
- The original history contained one database blob at `db.sqlite3`; no other database paths were found.
- The database contains 4 accounts, 6 books, and 63 outstanding JWT records. The Django session table is empty. The token expiry dates are between 2023-06-30 and 2023-07-15, so these recorded tokens have expired.
- Accounts were created between 2023-05-11 and 2023-05-15. None of the account email addresses matches an email literal in the original Python test fixtures, and none uses a reserved example/test domain. One username matches a test literal; that alone does not establish provenance.
- All 4 passwords are stored as PBKDF2-SHA256 hashes. There are no staff or superuser accounts. Empty session and last-login fields do not establish that an account was unused, especially when JWT records exist.
- Repository evidence cannot establish whether the accounts belong to real people. The database cannot be certified as synthetic test data and should be treated as potentially sensitive.
- The current tree ignores SQLite data. Previously downloaded archives, old clones, and GitHub's retained PR/cache references can still contain the database.
- The approved history rewrite changed descendant commit IDs. Other clones must be refreshed without merging the original history back. Third-party copies cannot be erased by rewriting this repository.

## Completed cleanup

- Created a private mirror and verified a full Git bundle backup outside the working repository.
- Rehearsed `git-filter-repo --sensitive-data-removal --no-fetch --invert-paths --path db.sqlite3` in a separate mirror containing all advertised refs.
- Rewrote 58 of 59 commits. Verified every cleaned commit tree, confirmed the database blob is unavailable in the cleaned object store, and passed `git fsck --full`.
- Published only the approved `main` and `v0.1.0` refs with atomic expected-old-commit leases. The rewritten main commit is `1e9e0df`; the rewritten tag points to `c067edf`. Subsequent documentation commits build on that cleaned history.
- The application tree is byte-for-byte unchanged by the rewrite. The tag's tree differs only by removal of `db.sqlite3`; the regenerated archive downloaded from GitHub was verified to contain no database.
- Temporarily enabled an administrator bypass in the `Protect default branch` ruleset with the owner's explicit approval. Restored and verified the original rules immediately after publication; force-push and PR protections remain active.
- Backend, frontend, and portable-deployment CI all passed on the rewritten main commit.
- Updated the active local checkout, removed its old reflog/object copies, and verified that the historical database blob is no longer available there. Moved the unchanged historical SQLite file from the working directory into the owner-only private backup; it was not migrated or used as the development database.

The private recovery backup intentionally retains the original history and must not be published. GitHub's 17 affected PR head refs are outside normal push control and remain a separate support-side cleanup task. This report does not claim those retained references or previously downloaded copies have been erased.

## Release scope checked

GitHub lists release `v0.1.0` with no manually attached assets and reported no forks at assessment time. The release now resolves to the cleaned tag and its generated source archive has been verified.

The public OCI source package `ghcr.io/fatmakahveci/django-react-booktracker:0.1.0` was independently confirmed to contain the same database. The reviewed manifest was `sha256:b0d5699290794bb0ab74f2835afa9e088162ce03d017050b0fd84ddbdb29777a`, version ID `1208181252`.

The owner's approved deletion was completed through the repository's package-admin Actions token in [cleanup run 35471120337](https://github.com/fatmakahveci/Django-React-Booktracker/actions/runs/35471120337). GitHub required deleting the package container because this was its sole version; the job rechecked that no other versions or tags existed before doing so. The version API returned 404 afterward, and fresh anonymous registry pull authorization returned 403. The package was removed rather than retagged.

Future archives from the current tree exclude SQLite and environment files through `.gitattributes`. This does not retroactively change old tags or package versions.

The privately preserved SQLite copy also has inconsistent Django migration history (`admin.0001_initial` precedes its account dependency). Use a new development database; any recovery of the historical file needs a separately reviewed, private migration plan.

## Remaining actions

1. Submit the prepared private GitHub Support request for the 17 affected PR refs, cached views, and unreachable sensitive objects. It has not been sent, and that server-side cleanup remains outstanding.
2. Refresh other clones without merging the old history back. Previously downloaded copies cannot be recalled. Retain the private recovery backup only for the agreed recovery period.
3. If any historical passwords or signing keys were used in a real deployment, rotate them there and invalidate sessions. No deployment or production credentials were available or changed during this assessment.

See [GitHub's sensitive-data removal procedure](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository) for PR/cache cleanup and collaboration requirements.
