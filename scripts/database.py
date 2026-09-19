#!/usr/bin/env python3
"""Private PostgreSQL backups and guarded restores into a new database only."""

import argparse
import hashlib
import os
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlparse


def connection_env():
    url = urlparse(os.environ["DATABASE_URL"])
    if url.scheme not in ("postgres", "postgresql"):
        raise SystemExit("DATABASE_URL must use PostgreSQL.")
    env = dict(os.environ)
    env.update(
        PGHOST=url.hostname or "localhost",
        PGPORT=str(url.port or 5432),
        PGUSER=unquote(url.username or ""),
        PGPASSWORD=unquote(url.password or ""),
        PGDATABASE=unquote(url.path.lstrip("/")),
        PGSSLMODE=os.environ.get("POSTGRES_SSLMODE", "prefer"),
    )
    return env


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    backup = subs.add_parser("backup")
    backup.add_argument("file", type=Path)
    restore = subs.add_parser("restore")
    restore.add_argument("file", type=Path)
    restore.add_argument("--new-database", required=True)
    args = parser.parse_args()
    env = connection_env()
    if args.command == "backup":
        with os.fdopen(
            os.open(args.file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb"
        ) as output:
            subprocess.run(
                ["pg_dump", "--format=custom", "--no-owner", "--no-acl"],
                env=env,
                stdout=output,
                check=True,
            )
        checksum = hashlib.sha256(args.file.read_bytes()).hexdigest()
        checksum_path = Path(str(args.file) + ".sha256")
        with os.fdopen(
            os.open(checksum_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w"
        ) as output:
            output.write(checksum + "\n")
        print("Backup and SHA-256 checksum created. Store both in encrypted off-host storage.")
    else:
        if not re.fullmatch(r"[a-z][a-z0-9_]{2,62}", args.new_database):
            raise SystemExit(
                "Use a new database name with 3–63 lowercase letters, digits or underscores."
            )
        if args.new_database == env["PGDATABASE"]:
            raise SystemExit("Refusing to restore over the source database.")
        if (
            hashlib.sha256(args.file.read_bytes()).hexdigest()
            != Path(str(args.file) + ".sha256").read_text().strip()
        ):
            raise SystemExit("Backup checksum mismatch.")
        subprocess.run(["createdb", args.new_database], env=env, check=True)
        env["PGDATABASE"] = args.new_database
        subprocess.run(
            [
                "pg_restore",
                "--dbname",
                args.new_database,
                "--exit-on-error",
                "--single-transaction",
                "--no-owner",
                "--no-acl",
                str(args.file),
            ],
            env=env,
            check=True,
        )
        print(
            f"Restored into {args.new_database}. Validate it before changing the application connection."
        )


if __name__ == "__main__":
    main()
