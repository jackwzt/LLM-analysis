from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "confirmatory_package" / "outputs"
TABLE_DIR = OUTPUT_DIR / "tables"
PRIMARY_METHODS = ["standard", "counterfactual_consistency_vote", "anti_sycophancy_truth_first", "debate"]


def bool_series(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().isin({"true", "1", "yes"})


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def bootstrap_ci(values: pd.Series, iterations: int = 1000, seed: int = 20260530) -> tuple[float, float]:
    clean = numeric(values).dropna().to_numpy(dtype=float)
    if len(clean) == 0:
        return np.nan, np.nan
    if len(clean) == 1:
        return float(clean[0]), float(clean[0])
    rng = np.random.default_rng(seed)
    boot = [np.mean(rng.choice(clean, size=len(clean), replace=True)) for _ in range(iterations)]
    return float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))


def load_trial_data() -> pd.DataFrame:
    path = OUTPUT_DIR / "confirmatory_trial_level.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run 02_build_confirmatory_dataset.py first.")
    frame = pd.read_csv(path, low_memory=False)
    frame["valid_response"] = bool_series(frame["valid_response"])
    frame["method_condition"] = frame["method_condition"].astype(str)
    frame = frame[frame["method_condition"].isin(PRIMARY_METHODS)].copy()
    if "analysis_tier" in frame.columns:
        full = frame[frame["analysis_tier"].astype(str).eq("confirmatory_full_cell")].copy()
        if not full.empty:
            frame = full
    return frame


def moral_item_gaps(frame: pd.DataFrame) -> pd.DataFrame:
    moral = frame[
        frame["valid_response"]
        & frame["dataset"].isin(["exp2", "exp3"])
        & frame["endorse_original_action"].notna()
        & frame["endorse_original_action"].astype(str).ne("")
    ].copy()
    if moral.empty:
        return pd.DataFrame()
    moral["endorse_original_action"] = numeric(moral["endorse_original_action"])
    rates = (
        moral.groupby(["model_id", "model_family", "dataset", "item_family_id", "method_condition", "framing_condition"], dropna=False)
        .agg(endorsement_rate=("endorse_original_action", "mean"), n=("endorse_original_action", "size"))
        .reset_index()
    )
    pivot = rates.pivot_table(
        index=["model_id", "model_family", "dataset", "item_family_id", "method_condition"],
        columns="framing_condition",
        values="endorsement_rate",
        aggfunc="mean",
    ).reset_index()
    for column in ["original", "yesno", "omission"]:
        if column not in pivot.columns:
            pivot[column] = np.nan
    pivot["yes_no_bias_abs"] = (pivot["original"] - pivot["yesno"]).abs()
    pivot["omission_bias_abs"] = (pivot["original"] - pivot["omission"]).abs()
    pivot["moral_bias_mean"] = pivot[["yes_no_bias_abs", "omission_bias_abs"]].mean(axis=1)
    return pivot


def summarize_moral(gaps: pd.DataFrame) -> pd.DataFrame:
    if gaps.empty:
        return pd.DataFrame()
    rows = []
    for keys, group in gaps.groupby(["model_id", "model_family", "dataset", "method_condition"], dropna=False):
        yes_ci = bootstrap_ci(group["yes_no_bias_abs"])
        omission_ci = bootstrap_ci(group["omission_bias_abs"])
        mean_ci = bootstrap_ci(group["moral_bias_mean"])
        rows.append(
            {
                "model_id": keys[0],
                "model_family": keys[1],
                "dataset": keys[2],
                "method_condition": keys[3],
                "n_item_families": int(group["item_family_id"].nunique()),
                "yes_no_bias_abs": group["yes_no_bias_abs"].mean(),
                "yes_no_ci_low": yes_ci[0],
                "yes_no_ci_high": yes_ci[1],
                "omission_bias_abs": group["omission_bias_abs"].mean(),
                "omission_ci_low": omission_ci[0],
                "omission_ci_high": omission_ci[1],
                "moral_bias_mean": group["moral_bias_mean"].mean(),
                "moral_bias_ci_low": mean_ci[0],
                "moral_bias_ci_high": mean_ci[1],
            }
        )
    return pd.DataFrame(rows)


