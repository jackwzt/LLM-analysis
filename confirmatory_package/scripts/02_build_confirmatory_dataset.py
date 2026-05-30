from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "confirmatory_package" / "outputs"
PRIMARY_METHODS = {"standard", "counterfactual_consistency_vote", "anti_sycophancy_truth_first", "debate"}
PRIMARY_DATASETS = {"exp2", "exp3", "sycophancy"}
EXPECTED_FULL_COUNTS = {"exp2": 1008, "exp3": 1008, "sycophancy": 1152}


def bool_series(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().isin({"true", "1", "yes"})


def infer_run_tier(run_name: str) -> str:
    name = run_name.lower()
    if name.startswith("repair_"):
        return "full"
    for tier in ["smoke", "pilot", "full", "confirmatory", "generated", "strict_item"]:
        if name.startswith(tier) or f"_{tier}_" in name:
            return "full" if tier in {"full", "confirmatory"} else tier
    return "unknown"


def infer_model_id(run_name: str) -> str:
    name = run_name.lower()
    if "deepseek_v4flash" in name or "deepseek-v4-flash" in name:
        return "deepseek_v4flash"
    if "deepseek_v4pro" in name or "deepseek-v4-pro" in name:
        return "deepseek_v4pro"
    if "deepseek_chat" in name or "deepseek" in name:
        return "deepseek_chat"
    if "qwen3_8b" in name:
        return "qwen3_8b_base"
    if name == "full_exp2_qwen":
        return "qwen3_32b_awq"
    if "qwen3_4b" in name:
        if "sft" in name or "distilled" in name or "adapter" in name:
            return "qwen3_4b_adapter"
        return "qwen3_4b_base"
    if "gemma4_e4b" in name:
        return "gemma4_e4b_base" if "sft" not in name else "gemma4_e4b_sft"
    if "gemma4_31b" in name:
        return "gemma4_31b"
    if "gemini" in name:
        return "gemini25_flash"
    if "zhipu" in name or "glm" in name:
        return "zhipu_glm51"
    if "aliyun" in name or "qwen36" in name:
        return "aliyun_qwen36"
    return run_name


def infer_family(model_id: str) -> str:
    model = model_id.lower()
    if "deepseek" in model:
        return "DeepSeek"
    if "qwen" in model or "aliyun" in model:
        return "Qwen"
    if "gemma" in model or "gemini" in model:
        return "Gemini/Gemma"
    if "glm" in model or "zhipu" in model:
        return "GLM"
    return "unknown"


def load_progress(run_dir: Path) -> tuple[float | None, str]:
    progress_path = run_dir / "progress.json"
    if not progress_path.exists():
        return None, ""
    try:
        payload = json.loads(progress_path.read_text(encoding="utf-8", errors="replace"))
        return float(payload.get("completion_rate", 0.0)), str(payload.get("last_note", ""))
    except Exception:
        return None, "unreadable progress.json"


def read_raw_trials(path: Path) -> pd.DataFrame | None:
    try:
        if path.stat().st_size < 10:
            return None
        if b"\x00" in path.read_bytes()[:4096]:
            return None
        return pd.read_csv(path, low_memory=False, on_bad_lines="skip")
    except Exception:
        return None


def normalize_frame(frame: pd.DataFrame, run_dir: Path) -> pd.DataFrame:
    run_name = run_dir.name
    frame = frame.copy()
    if "method_condition" not in frame.columns and "prompt_condition" in frame.columns:
        frame["method_condition"] = frame["prompt_condition"]
    if "prompt_condition" not in frame.columns and "method_condition" in frame.columns:
        frame["prompt_condition"] = frame["method_condition"]
    if "final_raw_output" not in frame.columns:
        frame["final_raw_output"] = ""
    completion_rate, progress_note = load_progress(run_dir)
    model_id = infer_model_id(run_name)
    frame["source_run"] = run_name
    frame["run_id"] = run_name
    frame["run_tier"] = infer_run_tier(run_name)
    frame["run_completion_rate"] = completion_rate if completion_rate is not None else ""
    frame["run_progress_note"] = progress_note
    frame["model_id"] = frame.get("model_id", model_id)
    frame["model_id"] = frame["model_id"].fillna(model_id).replace("", model_id)
    frame["model_family"] = frame["model_id"].map(infer_family)
    frame["provider"] = frame["model_family"].replace({"Gemini/Gemma": "mixed"})
    frame["item_family_id"] = frame.get("dilemma", "").astype(str)
    frame["item_id"] = frame["dataset"].astype(str) + "::" + frame["item_family_id"].astype(str) + "::" + frame["framing_condition"].astype(str)
    frame["bias_type"] = frame["dataset"].map(lambda value: "sycophancy" if str(value) == "sycophancy" else "moral_framing")
    frame["raw_final_output"] = frame["final_raw_output"]
    frame["valid_response"] = bool_series(frame["valid"]) if "valid" in frame.columns else False
    frame["invariant_target"] = frame.get("invariant_label", "")
    frame["answer_matches_invariant_target"] = pd.Series([""] * len(frame), index=frame.index, dtype=object)
    if "model_correct" in frame.columns:
        frame.loc[frame["bias_type"] == "sycophancy", "answer_matches_invariant_target"] = frame.loc[
            frame["bias_type"] == "sycophancy", "model_correct"
        ].astype(object)
    frame["moral_bias_indicator"] = ""
    frame["sycophancy_indicator"] = ""
    if "agrees_with_user_belief" in frame.columns:
        frame["wrong_belief_agreement"] = frame["agrees_with_user_belief"]
    else:
        frame["wrong_belief_agreement"] = ""
    frame["timestamp"] = ""
    frame["bundle_id"] = frame["dataset"].astype(str) + "::" + frame["item_family_id"].astype(str)
    return frame


def collect_trial_frames() -> tuple[pd.DataFrame, list[str]]:
    frames: list[pd.DataFrame] = []
    notes: list[str] = []
    for raw_path in sorted((PROJECT_ROOT / "results").glob("*/raw_trials.csv")):
        frame = read_raw_trials(raw_path)
        if frame is None:
            notes.append(f"Skipped unreadable or empty raw file: {raw_path.relative_to(PROJECT_ROOT)}")
            continue
        if "dataset" not in frame.columns or "framing_condition" not in frame.columns:
            notes.append(f"Skipped non-trial raw file: {raw_path.relative_to(PROJECT_ROOT)}")
            continue
        frames.append(normalize_frame(frame, raw_path.parent))
    if not frames:
        return pd.DataFrame(), notes
    return pd.concat(frames, ignore_index=True, sort=False), notes


def add_cell_status(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    counts = (
        frame.groupby(["model_id", "dataset", "method_condition"], dropna=False)
        .agg(cell_rows=("dataset", "size"), cell_valid_rows=("valid_response", "sum"))
        .reset_index()
    )
    counts["expected_full_rows"] = counts["dataset"].map(EXPECTED_FULL_COUNTS).fillna("")
    counts["cell_valid_rate"] = counts["cell_valid_rows"] / counts["cell_rows"].clip(lower=1)

    def status(row: pd.Series) -> str:
        expected = row.get("expected_full_rows", "")
        if expected == "":
            return "unknown_expected"
        if int(row["cell_rows"]) >= int(expected) and float(row["cell_valid_rate"]) >= 0.95:
            return "confirmatory_full_cell"
        return "exploratory_partial_or_low_valid"

    counts["analysis_tier"] = counts.apply(status, axis=1)
    return frame.merge(counts, on=["model_id", "dataset", "method_condition"], how="left")


def build_dataset() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    raw_frame, notes = collect_trial_frames()
    if raw_frame.empty:
        report = "# Dataset Build Report\n\nNo trial-level raw files were found.\n"
        (OUTPUT_DIR / "dataset_build_report.md").write_text(report, encoding="utf-8")
        return

    frame = raw_frame[raw_frame["method_condition"].isin(PRIMARY_METHODS) & raw_frame["dataset"].isin(PRIMARY_DATASETS)].copy()
    full_frame = frame[frame["run_tier"].eq("full")].copy()
    if not full_frame.empty:
        frame = full_frame
        tier_note = "Used full-tier rows and excluded smoke/pilot rows."
    else:
        tier_note = "No full-tier rows were available; retained available rows as exploratory."

    frame["_source_priority"] = frame["source_run"].str.contains("repair", case=False, na=False).astype(int)
    frame["_valid_priority"] = frame["valid_response"].astype(int)
    key_cols = ["model_id", "dataset", "item_family_id", "framing_condition", "method_condition", "replicate_id"]
    frame = frame.sort_values(["_valid_priority", "_source_priority"]).drop_duplicates(key_cols, keep="last")
    frame = frame.drop(columns=["_source_priority", "_valid_priority"], errors="ignore")
    frame = add_cell_status(frame)

    ordered_columns = [
        "model_id",
        "model_family",
        "provider",
        "dataset",
        "item_id",
        "item_family_id",
        "framing_condition",
        "bias_type",
        "method_condition",
        "run_tier",
        "analysis_tier",
        "source_run",
        "raw_final_output",
        "parsed_answer",
        "valid_response",
        "invariant_target",
        "answer_matches_invariant_target",
        "moral_bias_indicator",
        "sycophancy_indicator",
        "wrong_belief_agreement",
        "endorse_original_action",
        "correct_answer",
        "user_belief_answer",
        "belief_matches_truth",
        "model_correct",
        "agrees_with_user_belief",
        "latency_seconds",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "run_id",
        "timestamp",
        "bundle_id",
        "replicate_id",
        "cell_rows",
        "cell_valid_rows",
        "cell_valid_rate",
        "expected_full_rows",
        "run_completion_rate",
        "run_progress_note",
    ]
    existing_columns = [column for column in ordered_columns if column in frame.columns]
    extra_columns = [column for column in frame.columns if column not in existing_columns]
    output_frame = frame[existing_columns + extra_columns]
    output_frame.to_csv(OUTPUT_DIR / "confirmatory_trial_level.csv", index=False)

    summary = (
        output_frame.groupby(["model_id", "dataset", "method_condition", "analysis_tier"], dropna=False)
        .agg(rows=("dataset", "size"), valid_rate=("valid_response", "mean"))
        .reset_index()
    )
    summary.to_csv(OUTPUT_DIR / "tables" / "confirmatory_dataset_cell_summary.csv", index=False)

    report_lines = [
        "# Dataset Build Report",
        "",
        tier_note,
        "",
        f"Candidate primary-method rows written: {len(output_frame)}",
        f"Models: {', '.join(sorted(output_frame['model_id'].dropna().astype(str).unique()))}",
        f"Methods: {', '.join(sorted(output_frame['method_condition'].dropna().astype(str).unique()))}",
        f"Datasets: {', '.join(sorted(output_frame['dataset'].dropna().astype(str).unique()))}",
        "",
        "## Cell Summary",
        "",
        "```text",
        summary.to_string(index=False),
        "```",
        "",
        "## Notes",
        "",
    ]
    report_lines.extend([f"- {note}" for note in notes[:100]])
    (OUTPUT_DIR / "dataset_build_report.md").write_text("\n".join(report_lines), encoding="utf-8")
    print(f"Wrote {OUTPUT_DIR / 'confirmatory_trial_level.csv'}")


if __name__ == "__main__":
    build_dataset()
