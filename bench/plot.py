import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from analysis_data import HIT_RATES, describe, load_results, metric_values

DEFAULT_INPUT = "data/results-final.csv"
OUTPUT_DIR = Path("figures")
COLORS = {"A": "#35618f", "B": "#d1762f"}


def aggregate(groups, hit, variant, metric):
    values = metric_values(groups.get((hit, variant), []), metric)
    if not values:
        raise ValueError(f"Sem dados para hit_target={hit}, variante={variant}")
    return describe(values)


def style_axis(axis):
    axis.set_axisbelow(True)
    axis.grid(axis="y", color="#d9d9d9", linewidth=0.6)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.tick_params(labelsize=8)


def plot_latency(groups):
    positions = list(range(len(HIT_RATES)))
    width = 0.34
    fig, axes = plt.subplots(1, 2, figsize=(7.05, 2.65), sharex=True)

    for axis, metric, title in zip(axes, ("p50", "p95"), ("Latência p50", "Latência p95")):
        for offset, variant in ((-width / 2, "A"), (width / 2, "B")):
            stats = [aggregate(groups, hit, variant, metric) for hit in HIT_RATES]
            axis.bar(
                [p + offset for p in positions],
                [s["mean"] for s in stats],
                width=width,
                yerr=[s["std"] for s in stats],
                capsize=3,
                color=COLORS[variant],
                edgecolor="white",
                linewidth=0.5,
                label=f"Variante {variant}",
            )
        axis.set_title(title, fontsize=9, pad=5)
        axis.set_ylabel("Latência (ms)", fontsize=8)
        axis.set_xticks(positions, [f"{hit}%" for hit in HIT_RATES])
        axis.set_xlabel("Taxa de acerto alvo", fontsize=8)
        style_axis(axis)
        axis.legend(frameon=False, fontsize=7, loc="upper right")

    fig.tight_layout(w_pad=1.3)
    fig.savefig(OUTPUT_DIR / "fig1_latencia.png", dpi=300, facecolor="white", bbox_inches="tight")
    plt.close(fig)


def plot_sql(groups):
    positions = list(range(len(HIT_RATES)))
    width = 0.42
    fig, axis = plt.subplots(figsize=(4.8, 2.65))
    for offset, variant in ((-width / 2, "A"), (width / 2, "B")):
        stats = [aggregate(groups, hit, variant, "sql_per_req") for hit in HIT_RATES]
        axis.bar(
            [p + offset for p in positions],
            [s["mean"] for s in stats],
            width=width,
            yerr=[s["std"] for s in stats],
            capsize=3,
            color=COLORS[variant],
            edgecolor="white",
            linewidth=0.5,
            label=f"Variante {variant}",
        )
    axis.set_ylabel("Consultas SQL por pedido", fontsize=8)
    axis.set_xlabel("Taxa de acerto alvo", fontsize=8)
    axis.set_xticks(positions, [f"{hit}%" for hit in HIT_RATES])
    axis.legend(frameon=False, fontsize=7)
    style_axis(axis)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig2_sql.png", dpi=300, facecolor="white", bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Gera figuras dos resultados do benchmark.")
    parser.add_argument("input", nargs="?", default=DEFAULT_INPUT)
    args = parser.parse_args()

    groups = load_results(args.input)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    plot_latency(groups)
    plot_sql(groups)
    print(f"Figuras gravadas em {OUTPUT_DIR}/fig1_latencia.png e {OUTPUT_DIR}/fig2_sql.png")


if __name__ == "__main__":
    main()