def moral_reductions(summary: pd.DataFrame) -> pd.DataFrame:
    if summary.empty:
        return pd.DataFrame()
    baseline = summary[summary["method_condition"].eq("standard")][
        ["model_id", "dataset", "moral_bias_mean", "yes_no_bias_abs", "omission_bias_abs"]
    ].rename(
        columns={
            "moral_bias_mean": "standard_moral_bias_mean",
            "yes_no_bias_abs": "standard_yes_no_bias_abs",
            "omission_bias_abs": "standard_omission_bias_abs",
        }
    )
    merged = summary.merge(baseline, on=["model_id", "dataset"], how="left")
    merged["moral_bias_reduction"] = merged["standard_moral_bias_mean"] - merged["moral_bias_mean"]
    merged["moral_bias_reduction_pct"] = merged["moral_bias_reduction"] / merged["standard_moral_bias_mean"].replace(0, np.nan)
    return merged


def summarize_sycophancy(frame: pd.DataFrame) -> pd.DataFrame:
    syc = frame[frame["valid_response"] & frame["dataset"].eq("sycophancy")].copy()
    if syc.empty:
        return pd.DataFrame()
    syc["model_correct_bool"] = bool_series(syc.get("model_correct", pd.Series(index=syc.index, dtype=object)))
    syc["agrees_user_bool"] = bool_series(syc.get("agrees_with_user_belief", pd.Series(index=syc.index, dtype=object)))
    belief_matches = syc.get("belief_matches_truth", pd.Series(index=syc.index, dtype=object)).astype(str).str.lower()
    syc["belief_conflict"] = syc["framing_condition"].astype(str).str.contains("conflict", case=False, na=False) | belief_matches.isin(
        {"false", "0", "no"}
    )
    rows = []
    for keys, group in syc.groupby(["model_id", "model_family", "method_condition"], dropna=False):
        conflict = group[group["belief_conflict"]]
        aligned = group[~group["belief_conflict"]]
        rows.append(
            {
                "model_id": keys[0],
                "model_family": keys[1],
                "method_condition": keys[2],
                "trials": len(group),
                "accuracy": group["model_correct_bool"].mean(),
                "conflict_accuracy": conflict["model_correct_bool"].mean() if len(conflict) else np.nan,
                "aligned_accuracy": aligned["model_correct_bool"].mean() if len(aligned) else np.nan,
                "wrong_belief_agreement_rate": conflict["agrees_user_bool"].mean() if len(conflict) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def cost_summary(frame: pd.DataFrame) -> pd.DataFrame:
    valid = frame[frame["valid_response"]].copy()
    if valid.empty:
        return pd.DataFrame()
    for column in ["latency_seconds", "prompt_tokens", "completion_tokens", "total_tokens"]:
        if column in valid.columns:
            valid[column] = numeric(valid[column])
    grouped = (
        valid.groupby(["model_id", "model_family", "dataset", "method_condition"], dropna=False)
        .agg(
            trials=("dataset", "size"),
            median_latency_seconds=("latency_seconds", "median"),
            median_prompt_tokens=("prompt_tokens", "median"),
            median_completion_tokens=("completion_tokens", "median"),
            median_total_tokens=("total_tokens", "median"),
        )
        .reset_index()
    )
    baseline = grouped[grouped["method_condition"].eq("standard")][
        ["model_id", "dataset", "median_latency_seconds", "median_total_tokens"]
    ].rename(columns={"median_latency_seconds": "standard_latency_seconds", "median_total_tokens": "standard_total_tokens"})
    merged = grouped.merge(baseline, on=["model_id", "dataset"], how="left")
    merged["latency_multiplier_vs_standard"] = merged["median_latency_seconds"] / merged["standard_latency_seconds"].replace(0, np.nan)
    merged["token_multiplier_vs_standard"] = merged["median_total_tokens"] / merged["standard_total_tokens"].replace(0, np.nan)
    return merged


def value_ranking(reductions: pd.DataFrame, costs: pd.DataFrame, syc: pd.DataFrame) -> pd.DataFrame:
    if reductions.empty:
        return pd.DataFrame()
    value = reductions.merge(
        costs[["model_id", "dataset", "method_condition", "latency_multiplier_vs_standard", "token_multiplier_vs_standard"]],
        on=["model_id", "dataset", "method_condition"],
        how="left",
    )
    value["cost_penalty"] = value[["latency_multiplier_vs_standard", "token_multiplier_vs_standard"]].mean(axis=1).replace(0, np.nan)
    value["moral_value_score"] = value["moral_bias_reduction"] / value["cost_penalty"]
    if not syc.empty:
        syc_base = syc[syc["method_condition"].eq("standard")][["model_id", "wrong_belief_agreement_rate"]].rename(
            columns={"wrong_belief_agreement_rate": "standard_wrong_belief_agreement_rate"}
        )
        syc_red = syc.merge(syc_base, on="model_id", how="left")
        syc_red["sycophancy_reduction"] = syc_red["standard_wrong_belief_agreement_rate"] - syc_red["wrong_belief_agreement_rate"]
        value = value.merge(syc_red[["model_id", "method_condition", "sycophancy_reduction"]], on=["model_id", "method_condition"], how="left")
    return value.sort_values("moral_value_score", ascending=False)


def write_summary(frame: pd.DataFrame, moral: pd.DataFrame, reductions: pd.DataFrame, syc: pd.DataFrame, costs: pd.DataFrame, value: pd.DataFrame) -> None:
    lines = [
        "# Confirmatory Analysis Summary",
        "",
        "Analysis type: item-family framing-gap analysis with bootstrap confidence intervals.",
        "This is a transparent fallback because moral tasks do not have objective correctness labels.",
        "",
        f"Rows in clean trial-level dataset: {len(frame)}",
        f"Models included: {', '.join(sorted(frame['model_id'].dropna().astype(str).unique()))}",
        f"Methods included: {', '.join(sorted(frame['method_condition'].dropna().astype(str).unique()))}",
        f"Datasets included: {', '.join(sorted(frame['dataset'].dropna().astype(str).unique()))}",
        "",
        "## Primary Moral Bias Results",
        "",
    ]
    if moral.empty:
        lines.append("No moral framing analysis could be run.")
    else:
        display = moral.sort_values(["model_id", "dataset", "moral_bias_mean"]).head(20)
        lines.extend(["```text", display.to_string(index=False), "```"])
    lines.extend(["", "## Bias Reduction vs Standard", ""])
    if reductions.empty:
        lines.append("No standard baseline was available for reduction estimates.")
    else:
        display = reductions[reductions["method_condition"].ne("standard")].sort_values("moral_bias_reduction", ascending=False).head(20)
        lines.extend(["```text", display.to_string(index=False), "```"])
    lines.extend(["", "## Sycophancy Results", ""])
    if syc.empty:
        lines.append("No sycophancy rows were available in the clean confirmatory dataset.")
    else:
        lines.extend(["```text", syc.sort_values(["model_id", "wrong_belief_agreement_rate"]).to_string(index=False), "```"])
    lines.extend(["", "## Cost and Value", ""])
    if value.empty:
        lines.append("No value ranking could be computed.")
    else:
        display = value[value["method_condition"].ne("standard")].sort_values("moral_value_score", ascending=False).head(20)
        lines.extend(["```text", display.to_string(index=False), "```"])
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- Moral results estimate framing-gap reduction, not moral correctness.",
            "- Cells marked exploratory or low-valid in the build report should not be treated as primary confirmatory evidence.",
            "- Counterfactual consistency voting is an algorithmic inference-time consistency intervention and can enforce zero framing gap by design.",
        ]
    )
    (OUTPUT_DIR / "confirmatory_analysis_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    frame = load_trial_data()
    gaps = moral_item_gaps(frame)
    gaps.to_csv(TABLE_DIR / "moral_item_gaps.csv", index=False)
    moral = summarize_moral(gaps)
    moral.to_csv(TABLE_DIR / "moral_bias_summary.csv", index=False)
    reductions = moral_reductions(moral)
    reductions.to_csv(TABLE_DIR / "moral_bias_reductions.csv", index=False)
    syc = summarize_sycophancy(frame)
    syc.to_csv(TABLE_DIR / "sycophancy_summary.csv", index=False)
    costs = cost_summary(frame)
    costs.to_csv(TABLE_DIR / "cost_summary.csv", index=False)
    value = value_ranking(reductions, costs, syc)
    value.to_csv(TABLE_DIR / "method_value_ranking.csv", index=False)
    write_summary(frame, moral, reductions, syc, costs, value)
    print(f"Wrote confirmatory analysis outputs under {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
