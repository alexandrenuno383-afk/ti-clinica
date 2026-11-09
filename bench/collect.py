import csv, json, os, sys

res, name, variant, hit, rep, hits, misses, sql = sys.argv[1:9]
metrics = json.load(open(f"{res}/{name}.json"))["metrics"]


def val(metric, *keys):
    m = metrics.get(metric, {})
    v = m.get("values", m)
    for k in keys:
        if k in v:
            return v[k]
    return 0


reqs = val("http_reqs", "count")
hits, misses, sql = int(hits), int(misses), float(sql)
hit_real = hits / (hits + misses) if (hits + misses) else ""
row = {
    "name": name, "rep": rep, "variant": variant, "hit_target": hit,
    "hit_real": round(hit_real, 4) if hit_real != "" else "",
    "reqs": reqs,
    "rps": round(val("http_reqs", "rate"), 2),
    "avg_ms": round(val("http_req_duration", "avg"), 3),
    "p50_ms": round(val("http_req_duration", "med"), 3),
    "p95_ms": round(val("http_req_duration", "p(95)"), 3),
    "p99_ms": round(val("http_req_duration", "p(99)"), 3),
    "max_ms": round(val("http_req_duration", "max"), 3),
    "error_rate": val("http_req_failed", "rate", "value"),
    "dropped": val("dropped_iterations", "count"),
    "redis_hits": hits, "redis_misses": misses,
    "sql_calls": int(sql),
    "sql_per_req": round(sql / reqs, 4) if reqs else "",
}

path = f"{res}/results.csv"
new = not os.path.exists(path)
with open(path, "a", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(row))
    if new:
        w.writeheader()
    w.writerow(row)

print(f"{name}: p95={row['p95_ms']} ms | reqs={reqs} | acerto real={row['hit_real']} "
      f"| SQL/pedido={row['sql_per_req']} | erros={row['error_rate']} | perdidos={row['dropped']}")
if row["dropped"] or row["error_rate"]:
    print("  ATENÇÃO: houve pedidos perdidos ou erros; esta corrida não é fiável.")
