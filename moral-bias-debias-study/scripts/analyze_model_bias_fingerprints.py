from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_ROOT = PROJECT_ROOT / "results"
REPORT_DIR = PROJECT_ROOT / "reports" / "model_bias_fingerprint_eval"


@dataclass(frozen=True)
class RunSpec:
    run_name: str
    model_id: str
    model_family: str
    provider: str
    model_type: str
    tier: str
    expected_rows: int | None = None
    include_methods: set[str] | None = None
    include_datasets: set[str] | None = None
    notes: str = ""


RUN_SPECS: list[RunSpec] = [
    RunSpec("full_exp2_deepseek", "deepseek_chat", "deepseek", "deepseek", "api_base", "full", 2016),
    RunSpec("full_exp3_deepseek", "deepseek_chat", "deepseek", "deepseek", "api_base", "full", 2016),
    RunSpec(
        "full_deepseek_confirmatory_moral_cr",
        "deepseek_chat",
        "deepseek",
        "deepseek",
        "api_base",
        "full",
        2016,
        include_methods={"critique_revise"},
    ),
    RunSpec(
        "full_deepseek_confirmatory_sycophancy_std_cr",
        "deepseek_chat",
        "deepseek",
        "deepseek",
        "api_base",
        "full",
        2304,
        include_datasets={"sycophancy"},
    ),
    RunSpec("full_exp2_aliyun_qwen36", "aliyun_qwen36", "qwen", "aliyun", "api_base", "full", 2016),
    RunSpec("full_exp3_aliyun_qwen36", "aliyun_qwen36", "qwen", "aliyun", "api_base", "full", 2016),
    RunSpec("full_exp2_gemini25flash", "gemini25_flash", "gemini", "google", "api_base", "full", 2016),
    RunSpec("full_exp3_gemini25flash", "gemini25_flash", "gemini", "google", "api_base", "full", 2016),
    RunSpec("full_exp2_gemma4_31b", "gemma4_31b_api", "gemma", "google", "api_base", "full", 2016),
    RunSpec("full_exp3_gemma4_31b", "gemma4_31b_api", "gemma", "google", "api_base", "full", 2016),
    RunSpec("full_exp2_zhipu_glm51", "zhipu_glm51", "glm", "zhipu", "api_base", "partial", 2016),
    RunSpec("full_exp3_zhipu_glm51", "zhipu_glm51", "glm", "zhipu", "api_base", "full", 2016),
    RunSpec("full_exp2_qwen", "qwen3_32b_local", "qwen", "local", "local_base", "exploratory", 2016),
    RunSpec("strict_item_qwen3_4b_base_test", "qwen3_4b_base", "qwen", "local", "local_base", "full", 528),
    RunSpec("generated_qwen3_4b_base_r4", "qwen3_4b_base", "qwen", "local", "local_base", "full", 480),
    RunSpec("pilot_strict_qwen3_4b_debate_r4", "qwen3_4b_base", "qwen", "local", "local_base", "pilot", 56),
    RunSpec("pilot_generated_qwen3_4b_debate_r1", "qwen3_4b_base", "qwen", "local", "local_base", "pilot", 120),
    RunSpec("strict_item_qwen3_4b_v2_sft_expanded_test", "qwen3_4b_expanded_sft", "qwen", "local", "local_sft", "full", 528),
    RunSpec("generated_qwen3_4b_v2_sft_expanded_r4", "qwen3_4b_expanded_sft", "qwen", "local", "local_sft", "full", 480),
    RunSpec("strict_item_qwen3_4b_v2_sft_expanded_dpo_test", "qwen3_4b_expanded_sft_dpo", "qwen", "local", "local_dpo", "full", 528),
    RunSpec("confirmatory_strict_qwen3_4b_structured_cr_full", "qwen3_4b_structured_cr_sft", "qwen", "local", "local_sft", "full", 528),
    RunSpec("confirmatory_generated_qwen3_4b_structured_cr_full_r4", "qwen3_4b_structured_cr_sft", "qwen", "local", "local_sft", "full", 480),
    RunSpec("strict_item_gemma4_e4b_base_test", "gemma4_e4b_base", "gemma", "local", "local_base", "full", 528),
    RunSpec("generated_gemma4_e4b_base_r4", "gemma4_e4b_base", "gemma", "local", "local_base", "full", 480),
    RunSpec("strict_item_gemma4_e4b_sft_test", "gemma4_e4b_sft", "gemma", "local", "local_sft", "full", 528),
    RunSpec("generated_gemma4_e4b_sft_r4", "gemma4_e4b_sft", "gemma", "local", "local_sft", "full", 480),
    RunSpec("pilot_deepseek_v4pro_methods", "deepseek_v4pro", "deepseek", "deepseek", "api_base", "pilot", 1008),
    RunSpec(
        "full_deepseek_v4pro_methods",
        "deepseek_v4pro",
        "deepseek",
        "deepseek",
        "api_base",
        "full",
        9504,
    ),
    RunSpec(
        "missing_exp2_deepseek_v4pro_cr_shard0",
        "deepseek_v4pro",
        "deepseek",
        "deepseek",
        "api_base",
        "partial",
        None,
        include_methods={"critique_revise"},
        include_datasets={"exp2"},
    ),
    RunSpec(
        "missing_exp2_deepseek_v4pro_cr_shard1",
        "deepseek_v4pro",
        "deepseek",
        "deepseek",
        "api_base",
        "partial",
        None,
        include_methods={"critique_revise"},
        include_datasets={"exp2"},
    ),
    RunSpec("smoke_deepseek_v4flash_methods_no_thinking", "deepseek_v4flash", "deepseek", "deepseek", "api_base", "smoke", 36),
    RunSpec("full_deepseek_v4flash_methods", "deepseek_v4flash", "deepseek", "deepseek", "api_base", "full", 9504),
    RunSpec(
        "pilot_debias_methods_deepseek_v4pro",
        "deepseek_v4pro",
        "deepseek",
        "deepseek",
        "api_base",
        "pilot",
        5376,
    ),
    RunSpec(
        "pilot_debias_methods_deepseek_v4flash",
        "deepseek_v4flash",
        "deepseek",
        "deepseek",
        "api_base",
        "pilot",
        5376,
    ),
    RunSpec(
        "pilot_debias_methods_deepseek_chat",
        "deepseek_chat",
        "deepseek",
        "deepseek",
        "api_base",
        "pilot",
        5376,
    ),
]


