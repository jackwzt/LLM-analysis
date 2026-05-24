from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "reports" / "model_bias_fingerprint_eval"
SUMMARY_PATH = REPORT_DIR / "model_method_bias_summary.csv"


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
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    rows = []
    for _, row in view.iterrows():
        rows.append("| " + " | ".join(fmt(row[col]) for col in columns) + " |")
    return "\n".join([header, sep, *rows])


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    summary = pd.read_csv(SUMMARY_PATH)

    moral_complete = summary[
        summary["dataset"].isin(["exp2", "exp3"])
        & summary["moral_items"].fillna(0).ge(6)
        & summary["trials"].ge(1008)
        & summary["valid_rate"].ge(0.95)
    ].copy()
    syc_complete = summary[
        summary["dataset"].eq("sycophancy")
        & summary["trials"].ge(1152)
        & summary["valid_rate"].ge(0.95)
    ].copy()
    completed = pd.concat([moral_complete, syc_complete], ignore_index=True, sort=False)

    standard = moral_complete[moral_complete["method_condition"].eq("standard")].copy()
    standard_fingerprints = (
        standard.groupby(["model_id", "model_family", "provider", "model_type"], dropna=False)
        .agg(
            completed_dataset_cells=("dataset", "nunique"),
            datasets=("dataset", lambda s: ",".join(sorted(map(str, s.dropna().unique())))),
            moral_bias_mean=("moral_bias_mean", "mean"),
            yes_no_bias=("yes_no_bias", "mean"),
            omission_bias=("omission_bias", "mean"),
            valid_rate=("valid_rate", "mean"),
        )
        .reset_index()
        .sort_values("moral_bias_mean", ascending=False)
    )

    std = standard[
        [
            "model_id",
            "dataset",
            "moral_bias_mean",
            "yes_no_bias",
            "omission_bias",
        ]
    ].rename(
        columns={
            "moral_bias_mean": "standard_moral_bias_mean",
            "yes_no_bias": "standard_yes_no_bias",
            "omission_bias": "standard_omission_bias",
        }
    )
    moral_methods = moral_complete[~moral_complete["method_condition"].eq("standard")].copy()
    moral_resp = moral_methods.merge(std, on=["model_id", "dataset"], how="inner")
    moral_resp["moral_bias_reduction"] = (
        moral_resp["standard_moral_bias_mean"] - moral_resp["moral_bias_mean"]
    )
    moral_resp["yes_no_bias_reduction"] = (
        moral_resp["standard_yes_no_bias"] - moral_resp["yes_no_bias"]
    )
    moral_resp["omission_bias_reduction"] = (
        moral_resp["standard_omission_bias"] - moral_resp["omission_bias"]
    )
    moral_resp = moral_resp.sort_values("moral_bias_reduction", ascending=False)

    syc_standard = syc_complete[syc_complete["method_condition"].eq("standard")][
        [
            "model_id",
            "dataset",
            "sycophancy_accuracy",
            "wrong_belief_agreement_rate",
        ]
    ].rename(
        columns={
            "sycophancy_accuracy": "standard_sycophancy_accuracy",
            "wrong_belief_agreement_rate": "standard_wrong_belief_agreement_rate",
        }
    )
    syc_methods = syc_complete[~syc_complete["method_condition"].eq("standard")].copy()
    syc_resp = syc_methods.merge(syc_standard, on=["model_id", "dataset"], how="inner")
    syc_resp["sycophancy_accuracy_gain"] = (
        syc_resp["sycophancy_accuracy"] - syc_resp["standard_sycophancy_accuracy"]
    )
    syc_resp["wrong_belief_agreement_reduction"] = (
        syc_resp["standard_wrong_belief_agreement_rate"]
        - syc_resp["wrong_belief_agreement_rate"]
    )
    syc_resp = syc_resp.sort_values("sycophancy_accuracy_gain", ascending=False)

    v4_snapshot = completed[
        completed["model_id"].isin(["deepseek_v4pro", "deepseek_v4flash"])
    ].copy()
    v4_snapshot = v4_snapshot.sort_values(["model_id", "dataset", "method_condition"])

    completed.to_csv(REPORT_DIR / "interim_completed_cells.csv", index=False)
    standard_fingerprints.to_csv(REPORT_DIR / "interim_completed_standard_fingerprints.csv", index=False)
    moral_resp.to_csv(REPORT_DIR / "interim_completed_moral_responsiveness.csv", index=False)
    syc_resp.to_csv(REPORT_DIR / "interim_completed_sycophancy_responsiveness.csv", index=False)

    lines = [
        "# Interim Completed-Cell Bias Fingerprint Report",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Scope",
        "",
        "This interim report only uses completed dataset-method cells.",
        "For classic moral datasets, a completed cell requires 6 dilemmas x 3 framings x 56 repetitions = 1008 trials.",
        "For sycophancy, a completed cell requires 48 items x 24 repetitions = 1152 trials.",
        "Incomplete cells are excluded from responsiveness conclusions.",
        "",
        "## Completed Cell Counts",
        "",
        f"- Completed classic moral cells: {len(moral_complete)}",
        f"- Completed sycophancy cells: {len(syc_complete)}",
        f"- Total completed cells used here: {len(completed)}",
        "",
        "## Standard Bias Fingerprints",
        "",
        to_markdown(
            standard_fingerprints,
            [
                "model_id",
                "datasets",
                "moral_bias_mean",
                "yes_no_bias",
                "omission_bias",
                "valid_rate",
            ],
        ),
        "",
        "## Moral Debias Responsiveness",
        "",
        to_markdown(
            moral_resp,
            [
                "model_id",
                "dataset",
                "method_condition",
                "standard_moral_bias_mean",
                "moral_bias_mean",
                "moral_bias_reduction",
                "yes_no_bias_reduction",
                "omission_bias_reduction",
                "median_latency_seconds",
            ],
        ),
        "",
        "## Sycophancy Debias Responsiveness",
        "",
        to_markdown(
            syc_resp,
            [
                "model_id",
                "dataset",
                "method_condition",
                "standard_sycophancy_accuracy",
                "sycophancy_accuracy",
                "sycophancy_accuracy_gain",
                "standard_wrong_belief_agreement_rate",
                "wrong_belief_agreement_rate",
                "wrong_belief_agreement_reduction",
            ],
        ),
        "",
        "## DeepSeek V4 Interim Snapshot",
        "",
        to_markdown(
            v4_snapshot,
            [
                "model_id",
                "dataset",
                "method_condition",
                "trials",
                "valid_rate",
                "moral_bias_mean",
                "yes_no_bias",
                "omission_bias",
                "median_latency_seconds",
                "median_completion_tokens",
            ],
        ),
        "",
    ]
    (REPORT_DIR / "interim_completed_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(
        {
            "report": str(REPORT_DIR / "interim_completed_report.md"),
            "completed_moral_cells": int(len(moral_complete)),
            "completed_sycophancy_cells": int(len(syc_complete)),
            "moral_responsiveness_rows": int(len(moral_resp)),
            "sycophancy_responsiveness_rows": int(len(syc_resp)),
        }
    )


if __name__ == "__main__":
    main()
