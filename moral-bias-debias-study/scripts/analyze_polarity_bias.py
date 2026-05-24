from __future__ import annotations

import argparse
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


def to_markdown(frame: pd.DataFrame, columns: list[str]) -> str:
    if frame.empty:
        return "_No rows._"
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in frame[columns].iterrows():
        lines.append("| " + " | ".join(fmt(row[col]) for col in columns) + " |")
    return "\n".join(lines)


def load_runs(run_specs: list[str]) -> pd.DataFrame:
    frames = []
    for spec in run_specs:
        if "=" not in spec:
            raise ValueError("Run spec must be model_id=run_name")
        model_id, run_name = spec.split("=", 1)
        path = PROJECT_ROOT / "results" / run_name / "raw_trials.csv"
        if not path.exists():
            raise FileNotFoundError(path)
        frame = pd.read_csv(path)
        if frame.empty:
            continue
        frame["model_id"] = model_id
        frame["source_run"] = run_name
        frames.append(frame)
    if not frames:
        raise RuntimeError("No polarity runs loaded.")
    return pd.concat(frames, ignore_index=True, sort=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze polarity/negation bias runs.")
    parser.add_argument("--runs", nargs="+", required=True, help="model_id=run_name entries.")
    parser.add_argument("--output-prefix", default="polarity_bias")
    args = parser.parse_args()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    trials = load_runs(args.runs)
    metadata = pd.read_csv(METADATA_PATH)
    trials = trials.merge(metadata, on="model_id", how="left")

    trials["valid"] = trials["valid"].astype(str).str.lower().isin(["true", "1", "yes"])
    trials["endorse_positive_proposition"] = pd.to_numeric(
        trials["endorse_positive_proposition"], errors="coerce"
    )
    trials["model_correct"] = trials["model_correct"].astype(str).str.lower().isin(["true", "1", "yes"])
    valid = trials[trials["valid"]].copy()

    rates = (
        valid.groupby(
            [
                "model_id",
                "provider_family",
                "method_condition",
                "task_family",
                "dilemma",
                "framing_condition",
            ],
            dropna=False,
        )
        .agg(
            endorse_rate=("endorse_positive_proposition", "mean"),
            accuracy=("model_correct", "mean"),
            n=("dilemma", "size"),
        )
        .reset_index()
    )
    pivot = rates.pivot_table(
        index=["model_id", "provider_family", "method_condition", "task_family", "dilemma"],
        columns="framing_condition",
        values=["endorse_rate", "accuracy"],
        aggfunc="mean",
    )
    pivot.columns = [f"{metric}_{polarity}" for metric, polarity in pivot.columns]
    pivot = pivot.reset_index()
    for col in ["endorse_rate_positive", "endorse_rate_negative", "accuracy_positive", "accuracy_negative"]:
        if col not in pivot:
            pivot[col] = pd.NA
    pivot["polarity_gap_abs"] = (
        pivot["endorse_rate_positive"] - pivot["endorse_rate_negative"]
    ).abs()
    pivot["polarity_gap_signed"] = (
        pivot["endorse_rate_positive"] - pivot["endorse_rate_negative"]
    )
    pivot["accuracy_mean"] = pivot[["accuracy_positive", "accuracy_negative"]].mean(axis=1)

    summary = (
        pivot.groupby(["model_id", "provider_family", "method_condition", "task_family"], dropna=False)
        .agg(
            items=("dilemma", "nunique"),
            polarity_gap_abs=("polarity_gap_abs", "mean"),
            polarity_gap_signed=("polarity_gap_signed", "mean"),
            accuracy_mean=("accuracy_mean", "mean"),
            endorse_positive_rate=("endorse_rate_positive", "mean"),
            endorse_negative_rate=("endorse_rate_negative", "mean"),
        )
        .reset_index()
        .sort_values(["polarity_gap_abs", "accuracy_mean"], ascending=[False, True])
    )

    model_summary = (
        summary.groupby(["model_id", "provider_family", "method_condition"], dropna=False)
        .agg(
            task_families=("task_family", lambda s: ",".join(sorted(map(str, s.dropna().unique())))),
            polarity_gap_abs=("polarity_gap_abs", "mean"),
            polarity_gap_signed=("polarity_gap_signed", "mean"),
            accuracy_mean=("accuracy_mean", "mean"),
        )
        .reset_index()
        .sort_values("polarity_gap_abs", ascending=False)
    )

    trials.to_csv(REPORT_DIR / f"{args.output_prefix}_trials_enriched.csv", index=False)
    pivot.to_csv(REPORT_DIR / f"{args.output_prefix}_item_metrics.csv", index=False)
    summary.to_csv(REPORT_DIR / f"{args.output_prefix}_task_summary.csv", index=False)
    model_summary.to_csv(REPORT_DIR / f"{args.output_prefix}_model_summary.csv", index=False)

    lines = [
        "# Polarity / Negation Bias Report",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Definition",
        "",
        "`polarity_gap_abs = |endorse_positive_rate(positive question) - endorse_positive_rate(negative question)|`.",
        "Lower is better: equivalent positive/negative questions should map to the same underlying proposition judgment.",
        "",
        "## Model Summary",
        "",
        to_markdown(
            model_summary,
            [
                "model_id",
                "provider_family",
                "method_condition",
                "task_families",
                "polarity_gap_abs",
                "accuracy_mean",
            ],
        ),
        "",
        "## Task-Family Summary",
        "",
        to_markdown(
            summary,
            [
                "model_id",
                "method_condition",
                "task_family",
                "items",
                "polarity_gap_abs",
                "accuracy_mean",
                "endorse_positive_rate",
                "endorse_negative_rate",
            ],
        ),
        "",
    ]
    (REPORT_DIR / f"{args.output_prefix}_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(
        {
            "report": str(REPORT_DIR / f"{args.output_prefix}_report.md"),
            "models": int(model_summary["model_id"].nunique()),
            "trials": int(len(trials)),
        }
    )


if __name__ == "__main__":
    main()
