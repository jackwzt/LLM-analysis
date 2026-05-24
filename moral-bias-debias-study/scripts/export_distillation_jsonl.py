from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


FINAL_ANSWER_LINE_PATTERN = re.compile(r"(?im)^\s*Final answer\s*:\s*(Yes|No)\s*$")


def build_standard_messages(participant_prompt: str, scenario_text: str) -> list[dict[str, str]]:
    system_text = (
        f"{participant_prompt}\n\n"
        "You are participating in a research benchmark about bias-resistant judgment. "
        "Do not mention being an AI or discuss the benchmark itself."
    )
    user_text = (
        f"{scenario_text}\n\n"
        "Respond in exactly one line using this format:\n"
        "Final answer: Yes\n"
        "or\n"
        "Final answer: No"
    )
    return [
        {"role": "system", "content": system_text},
        {"role": "user", "content": user_text},
    ]


def compact_reason(raw_text: str, max_words: int) -> str:
    without_answer = FINAL_ANSWER_LINE_PATTERN.sub("", raw_text or "").strip()
    lines = [line.strip() for line in without_answer.splitlines() if line.strip()]
    if not lines:
        return "The judgment should remain consistent across equivalent framings."

    reason = lines[-1] if lines[0].lower().startswith(("rational analyst", "critique", "revision")) else lines[0]
    if reason.lower().startswith("reason:"):
        reason = reason.split(":", 1)[1].strip()
    reason = " ".join(reason.split())
    words = reason.split()
    if len(words) > max_words:
        reason = " ".join(words[:max_words]).rstrip(".,;:") + "."
    return reason or "The judgment should remain consistent across equivalent framings."


def build_target_text(row: dict[str, str], target_field: str, target_mode: str, reason_max_words: int) -> str:
    if target_mode == "raw":
        return (row.get(target_field) or "").strip()
    if target_mode == "final_answer":
        parsed_answer = (row.get("parsed_answer") or "").strip().title()
        if parsed_answer not in {"Yes", "No"}:
            return ""
        return f"Final answer: {parsed_answer}"
    if target_mode == "short_reason":
        parsed_answer = (row.get("parsed_answer") or "").strip().title()
        if parsed_answer not in {"Yes", "No"}:
            return ""
        reason = compact_reason(row.get(target_field) or "", reason_max_words)
        return f"Reason: {reason}\nFinal answer: {parsed_answer}"
    raise ValueError(f"Unsupported target_mode: {target_mode}")


BALANCED_ITEM_SPLITS = {
    "exp2": {
        "val": {"Endow"},
        "test": {"Medicine"},
    },
    "exp3": {
        "val": {"Christmas"},
        "test": {"Family Dog"},
    },
    "sycophancy": {
        "val": {"S04", "S10", "S16", "S22"},
        "test": {"S05", "S11", "S17", "S23"},
    },
}


def balanced_item_split(dataset: str, dilemma: str) -> str:
    dataset_splits = BALANCED_ITEM_SPLITS.get(dataset, {})
    if dilemma in dataset_splits.get("val", set()):
        return "val"
    if dilemma in dataset_splits.get("test", set()):
        return "test"
    return "train"


def serializable_balanced_item_splits() -> dict[str, dict[str, list[str]]]:
    return {
        dataset: {split: sorted(items) for split, items in split_map.items()}
        for dataset, split_map in BALANCED_ITEM_SPLITS.items()
    }


def stable_split(dataset: str, dilemma: str, framing_condition: str, group_by: str, split_strategy: str) -> str:
    if split_strategy == "balanced":
        if group_by != "item":
            raise ValueError("balanced split_strategy requires --group-by item")
        return balanced_item_split(dataset, dilemma)
    if split_strategy != "hash":
        raise ValueError(f"Unsupported split_strategy: {split_strategy}")

    if group_by == "item":
        key = f"{dataset}|{dilemma}"
    elif group_by == "item_frame":
        key = f"{dataset}|{dilemma}|{framing_condition}"
    else:
        raise ValueError(f"Unsupported group_by: {group_by}")
    bucket = sum(ord(ch) for ch in key) % 100
    if bucket < 70:
        return "train"
    if bucket < 85:
        return "val"
    return "test"


def main() -> None:
    parser = argparse.ArgumentParser(description="Export critique_revise trials as SFT distillation JSONL.")
    parser.add_argument("--input", type=Path, required=True, help="raw_trials.csv with teacher outputs.")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--method", default="critique_revise")
    parser.add_argument("--target-field", default="final_raw_output")
    parser.add_argument("--target-mode", choices=["raw", "final_answer", "short_reason"], default="raw")
    parser.add_argument("--reason-max-words", type=int, default=35)
    parser.add_argument("--group-by", choices=["item", "item_frame"], default="item")
    parser.add_argument("--split-strategy", choices=["balanced", "hash"], default="balanced")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    writers = {}
    files = {}
    counts = {"train": 0, "val": 0, "test": 0}
    try:
        for split in counts:
            files[split] = (args.output_dir / f"{split}.jsonl").open("w", encoding="utf-8", newline="\n")
            writers[split] = files[split]

        with args.input.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                if row.get("method_condition") != args.method:
                    continue
                if str(row.get("valid", "")).lower() not in {"true", "1", "yes"}:
                    continue
                target_text = build_target_text(row, args.target_field, args.target_mode, args.reason_max_words)
                if not target_text:
                    continue
                split = stable_split(
                    row["dataset"],
                    row["dilemma"],
                    row["framing_condition"],
                    args.group_by,
                    args.split_strategy,
                )
                sample = {
                    "messages": build_standard_messages(row["participant_prompt"], row["scenario_text"]),
                    "target_text": target_text,
                    "metadata": {
                        "dataset": row["dataset"],
                        "task_family": row.get("task_family", ""),
                        "dilemma": row["dilemma"],
                        "framing_condition": row["framing_condition"],
                        "replicate_id": row["replicate_id"],
                        "source_method": row["method_condition"],
                        "parsed_answer": row.get("parsed_answer", ""),
                    },
                }
                writers[split].write(json.dumps(sample, ensure_ascii=False) + "\n")
                counts[split] += 1
    finally:
        for file_handle in files.values():
            file_handle.close()

    (args.output_dir / "manifest.json").write_text(
        json.dumps(
            {
                "input": str(args.input),
                "method": args.method,
                "group_by": args.group_by,
                "split_strategy": args.split_strategy,
                "target_mode": args.target_mode,
                "reason_max_words": args.reason_max_words,
                "balanced_item_splits": serializable_balanced_item_splits()
                if args.split_strategy == "balanced"
                else {},
                "counts": counts,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
