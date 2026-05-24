from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "reports" / "model_bias_fingerprint_eval"
METADATA_PATH = PROJECT_ROOT / "data" / "derived" / "model_metadata.csv"


def fmt(value: object, digits: int = 3) -> str:
    if pd.isna(value):
        return "NA"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def md_table(frame: pd.DataFrame, columns: list[str]) -> str:
    if frame.empty:
        return "No rows.\n"
    data = frame.loc[:, columns].copy()
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in data.iterrows():
        lines.append("| " + " | ".join(fmt(row[col]) for col in columns) + " |")
    return "\n".join(lines) + "\n"


def read_csv(name: str) -> pd.DataFrame:
    path = REPORT_DIR / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def add_metadata(frame: pd.DataFrame, metadata: pd.DataFrame) -> pd.DataFrame:
    if frame.empty or "model_id" not in frame.columns:
        return frame
    return frame.merge(metadata, on="model_id", how="left", suffixes=("", "_meta"))


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    metadata = pd.read_csv(METADATA_PATH)

    method_summary = add_metadata(read_csv("model_method_bias_summary.csv"), metadata)
    inventory = add_metadata(read_csv("run_inventory.csv"), metadata)
    responsiveness = add_metadata(read_csv("interim_completed_moral_responsiveness.csv"), metadata)
    syc_resp = add_metadata(read_csv("interim_completed_sycophancy_responsiveness.csv"), metadata)
    polarity_model = add_metadata(read_csv("polarity_interim_local_api_model_summary.csv"), metadata)
    polarity_task = add_metadata(read_csv("polarity_interim_local_api_task_summary.csv"), metadata)

    api_method = method_summary[method_summary["deployment"].eq("api")].copy()
    api_inventory = inventory[inventory["deployment"].eq("api")].copy() if not inventory.empty else pd.DataFrame()
    api_responsiveness = responsiveness[responsiveness["deployment"].eq("api")].copy()
    api_syc_resp = syc_resp[syc_resp["deployment"].eq("api")].copy() if not syc_resp.empty else pd.DataFrame()
    api_polarity_model = polarity_model[polarity_model["deployment"].eq("api")].copy()
    api_polarity_task = polarity_task[polarity_task["deployment"].eq("api")].copy()

    moral_standard_all = api_method[
        api_method["method_condition"].eq("standard")
        & api_method["dataset"].isin(["exp2", "exp3"])
        & api_method["moral_bias_mean"].notna()
    ].copy()
    moral_standard = moral_standard_all[
        moral_standard_all["analysis_tier"].isin(["full", "partial"])
        & (pd.to_numeric(moral_standard_all["trials"], errors="coerce") >= 1000)
        & (pd.to_numeric(moral_standard_all["moral_items"], errors="coerce") >= 6)
    ].copy()
    moral_standard = moral_standard.sort_values(
        ["dataset", "moral_bias_mean", "model_id"], ascending=[True, False, True]
    )

    model_level_standard = (
        moral_standard.groupby(["model_id", "provider_family", "model_line", "variant_type"], dropna=False)
        .agg(
            datasets=("dataset", lambda s: ",".join(sorted(map(str, s.unique())))),
            dataset_cells=("dataset", "nunique"),
            moral_bias_mean=("moral_bias_mean", "mean"),
            yes_no_bias=("yes_no_bias", "mean"),
            omission_bias=("omission_bias", "mean"),
            valid_rate=("valid_rate", "mean"),
        )
        .reset_index()
        .sort_values("moral_bias_mean", ascending=False)
    )

    api_responsiveness = api_responsiveness.sort_values("moral_bias_reduction", ascending=False)
    method_family = (
        api_responsiveness.groupby(["provider_family", "method_condition"], dropna=False)
        .agg(
            cells=("dataset", "count"),
            moral_bias_reduction=("moral_bias_reduction", "mean"),
            yes_no_bias_reduction=("yes_no_bias_reduction", "mean"),
            omission_bias_reduction=("omission_bias_reduction", "mean"),
            median_latency_seconds=("median_latency_seconds", "median"),
        )
        .reset_index()
        .sort_values(["moral_bias_reduction"], ascending=False)
    )

    syc_summary = api_method[
        api_method["dataset"].eq("sycophancy") & api_method["sycophancy_accuracy"].notna()
    ].copy()
    syc_summary = syc_summary.sort_values(["model_id", "method_condition"])

    api_outputs = {
        "api_run_inventory.csv": api_inventory,
        "api_moral_standard_by_dataset.csv": moral_standard,
        "api_moral_standard_by_model.csv": model_level_standard,
        "api_moral_debias_responsiveness.csv": api_responsiveness,
        "api_moral_method_by_family.csv": method_family,
        "api_sycophancy_summary.csv": syc_summary,
        "api_sycophancy_responsiveness.csv": api_syc_resp,
        "api_polarity_model_summary.csv": api_polarity_model,
        "api_polarity_task_summary.csv": api_polarity_task,
    }
    for filename, frame in api_outputs.items():
        frame.to_csv(REPORT_DIR / filename, index=False)

    report: list[str] = []
    report.append("# API Results Analysis\n")
    report.append("Generated: 2026-04-28\n")
    report.append("Scope: API models only. Local open-weight baselines and adapters are excluded except where used as context in separate reports.\n")

    report.append("## Run Coverage\n")
    inv_cols = [
        "run",
        "model_id",
        "analysis_tier",
        "rows",
        "expected_rows",
        "datasets",
        "methods",
        "valid_rate",
    ]
    if not api_inventory.empty:
        inv = api_inventory.copy()
        inv = inv.rename(columns={"source_run": "run"})
        inv = inv[[col for col in inv_cols if col in inv.columns]].sort_values(["model_id", "run"])
        report.append(md_table(inv, [col for col in inv_cols if col in inv.columns]))
    else:
        report.append("No API inventory rows found.\n")

    report.append("## Standard Moral Framing Fingerprint\n")
    report.append("Lower `moral_bias_mean` is better. These are standard-prompt results only.\n")
    report.append(
        md_table(
            model_level_standard,
            [
                "model_id",
                "provider_family",
                "datasets",
                "moral_bias_mean",
                "yes_no_bias",
                "omission_bias",
                "valid_rate",
            ],
        )
    )

    report.append("## Dataset-Level Moral Fingerprints\n")
    report.append(
        md_table(
            moral_standard,
            [
                "model_id",
                "dataset",
                "analysis_tier",
                "trials",
                "valid_rate",
                "moral_bias_mean",
                "yes_no_bias",
                "omission_bias",
                "yes_no_bias_signed",
                "omission_bias_signed",
            ],
        )
    )

    report.append("## Debias Responsiveness\n")
    report.append("Higher `moral_bias_reduction` is better. Negative values mean the method worsened framing bias.\n")
    report.append(
        md_table(
            api_responsiveness,
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
        )
    )

    report.append("## Method Response By API Family\n")
    report.append(
        md_table(
            method_family,
            [
                "provider_family",
                "method_condition",
                "cells",
                "moral_bias_reduction",
                "yes_no_bias_reduction",
                "omission_bias_reduction",
                "median_latency_seconds",
            ],
        )
    )

    report.append("## Sycophancy\n")
    if not syc_summary.empty:
        report.append(
            md_table(
                syc_summary,
                [
                    "model_id",
                    "method_condition",
                    "analysis_tier",
                    "sycophancy_trials",
                    "sycophancy_accuracy",
                    "aligned_accuracy",
                    "conflict_accuracy",
                    "wrong_belief_agreement_rate",
                    "median_latency_seconds",
                ],
            )
        )
    else:
        report.append("No API sycophancy rows available.\n")

    report.append("## Polarity / Negation Bias\n")
    report.append("DeepSeek V4 polarity rows are currently partial because full API runs were paused.\n")
    if not api_polarity_model.empty:
        report.append(
            md_table(
                api_polarity_model,
                [
                    "model_id",
                    "provider_family",
                    "method_condition",
                    "task_families",
                    "polarity_gap_abs",
                    "accuracy_mean",
                ],
            )
        )
    else:
        report.append("No API polarity rows available.\n")

    report.append("## Main Findings\n")
    report.append("1. DeepSeek-family API models show the largest raw moral framing bias under standard prompting, especially V4-Pro and V4-Flash on Exp2.\n")
    report.append("2. Debate has the strongest raw effect on DeepSeek V4-Pro, but critique-revise is the better cost-adjusted choice because it is faster and still removes most of the bias.\n")
    report.append("3. V4-Flash responds better to critique-revise than debate, so even within one model family the best debias method is variant-specific.\n")
    report.append("4. Gemini 2.5 Flash is dataset-sensitive: low Exp2 standard bias but high Exp3 standard bias, and debate helps Exp3 while slightly worsening Exp2.\n")
    report.append("5. Aliyun Qwen3.6 is medium-bias overall; debate helps more on Exp3 than Exp2.\n")
    report.append("6. GLM-5.1 Exp3 shows high standard bias and lower valid rate under debate, so its debate results should be treated cautiously.\n")
    report.append("7. DeepSeek chat sycophancy is strongly improved by critique-revise, reducing wrong-belief agreement from 0.125 to 0.000.\n")
    report.append("8. Current partial polarity results suggest DeepSeek V4-Pro/Flash do not fail simple positive/negative question equivalence, meaning their moral yes-no bias is not just a simple negation-comprehension bug.\n")

    report.append("## Recommended Next Analyses\n")
    report.append("1. Complete DeepSeek V4-Pro/V4-Flash polarity full runs to verify the partial zero-gap finding.\n")
    report.append("2. Run sycophancy full for V4-Pro/V4-Flash because pilot V4-Pro standard had high wrong-belief agreement.\n")
    report.append("3. Fit a model-level meta-regression where outcome is `bias_reduction` and predictors are `provider_family`, `method_condition`, `bias_type`, and baseline bias.\n")
    report.append("4. Separate conclusions by dataset: Exp2 and Exp3 often differ enough that pooled averages hide the mechanism.\n")

    (REPORT_DIR / "api_results_analysis_report.md").write_text("\n".join(report), encoding="utf-8")

    print(REPORT_DIR / "api_results_analysis_report.md")


if __name__ == "__main__":
    main()
