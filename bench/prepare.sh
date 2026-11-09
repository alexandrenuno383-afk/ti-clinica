#!/usr/bin/env bash
# Prepara um conjunto determinístico e limpo antes das corridas.
set -euo pipefail
cd "$(dirname "$0")/.."

docker compose exec -T web python manage.py migrate --noinput
docker compose exec -T web python manage.py seed_users --count 10000
docker compose exec -T redis redis-cli -n 1 FLUSHDB >/dev/null
docker compose exec -T db psql -U clinic -d clinic -c "SELECT pg_stat_statements_reset();" >/dev/null
curl -fsS localhost:8000/api/v1/users/1/ >/dev/null
echo "Base pronta: 10000 utilizadores determinísticos; Redis e estatísticas SQL limpos."
