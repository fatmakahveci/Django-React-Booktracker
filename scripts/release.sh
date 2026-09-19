#!/usr/bin/env bash
# Build reviewed source, stop writes, back up, migrate and check deployment health.
set -euo pipefail
mode="${1:-}"
if [[ "$mode" != "deploy" && "$mode" != "rollback-code" ]]; then
  echo 'Usage: scripts/release.sh deploy|rollback-code (run from the reviewed version checkout)' >&2
  exit 2
fi
compose=(docker compose -f compose.yaml -f deploy/compose.production.yaml)
if [[ "${BOOKTRACKER_TLS:-false}" == true ]]; then compose+=(-f deploy/compose.tls.yaml); fi
"${compose[@]}" config --quiet
"${compose[@]}" build
if [[ "$mode" == deploy ]]; then
  "${compose[@]}" stop web api
  mkdir -p backups
  chmod 700 backups
  backup="backups/pre-deploy-$(date -u +%Y%m%dT%H%M%SZ).dump"
  umask 077
  "${compose[@]}" exec -T postgres sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc --no-owner --no-acl' > "$backup"
  python3 -c 'import hashlib, pathlib, sys; p=pathlib.Path(sys.argv[1]); pathlib.Path(str(p)+".sha256").write_text(hashlib.sha256(p.read_bytes()).hexdigest()+"\n")' "$backup"
  "${compose[@]}" run --rm api python manage.py migrate --noinput
fi
# rollback-code does not reverse schemas; use only after checking migration compatibility.
"${compose[@]}" up -d --wait --wait-timeout 120
curl --fail --silent --show-error "${DJANGO_PUBLIC_URL:?Export DJANGO_PUBLIC_URL}/api/health/ready/"
echo 'Release health check passed.'
