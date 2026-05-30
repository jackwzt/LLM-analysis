from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "confirmatory_package" / "outputs"
TABLE_DIR = OUTPUT_DIR / "tables"


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, low_memory=False)


def build_heterogeneity_table() -> pd.DataFrame:
    reductions = read_csv(TABLE_DIR / "moral_bias_reductions.csv")
    costs = read_csv(TABLE_DIR / "cost_summary.csv")
    values = read_csv(TABLE_DIR / "method_value_ranking.csv")
    cells = read_csv(TABLE_DIR / "confirmatory_dataset_cell_summary.csv")
    if reductions.empty:
        return pd.DataFrame()

    table = reductions[
        [
            "model_id",
            "model_family",
            "dataset",
            "method_condition",
            "moral_bias_mean",
            "moral_bias_reduction",
            "moral_bias_reduction_pct",
            "moral_bias_ci_low",
            "moral_bias_ci_high",
        ]
    ].copy()
    table = table.rename(
        columns={
            "moral_bias_reduction": "reduction_vs_standard",
            "moral_bias_ci_low": "bootstrap_ci_low",
            "moral_bias_ci_high": "bootstrap_ci_high",
        }
    )

    if not cells.empty:
        cell = cells.rename(columns={"rows": "n_trials"})
        cell["n_valid"] = (pd.to_numeric(cell["n_trials"], errors="coerce") * pd.to_numeric(cell["valid_rate"], errors="coerce")).round().astype("Int64")
        table = table.merge(
            cell[["model_id", "dataset", "method_condition", "analysis_tier", "n_trials", "n_valid", "valid_rate"]],
            on=["model_id", "dataset", "method_condition"],
            how="left",
        )

    if not costs.empty:
        table = table.merge(
            costs[
                [
                    "model_id",
                    "dataset",
                    "method_condition",
                    "latency_multiplier_vs_standard",
                    "token_multiplier_vs_standard",
                ]
            ],
            on=["model_id", "dataset", "method_condition"],
            how="left",
        )

    if not values.empty and "moral_value_score" in values.columns:
        table = table.merge(
            values[["model_id", "dataset", "method_condition", "moral_value_score"]].rename(columns={"moral_value_score": "value_score"}),
            on=["model_id", "dataset", "method_condition"],
            how="left",
        )

    columns = [
        "model_id",
        "model_family",
        "dataset",
        "method_condition",
        "analysis_tier",
        "n_trials",
        "n_valid",
        "valid_rate",
        "moral_bias_mean",
        "reduction_vs_standard",
        "moral_bias_reduction_pct",
        "bootstrap_ci_low",
        "bootstrap_ci_high",
        "latency_multiplier_vs_standard",
        "token_multiplier_vs_standard",
        "value_score",
    ]
    return table[[column for column in columns if column in table.columns]].sort_values(["model_id", "dataset", "method_condition"])


def write_narrative(table: pd.DataFrame) -> None:
    v4 = table[(table["model_id"].eq("deepseek_v4flash")) & (table["method_condition"].eq("anti_sycophancy_truth_first"))]
    lines = [
        "# Model-Dataset-Method Heterogeneity Summary",
        "",
        "Status: derived from confirmatory aggregate tables.",
        "",
        "The current main full-cell subset is 42,912 rows. `anti_sycophancy_truth_first` is now included after the valid-only repair of DeepSeek V4-Flash full cells.",
        "",
        "Effects should be interpreted by model and dataset, not as universal LLM claims.",
        "",
        "## DeepSeek V4-Flash Anti-Sycophancy Truth-First",
        "",
    ]
    if v4.empty:
        lines.append("DeepSeek V4-Flash `anti_sycophancy_truth_first` rows were not found in the heterogeneity table.")
    else:
        lines.append("Observed reductions:")
        lines.append("")
        for _, row in v4.iterrows():
            pct = float(row["moral_bias_reduction_pct"]) * 100 if pd.notna(row["moral_bias_reduction_pct"]) else float("nan")
            lines.append(
                f"- `{row['dataset']}`: moral bias mean = {row['moral_bias_mean']:.3f}; "
                f"reduction vs standard = {pct:.1f}%."
            )
    lines.extend(
        [
            "",
            "Required interpretation notes:",
            "",
            "- DeepSeek V4-Flash `exp2` reduction is 45.1%.",
            "- DeepSeek V4-Flash `exp3` reduction is 63.9%.",
            "- Sycophancy wrong-belief agreement has a floor effect for DeepSeek V4-Flash because the standard condition is already 0.000.",
            "- `counterfactual_consistency_vote` is a consistency-enforcement procedure; it should not be interpreted as eliminating internal model bias.",
            "- Moral tasks do not have objective correctness labels, so the analysis uses framing-gap reduction rather than moral accuracy.",
            "",
            "## Table Preview",
            "",
            "```text",
            table.head(30).to_string(index=False) if not table.empty else "No heterogeneity rows available.",
            "```",
        ]
    )
    (OUTPUT_DIR / "model_dataset_method_heterogeneity_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    table = build_heterogeneity_table()
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(TABLE_DIR / "model_dataset_method_heterogeneity_summary.csv", index=False)
    write_narrative(table)
    print(f"Wrote heterogeneity summary under {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
