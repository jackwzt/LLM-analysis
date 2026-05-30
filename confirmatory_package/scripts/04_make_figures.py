from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "confirmatory_package" / "outputs"
TABLE_DIR = OUTPUT_DIR / "tables"
FIGURE_DIR = OUTPUT_DIR / "figures"


def save_figure(name: str) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    for suffix in ["png", "pdf"]:
        plt.savefig(FIGURE_DIR / f"{name}.{suffix}", bbox_inches="tight", dpi=180)
    plt.close()


def load_csv(name: str) -> pd.DataFrame:
    path = TABLE_DIR / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def baseline_model_bias(moral: pd.DataFrame) -> None:
    data = moral[moral["method_condition"].eq("standard")].copy()
    if data.empty:
        return
    data = data.groupby("model_id", as_index=False)["moral_bias_mean"].mean().sort_values("moral_bias_mean")
    plt.figure(figsize=(9, max(3, 0.4 * len(data))))
    plt.barh(data["model_id"], data["moral_bias_mean"], color="#4C78A8")
    plt.xlabel("Mean moral framing bias")
    plt.title("Baseline Moral Framing Bias by Model")
    save_figure("baseline_model_bias")


def method_reduction_plot(reductions: pd.DataFrame) -> None:
    data = reductions[reductions["method_condition"].ne("standard")].copy()
    if data.empty:
        return
    data = data.groupby("method_condition", as_index=False)["moral_bias_reduction"].mean().sort_values("moral_bias_reduction")
    plt.figure(figsize=(8, 4.5))
    plt.bar(data["method_condition"], data["moral_bias_reduction"], color="#F58518")
    plt.ylabel("Mean bias reduction vs standard")
    plt.xticks(rotation=25, ha="right")
    plt.title("Method-Level Moral Bias Reduction")
    save_figure("method_moral_bias_reduction")


def cost_effectiveness_scatter(value: pd.DataFrame) -> None:
    data = value[value["method_condition"].ne("standard")].copy()
    if data.empty:
        return
    data["cost_multiplier"] = data[["latency_multiplier_vs_standard", "token_multiplier_vs_standard"]].mean(axis=1)
    plt.figure(figsize=(7, 5))
    for method, group in data.groupby("method_condition"):
        plt.scatter(group["cost_multiplier"], group["moral_bias_reduction"], label=method, s=55, alpha=0.8)
    plt.axhline(0, color="black", linewidth=0.8)
    plt.xlabel("Mean cost multiplier vs standard")
    plt.ylabel("Moral bias reduction vs standard")
    plt.title("Cost-Effectiveness of Debiasing Methods")
    plt.legend(fontsize=8)
    save_figure("cost_effectiveness_scatter")


def model_method_heatmap(reductions: pd.DataFrame) -> None:
    data = reductions.pivot_table(index="model_id", columns="method_condition", values="moral_bias_reduction", aggfunc="mean")
    if data.empty:
        return
    data = data[[column for column in data.columns if column != "standard"]]
    if data.empty:
        return
    plt.figure(figsize=(max(6, 1.5 * len(data.columns)), max(3, 0.45 * len(data))))
    matrix = data.to_numpy(dtype=float)
    vmax = np.nanmax(np.abs(matrix)) if np.isfinite(matrix).any() else 1.0
    plt.imshow(matrix, aspect="auto", cmap="RdBu_r", vmin=-vmax, vmax=vmax)
    plt.colorbar(label="Bias reduction vs standard")
    plt.xticks(range(len(data.columns)), data.columns, rotation=25, ha="right")
    plt.yticks(range(len(data.index)), data.index)
    plt.title("Model-by-Method Bias Reduction")
    save_figure("model_method_heatmap")


def value_score_ranking(value: pd.DataFrame) -> None:
    data = value[value["method_condition"].ne("standard")].copy()
    if data.empty or "moral_value_score" not in data.columns:
        return
    data = data.groupby("method_condition", as_index=False)["moral_value_score"].mean().sort_values("moral_value_score")
    plt.figure(figsize=(8, 4.5))
    plt.barh(data["method_condition"], data["moral_value_score"], color="#54A24B")
    plt.xlabel("Mean value score")
    plt.title("Method Value-Score Ranking")
    save_figure("method_value_score_ranking")


def main() -> None:
    moral = load_csv("moral_bias_summary.csv")
    reductions = load_csv("moral_bias_reductions.csv")
    value = load_csv("method_value_ranking.csv")
    baseline_model_bias(moral)
    method_reduction_plot(reductions)
    cost_effectiveness_scatter(value)
    model_method_heatmap(reductions)
    value_score_ranking(value)
    print(f"Wrote figures under {FIGURE_DIR}")


if __name__ == "__main__":
    main()
