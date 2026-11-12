import argparse
import csv
import statistics
from pathlib import Path

from analysis_data import HIT_RATES, VARIANTS, describe, load_results, metric_values

DEFAULT_INPUT = "data/results-final.csv"
SUMMARY_PATH = Path("data/summary.csv")


def iqr(values):
    if len(values) < 2:
        return 0.0
    quartiles = statistics.quantiles(values, n=4, method="inclusive")
    return quartiles[2] - quartiles[0]


def paired_rows(groups, hit):
    by_rep = {}
    for variant in VARIANTS:
        for row in groups.get((hit, variant), []):
            by_rep.setdefault(int(row["rep"]), {})[variant] = row
    return [rows for _, rows in sorted(by_rep.items()) if all(v in rows for v in VARIANTS)]


def write_summary_csv(groups):
    fields = ["hit_target", "variant", "n"]
    for metric in ("p50", "p95", "avg"):
        fields.extend(f"{metric}_{stat}_ms" for stat in ("mean", "std", "median"))

    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SUMMARY_PATH.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for hit in HIT_RATES:
            for variant in VARIANTS:
                rows = groups.get((hit, variant), [])
                result = {"hit_target": hit, "variant": variant, "n": len(rows)}
                for metric in ("p50", "p95", "avg"):
                    stats = describe(metric_values(rows, metric))
                    for stat in ("mean", "std", "median"):
                        value = stats[stat]
                        result[f"{metric}_{stat}_ms"] = (
                            round(value, 6) if isinstance(value, (float, int)) else value
                        )
                writer.writerow(result)


def print_existing_table(groups):
    print(
        f"{'acerto':>7} {'n':>2} {'p95 A':>9} {'p95 B':>9} "
        f"{'redução p95 (mediana)':>22} {'IQR':>6} {'acerto real':>12} "
        f"{'SQL/ped A':>10} {'SQL/ped B':>10}"
    )
    reductions_by_hit = {}
    for hit in HIT_RATES:
        reductions, p95_a, p95_b, real_hits, sql_a, sql_b = [], [], [], [], [], []
        for pair in paired_rows(groups, hit):
            a, b = pair["A"], pair["B"]
            a_p95, b_p95 = float(a["p95_ms"]), float(b["p95_ms"])
            reductions.append((a_p95 - b_p95) / a_p95 * 100)
            p95_a.append(a_p95)
            p95_b.append(b_p95)
            if b.get("hit_real", "") != "":
                real_hits.append(float(b["hit_real"]) * 100)
            sql_a.append(float(a["sql_per_req"]))
            sql_b.append(float(b["sql_per_req"]))
        if not reductions:
            continue
        reductions_by_hit[hit] = statistics.median(reductions)
        print(
            f"{hit:>6}% {len(reductions):>2} {statistics.median(p95_a):>7.2f}ms "
            f"{statistics.median(p95_b):>7.2f}ms {statistics.median(reductions):>20.1f}% "
            f"{iqr(reductions):>6.1f} "
            f"{(statistics.median(real_hits) if real_hits else 0):>11.1f}% "
            f"{statistics.median(sql_a):>10.3f} {statistics.median(sql_b):>10.3f}"
        )

    if 99 in reductions_by_hit and 80 in reductions_by_hit:
        confirmed = reductions_by_hit[99] >= 50 and reductions_by_hit[80] < 50
        print(
            "\nCritério (≥ 50 % com 99 % e < 50 % com 80 %):",
            "HIPÓTESE CONFIRMADA" if confirmed else "HIPÓTESE NÃO CONFIRMADA",
        )


def print_descriptive_table(groups):
    print("\nEstatísticas por variante e taxa de acerto (média, desvio padrão e mediana)")
    print(
        f"{'acerto':>7} {'var':>4} {'n':>2} "
        f"{'p50 média':>10} {'DP':>8} {'mediana':>9} "
        f"{'p95 média':>10} {'DP':>8} {'mediana':>9} "
        f"{'avg média':>10} {'DP':>8} {'mediana':>9}"
    )
    for hit in HIT_RATES:
        for variant in VARIANTS:
            rows = groups.get((hit, variant), [])
            if not rows:
                continue
            stats = {metric: describe(metric_values(rows, metric)) for metric in ("p50", "p95", "avg")}
            print(
                f"{hit:>6}% {variant:>4} {len(rows):>2} "
                + " ".join(
                    f"{stats[m]['mean']:>9.3f} {stats[m]['std']:>8.3f} "
                    f"{stats[m]['median']:>9.3f}"
                    for m in ("p50", "p95", "avg")
                )
            )


def main():
    parser = argparse.ArgumentParser(description="Resume os resultados do benchmark.")
    parser.add_argument("input", nargs="?", default=DEFAULT_INPUT)
    args = parser.parse_args()

    groups = load_results(args.input)
    print_existing_table(groups)
    print_descriptive_table(groups)
    write_summary_csv(groups)
    print(f"\nResumo detalhado gravado em {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
