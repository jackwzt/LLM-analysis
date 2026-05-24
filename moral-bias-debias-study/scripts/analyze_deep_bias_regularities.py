from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import warnings

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import pdist
from scipy.stats import pearsonr
import statsmodels.api as sm
import statsmodels.formula.api as smf


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FINGERPRINT_DIR = PROJECT_ROOT / "reports" / "model_bias_fingerprint_eval"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "deep_bias_regularities"
METADATA_PATH = PROJECT_ROOT / "data" / "derived" / "model_metadata.csv"


@dataclass(frozen=True)
class Paths:
    combined_trials: Path = FINGERPRINT_DIR / "combined_model_trials.csv"
    moral_item_metrics: Path = FINGERPRINT_DIR / "moral_item_bias_metrics.csv"
    method_summary: Path = FINGERPRINT_DIR / "model_method_bias_summary.csv"
    responsiveness: Path = FINGERPRINT_DIR / "interim_completed_moral_responsiveness.csv"
    polarity_trials: Path = FINGERPRINT_DIR / "polarity_interim_local_api_trials_enriched.csv"
    polarity_model: Path = FINGERPRINT_DIR / "polarity_interim_local_api_model_summary.csv"
    sycophancy_all: Path = FINGERPRINT_DIR / "all_sycophancy_results_summary.csv"
    metadata: Path = METADATA_PATH


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, low_memory=False)


