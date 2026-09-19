#!/usr/bin/env python3
"""Generate local-only credentials without printing them or replacing existing files."""

import argparse
import os
import secrets
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--output", default=".env")
args = parser.parse_args()
root = Path(__file__).resolve().parent.parent
content = (
    (root / ".env.example")
    .read_text()
    .replace("DJANGO_SECRET_KEY=\n", f"DJANGO_SECRET_KEY={secrets.token_urlsafe(64)}\n")
    .replace("POSTGRES_PASSWORD=\n", f"POSTGRES_PASSWORD={secrets.token_hex(24)}\n")
)
with os.fdopen(os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w") as output:
    output.write(content)
print(f"Created {args.output} with private local credentials.")
