from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = PROJECT_ROOT / "confirmatory_package" / "outputs" / "data_inventory.csv"
EXTENSIONS = {".csv", ".tsv", ".json", ".jsonl", ".md", ".txt"}
SKIP_DIRS = {".git", ".venv", ".venv312", "__pycache__", ".pytest_cache", "models", "logs"}
TABULAR_EXTENSIONS = {".csv", ".tsv", ".jsonl"}
MODEL_COLUMNS = ["model_id", "model", "api_model_id"]
METHOD_COLUMNS = ["method_condition", "prompt_condition", "method"]
DATASET_COLUMNS = ["dataset", "task_family"]


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def iter_candidate_files() -> list[Path]:
    files: list[Path] = []
    for path in PROJECT_ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        if should_skip(path.relative_to(PROJECT_ROOT)):
            continue
        files.append(path)
    return sorted(files)


def count_lines(path: Path) -> int | None:
    try:
        with path.open("rb") as handle:
            return sum(1 for _ in handle)
    except Exception:
        return None


def has_binary_nuls(path: Path) -> bool:
    try:
        sample = path.read_bytes()[:4096]
    except Exception:
        return False
    return b"\x00" in sample


def read_sample(path: Path) -> tuple[list[str], int | None, str | None]:
    suffix = path.suffix.lower()
    if has_binary_nuls(path):
        return [], None, "contains NUL bytes; likely corrupt or binary"
    try:
        if suffix in {".csv", ".tsv"}:
            sep = "\t" if suffix == ".tsv" else ","
            sample = pd.read_csv(path, sep=sep, nrows=200, low_memory=False)
            line_count = count_lines(path)
            row_count = max(0, line_count - 1) if line_count is not None else None
            return list(sample.columns), row_count, None
        if suffix == ".jsonl":
            columns: set[str] = set()
            rows = 0
            with path.open("r", encoding="utf-8", errors="replace") as handle:
                for line in handle:
                    if not line.strip():
                        continue
                    rows += 1
                    if rows <= 200:
                        try:
                            payload = json.loads(line)
                        except Exception:
                            continue
                        if isinstance(payload, dict):
                            columns.update(payload.keys())
            return sorted(columns), rows, None
        if suffix == ".json":
            payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            if isinstance(payload, dict):
                return sorted(payload.keys()), None, None
            if isinstance(payload, list) and payload and isinstance(payload[0], dict):
                keys: set[str] = set()
                for item in payload[:200]:
                    if isinstance(item, dict):
                        keys.update(item.keys())
                return sorted(keys), len(payload), None
            return [], None, f"json root type: {type(payload).__name__}"
    except Exception as exc:
        return [], None, f"{type(exc).__name__}: {exc}"
    return [], None, None


def unique_count(path: Path, candidates: list[str]) -> int | None:
    suffix = path.suffix.lower()
    if suffix not in {".csv", ".tsv"} or has_binary_nuls(path):
        return None
    try:
        sep = "\t" if suffix == ".tsv" else ","
        header = pd.read_csv(path, sep=sep, nrows=0).columns
        usecols = [column for column in candidates if column in header]
        if not usecols:
            return None
        frame = pd.read_csv(path, sep=sep, usecols=usecols, low_memory=False)
        return int(frame[usecols[0]].nunique(dropna=True))
    except Exception:
        return None


def classify(path: Path, columns: list[str], parse_error: str | None) -> tuple[str, str]:
    suffix = path.suffix.lower()
    lower_columns = {column.lower() for column in columns}
    rel = str(path.relative_to(PROJECT_ROOT)).replace("\\", "/").lower()
    if parse_error and "nul bytes" in parse_error.lower():
        return "not_relevant_or_corrupt", "binary/NUL content detected"
    if suffix in {".md", ".txt"}:
        return "report_only", "text or markdown document"
    has_method = bool(lower_columns.intersection(METHOD_COLUMNS))
    has_dataset = "dataset" in lower_columns
    has_trial_markers = {"framing_condition", "replicate_id"}.issubset(lower_columns)
    has_response = bool({"parsed_answer", "valid", "valid_response", "final_raw_output"}.intersection(lower_columns))
    if has_dataset and has_method and has_trial_markers and has_response:
        return "trial_level", "has dataset/method/framing/replicate/response columns"
    metric_markers = {
        "moral_bias_mean",
        "yes_no_bias_abs",
        "omission_bias_abs",
        "wrong_belief_agreement_rate",
        "sycophancy_accuracy",
        "bias_reduction",
    }
    if has_method and bool(lower_columns.intersection(metric_markers)):
        return "aggregate_level", "has method-level metric columns"
    if "reports/" in rel or "results/" in rel or "data/" in rel:
        return "possibly_relevant", "project data/report path but schema is not a primary analysis table"
    return "not_relevant", "schema/path does not look analysis-ready"


def main() -> None:
    rows: list[dict[str, Any]] = []
    for path in iter_candidate_files():
        columns, row_count, parse_error = read_sample(path)
        file_type, notes = classify(path, columns, parse_error)
        rows.append(
            {
                "file_path": str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "file_type": path.suffix.lower().lstrip("."),
                "size_bytes": path.stat().st_size,
                "row_count": row_count if row_count is not None else "",
                "column_names": ";".join(columns),
                "unique_model_count": unique_count(path, MODEL_COLUMNS) or "",
                "unique_method_count": unique_count(path, METHOD_COLUMNS) or "",
                "unique_dataset_count": unique_count(path, DATASET_COLUMNS) or "",
                "analysis_level": file_type,
                "notes": notes,
                "parse_error": parse_error or "",
            }
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else [])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {OUTPUT_PATH} with {len(rows)} files")


if __name__ == "__main__":
    main()