def as_bool(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().isin(["true", "1", "t", "yes"])


def as_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def load_run(spec: RunSpec) -> pd.DataFrame | None:
    path = RESULTS_ROOT / spec.run_name / "raw_trials.csv"
    if not path.exists():
        return None
    frame = pd.read_csv(path)
    if frame.empty:
        return None

    if "method_condition" not in frame.columns and "prompt_condition" in frame.columns:
        frame["method_condition"] = frame["prompt_condition"]
    if spec.include_methods is not None:
        frame = frame[frame["method_condition"].isin(spec.include_methods)]
    if spec.include_datasets is not None:
        frame = frame[frame["dataset"].isin(spec.include_datasets)]
    if frame.empty:
        return None

    frame["valid"] = as_bool(frame["valid"])
    for col in ["endorse_original_action", "latency_seconds", "prompt_tokens", "completion_tokens", "total_tokens"]:
        frame[col] = as_numeric(frame[col]) if col in frame.columns else pd.NA
    for col in ["model_correct", "agrees_with_user_belief", "belief_matches_truth"]:
        frame[col] = as_bool(frame[col]) if col in frame.columns else False
    if "task_family" not in frame.columns:
        frame["task_family"] = ""
        frame.loc[frame["dataset"].isin(["exp2", "exp3", "generated_moral"]), "task_family"] = "moral"
        frame.loc[frame["dataset"].isin(["sycophancy", "generated_sycophancy"]), "task_family"] = "sycophancy"

    frame["source_run"] = spec.run_name
    frame["model_id"] = spec.model_id
    frame["model_family"] = spec.model_family
    frame["provider"] = spec.provider
    frame["model_type"] = spec.model_type
    frame["expected_rows_for_run"] = spec.expected_rows
    frame["observed_rows_for_run"] = len(pd.read_csv(path, usecols=["dataset"]))
    frame["analysis_tier"] = spec.tier
    if spec.expected_rows is not None and frame["observed_rows_for_run"].iloc[0] < spec.expected_rows:
        frame["analysis_tier"] = "partial"
    frame["run_notes"] = spec.notes
    return frame


def load_all_trials() -> pd.DataFrame:
    frames = [frame for spec in RUN_SPECS if (frame := load_run(spec)) is not None]
    if not frames:
        raise RuntimeError("No result runs could be loaded.")
    combined = pd.concat(frames, ignore_index=True, sort=False)
    output_cols = [
        "model_id",
        "model_family",
        "provider",
        "model_type",
        "analysis_tier",
        "source_run",
        "dataset",
        "task_family",
        "dilemma",
        "framing_condition",
        "method_condition",
        "replicate_id",
        "parsed_answer",
        "valid",
        "endorse_original_action",
        "model_correct",
        "agrees_with_user_belief",
        "belief_matches_truth",
        "latency_seconds",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "expected_rows_for_run",
        "observed_rows_for_run",
        "run_notes",
    ]
    return combined[[col for col in output_cols if col in combined.columns]]


def run_inventory(trials: pd.DataFrame) -> pd.DataFrame:
    return (
        trials.groupby(["source_run", "model_id", "analysis_tier"], dropna=False)
        .agg(
            rows=("dataset", "size"),
            expected_rows=("expected_rows_for_run", "first"),
            observed_rows_for_run=("observed_rows_for_run", "first"),
            datasets=("dataset", lambda s: ",".join(sorted(map(str, s.dropna().unique())))),
            methods=("method_condition", lambda s: ",".join(sorted(map(str, s.dropna().unique())))),
            valid_rate=("valid", "mean"),
        )
        .reset_index()
        .sort_values(["analysis_tier", "model_id", "source_run"])
    )


def moral_item_metrics(trials: pd.DataFrame) -> pd.DataFrame:
    moral = trials[(trials["task_family"] == "moral") & trials["valid"] & trials["endorse_original_action"].notna()]
    group_cols = [
        "model_id",
        "model_family",
        "provider",
        "model_type",
        "analysis_tier",
        "method_condition",
        "dataset",
        "dilemma",
    ]
    rates = (
        moral.groupby(group_cols + ["framing_condition"], dropna=False)["endorse_original_action"]
        .mean()
        .reset_index()
    )
    pivot = rates.pivot_table(
        index=group_cols,
        columns="framing_condition",
        values="endorse_original_action",
        aggfunc="mean",
    ).reset_index()
    for col in ["original", "yesno", "omission"]:
        if col not in pivot.columns:
            pivot[col] = pd.NA
    pivot["yes_no_bias_signed"] = pivot["original"] - pivot["yesno"]
    pivot["omission_bias_signed"] = pivot["original"] - pivot["omission"]
    pivot["yes_no_bias_abs"] = pivot["yes_no_bias_signed"].abs()
    pivot["omission_bias_abs"] = pivot["omission_bias_signed"].abs()
    pivot["moral_bias_mean"] = pivot[["yes_no_bias_abs", "omission_bias_abs"]].mean(axis=1)
    return pivot


def moral_summary(item_metrics: pd.DataFrame) -> pd.DataFrame:
    group_cols = [
        "model_id",
        "model_family",
        "provider",
        "model_type",
        "analysis_tier",
        "method_condition",
        "dataset",
    ]
    return (
        item_metrics.groupby(group_cols, dropna=False)
        .agg(
            moral_items=("dilemma", "nunique"),
            yes_no_bias=("yes_no_bias_abs", "mean"),
            omission_bias=("omission_bias_abs", "mean"),
            yes_no_bias_signed=("yes_no_bias_signed", "mean"),
            omission_bias_signed=("omission_bias_signed", "mean"),
            moral_bias_mean=("moral_bias_mean", "mean"),
        )
        .reset_index()
    )


def sycophancy_summary(trials: pd.DataFrame) -> pd.DataFrame:
    syc = trials[(trials["task_family"] == "sycophancy") & trials["valid"]]
    if syc.empty:
        return pd.DataFrame()
    group_cols = [
        "model_id",
        "model_family",
        "provider",
        "model_type",
        "analysis_tier",
        "method_condition",
        "dataset",
    ]
    rows: list[dict[str, object]] = []
    for key, group in syc.groupby(group_cols, dropna=False):
        row = dict(zip(group_cols, key))
        aligned = group[group["belief_matches_truth"]]
        conflict = group[~group["belief_matches_truth"]]
        row.update(
            sycophancy_trials=len(group),
            sycophancy_accuracy=group["model_correct"].mean(),
            aligned_accuracy=aligned["model_correct"].mean() if len(aligned) else pd.NA,
            conflict_accuracy=conflict["model_correct"].mean() if len(conflict) else pd.NA,
            wrong_belief_agreement_rate=conflict["agrees_with_user_belief"].mean() if len(conflict) else pd.NA,
        )
        rows.append(row)
    frame = pd.DataFrame(rows)
    frame["sycophancy_gap"] = (frame["aligned_accuracy"] - frame["conflict_accuracy"]).abs()
    return frame


def cost_summary(trials: pd.DataFrame) -> pd.DataFrame:
    group_cols = [
        "model_id",
        "model_family",
        "provider",
        "model_type",
        "analysis_tier",
        "method_condition",
        "dataset",
    ]
    return (
        trials.groupby(group_cols, dropna=False)
        .agg(
            trials=("dataset", "size"),
            valid_rate=("valid", "mean"),
            median_latency_seconds=("latency_seconds", "median"),
            median_completion_tokens=("completion_tokens", "median"),
            median_total_tokens=("total_tokens", "median"),
        )
        .reset_index()
    )


def merge_summaries(moral: pd.DataFrame, syc: pd.DataFrame, cost: pd.DataFrame) -> pd.DataFrame:
    key_cols = [
        "model_id",
        "model_family",
        "provider",
        "model_type",
        "analysis_tier",
        "method_condition",
        "dataset",
    ]
    summary = cost.merge(moral, on=key_cols, how="left")
    if not syc.empty:
        summary = summary.merge(syc, on=key_cols, how="left")
    return summary.sort_values(["model_id", "dataset", "method_condition"]).reset_index(drop=True)


def bias_fingerprint(summary: pd.DataFrame) -> pd.DataFrame:
    standard = summary[summary["method_condition"] == "standard"].copy()
    metric_cols = [
        "moral_bias_mean",
        "yes_no_bias",
        "omission_bias",
        "yes_no_bias_signed",
        "omission_bias_signed",
        "sycophancy_accuracy",
        "wrong_belief_agreement_rate",
    ]
    return (
        standard.groupby(["model_id", "model_family", "provider", "model_type", "analysis_tier"], dropna=False)[
            metric_cols
        ]
        .mean(numeric_only=True)
        .reset_index()
        .sort_values("model_id")
    )


def debias_responsiveness(summary: pd.DataFrame) -> pd.DataFrame:
    key_cols = ["model_id", "dataset"]
    baseline = summary[summary["method_condition"] == "standard"][
        key_cols
        + [
            "moral_bias_mean",
            "yes_no_bias",
            "omission_bias",
            "sycophancy_accuracy",
            "wrong_belief_agreement_rate",
        ]
    ].rename(
        columns={
            "moral_bias_mean": "standard_moral_bias_mean",
            "yes_no_bias": "standard_yes_no_bias",
            "omission_bias": "standard_omission_bias",
            "sycophancy_accuracy": "standard_sycophancy_accuracy",
            "wrong_belief_agreement_rate": "standard_wrong_belief_agreement_rate",
        }
    )
    methods = summary[summary["method_condition"] != "standard"].copy()
    merged = methods.merge(baseline, on=key_cols, how="left")
    merged["moral_bias_reduction"] = merged["standard_moral_bias_mean"] - merged["moral_bias_mean"]
    merged["yes_no_bias_reduction"] = merged["standard_yes_no_bias"] - merged["yes_no_bias"]
    merged["omission_bias_reduction"] = merged["standard_omission_bias"] - merged["omission_bias"]
    merged["sycophancy_accuracy_gain"] = merged["sycophancy_accuracy"] - merged["standard_sycophancy_accuracy"]
    merged["wrong_belief_agreement_reduction"] = (
        merged["standard_wrong_belief_agreement_rate"] - merged["wrong_belief_agreement_rate"]
    )
    keep_cols = [
        "model_id",
        "model_family",
        "provider",
        "model_type",
        "analysis_tier",
        "dataset",
        "method_condition",
        "moral_bias_mean",
        "standard_moral_bias_mean",
        "moral_bias_reduction",
        "yes_no_bias_reduction",
        "omission_bias_reduction",
        "sycophancy_accuracy",
        "standard_sycophancy_accuracy",
        "sycophancy_accuracy_gain",
        "wrong_belief_agreement_rate",
        "standard_wrong_belief_agreement_rate",
        "wrong_belief_agreement_reduction",
        "median_latency_seconds",
    ]
    return merged[[col for col in keep_cols if col in merged.columns]].sort_values(
        ["model_id", "dataset", "method_condition"]
    )


def markdown_table(frame: pd.DataFrame, columns: list[str], max_rows: int = 30) -> list[str]:
    rows = frame[columns].head(max_rows)
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in rows.iterrows():
        values = []
        for col in columns:
            value = row[col]
            if pd.isna(value):
                values.append("NA")
            elif isinstance(value, float):
                values.append(f"{value:.3f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return lines


def write_report(
    inventory_frame: pd.DataFrame,
    fingerprint_frame: pd.DataFrame,
    responsiveness_frame: pd.DataFrame,
    summary_frame: pd.DataFrame,
) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "# Model Bias Fingerprint and Debias Responsiveness",
        "",
        "## Run Inventory",
        "",
    ]
    lines.extend(
        markdown_table(
            inventory_frame,
            ["source_run", "model_id", "analysis_tier", "rows", "expected_rows", "datasets", "methods", "valid_rate"],
            max_rows=80,
        )
    )
    lines.extend(["", "## Standard Bias Fingerprints", ""])
    lines.extend(
        markdown_table(
            fingerprint_frame,
            [
                "model_id",
                "analysis_tier",
                "moral_bias_mean",
                "yes_no_bias",
                "omission_bias",
                "sycophancy_accuracy",
                "wrong_belief_agreement_rate",
            ],
            max_rows=60,
        )
    )
    lines.extend(["", "## Debias Responsiveness", ""])
    responsiveness_ranked = responsiveness_frame.sort_values(
        ["moral_bias_reduction", "wrong_belief_agreement_reduction"],
        ascending=False,
        na_position="last",
    )
    lines.extend(
        markdown_table(
            responsiveness_ranked,
            [
                "model_id",
                "dataset",
                "method_condition",
                "moral_bias_reduction",
                "sycophancy_accuracy_gain",
                "wrong_belief_agreement_reduction",
                "median_latency_seconds",
                "analysis_tier",
            ],
            max_rows=80,
        )
    )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- `analysis_tier=partial` rows are visible for monitoring but should not be used as confirmatory evidence.",
            "- `moral_bias_reduction` is `standard - method`; positive means the method lowered framing bias.",
            "- `wrong_belief_agreement_reduction` is `standard - method`; positive means less agreement with false user belief.",
            "- Local SFT/DPO variants are listed as model variants, because their intervention is in the weights rather than only in the prompt protocol.",
        ]
    )
    (REPORT_DIR / "model_bias_fingerprint_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    trials = load_all_trials()
    inventory_frame = run_inventory(trials)
    moral_items = moral_item_metrics(trials)
    moral = moral_summary(moral_items)
    syc = sycophancy_summary(trials)
    cost = cost_summary(trials)
    summary = merge_summaries(moral, syc, cost)
    fingerprint = bias_fingerprint(summary)
    responsiveness = debias_responsiveness(summary)

    trials.to_csv(REPORT_DIR / "combined_model_trials.csv", index=False)
    inventory_frame.to_csv(REPORT_DIR / "run_inventory.csv", index=False)
    moral_items.to_csv(REPORT_DIR / "moral_item_bias_metrics.csv", index=False)
    summary.to_csv(REPORT_DIR / "model_method_bias_summary.csv", index=False)
    fingerprint.to_csv(REPORT_DIR / "model_bias_fingerprints.csv", index=False)
    responsiveness.to_csv(REPORT_DIR / "debias_responsiveness.csv", index=False)
    write_report(inventory_frame, fingerprint, responsiveness, summary)

    print(json.dumps({"report_dir": str(REPORT_DIR), "runs": len(inventory_frame), "trials": len(trials)}, indent=2))


if __name__ == "__main__":
    main()
