# Historical data assessment

Reviewed 2026-09-19. No individual records, emails, password hashes, or book contents were exported into this report.

- `db.sqlite3` was introduced in commit `2377775` and removed in `d1767b9`.
- The retained historical database contains 4 account records and 6 book records. The Django session table contains no records.
- These counts do not establish whether the accounts belong to real people. Treat them as potentially sensitive until the owner confirms their origin.
- The current tree ignores SQLite data. Historical commits and previously generated source archives can still contain the database.
- Rewriting history would change descendant commit IDs and require coordinated force-pushes, refreshed clones, and cleanup of affected release assets. Forks and third-party copies cannot be erased by rewriting this repository.

## Recommended next steps

1. Privately establish whether the historical accounts or development signing key were ever used outside testing.
2. If so, rotate affected credentials in the actual deployment and invalidate sessions. No production credentials were changed in this task.
3. Inventory affected release assets and package versions before approving history changes.
4. Back up refs, then rehearse cleanup in an isolated mirror with `git filter-repo --path db.sqlite3 --invert-paths`. Validate commit trees and release archives before deciding which refs to force-push.
5. Obtain explicit approval for the reviewed ref changes. Never run a blanket force-push from the working repository.

This task is intentionally report-only at the owner's request. It does not claim the historical exposure has been removed.

## Release scope checked

GitHub currently lists release `v0.1.0` with no manually attached release assets. Its Git tag still contains `db.sqlite3`, so GitHub-generated source archives for that tag also include the file. Previously published OCI source-package copies were not deleted or claimed remediated. Future archives from the current tree exclude SQLite and environment files through `.gitattributes`. This does not retroactively change old tags or package versions.

The preserved historical/local SQLite copy also has inconsistent Django migration history (`admin.0001_initial` precedes its account dependency). It was not repaired or migrated. Use a new development database; any recovery of the historical file needs a separately reviewed, private migration plan.
