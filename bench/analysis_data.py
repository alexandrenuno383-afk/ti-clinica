"""Shared CSV loading and descriptive statistics for benchmark analysis."""

import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean, median, stdev

METRICS = {
    "p50": "p50_ms",
    "p95": "p95_ms",
    "avg": "avg_ms",
    "sql_per_req": "sql_per_req",
}
HIT_RATES = (0, 80, 99)
VARIANTS = ("A", "B")


def load_results(path):
    """Load rows grouped by (target hit rate, variant), rejecting duplicates."""
    groups = defaultdict(list)
    seen = set()
    with Path(path).open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            hit = int(row["hit_target"])
            variant = row["variant"]
            rep = int(row["rep"])
            key = (hit, variant, rep)
            if key in seen:
                raise ValueError(f"Repetição duplicada no CSV: {key}")
            seen.add(key)
            groups[(hit, variant)].append(row)
    return groups


def describe(values):
    """Return count, mean, sample standard deviation, and median."""
    values = list(values)
    if not values:
        return {"n": 0, "mean": "", "std": "", "median": ""}
    return {
        "n": len(values),
        "mean": mean(values),
        "std": stdev(values) if len(values) > 1 else 0.0,
        "median": median(values),
    }


def metric_values(rows, metric):
    field = METRICS[metric]
    return [float(row[field]) for row in rows if row.get(field, "") != ""]
