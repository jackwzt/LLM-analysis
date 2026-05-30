from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "confirmatory_package" / "outputs"
TABLE_DIR = OUTPUT_DIR / "tables"
FINGERPRINT_TABLE_DIR = PROJECT_ROOT / "fingerprint_package" / "outputs" / "tables"
PUBLIC_DIR = OUTPUT_DIR / "public_summary"


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, low_memory=False)


def add_cell_counts(frame: pd.DataFrame) -> pd.DataFrame:
    cell = read_csv(TABLE_DIR / "confirmatory_dataset_cell_summary.csv")
    if cell.empty:
        return frame
    cell = cell.rename(columns={"rows": "n_trials"})
    cell["n_valid"] = (pd.to_numeric(cell["n_trials"], errors="coerce") * pd.to_numeric(cell["valid_rate"], errors="coerce")).round().astype("Int64")
    keep = ["model_id", "dataset", "method_condition", "analysis_tier", "n_trials", "n_valid", "valid_rate"]
    return frame.merge(cell[keep], on=["model_id", "dataset", "method_condition"], how="left")


def make_public_moral() -> pd.DataFrame:
    reductions = read_csv(TABLE_DIR / "moral_bias_reductions.csv")
    costs = read_csv(TABLE_DIR / "cost_summary.csv")
    values = read_csv(TABLE_DIR / "method_value_ranking.csv")
    if reductions.empty:
        return pd.DataFrame()

    moral = reductions[
        [
            "model_id",
            "model_family",
            "dataset",
            "method_condition",
            "moral_bias_mean",
            "moral_bias_reduction",
            "moral_bias_ci_low",
            "moral_bias_ci_high",
        ]
    ].copy()
    moral = moral.rename(
        columns={
            "moral_bias_reduction": "moral_bias_reduction_vs_standard",
            "moral_bias_ci_low": "bootstrap_ci_low",
            "moral_bias_ci_high": "bootstrap_ci_high",
        }
    )
    moral = add_cell_counts(moral)

    if not costs.empty:
        moral = moral.merge(
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
        moral = moral.merge(
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
        "moral_bias_reduction_vs_standard",
        "bootstrap_ci_low",
        "bootstrap_ci_high",
        "latency_multiplier_vs_standard",
        "token_multiplier_vs_standard",
        "value_score",
    ]
    return moral[[column for column in columns if column in moral.columns]].sort_values(["model_id", "dataset", "method_condition"])


def make_public_sycophancy() -> pd.DataFrame:
    syc = read_csv(TABLE_DIR / "sycophancy_summary.csv")
    costs = read_csv(TABLE_DIR / "cost_summary.csv")
    values = read_csv(TABLE_DIR / "method_value_ranking.csv")
    if syc.empty:
        return pd.DataFrame()

    syc = syc.copy()
    syc["dataset"] = "sycophancy"
    baseline = syc[syc["method_condition"].eq("standard")][["model_id", "wrong_belief_agreement_rate"]].rename(
        columns={"wrong_belief_agreement_rate": "standard_wrong_belief_agreement"}
    )
    syc = syc.merge(baseline, on="model_id", how="left")
    syc["wrong_belief_agreement_reduction_vs_standard"] = syc["standard_wrong_belief_agreement"] - syc["wrong_belief_agreement_rate"]
    syc = syc.rename(
        columns={
            "wrong_belief_agreement_rate": "wrong_belief_agreement",
            "accuracy": "sycophancy_accuracy",
            "trials": "n_trials_from_summary",
        }
    )
    syc = add_cell_counts(syc)
    if "n_trials" not in syc.columns:
        syc["n_trials"] = syc["n_trials_from_summary"]
    syc["n_trials"] = syc["n_trials"].fillna(syc.get("n_trials_from_summary"))
    syc["n_valid"] = syc["n_valid"].fillna(syc["n_trials"]).astype("Int64")
    syc["valid_rate"] = syc["valid_rate"].fillna(1.0)

    if not costs.empty:
        syc = syc.merge(
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
        method_values = values.groupby(["model_id", "method_condition"], as_index=False)["moral_value_score"].mean()
        syc = syc.merge(
            method_values.rename(columns={"moral_value_score": "value_score"}),
            on=["model_id", "method_condition"],
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
        "wrong_belief_agreement",
        "wrong_belief_agreement_reduction_vs_standard",
        "sycophancy_accuracy",
        "latency_multiplier_vs_standard",
        "token_multiplier_vs_standard",
        "value_score",
    ]
    return syc[[column for column in columns if column in syc.columns]].sort_values(["model_id", "method_condition"])


def make_public_fingerprint() -> pd.DataFrame:
    fingerprint = read_csv(FINGERPRINT_TABLE_DIR / "fingerprint_matrix.csv")
    if fingerprint.empty:
        return pd.DataFrame()
    drop_cols = [column for column in fingerprint.columns if column.lower() in {"notes"} or "raw" in column.lower()]
    public = fingerprint.drop(columns=drop_cols, errors="ignore")
    return public


def figure_type(path: Path) -> str:
    name = path.stem.lower()
    if "baseline" in name:
        return "baseline_bias"
    if "reduction" in name:
        return "method_reduction"
    if "cost" in name:
        return "cost_effectiveness"
    if "model_method" in name:
        return "model_method_heatmap"
    if "value" in name:
        return "value_score_ranking"
    if "heatmap" in name:
        return "fingerprint_heatmap"
    if "dendrogram" in name:
        return "fingerprint_dendrogram"
    if "pca" in name:
        return "fingerprint_pca"
    return "other"


def make_figure_manifest() -> pd.DataFrame:
    rows = []
    for folder in [OUTPUT_DIR / "figures", PROJECT_ROOT / "fingerprint_package" / "outputs" / "figures"]:
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*")):
            if path.suffix.lower() not in {".png", ".pdf"}:
                continue
            rows.append(
                {
                    "file_path": path.relative_to(PROJECT_ROOT).as_posix(),
                    "figure_type": figure_type(path),
                    "format": path.suffix.lower().lstrip("."),
                    "safe_to_upload": True,
                    "notes": "Derived aggregate figure; no raw prompts or model outputs.",
                }
            )
    return pd.DataFrame(rows)


def write_report(moral: pd.DataFrame, syc: pd.DataFrame, fingerprint: pd.DataFrame, manifest: pd.DataFrame) -> None:
    lines = [
        "# Public Summary Build Report",
        "",
        "Status: generated GitHub-safe public summary tables from aggregate outputs.",
        "",
        "Excluded by design:",
        "",
        "- raw model outputs",
        "- scenario text",
        "- participant prompts",
        "- method traces",
        "- provider metadata",
        "- raw API responses",
        "- API keys or credentials",
        "- local private paths",
        "",
        "Generated files:",
        "",
        f"- `public_moral_model_dataset_method_summary.csv`: {len(moral)} rows",
        f"- `public_sycophancy_model_dataset_method_summary.csv`: {len(syc)} rows",
        f"- `public_fingerprint_matrix.csv`: {len(fingerprint)} rows",
        f"- `public_figure_manifest.csv`: {len(manifest)} rows",
        "",
        "Notes:",
        "",
        "- `confirmatory_trial_level.csv` is intentionally not copied into the public summary folder.",
        "- Public tables are aggregate/model-level only.",
        "- Manual review is still recommended before GitHub upload.",
    ]
    (PUBLIC_DIR / "public_summary_build_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    moral = make_public_moral()
    syc = make_public_sycophancy()
    fingerprint = make_public_fingerprint()
    manifest = make_figure_manifest()

    moral.to_csv(PUBLIC_DIR / "public_moral_model_dataset_method_summary.csv", index=False)
    syc.to_csv(PUBLIC_DIR / "public_sycophancy_model_dataset_method_summary.csv", index=False)
    fingerprint.to_csv(PUBLIC_DIR / "public_fingerprint_matrix.csv", index=False)
    manifest.to_csv(PUBLIC_DIR / "public_figure_manifest.csv", index=False)
    write_report(moral, syc, fingerprint, manifest)
    print(f"Wrote public summary outputs under {PUBLIC_DIR}")


if __name__ == "__main__":
    main()
