#!/usr/bin/env bash
# 30 corridas: 5 repetições x (0, 80, 99 %) x (A, B), ordem embaralhada em cada repetição.
set -euo pipefail
cd "$(dirname "$0")/.."
REPS="${REPS:-5}"
for rep in $(seq 1 "$REPS"); do
  printf '%s\n' "A 0" "B 0" "A 80" "B 80" "A 99" "B 99" | shuf | while read -r v h; do
    bench/run_one.sh "$v" "$h" "$rep"
    sleep 5
  done
done
echo "Concluído. Resultados em results/results.csv"
