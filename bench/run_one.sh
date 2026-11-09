#!/usr/bin/env bash
# Uso: bench/run_one.sh <A|B> <taxa de acerto em %> <repetição>
set -euo pipefail
cd "$(dirname "$0")/.."
source bench/config.sh

V="$1"; H="$2"; REP="$3"
RES="${RESULTS_DIR:-results}"
export WARMUP_S="${WARMUP_S:-15}" MEASURE_S="${MEASURE_S:-120}" RATE="${RATE:-50}"
NAME="${V}_h${H}_r${REP}"
mkdir -p "$RES"

redis() { docker compose exec -T redis redis-cli -n 1 "$@"; }
psql_() { docker compose exec -T db psql -U clinic -d clinic -At "$@"; }

k6run() {
  local phase="$1"; shift
  docker run --rm --user "$(id -u):$(id -g)" --network "$NET" --cpuset-cpus "$K6_CPUS" \
    -v "$PWD/bench/k6:/scripts:ro" -v "$PWD/$RES:/results" \
    -e BASE_URL=http://web:8000 -e VARIANT="$V" \
    -e HIT_RATE="$(awk "BEGIN{print $H/100}")" -e PHASE="$phase" \
    -e RATE="$RATE" -e WARMUP_S="$WARMUP_S" -e MEASURE_S="$MEASURE_S" \
    "$K6_IMAGE" run "$@" /scripts/client.js
}

echo "=== $NAME (aplicação: CPUs $APP_CPUS | k6: CPU $K6_CPUS) ==="
curl -fsS localhost:8000/api/v1/users/1/ >/dev/null   # servidor pronto?
docker update --cpuset-cpus "$APP_CPUS" $(docker compose ps -q web db redis) >/dev/null

# 1. Estado limpo e conjunto quente
redis flushdb >/dev/null
docker compose exec -T web python manage.py warm_user_cache --count 1000 >/dev/null

# 2. Aquecimento (excluído dos resultados)
k6run warmup --quiet >/dev/null 2>&1

# 3. Zerar contadores: só a medição conta
redis config resetstat >/dev/null
psql_ -c "SELECT pg_stat_statements_reset();" >/dev/null

# 4. Medição
k6run measure --quiet --summary-export "/results/$NAME.json" 2>&1 | tee "$RES/$NAME.log" >/dev/null

# 5. Contadores no fim da medição
STATS=$(redis info stats | tr -d '\r')
HITS=$(echo "$STATS" | awk -F: '$1=="keyspace_hits"{print $2}')
MISSES=$(echo "$STATS" | awk -F: '$1=="keyspace_misses"{print $2}')
SQL=$(psql_ -c "SELECT coalesce(sum(calls),0) FROM pg_stat_statements WHERE query LIKE '%accounts_user%';")

python3 bench/collect.py "$RES" "$NAME" "$V" "$H" "$REP" "$HITS" "$MISSES" "$SQL"