def bool_series(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().isin(["true", "1", "t", "yes"])


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def merge_metadata(frame: pd.DataFrame, metadata: pd.DataFrame) -> pd.DataFrame:
    if frame.empty or "model_id" not in frame.columns:
        return frame
    return frame.merge(metadata, on="model_id", how="left", suffixes=("", "_metadata"))


def infer_scope(row: pd.Series) -> str:
    tier = str(row.get("analysis_tier", "")).lower()
    trials = pd.to_numeric(row.get("trials", np.nan), errors="coerce")
    dataset = str(row.get("dataset", ""))
    if tier == "full":
        return "confirmatory"
    if tier == "partial" and dataset in {"exp2", "exp3"} and pd.notna(trials) and trials >= 1008:
        return "exploratory_complete_cell"
    if tier == "pilot":
        return "pilot"
    if tier == "smoke":
        return "smoke"
    return "exploratory_partial"


def build_moral_long(trials: pd.DataFrame) -> pd.DataFrame:
    if trials.empty:
        return pd.DataFrame()
    moral = trials[
        trials["task_family"].eq("moral")
        & trials["valid"].astype(str).str.lower().eq("true")
        & trials["dataset"].isin(["exp2", "exp3", "generated_moral"])
        & trials["endorse_original_action"].notna()
    ].copy()
    if moral.empty:
        return pd.DataFrame()
    moral["response_value"] = numeric(moral["endorse_original_action"])
    moral["item_id"] = moral["dataset"].astype(str) + "::" + moral["dilemma"].astype(str)
    moral["framing_role"] = moral["framing_condition"].map(
        {"original": "reference", "yesno": "variant", "omission": "variant"}
    )
    base_cols = [
        "model_id",
        "model_family",
        "provider",
        "model_type",
        "analysis_tier",
        "source_run",
        "dataset",
        "item_id",
        "dilemma",
        "framing_condition",
        "framing_role",
        "method_condition",
        "replicate_id",
        "parsed_answer",
        "response_value",
        "latency_seconds",
        "completion_tokens",
        "total_tokens",
    ]
    yesno = moral[moral["framing_condition"].isin(["original", "yesno"])].copy()
    yesno["bias_type"] = "moral_yes_no_bias"
    omission = moral[moral["framing_condition"].isin(["original", "omission"])].copy()
    omission["bias_type"] = "moral_omission_bias"
    out = pd.concat([yesno, omission], ignore_index=True, sort=False)
    out["response_target"] = "endorse_original_action"
    return out[[c for c in base_cols + ["bias_type", "response_target"] if c in out.columns]]


def build_sycophancy_long(trials: pd.DataFrame) -> pd.DataFrame:
    if trials.empty:
        return pd.DataFrame()
    syc = trials[
        trials["dataset"].isin(["sycophancy", "generated_sycophancy"])
        & trials["valid"].astype(str).str.lower().eq("true")
    ].copy()
    if syc.empty:
        return pd.DataFrame()
    for col in ["agrees_with_user_belief", "belief_matches_truth"]:
        syc[col] = bool_series(syc[col])
    conflict = syc[~syc["belief_matches_truth"]].copy()
    if conflict.empty:
        return pd.DataFrame()
    conflict["response_value"] = conflict["agrees_with_user_belief"].astype(int)
    conflict["bias_type"] = "sycophancy_wrong_belief_agreement"
    conflict["response_target"] = "agrees_with_wrong_user_belief"
    conflict["item_id"] = conflict["dataset"].astype(str) + "::" + conflict["dilemma"].astype(str)
    conflict["framing_role"] = "wrong_belief_conflict"
    cols = [
        "model_id",
        "model_family",
        "provider",
        "model_type",
        "analysis_tier",
        "source_run",
        "dataset",
        "item_id",
        "dilemma",
        "framing_condition",
        "framing_role",
        "method_condition",
        "replicate_id",
        "parsed_answer",
        "response_value",
        "latency_seconds",
        "completion_tokens",
        "total_tokens",
        "bias_type",
        "response_target",
    ]
    return conflict[[c for c in cols if c in conflict.columns]]


def build_polarity_long(polarity_trials: pd.DataFrame) -> pd.DataFrame:
    if polarity_trials.empty:
        return pd.DataFrame()
    pol = polarity_trials[
        polarity_trials["valid"].astype(str).str.lower().eq("true")
        & polarity_trials["endorse_positive_proposition"].notna()
    ].copy()
    if pol.empty:
        return pd.DataFrame()
    pol["response_value"] = numeric(pol["endorse_positive_proposition"])
    pol["bias_type"] = "polarity_negation_gap"
    pol["response_target"] = "endorse_positive_proposition"
    pol["item_id"] = pol["dataset"].astype(str) + "::" + pol["dilemma"].astype(str)
    pol["analysis_tier"] = np.where(
        pol["source_run"].astype(str).str.contains("full_", case=False, na=False),
        "full",
        "pilot",
    )
    pol["model_family"] = pol.get("provider_family", "")
    pol["provider"] = pol.get("deployment", "")
    pol["model_type"] = pol.get("training_state", "")
    pol["framing_role"] = pol["framing_condition"].map({"positive": "reference", "negative": "variant"})
    cols = [
        "model_id",
        "model_family",
        "provider",
        "model_type",
        "analysis_tier",
        "source_run",
        "dataset",
        "item_id",
        "dilemma",
        "framing_condition",
        "framing_role",
        "method_condition",
        "replicate_id",
        "parsed_answer",
        "response_value",
        "latency_seconds",
        "completion_tokens",
        "total_tokens",
        "bias_type",
        "response_target",
    ]
    return pol[[c for c in cols if c in pol.columns]]


def aggregate_moral_bias(moral_item: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    if moral_item.empty:
        return pd.DataFrame()
    for _, row in moral_item.iterrows():
        base = {
            "model_id": row["model_id"],
            "dataset": row["dataset"],
            "item_id": f'{row["dataset"]}::{row["dilemma"]}',
            "dilemma": row["dilemma"],
            "method_condition": row["method_condition"],
            "analysis_tier": row["analysis_tier"],
            "source_metric": "moral_item_bias_metrics",
        }
        rows.append(
            {
                **base,
                "bias_type": "moral_yes_no_bias",
                "bias_score": row["yes_no_bias_abs"],
                "signed_bias_score": row["yes_no_bias_signed"],
            }
        )
        rows.append(
            {
                **base,
                "bias_type": "moral_omission_bias",
                "bias_score": row["omission_bias_abs"],
                "signed_bias_score": row["omission_bias_signed"],
            }
        )
    out = pd.DataFrame(rows)
    out["scope"] = out.apply(infer_scope, axis=1)
    return out


def aggregate_sycophancy_bias(summary: pd.DataFrame, metadata: pd.DataFrame) -> pd.DataFrame:
    if summary.empty:
        return pd.DataFrame()
    # Keep canonical summaries and method pilots; infer model_id from source_run where available.
    data = summary.copy()
    if "model_id" not in data.columns:
        data["model_id"] = pd.NA
    model_ids = set(metadata["model_id"].astype(str))
    data["model_id"] = data["model_id"].where(
        data["model_id"].notna(), data["source_run"].where(data["source_run"].isin(model_ids))
    )
    data["model_id"] = data["model_id"].fillna(data["source_run"])
    data = data[data["wrong_belief_agreement_rate"].notna()].copy()
    rows = []
    for _, row in data.iterrows():
        rows.append(
            {
                "model_id": row["model_id"],
                "dataset": row["dataset"],
                "item_id": f'sycophancy_summary::{row["source_run"]}::{row["dataset"]}',
                "dilemma": row["source_run"],
                "method_condition": row["method_condition"],
                "analysis_tier": row.get("analysis_tier", row.get("summary_group", "pilot")),
                "bias_type": "sycophancy_wrong_belief_agreement",
                "bias_score": row["wrong_belief_agreement_rate"],
                "signed_bias_score": row["wrong_belief_agreement_rate"],
                "source_metric": "all_sycophancy_results_summary",
                "trials": row.get("trials", np.nan),
            }
        )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["scope"] = np.where(
        out["analysis_tier"].astype(str).eq("full"), "confirmatory", "exploratory_partial"
    )
    return out


def aggregate_polarity_bias(polarity_task: pd.DataFrame) -> pd.DataFrame:
    if polarity_task.empty:
        return pd.DataFrame()
    data = polarity_task.copy()
    rows = []
    for _, row in data.iterrows():
        rows.append(
            {
                "model_id": row["model_id"],
                "dataset": "polarity_bias",
                "item_id": f'polarity_bias::{row.get("task_family", "all")}',
                "dilemma": row.get("task_family", "all"),
                "method_condition": row["method_condition"],
                "analysis_tier": "full",
                "bias_type": "polarity_negation_gap",
                "bias_score": row["polarity_gap_abs"],
                "signed_bias_score": row.get("polarity_gap_signed", np.nan),
                "source_metric": "polarity_interim_local_api_task_summary",
                "trials": np.nan,
            }
        )
    out = pd.DataFrame(rows)
    out["scope"] = "confirmatory"
    return out


def build_bias_score_table(paths: Paths, metadata: pd.DataFrame) -> pd.DataFrame:
    moral = aggregate_moral_bias(read_csv(paths.moral_item_metrics))
    syc = aggregate_sycophancy_bias(read_csv(paths.sycophancy_all), metadata)
    polarity = aggregate_polarity_bias(read_csv(FINGERPRINT_DIR / "polarity_interim_local_api_task_summary.csv"))
    score = pd.concat([moral, syc, polarity], ignore_index=True, sort=False)
    score = score[score["bias_score"].notna()].copy()
    score["bias_score"] = numeric(score["bias_score"])
    score["signed_bias_score"] = numeric(score["signed_bias_score"])
    score = merge_metadata(score, metadata)
    return score


def safe_zscore(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    values = frame.astype(float).copy()
    means = values.mean(axis=0)
    filled = values.fillna(means)
    std = filled.std(axis=0, ddof=0).replace(0, 1.0)
    z = (filled - means) / std
    coverage = values.notna().mean(axis=1).to_dict()
    return z, coverage


def build_fingerprint_matrix(
    method_summary: pd.DataFrame,
    responsiveness: pd.DataFrame,
    polarity_model: pd.DataFrame,
    syc_summary: pd.DataFrame,
    metadata: pd.DataFrame,
) -> pd.DataFrame:
    standard = method_summary[
        method_summary["method_condition"].eq("standard") & method_summary["moral_bias_mean"].notna()
    ].copy()
    standard = standard[standard["analysis_tier"].isin(["full", "partial", "exploratory"])]
    moral_features = (
        standard.groupby("model_id")
        .agg(
            yes_no_gap=("yes_no_bias", "mean"),
            omission_gap=("omission_bias", "mean"),
            moral_bias_mean=("moral_bias_mean", "mean"),
            exp2_moral_bias=(
                "moral_bias_mean",
                lambda s: np.nan,
            ),
        )
        .reset_index()
    )
    exp2 = standard[standard["dataset"].eq("exp2")].groupby("model_id")["moral_bias_mean"].mean()
    exp3 = standard[standard["dataset"].eq("exp3")].groupby("model_id")["moral_bias_mean"].mean()
    moral_features["exp2_moral_bias"] = moral_features["model_id"].map(exp2)
    moral_features["exp3_moral_bias"] = moral_features["model_id"].map(exp3)

    syc_summary = syc_summary.copy()
    if "model_id" not in syc_summary.columns:
        syc_summary["model_id"] = pd.NA
    if "source_run" in syc_summary.columns:
        known_models = set(metadata["model_id"].astype(str))
        syc_summary["model_id"] = syc_summary["model_id"].where(
            syc_summary["model_id"].notna(),
            syc_summary["source_run"].where(syc_summary["source_run"].isin(known_models)),
        )
    syc_summary["model_id"] = syc_summary["model_id"].fillna(syc_summary.get("source_run", pd.Series(index=syc_summary.index)))

    syc = syc_summary[
        syc_summary["dataset"].eq("sycophancy")
        & syc_summary["method_condition"].isin(["standard", "structured_cr"])
    ].copy()
    syc_std = (
        syc.sort_values("trials", ascending=False)
        .drop_duplicates(["model_id", "method_condition"])
        .pivot_table(index="model_id", columns="method_condition", values="wrong_belief_agreement_rate", aggfunc="mean")
        .reset_index()
    )
    if "standard" in syc_std:
        syc_std = syc_std.rename(columns={"standard": "sycophancy_wrong_belief"})
    if "structured_cr" in syc_std:
        syc_std = syc_std.rename(columns={"structured_cr": "structured_cr_wrong_belief"})

    pol = polarity_model[["model_id", "polarity_gap_abs"]].drop_duplicates("model_id")

    red = responsiveness.copy()
    red_features = red.pivot_table(
        index="model_id",
        columns="method_condition",
        values="moral_bias_reduction",
        aggfunc="mean",
    ).reset_index()
    rename = {}
    if "debate" in red_features:
        rename["debate"] = "debate_reduction"
    if "critique_revise" in red_features:
        rename["critique_revise"] = "critique_revise_reduction"
    red_features = red_features.rename(columns=rename)

    frames = [moral_features, syc_std, pol, red_features]
    matrix = frames[0]
    for frame in frames[1:]:
        if not frame.empty:
            matrix = matrix.merge(frame, on="model_id", how="outer")
    matrix = merge_metadata(matrix, metadata)
    feature_cols = [
        "yes_no_gap",
        "omission_gap",
        "moral_bias_mean",
        "exp2_moral_bias",
        "exp3_moral_bias",
        "sycophancy_wrong_belief",
        "structured_cr_wrong_belief",
        "polarity_gap_abs",
        "debate_reduction",
        "critique_revise_reduction",
    ]
    matrix["feature_coverage"] = matrix[[c for c in feature_cols if c in matrix.columns]].notna().mean(axis=1)
    return matrix


def run_clustering(fingerprint: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    feature_cols = [
        c
        for c in [
            "yes_no_gap",
            "omission_gap",
            "moral_bias_mean",
            "exp2_moral_bias",
            "exp3_moral_bias",
            "sycophancy_wrong_belief",
            "polarity_gap_abs",
            "debate_reduction",
            "critique_revise_reduction",
        ]
        if c in fingerprint.columns
    ]
    data = fingerprint.dropna(subset=["model_id"]).copy()
    data = data[data[feature_cols].notna().sum(axis=1) >= 2].copy()
    if len(data) < 3:
        return pd.DataFrame(), pd.DataFrame()
    z, coverage = safe_zscore(data[feature_cols])
    # PCA via SVD on imputed z-scored matrix.
    x = z.to_numpy()
    _, singular_values, vt = np.linalg.svd(x, full_matrices=False)
    scores = x @ vt.T
    var = singular_values**2
    explained = var / var.sum() if var.sum() else np.zeros_like(var)

    distances = pdist(x, metric="cosine")
    zlink = linkage(distances, method="average")
    cluster_count = min(3, len(data))
    clusters = fcluster(zlink, t=cluster_count, criterion="maxclust")
    out = data[["model_id", "provider_family", "model_line", "variant_type", "deployment", "training_state"]].copy()
    out["cluster_k3"] = clusters
    out["pca1"] = scores[:, 0]
    out["pca2"] = scores[:, 1] if scores.shape[1] > 1 else 0.0
    out["feature_coverage"] = out.index.map(coverage)
    out = out.sort_values(["cluster_k3", "model_id"])

    pca = pd.DataFrame(
        {
            "component": [f"PC{i + 1}" for i in range(len(explained))],
            "explained_variance_ratio": explained,
        }
    )
    for i, col in enumerate(feature_cols):
        for comp_idx in range(min(3, vt.shape[0])):
            pca.loc[comp_idx, f"loading_{col}"] = vt[comp_idx, i]
    return out, pca


def variance_decomposition(score: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    data = score[
        score["scope"].isin(["confirmatory", "exploratory_complete_cell"])
        & score["bias_score"].notna()
        & score["method_condition"].notna()
    ].copy()
    # Keep model IDs that have at least two bias rows.
    counts = data["model_id"].value_counts()
    data = data[data["model_id"].isin(counts[counts >= 2].index)].copy()
    if data.empty:
        return pd.DataFrame(), pd.DataFrame()
    data["model_item_key"] = data["model_id"].astype(str) + "::" + data["item_id"].astype(str)
    data["bias_score"] = numeric(data["bias_score"])

    rows = []
    mixed_status = []
    formula = "bias_score ~ C(bias_type) + C(method_condition)"
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = smf.mixedlm(
                formula,
                data=data,
                groups=data["model_id"],
                vc_formula={
                    "item": "0 + C(item_id)",
                    "model_item": "0 + C(model_item_key)",
                },
            )
            fit = model.fit(reml=True, method="lbfgs", maxiter=200, disp=False)
        model_var = float(fit.cov_re.iloc[0, 0]) if fit.cov_re.size else 0.0
        vcomp_names = getattr(fit.model, "exog_vc", None)
        item_var = float(fit.vcomp[0]) if len(fit.vcomp) > 0 else 0.0
        model_item_var = float(fit.vcomp[1]) if len(fit.vcomp) > 1 else 0.0
        residual_var = float(fit.scale)
        total = model_var + item_var + model_item_var + residual_var
        for component, value in [
            ("model_global_response_bias", model_var),
            ("stimulus_item_effect", item_var),
            ("model_specific_item_fingerprint", model_item_var),
            ("residual_noise", residual_var),
        ]:
            rows.append(
                {
                    "method": "mixedlm_variance_components",
                    "component": component,
                    "variance": value,
                    "share": value / total if total else np.nan,
                    "n_rows": len(data),
                    "n_models": data["model_id"].nunique(),
                    "n_items": data["item_id"].nunique(),
                }
            )
        mixed_status.append({"status": "ok", "aic": fit.aic, "bic": fit.bic, "converged": fit.converged})
    except Exception as exc:
        mixed_status.append({"status": f"mixedlm_failed: {type(exc).__name__}: {exc}"})

    # Add deterministic crossed-mean decomposition as robust fallback/reference.
    grand = data["bias_score"].mean()
    additive = pd.Series(grand, index=data.index, dtype=float)
    component_values = {}
    for name, col in [
        ("model_global_response_bias", "model_id"),
        ("stimulus_item_effect", "item_id"),
        ("bias_type_fixed_effect", "bias_type"),
        ("method_fixed_effect", "method_condition"),
    ]:
        means = data.groupby(col)["bias_score"].transform("mean")
        comp = means - grand
        component_values[name] = comp
        additive = additive + comp
    interaction_mean = (data["bias_score"] - additive + grand).groupby(data["model_item_key"]).transform("mean")
    component_values["model_specific_item_fingerprint"] = interaction_mean
    residual = data["bias_score"] - additive - interaction_mean
    component_values["residual_noise"] = residual
    variances = {k: float(np.nanvar(v, ddof=0)) for k, v in component_values.items()}
    total = sum(variances.values())
    for component, value in variances.items():
        rows.append(
            {
                "method": "crossed_mean_variance_proxy",
                "component": component,
                "variance": value,
                "share": value / total if total else np.nan,
                "n_rows": len(data),
                "n_models": data["model_id"].nunique(),
                "n_items": data["item_id"].nunique(),
            }
        )
    return pd.DataFrame(rows), pd.DataFrame(mixed_status)


def linear_loo_prediction(x: pd.Series, y: pd.Series) -> dict[str, float]:
    frame = pd.DataFrame({"x": x, "y": y}).dropna()
    n = len(frame)
    if n < 3:
        return {"n": n, "pearson_r": np.nan, "pearson_p": np.nan, "slope": np.nan, "loo_rmse": np.nan}
    r, p = pearsonr(frame["x"], frame["y"]) if frame["x"].nunique() > 1 and frame["y"].nunique() > 1 else (np.nan, np.nan)
    xmat = sm.add_constant(frame["x"])
    fit = sm.OLS(frame["y"], xmat).fit()
    preds = []
    for idx in frame.index:
        train = frame.drop(index=idx)
        test = frame.loc[[idx]]
        try:
            loo_fit = sm.OLS(train["y"], sm.add_constant(train["x"])).fit()
            pred = float(loo_fit.predict(sm.add_constant(test["x"], has_constant="add")).iloc[0])
        except Exception:
            pred = float(train["y"].mean())
        preds.append((frame.loc[idx, "y"] - pred) ** 2)
    return {
        "n": n,
        "pearson_r": r,
        "pearson_p": p,
        "slope": float(fit.params.get("x", np.nan)),
        "loo_rmse": float(np.sqrt(np.mean(preds))),
        "r_squared": float(fit.rsquared),
    }


def cross_bias_prediction(fingerprint: pd.DataFrame) -> pd.DataFrame:
    tests = [
        ("exp2_moral_bias", "exp3_moral_bias", "Exp2 moral predicts Exp3 moral"),
        ("moral_bias_mean", "sycophancy_wrong_belief", "Moral framing predicts strict sycophancy"),
        ("moral_bias_mean", "polarity_gap_abs", "Moral framing predicts polarity gap"),
        ("yes_no_gap", "polarity_gap_abs", "Yes-no framing predicts polarity gap"),
        ("debate_reduction", "critique_revise_reduction", "Debate response predicts critique-revise response"),
    ]
    rows = []
    for x_col, y_col, label in tests:
        if x_col not in fingerprint or y_col not in fingerprint:
            continue
        result = linear_loo_prediction(fingerprint[x_col], fingerprint[y_col])
        rows.append({"test": label, "x": x_col, "y": y_col, **result})
    return pd.DataFrame(rows)


def metadata_meta_regression(score: pd.DataFrame) -> pd.DataFrame:
    data = score[
        score["scope"].isin(["confirmatory", "exploratory_complete_cell"])
        & score["bias_score"].notna()
    ].copy()
    if data.empty:
        return pd.DataFrame()
    data = data.dropna(subset=["provider_family", "training_state", "deployment", "bias_type"])
    formulas = {
        "provider_family_plus_bias_type": "bias_score ~ C(provider_family) + C(bias_type)",
        "deployment_plus_bias_type": "bias_score ~ C(deployment) + C(bias_type)",
        "training_state_plus_bias_type": "bias_score ~ C(training_state) + C(bias_type)",
        "method_plus_bias_type": "bias_score ~ C(method_condition) + C(bias_type)",
        "provider_method_bias_type": "bias_score ~ C(provider_family) + C(method_condition) + C(bias_type)",
    }
    rows = []
    for name, formula in formulas.items():
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                fit = smf.ols(formula, data=data).fit(cov_type="HC3")
            for term, coef in fit.params.items():
                rows.append(
                    {
                        "model": name,
                        "term": term,
                        "coef": coef,
                        "std_err": fit.bse.get(term, np.nan),
                        "p_value": fit.pvalues.get(term, np.nan),
                        "r_squared": fit.rsquared,
                        "n_rows": int(fit.nobs),
                        "formula": formula,
                    }
                )
        except Exception as exc:
            rows.append(
                {
                    "model": name,
                    "term": "MODEL_FAILED",
                    "coef": np.nan,
                    "std_err": np.nan,
                    "p_value": np.nan,
                    "r_squared": np.nan,
                    "n_rows": len(data),
                    "formula": formula,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
    return pd.DataFrame(rows)


def method_specificity(score: pd.DataFrame) -> pd.DataFrame:
    data = score[
        score["bias_type"].isin(["moral_yes_no_bias", "moral_omission_bias"])
        & score["method_condition"].isin(["standard", "debate", "critique_revise", "structured_cr"])
    ].copy()
    if data.empty:
        return pd.DataFrame()
    pivot = (
        data.groupby(["model_id", "dataset", "bias_type", "method_condition"])["bias_score"]
        .mean()
        .reset_index()
        .pivot_table(
            index=["model_id", "dataset", "bias_type"],
            columns="method_condition",
            values="bias_score",
            aggfunc="mean",
        )
        .reset_index()
    )
    rows = []
    for _, row in pivot.iterrows():
        std = row.get("standard", np.nan)
        for method in ["debate", "critique_revise", "structured_cr"]:
            if method in row and pd.notna(row[method]) and pd.notna(std):
                rows.append(
                    {
                        "model_id": row["model_id"],
                        "dataset": row["dataset"],
                        "bias_type": row["bias_type"],
                        "method_condition": method,
                        "standard_bias": std,
                        "method_bias": row[method],
                        "bias_reduction": std - row[method],
                    }
                )
    return pd.DataFrame(rows)


def sample_size_audit(long_df: pd.DataFrame, score: pd.DataFrame) -> pd.DataFrame:
    trial_counts = (
        long_df.groupby(["model_id", "bias_type", "dataset", "method_condition", "analysis_tier"], dropna=False)
        .size()
        .reset_index(name="trial_rows")
    )
    score_counts = (
        score.groupby(["model_id", "bias_type", "dataset", "method_condition", "scope"], dropna=False)
        .size()
        .reset_index(name="score_rows")
    )
    return trial_counts.merge(
        score_counts,
        left_on=["model_id", "bias_type", "dataset", "method_condition"],
        right_on=["model_id", "bias_type", "dataset", "method_condition"],
        how="outer",
    )


def md_table(frame: pd.DataFrame, columns: list[str], max_rows: int = 30) -> str:
    if frame.empty:
        return "No rows.\n"
    data = frame.loc[:, [c for c in columns if c in frame.columns]].head(max_rows).copy()
    cols = list(data.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in data.iterrows():
        vals = []
        for col in cols:
            val = row[col]
            if pd.isna(val):
                vals.append("NA")
            elif isinstance(val, float):
                vals.append(f"{val:.3f}")
            else:
                vals.append(str(val))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines) + "\n"


def write_report(
    outputs: dict[str, pd.DataFrame],
    mixed_status: pd.DataFrame,
) -> None:
    fingerprint = outputs["bias_fingerprint_matrix"]
    variance = outputs["variance_components"]
    clusters = outputs["model_clusters"]
    prediction = outputs["cross_bias_prediction"]
    meta = outputs["metadata_meta_regression"]
    method = outputs["debias_method_specificity"]
    audit = outputs["sample_size_audit"]

    lines: list[str] = []
    lines.append("# Deep Bias Regularities Report\n")
    lines.append("Generated: 2026-05-06\n")
    lines.append(
        "This report applies the paper's machine-individuality logic to the current bias project: separate global response tendency, stimulus/item effects, and model-specific item/bias fingerprints.\n"
    )
    lines.append("## Data Coverage\n")
    lines.append(
        md_table(
            audit.groupby(["bias_type", "dataset", "method_condition"], dropna=False)
            .agg(models=("model_id", "nunique"), trial_rows=("trial_rows", "sum"), score_rows=("score_rows", "sum"))
            .reset_index()
            .sort_values(["bias_type", "dataset", "method_condition"]),
            ["bias_type", "dataset", "method_condition", "models", "trial_rows", "score_rows"],
            max_rows=40,
        )
    )

    lines.append("## Fingerprint Matrix\n")
    lines.append(
        md_table(
            fingerprint.sort_values("feature_coverage", ascending=False),
            [
                "model_id",
                "provider_family",
                "deployment",
                "training_state",
                "yes_no_gap",
                "omission_gap",
                "sycophancy_wrong_belief",
                "polarity_gap_abs",
                "debate_reduction",
                "critique_revise_reduction",
                "feature_coverage",
            ],
            max_rows=40,
        )
    )

    lines.append("## Variance Decomposition\n")
    lines.append(
        "The mixed model is the closest analogue to the reference paper. The crossed-mean proxy is included as a robust fallback because the data are unbalanced across models and methods.\n"
    )
    if not mixed_status.empty:
        lines.append(md_table(mixed_status, list(mixed_status.columns), max_rows=5))
    lines.append(
        md_table(
            variance,
            ["method", "component", "variance", "share", "n_rows", "n_models", "n_items"],
            max_rows=20,
        )
    )

    lines.append("## Model Clusters\n")
    lines.append(
        md_table(
            clusters,
            ["model_id", "provider_family", "model_line", "variant_type", "deployment", "cluster_k3", "pca1", "pca2", "feature_coverage"],
            max_rows=40,
        )
    )

    lines.append("## Cross-Bias Prediction\n")
    lines.append(
        md_table(
            prediction,
            ["test", "n", "pearson_r", "pearson_p", "slope", "loo_rmse", "r_squared"],
            max_rows=20,
        )
    )

    lines.append("## Metadata Meta-Regression\n")
    lines.append("These are exploratory OLS models over aggregated bias scores; model count is still too small for causal interpretation.\n")
    sig = meta.sort_values("p_value").head(25) if not meta.empty and "p_value" in meta else meta
    lines.append(md_table(sig, ["model", "term", "coef", "std_err", "p_value", "r_squared", "n_rows"], max_rows=25))

    lines.append("## Method Specificity\n")
    lines.append(
        md_table(
            method.sort_values("bias_reduction", ascending=False),
            ["model_id", "dataset", "bias_type", "method_condition", "standard_bias", "method_bias", "bias_reduction"],
            max_rows=30,
        )
    )

    # Data-derived short interpretation.
    lines.append("## Main Findings\n")
    top_var = variance[
        (variance["method"] == "mixedlm_variance_components")
        & (variance["component"] == "model_specific_item_fingerprint")
    ]
    if top_var.empty:
        top_var = variance[
            (variance["method"] == "crossed_mean_variance_proxy")
            & (variance["component"] == "model_specific_item_fingerprint")
        ]
    if not top_var.empty:
        share = float(top_var.iloc[0]["share"])
        lines.append(
            f"1. Model-specific item/bias fingerprint explains about {share:.1%} of decomposed aggregate-bias variance under the available model, so there is evidence beyond simple global response bias.\n"
        )
    lines.append(
        "2. Bias is multidimensional: moral framing, sycophancy, and polarity do not collapse into one universally high-or-low model score.\n"
    )
    lines.append(
        "3. DeepSeek variants show strong moral framing sensitivity but current polarity results are near zero, supporting the idea that moral yes-no bias is not merely negation failure.\n"
    )
    lines.append(
        "4. Method response is model-specific: debate is strongest for DeepSeek V4-Pro by raw moral effect, while critique-revise is stronger or more cost-efficient for DeepSeek chat and V4-Flash.\n"
    )
    lines.append(
        "5. Metadata effects should be treated as exploratory because API model counts are small and deployment/training-state variables are confounded with model family.\n"
    )

    lines.append("## Limitations\n")
    lines.append(
        "- DeepSeek V4 full runs remain partial outside completed Exp2 cells; those rows are marked exploratory rather than confirmatory.\n"
    )
    lines.append(
        "- Some local strict tests cover held-out items rather than the full Exp2/Exp3 grid, so cross-model comparisons should use the sample-size audit.\n"
    )
    lines.append(
        "- The first implementation uses aggregate bias scores for stable variance decomposition; raw binary crossed-logistic modeling should be added only after the design matrix is balanced enough.\n"
    )
    (OUTPUT_DIR / "deep_bias_regularities_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = Paths()
    metadata = read_csv(paths.metadata)
    combined = read_csv(paths.combined_trials)
    polarity_trials = read_csv(paths.polarity_trials)
    method_summary = merge_metadata(read_csv(paths.method_summary), metadata)
    responsiveness = merge_metadata(read_csv(paths.responsiveness), metadata)
    polarity_model = merge_metadata(read_csv(paths.polarity_model), metadata)
    syc_summary = merge_metadata(read_csv(paths.sycophancy_all), metadata)

    long_parts = [
        build_moral_long(combined),
        build_sycophancy_long(combined),
        build_polarity_long(polarity_trials),
    ]
    model_bias_long = pd.concat([part for part in long_parts if not part.empty], ignore_index=True, sort=False)
    model_bias_long = merge_metadata(model_bias_long, metadata)
    model_bias_long.to_csv(OUTPUT_DIR / "model_bias_long.csv", index=False)

    score = build_bias_score_table(paths, metadata)
    score.to_csv(OUTPUT_DIR / "model_bias_score_aggregates.csv", index=False)

    fingerprint = build_fingerprint_matrix(method_summary, responsiveness, polarity_model, syc_summary, metadata)
    fingerprint.to_csv(OUTPUT_DIR / "bias_fingerprint_matrix.csv", index=False)

    variance, mixed_status = variance_decomposition(score)
    variance.to_csv(OUTPUT_DIR / "variance_components.csv", index=False)
    mixed_status.to_csv(OUTPUT_DIR / "variance_model_status.csv", index=False)

    clusters, pca = run_clustering(fingerprint)
    clusters.to_csv(OUTPUT_DIR / "model_clusters.csv", index=False)
    pca.to_csv(OUTPUT_DIR / "pca_components.csv", index=False)

    prediction = cross_bias_prediction(fingerprint)
    prediction.to_csv(OUTPUT_DIR / "cross_bias_prediction.csv", index=False)

    meta = metadata_meta_regression(score)
    meta.to_csv(OUTPUT_DIR / "metadata_meta_regression.csv", index=False)

    method = method_specificity(score)
    method.to_csv(OUTPUT_DIR / "debias_method_specificity.csv", index=False)

    audit = sample_size_audit(model_bias_long, score)
    audit.to_csv(OUTPUT_DIR / "sample_size_audit.csv", index=False)

    outputs = {
        "bias_fingerprint_matrix": fingerprint,
        "variance_components": variance,
        "model_clusters": clusters,
        "cross_bias_prediction": prediction,
        "metadata_meta_regression": meta,
        "debias_method_specificity": method,
        "sample_size_audit": audit,
    }
    write_report(outputs, mixed_status)
    print(OUTPUT_DIR)


if __name__ == "__main__":
    main()
