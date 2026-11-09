import csv, statistics, sys
from collections import defaultdict

path = sys.argv[1] if len(sys.argv) > 1 else "results/results.csv"
data = defaultdict(dict)
for r in csv.DictReader(open(path)):
    data[(int(r["hit_target"]), int(r["rep"]))][r["variant"]] = r


def med(x):
    return statistics.median(x)


def iqr(x):
    if len(x) < 2:
        return 0.0
    q = statistics.quantiles(x, n=4, method="inclusive")
    return q[2] - q[0]


print(f"{'acerto':>7} {'n':>2} {'p95 A':>9} {'p95 B':>9} {'redução p95 (mediana)':>22} {'IQR':>6} "
      f"{'acerto real':>12} {'SQL/ped A':>10} {'SQL/ped B':>10}")
summary = {}
for h in sorted({k[0] for k in data}):
    red, pa, pb, hr, sa, sb = [], [], [], [], [], []
    for (hh, rep), v in sorted(data.items()):
        if hh != h or "A" not in v or "B" not in v:
            continue
        a, b = float(v["A"]["p95_ms"]), float(v["B"]["p95_ms"])
        red.append((a - b) / a * 100)
        pa.append(a); pb.append(b)
        if v["B"]["hit_real"] != "":
            hr.append(float(v["B"]["hit_real"]) * 100)
        sa.append(float(v["A"]["sql_per_req"])); sb.append(float(v["B"]["sql_per_req"]))
    if not red:
        continue
    summary[h] = med(red)
    print(f"{h:>6}% {len(red):>2} {med(pa):>7.2f}ms {med(pb):>7.2f}ms {med(red):>20.1f}% "
          f"{iqr(red):>6.1f} {(med(hr) if hr else 0):>11.1f}% {med(sa):>10.3f} {med(sb):>10.3f}")

if 99 in summary and 80 in summary:
    ok = summary[99] >= 50 and summary[80] < 50
    print("\nCritério (≥ 50 % com 99 % e < 50 % com 80 %):",
          "HIPÓTESE CONFIRMADA" if ok else "HIPÓTESE NÃO CONFIRMADA")
