from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "reports" / "model_bias_fingerprint_eval"
METADATA_PATH = PROJECT_ROOT / "data" / "derived" / "model_metadata.csv"


def fmt(value: object) -> str:
    if pd.isna(value):
        return "NA"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def to_markdown(frame: pd.DataFrame, columns: list[str], max_rows: int | None = None) -> str:
    view = frame[columns].copy()
    if max_rows is not None:
        view = view.head(max_rows)
    if view.empty:
        return "_No rows._"
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(fmt(row[col]) for col in columns) + " |")
    return "\n".join(lines)


def merge_metadata(frame: pd.DataFrame, metadata: pd.DataFrame) -> pd.DataFrame:
    merged = frame.merge(metadata, on="model_id", how="left", suffixes=("", "_metadata"))
    missing = sorted(merged.loc[merged["provider_family"].isna(), "model_id"].dropna().unique())
    if missing:
        raise ValueError(f"Missing metadata for model_id(s): {missing}")
    return merged


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    metadata = pd.read_csv(METADATA_PATH)
    fingerprints = pd.read_csv(REPORT_DIR / "interim_completed_standard_fingerprints.csv")
    responsiveness = pd.read_csv(REPORT_DIR / "interim_completed_moral_responsiveness.csv")

    enriched_fp = merge_metadata(fingerprints, metadata)
    enriched_resp = merge_metadata(responsiveness, metadata)

    family_fp = (
        enriched_fp.groupby(["provider_family"], dropna=False)
        .agg(
            model_count=("model_id", "nunique"),
            completed_dataset_cells=("completed_dataset_cells", "sum"),
            moral_bias_mean=("moral_bias_mean", "mean"),
            yes_no_bias=("yes_no_bias", "mean"),
            omission_bias=("omission_bias", "mean"),
            highest_bias_model=("model_id", lambda s: ",".join(sorted(set(map(str, s))))),
        )
        .reset_index()
        .sort_values("moral_bias_mean", ascending=False)
    )

    state_fp = (
        enriched_fp.groupby(["deployment", "training_state"], dropna=False)
        .agg(
            model_count=("model_id", "nunique"),
            moral_bias_mean=("moral_bias_mean", "mean"),
            yes_no_bias=("yes_no_bias", "mean"),
            omission_bias=("omission_bias", "mean"),
        )
        .reset_index()
        .sort_values("moral_bias_mean", ascending=False)
    )

    enriched_resp["cost_adjusted_reduction_per_second"] = (
        enriched_resp["moral_bias_reduction"] / enriched_resp["median_latency_seconds"]
    )
    family_resp = (
        enriched_resp.groupby(["provider_family", "method_condition"], dropna=False)
        .agg(
            cells=("dataset", "size"),
            moral_bias_reduction=("moral_bias_reduction", "mean"),
            yes_no_bias_reduction=("yes_no_bias_reduction", "mean"),
            omission_bias_reduction=("omission_bias_reduction", "mean"),
            median_latency_seconds=("median_latency_seconds", "median"),
            cost_adjusted_reduction_per_second=("cost_adjusted_reduction_per_second", "mean"),
        )
        .reset_index()
        .sort_values("moral_bias_reduction", ascending=False)
    )

    best_effect = (
        enriched_resp.sort_values("moral_bias_reduction", ascending=False)
        .groupby(["model_id", "dataset"], dropna=False)
        .head(1)
        .copy()
        .sort_values(["provider_family", "model_id", "dataset"])
    )
    cost_source = enriched_resp[enriched_resp["cost_adjusted_reduction_per_second"].notna()].copy()
    best_cost = (
        cost_source.sort_values("cost_adjusted_reduction_per_second", ascending=False)
        .groupby(["model_id", "dataset"], dropna=False)
        .head(1)
        .copy()
        .sort_values(["provider_family", "model_id", "dataset"])
    )

    deepseek_v4 = enriched_resp[
        enriched_resp["model_id"].isin(["deepseek_v4pro", "deepseek_v4flash"])
        & enriched_resp["dataset"].eq("exp2")
    ].copy()
    deepseek_v4 = deepseek_v4.sort_values(["model_id", "moral_bias_reduction"], ascending=[True, False])

    enriched_fp.to_csv(REPORT_DIR / "family_enriched_standard_fingerprints.csv", index=False)
    enriched_resp.to_csv(REPORT_DIR / "family_enriched_moral_responsiveness.csv", index=False)
    family_fp.to_csv(REPORT_DIR / "family_standard_fingerprint_summary.csv", index=False)
    state_fp.to_csv(REPORT_DIR / "family_training_state_fingerprint_summary.csv", index=False)
    family_resp.to_csv(REPORT_DIR / "family_method_responsiveness_summary.csv", index=False)
    best_effect.to_csv(REPORT_DIR / "family_best_method_by_effect.csv", index=False)
    best_cost.to_csv(REPORT_DIR / "family_best_method_by_cost.csv", index=False)

    lines = [
        "# Model Family Bias Pattern Report",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Interpretation Rules",
        "",
        "- `moral_bias_mean` is lower when the model is less framing-sensitive under standard prompting.",
        "- `moral_bias_reduction` is `standard - method`; higher means stronger debiasing.",
        "- `cost_adjusted_reduction_per_second` is only computed when latency is available.",
        "- Current coverage is interim: DeepSeek V4 results are Exp2-complete; some older models cover Exp2+Exp3.",
        "",
        "## Family-Level Standard Fingerprints",
        "",
        to_markdown(
            family_fp,
            [
                "provider_family",
                "model_count",
                "completed_dataset_cells",
                "moral_bias_mean",
                "yes_no_bias",
                "omission_bias",
            ],
        ),
        "",
        "## Training-State Fingerprints",
        "",
        to_markdown(
            state_fp,
            [
                "deployment",
                "training_state",
                "model_count",
                "moral_bias_mean",
                "yes_no_bias",
                "omission_bias",
            ],
        ),
        "",
        "## Method Responsiveness By Family",
        "",
        to_markdown(
            family_resp,
            [
                "provider_family",
                "method_condition",
                "cells",
                "moral_bias_reduction",
                "yes_no_bias_reduction",
                "omission_bias_reduction",
                "median_latency_seconds",
                "cost_adjusted_reduction_per_second",
            ],
        ),
        "",
        "## Best Method By Effect",
        "",
        to_markdown(
            best_effect,
            [
                "model_id",
                "dataset",
                "method_condition",
                "standard_moral_bias_mean",
                "moral_bias_mean",
                "moral_bias_reduction",
                "median_latency_seconds",
            ],
        ),
        "",
        "## Best Method By Cost-Adjusted Effect",
        "",
        to_markdown(
            best_cost,
            [
                "model_id",
                "dataset",
                "method_condition",
                "moral_bias_reduction",
                "median_latency_seconds",
                "cost_adjusted_reduction_per_second",
            ],
        ),
        "",
        "## DeepSeek V4 Variant Pattern",
        "",
        to_markdown(
            deepseek_v4,
            [
                "model_id",
                "method_condition",
                "standard_moral_bias_mean",
                "moral_bias_mean",
                "moral_bias_reduction",
                "median_latency_seconds",
                "cost_adjusted_reduction_per_second",
            ],
        ),
        "",
        "## Draft Regularities",
        "",
        "1. High baseline bias does not imply a fixed best intervention: DeepSeek V4-Pro and V4-Flash both have high Exp2 standard bias, but their strongest method differs.",
        "2. Debate appears strongest for DeepSeek V4-Pro by raw effect, while critique-revise is the cost-adjusted winner and the raw-effect winner for V4-Flash.",
        "3. Model family is informative but insufficient: provider-level averages hide variant-level differences between Pro and Flash.",
        "4. Low baseline-bias models have less room for improvement and can even worsen under debate, as seen in Gemini Exp2 and Qwen3-32B local Exp2.",
        "5. Method selection should be fingerprint-conditioned rather than globally fixed.",
        "",
    ]
    (REPORT_DIR / "model_family_pattern_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(
        {
            "report": str(REPORT_DIR / "model_family_pattern_report.md"),
            "models": int(enriched_fp["model_id"].nunique()),
            "families": int(enriched_fp["provider_family"].nunique()),
            "responsiveness_rows": int(len(enriched_resp)),
        }
    )


if __name__ == "__main__":
    main()
