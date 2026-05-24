from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_ROOT = PROJECT_ROOT / "results"
REPORT_DIR = PROJECT_ROOT / "reports" / "debias_method_pilot"

RUNS = {
    "pilot_debias_methods_deepseek_v4pro": "deepseek_v4pro",
    "pilot_debias_methods_deepseek_v4flash": "deepseek_v4flash",
    "pilot_debias_methods_deepseek_chat": "deepseek_chat",
}

METHODS = [
    "standard",
    "debate",
    "critique_revise",
    "self_debias_reprompt",
    "counterfactual_consistency_vote",
    "constitutional_critic",
    "anti_sycophancy_truth_first",
    "frame_invariant_rationale",
]


def as_bool(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().isin(["true", "1", "yes", "t"])


def load_trials() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for run_name, model_id in RUNS.items():
        path = RESULTS_ROOT / run_name / "raw_trials.csv"
        frame = pd.read_csv(path, on_bad_lines="skip")
        frame["source_run"] = run_name
        frame["model_id"] = model_id
        frame["valid"] = as_bool(frame["valid"])
        for col in ["endorse_original_action", "latency_seconds", "prompt_tokens", "completion_tokens", "total_tokens"]:
            frame[col] = pd.to_numeric(frame[col], errors="coerce")
        for col in ["model_correct", "agrees_with_user_belief", "belief_matches_truth"]:
            frame[col] = as_bool(frame[col])
        frames.append(frame)
    return pd.concat(frames, ignore_index=True, sort=False)


def moral_item_metrics(trials: pd.DataFrame) -> pd.DataFrame:
    moral = trials[(trials["task_family"].eq("moral")) & trials["valid"]].copy()
    rows: list[dict[str, object]] = []
    for key, group in moral.groupby(["model_id", "dataset", "method_condition", "dilemma"], dropna=False):
        rates = group.groupby("framing_condition")["endorse_original_action"].mean()
        if not {"original", "yesno", "omission"} <= set(rates.index):
            continue
        yes_no = abs(float(rates["original"]) - float(rates["yesno"]))
        omission = abs(float(rates["original"]) - float(rates["omission"]))
        rows.append(
            {
                "model_id": key[0],
                "dataset": key[1],
                "method_condition": key[2],
                "dilemma": key[3],
                "yes_no_bias_abs": yes_no,
                "omission_bias_abs": omission,
                "moral_bias_mean": (yes_no + omission) / 2,
            }
        )
    return pd.DataFrame(rows)


def method_summary(trials: pd.DataFrame, moral_items: pd.DataFrame) -> pd.DataFrame:
    cost = (
        trials.groupby(["model_id", "dataset", "method_condition"], dropna=False)
        .agg(
            trials=("dataset", "size"),
            valid_rate=("valid", "mean"),
            median_latency_seconds=("latency_seconds", "median"),
            median_prompt_tokens=("prompt_tokens", "median"),
            median_completion_tokens=("completion_tokens", "median"),
            median_total_tokens=("total_tokens", "median"),
        )
        .reset_index()
    )
    moral = (
        moral_items.groupby(["model_id", "dataset", "method_condition"], dropna=False)
        .agg(
            moral_items=("dilemma", "nunique"),
            yes_no_bias_abs=("yes_no_bias_abs", "mean"),
            omission_bias_abs=("omission_bias_abs", "mean"),
            moral_bias_mean=("moral_bias_mean", "mean"),
        )
        .reset_index()
    )

    syc = trials[(trials["task_family"].eq("sycophancy")) & trials["valid"]].copy()
    syc_rows: list[dict[str, object]] = []
    for key, group in syc.groupby(["model_id", "dataset", "method_condition"], dropna=False):
        aligned = group[group["belief_matches_truth"]]
        conflict = group[~group["belief_matches_truth"]]
        syc_rows.append(
            {
                "model_id": key[0],
                "dataset": key[1],
                "method_condition": key[2],
                "sycophancy_accuracy": group["model_correct"].mean(),
                "aligned_accuracy": aligned["model_correct"].mean(),
                "conflict_accuracy": conflict["model_correct"].mean(),
                "wrong_belief_agreement_rate": conflict["agrees_with_user_belief"].mean(),
            }
        )
    syc_summary = pd.DataFrame(syc_rows)

    summary = cost.merge(moral, on=["model_id", "dataset", "method_condition"], how="left")
    summary = summary.merge(syc_summary, on=["model_id", "dataset", "method_condition"], how="left")
    return summary


def add_reductions(summary: pd.DataFrame) -> pd.DataFrame:
    baseline_cols = [
        "model_id",
        "dataset",
        "moral_bias_mean",
        "yes_no_bias_abs",
        "omission_bias_abs",
        "sycophancy_accuracy",
        "wrong_belief_agreement_rate",
        "median_latency_seconds",
        "median_total_tokens",
    ]
    baseline = summary[summary["method_condition"].eq("standard")][baseline_cols].rename(
        columns={
            "moral_bias_mean": "standard_moral_bias_mean",
            "yes_no_bias_abs": "standard_yes_no_bias_abs",
            "omission_bias_abs": "standard_omission_bias_abs",
            "sycophancy_accuracy": "standard_sycophancy_accuracy",
            "wrong_belief_agreement_rate": "standard_wrong_belief_agreement_rate",
            "median_latency_seconds": "standard_latency_seconds",
            "median_total_tokens": "standard_total_tokens",
        }
    )
    merged = summary.merge(baseline, on=["model_id", "dataset"], how="left")
    merged["moral_bias_reduction"] = merged["standard_moral_bias_mean"] - merged["moral_bias_mean"]
    merged["moral_bias_reduction_pct"] = merged["moral_bias_reduction"] / merged["standard_moral_bias_mean"]
    merged["yes_no_bias_reduction"] = merged["standard_yes_no_bias_abs"] - merged["yes_no_bias_abs"]
    merged["omission_bias_reduction"] = merged["standard_omission_bias_abs"] - merged["omission_bias_abs"]
    merged["sycophancy_accuracy_gain"] = merged["sycophancy_accuracy"] - merged["standard_sycophancy_accuracy"]
    merged["wrong_belief_agreement_reduction"] = (
        merged["standard_wrong_belief_agreement_rate"] - merged["wrong_belief_agreement_rate"]
    )
    merged["wrong_belief_reduction_pct"] = (
        merged["wrong_belief_agreement_reduction"] / merged["standard_wrong_belief_agreement_rate"]
    )
    merged["latency_multiplier_vs_standard"] = merged["median_latency_seconds"] / merged["standard_latency_seconds"]
    merged["token_multiplier_vs_standard"] = merged["median_total_tokens"] / merged["standard_total_tokens"]
    return merged


def aggregate_methods(reduced: pd.DataFrame) -> pd.DataFrame:
    candidates = reduced[~reduced["method_condition"].eq("standard")].copy()
    moral = candidates[candidates["dataset"].isin(["exp2", "exp3"])].copy()
    syc = candidates[candidates["dataset"].eq("sycophancy")].copy()

    moral_agg = (
        moral.groupby("method_condition", dropna=False)
        .agg(
            moral_cells=("dataset", "size"),
            moral_bias_mean=("moral_bias_mean", "mean"),
            moral_bias_reduction=("moral_bias_reduction", "mean"),
            moral_bias_reduction_pct=("moral_bias_reduction_pct", "mean"),
            valid_rate=("valid_rate", "mean"),
            median_latency_seconds=("median_latency_seconds", "median"),
            median_total_tokens=("median_total_tokens", "median"),
            latency_multiplier_vs_standard=("latency_multiplier_vs_standard", "median"),
            token_multiplier_vs_standard=("token_multiplier_vs_standard", "median"),
        )
        .reset_index()
    )
    syc_agg = (
        syc.groupby("method_condition", dropna=False)
        .agg(
            sycophancy_cells=("dataset", "size"),
            sycophancy_accuracy=("sycophancy_accuracy", "mean"),
            wrong_belief_agreement_rate=("wrong_belief_agreement_rate", "mean"),
            wrong_belief_agreement_reduction=("wrong_belief_agreement_reduction", "mean"),
            wrong_belief_reduction_pct=("wrong_belief_reduction_pct", "mean"),
        )
        .reset_index()
    )
    agg = moral_agg.merge(syc_agg, on="method_condition", how="outer")
    for col in ["moral_bias_reduction_pct", "wrong_belief_reduction_pct"]:
        agg[col] = agg[col].replace([float("inf"), -float("inf")], pd.NA)

    # Lower cost is better; combine effect and cost into an exploratory score.
    agg["effect_score"] = agg[["moral_bias_reduction_pct", "wrong_belief_reduction_pct"]].mean(axis=1, skipna=True)
    agg["cost_penalty"] = agg[["latency_multiplier_vs_standard", "token_multiplier_vs_standard"]].mean(axis=1, skipna=True)
    agg["value_score"] = agg["effect_score"] / agg["cost_penalty"]
    return agg.sort_values(["value_score", "effect_score"], ascending=False)


def recommend_methods(agg: pd.DataFrame) -> pd.DataFrame:
    pool = agg[
        agg["method_condition"].isin(
            [
                "self_debias_reprompt",
                "counterfactual_consistency_vote",
                "constitutional_critic",
                "anti_sycophancy_truth_first",
                "frame_invariant_rationale",
            ]
        )
    ].copy()
    rows = []
    moral_pick = pool.sort_values(["moral_bias_reduction_pct", "value_score"], ascending=False).iloc[0]
    syc_pick = pool.sort_values(["wrong_belief_agreement_reduction", "value_score"], ascending=False).iloc[0]
    value_pick = pool.sort_values(["value_score", "effect_score"], ascending=False).iloc[0]
    for reason, row in [
        ("best_moral_framing_reduction", moral_pick),
        ("best_sycophancy_reduction", syc_pick),
        ("best_cost_adjusted_value", value_pick),
    ]:
        item = row.to_dict()
        item["recommendation_reason"] = reason
        rows.append(item)
    recommended = pd.DataFrame(rows).drop_duplicates(subset=["method_condition"], keep="first")
    if len(recommended) < 3:
        used = set(recommended["method_condition"])
        for _, row in pool.sort_values(["effect_score", "value_score"], ascending=False).iterrows():
            if row["method_condition"] in used:
                continue
            item = row.to_dict()
            item["recommendation_reason"] = "next_best_effect_score"
            rows.append(item)
            used.add(row["method_condition"])
            if len(used) >= 3:
                break
        recommended = pd.DataFrame(rows).drop_duplicates(subset=["method_condition"], keep="first")
    return recommended


def fmt(value: object, digits: int = 3) -> str:
    if pd.isna(value):
        return "NA"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def md_table(frame: pd.DataFrame, columns: list[str], max_rows: int = 40) -> str:
    if frame.empty:
        return "No rows.\n"
    rows = frame.loc[:, columns].head(max_rows)
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in rows.iterrows():
        lines.append("| " + " | ".join(fmt(row[col]) for col in columns) + " |")
    return "\n".join(lines) + "\n"


def write_report(summary: pd.DataFrame, reduced: pd.DataFrame, agg: pd.DataFrame, recommended: pd.DataFrame) -> None:
    lines = [
        "# Debias Method Pilot Report",
        "",
        "Scope: DeepSeek V4-Pro, V4-Flash, and DeepSeek Chat pilot runs over exp2, exp3, and sycophancy.",
        "",
        "## Recommended New Methods For Full Confirmatory",
        "",
        md_table(
            recommended,
            [
                "method_condition",
                "recommendation_reason",
                "moral_bias_reduction_pct",
                "wrong_belief_agreement_reduction",
                "latency_multiplier_vs_standard",
                "token_multiplier_vs_standard",
                "value_score",
            ],
        ),
        "",
        "## Aggregate Method Ranking",
        "",
        md_table(
            agg,
            [
                "method_condition",
                "moral_bias_reduction_pct",
                "wrong_belief_agreement_reduction",
                "sycophancy_accuracy",
                "latency_multiplier_vs_standard",
                "token_multiplier_vs_standard",
                "value_score",
            ],
            max_rows=20,
        ),
        "",
        "## Model-Level Detailed Results",
        "",
        md_table(
            reduced.sort_values(["model_id", "dataset", "method_condition"]),
            [
                "model_id",
                "dataset",
                "method_condition",
                "valid_rate",
                "moral_bias_mean",
                "moral_bias_reduction",
                "sycophancy_accuracy",
                "wrong_belief_agreement_rate",
                "median_latency_seconds",
                "median_total_tokens",
            ],
            max_rows=120,
        ),
    ]
    (REPORT_DIR / "debias_method_pilot_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    trials = load_trials()
    moral_items = moral_item_metrics(trials)
    summary = method_summary(trials, moral_items)
    reduced = add_reductions(summary)
    agg = aggregate_methods(reduced)
    recommended = recommend_methods(agg)

    trials.to_csv(REPORT_DIR / "pilot_trials_combined.csv", index=False)
    moral_items.to_csv(REPORT_DIR / "pilot_moral_item_metrics.csv", index=False)
    summary.to_csv(REPORT_DIR / "pilot_method_summary.csv", index=False)
    reduced.to_csv(REPORT_DIR / "pilot_method_reductions.csv", index=False)
    agg.to_csv(REPORT_DIR / "pilot_method_aggregate_ranking.csv", index=False)
    recommended.to_csv(REPORT_DIR / "pilot_recommended_methods.csv", index=False)
    write_report(summary, reduced, agg, recommended)
    print(REPORT_DIR)


if __name__ == "__main__":
    main()
