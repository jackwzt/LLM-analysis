from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "fingerprint_package" / "outputs"
TABLE_DIR = OUTPUT_DIR / "tables"
CONFIRMATORY_TABLE_DIR = PROJECT_ROOT / "confirmatory_package" / "outputs" / "tables"


def infer_family(model_id: str) -> str:
    model = str(model_id).lower()
    if "deepseek" in model:
        return "DeepSeek"
    if "qwen" in model or "aliyun" in model:
        return "Qwen"
    if "gemma" in model or "gemini" in model:
        return "Gemini/Gemma"
    if "glm" in model or "zhipu" in model:
        return "GLM"
    return "unknown"


def infer_local_or_api(model_id: str) -> str:
    model = str(model_id).lower()
    if any(token in model for token in ["deepseek", "gemini", "aliyun", "zhipu", "glm"]):
        return "api"
    if any(token in model for token in ["qwen3_4b", "qwen3_8b", "gemma4_e4b", "gemma4_31b"]):
        return "local"
    return "unknown"


def infer_size(model_id: str) -> str:
    model = str(model_id).lower()
    for token in ["4b", "8b", "31b", "32b"]:
        if token in model:
            return token.upper()
    return "unknown"


def metadata_for(models: list[str]) -> pd.DataFrame:
    rows = []
    for model_id in models:
        family = infer_family(model_id)
        rows.append(
            {
                "model_id": model_id,
                "model_family": family,
                "provider": family,
                "open_or_closed": "open" if infer_local_or_api(model_id) == "local" else "closed_or_api",
                "local_or_api": infer_local_or_api(model_id),
                "approx_size": infer_size(model_id),
                "training_stage": "unknown",
            }
        )
    return pd.DataFrame(rows)


def load_existing_fingerprint() -> pd.DataFrame:
    path = PROJECT_ROOT / "reports" / "deep_bias_regularities" / "bias_fingerprint_matrix.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def add_confirmatory_features(features: pd.DataFrame) -> pd.DataFrame:
    moral_path = CONFIRMATORY_TABLE_DIR / "moral_bias_summary.csv"
    reduction_path = CONFIRMATORY_TABLE_DIR / "moral_bias_reductions.csv"
    cost_path = CONFIRMATORY_TABLE_DIR / "cost_summary.csv"
    syc_path = CONFIRMATORY_TABLE_DIR / "sycophancy_summary.csv"

    rows: dict[str, dict[str, float | str]] = {}

    if moral_path.exists():
        moral = pd.read_csv(moral_path)
        for model_id, group in moral.groupby("model_id"):
            row = rows.setdefault(model_id, {"model_id": model_id})
            standard = group[group["method_condition"].eq("standard")]
            if not standard.empty:
                row["baseline_moral_bias_mean"] = standard["moral_bias_mean"].mean()
                row["yes_no_gap"] = standard["yes_no_bias_abs"].mean()
                row["omission_gap"] = standard["omission_bias_abs"].mean()
                by_dataset = standard.groupby("dataset")["moral_bias_mean"].mean()
                if {"exp2", "exp3"}.issubset(set(by_dataset.index)):
                    row["cross_dataset_stability"] = 1.0 - abs(float(by_dataset["exp2"]) - float(by_dataset["exp3"]))
            row["method_sensitivity_sd"] = group.groupby("method_condition")["moral_bias_mean"].mean().std()

    if reduction_path.exists():
        reductions = pd.read_csv(reduction_path)
        for model_id, group in reductions.groupby("model_id"):
            row = rows.setdefault(model_id, {"model_id": model_id})
            for method, feature in [
                ("counterfactual_consistency_vote", "counterfactual_consistency_vote_reduction"),
                ("anti_sycophancy_truth_first", "anti_sycophancy_truth_first_reduction"),
                ("debate", "debate_reduction"),
                ("critique_revise", "critique_revise_reduction"),
            ]:
                subset = group[group["method_condition"].eq(method)]
                if not subset.empty:
                    row[feature] = subset["moral_bias_reduction"].mean()

    if cost_path.exists():
        costs = pd.read_csv(cost_path)
        for model_id, group in costs.groupby("model_id"):
            row = rows.setdefault(model_id, {"model_id": model_id})
            for method, prefix in [
                ("counterfactual_consistency_vote", "counterfactual"),
                ("debate", "debate"),
            ]:
                subset = group[group["method_condition"].eq(method)]
                if not subset.empty:
                    row[f"latency_multiplier_{prefix}"] = subset["latency_multiplier_vs_standard"].mean()
                    row[f"token_multiplier_{prefix}"] = subset["token_multiplier_vs_standard"].mean()

    if syc_path.exists():
        syc = pd.read_csv(syc_path)
        for model_id, group in syc.groupby("model_id"):
            row = rows.setdefault(model_id, {"model_id": model_id})
            standard = group[group["method_condition"].eq("standard")]
            if not standard.empty:
                row["sycophancy_wrong_belief_rate"] = standard["wrong_belief_agreement_rate"].mean()
                row["sycophancy_accuracy"] = standard["accuracy"].mean()

    confirmatory = pd.DataFrame(rows.values())
    if confirmatory.empty:
        return features
    if features.empty:
        return confirmatory
    return features.merge(confirmatory, on="model_id", how="outer", suffixes=("", "_confirmatory"))


def main() -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    features = load_existing_fingerprint()
    features = add_confirmatory_features(features)
    if features.empty:
        features = pd.DataFrame(columns=["model_id"])

    models = sorted(features["model_id"].dropna().astype(str).unique()) if "model_id" in features.columns else []
    metadata = metadata_for(models)
    if not metadata.empty:
        existing_meta = [column for column in metadata.columns if column in features.columns and column != "model_id"]
        features = features.drop(columns=existing_meta, errors="ignore").merge(metadata, on="model_id", how="left")

    numeric_cols = features.select_dtypes(include=[np.number]).columns.tolist()
    if "best_value_score" not in features.columns and "counterfactual_consistency_vote_reduction" in features.columns:
        token = features.get("token_multiplier_counterfactual", pd.Series(np.nan, index=features.index)).replace(0, np.nan)
        features["best_value_score"] = features["counterfactual_consistency_vote_reduction"] / token

    features.to_csv(TABLE_DIR / "fingerprint_matrix.csv", index=False)
    metadata.to_csv(TABLE_DIR / "model_metadata.csv", index=False)
    print(f"Wrote {TABLE_DIR / 'fingerprint_matrix.csv'} with {len(features)} models and {len(numeric_cols)} numeric features")


if __name__ == "__main__":
    main()
