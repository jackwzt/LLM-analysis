from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from moral_bias_eval.experiment import (  # noqa: E402
    RunOptions,
    _dry_run_method_payload,
    attach_frame_bundles,
    _load_existing_rows,
    _resolve_generator,
    _trial_key_from_values,
    _write_checkpoint,
    compute_endorsement,
    load_config,
    parse_final_answer,
    phase_repetitions,
)
from moral_bias_eval.methods import MethodRunConfig, run_method_trial  # noqa: E402
from moral_bias_eval.stimuli import get_phase_stimuli, write_stimuli_csv  # noqa: E402


def _rows_to_keys(rows: list[dict[str, Any]]) -> set[tuple[str, str, str, str, int]]:
    keys: set[tuple[str, str, str, str, int]] = set()
    for row in rows:
        keys.add(
            _trial_key_from_values(
                str(row["dataset"]),
                str(row["dilemma"]),
                str(row["framing_condition"]),
                str(row.get("method_condition", row.get("prompt_condition", "standard"))),
                int(row["replicate_id"]),
            )
        )
    return keys


def _load_target_keys(target_raw: Path) -> set[tuple[str, str, str, str, int]]:
    if not target_raw.exists():
        return set()
    return _rows_to_keys(pd.read_csv(target_raw, on_bad_lines="skip").to_dict(orient="records"))


def _build_pending_trials(
    *,
    frame: pd.DataFrame,
    phase: str,
    datasets: list[str],
    methods: list[str],
    repetitions_override: int | None,
    target_keys: set[tuple[str, str, str, str, int]],
    output_keys: set[tuple[str, str, str, str, int]],
    shard_count: int,
    shard_index: int,
) -> tuple[list[tuple[str, str, int, pd.Series]], int]:
    pending: list[tuple[str, str, int, pd.Series]] = []
    assigned_total = 0
    missing_index = 0

    for dataset in datasets:
        dataset_frame = frame[frame["dataset"] == dataset].reset_index(drop=True)
        repetitions = phase_repetitions(phase, dataset, repetitions_override)
        for method_condition in methods:
            for replicate_id in range(1, repetitions + 1):
                for _, stimulus in dataset_frame.iterrows():
                    key = _trial_key_from_values(
                        dataset,
                        str(stimulus["dilemma"]),
                        str(stimulus["framing_condition"]),
                        method_condition,
                        replicate_id,
                    )
                    if key in target_keys:
                        continue
                    assigned = missing_index % shard_count
                    missing_index += 1
                    if assigned != shard_index:
                        continue
                    assigned_total += 1
                    if key in output_keys:
                        continue
                    pending.append((dataset, method_condition, replicate_id, stimulus))

    return pending, assigned_total


def _make_row(
    *,
    stimulus: pd.Series,
    method_condition: str,
    replicate_id: int,
    seed: int,
    method_data: dict[str, Any],
) -> dict[str, Any]:
    parsed_answer, valid = parse_final_answer(str(method_data["final_raw_output"]))
    endorse = (
        compute_endorsement(parsed_answer, bool(stimulus["yes_means_invariant"]))
        if str(stimulus["task_family"]) == "moral"
        else ""
    )
    user_belief_answer = str(stimulus.get("user_belief_answer", "") or "")
    correct_answer = str(stimulus.get("correct_answer", "") or "")
    agrees_with_user = parsed_answer == user_belief_answer if valid and user_belief_answer else ""
    model_correct = parsed_answer == correct_answer if valid and correct_answer else ""

    return {
        "dataset": stimulus["dataset"],
        "task_family": stimulus["task_family"],
        "dilemma": stimulus["dilemma"],
        "framing_condition": stimulus["framing_condition"],
        "prompt_condition": method_condition,
        "method_condition": method_condition,
        "replicate_id": replicate_id,
        "seed": seed,
        "scenario_text": stimulus["scenario_text"],
        "neutral_scenario_text": stimulus.get("neutral_scenario_text", ""),
        "participant_prompt": stimulus["participant_prompt"],
        "action_label": stimulus["action_label"],
        "invariant_label": stimulus["invariant_label"],
        "yes_means_invariant": bool(stimulus["yes_means_invariant"]),
        "correct_answer": correct_answer,
        "user_belief_answer": user_belief_answer,
        "belief_matches_truth": stimulus.get("belief_matches_truth", ""),
        "question_kind": stimulus.get("question_kind", ""),
        "parsed_answer": parsed_answer or "",
        "valid": bool(valid),
        "endorse_original_action": "" if endorse == "" or endorse is None else endorse,
        "model_correct": model_correct,
        "agrees_with_user_belief": agrees_with_user,
        **method_data,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run only trials missing from another run's raw_trials.csv.")
    parser.add_argument("--target-raw", type=Path, required=True)
    parser.add_argument("--phase", choices=["smoke", "pilot", "full"], required=True)
    parser.add_argument("--datasets", nargs="+", required=True)
    parser.add_argument("--methods", nargs="+", required=True)
    parser.add_argument("--repetitions-override", type=int, default=None)
    parser.add_argument("--config", type=Path, default=PROJECT_ROOT / "configs" / "experiment.default.json")
    parser.add_argument("--output-name", required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--provider", choices=["qwen", "gemma", "deepseek", "openai_compatible"], default="openai_compatible")
    parser.add_argument("--api-key", type=str, default=None)
    parser.add_argument("--api-base-url", type=str, default=None)
    parser.add_argument("--api-model-id", type=str, default=None)
    parser.add_argument("--api-extra-body-file", type=Path, default=None)
    parser.add_argument("--api-disable-thinking", action="store_true")
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--shard-index", type=int, default=0)
    args = parser.parse_args()

    if args.shard_count < 1:
        raise ValueError("--shard-count must be >= 1")
    if not 0 <= args.shard_index < args.shard_count:
        raise ValueError("--shard-index must be in [0, shard_count)")

    config = load_config(args.config)
    api_extra_body = (
        json.loads(args.api_extra_body_file.read_text(encoding="utf-8"))
        if args.api_extra_body_file
        else None
    )

    output_dir = PROJECT_ROOT / "results" / args.output_name
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_trials_path = output_dir / "raw_trials.csv"
    existing_rows = _load_existing_rows(raw_trials_path) if args.resume else []
    rows = list(existing_rows)
    output_keys = _rows_to_keys(rows)
    target_keys = _load_target_keys(args.target_raw)

    stimuli_path = PROJECT_ROOT / "data" / "derived" / "stimuli.csv"
    frame = write_stimuli_csv(Path(config["workspace_root"]), stimuli_path)
    frame = get_phase_stimuli(frame, args.phase, args.datasets)
    frame = attach_frame_bundles(frame)

    pending, assigned_total = _build_pending_trials(
        frame=frame,
        phase=args.phase,
        datasets=args.datasets,
        methods=args.methods,
        repetitions_override=args.repetitions_override,
        target_keys=target_keys,
        output_keys=output_keys,
        shard_count=args.shard_count,
        shard_index=args.shard_index,
    )

    options = RunOptions(
        project_root=PROJECT_ROOT,
        workspace_root=Path(config["workspace_root"]),
        phase=args.phase,
        datasets=args.datasets,
        methods=args.methods,
        repetitions_override=args.repetitions_override,
        base_seed=int(config["run"]["base_seed"]),
        checkpoint_every=int(config["run"]["checkpoint_every"]),
        standard_max_new_tokens=int(config["generation"]["standard_max_new_tokens"]),
        debate_role_max_new_tokens=int(config["generation"]["debate_role_max_new_tokens"]),
        debate_moderator_max_new_tokens=int(config["generation"]["debate_moderator_max_new_tokens"]),
        dry_run=bool(args.dry_run),
        output_name=args.output_name,
        resume=bool(args.resume),
        provider=args.provider,
        deepseek_api_key=None,
        api_key=args.api_key,
        api_base_url=args.api_base_url,
        api_model_id=args.api_model_id,
        api_extra_body=api_extra_body,
        api_disable_thinking=bool(args.api_disable_thinking),
        filter_groups_jsonl=None,
        filter_group_by="item",
    )

    generator = None if args.dry_run else _resolve_generator(config, options)
    method_config = MethodRunConfig(
        standard_max_new_tokens=options.standard_max_new_tokens,
        debate_role_max_new_tokens=options.debate_role_max_new_tokens,
        debate_moderator_max_new_tokens=options.debate_moderator_max_new_tokens,
    )

    _write_checkpoint(rows, output_dir, assigned_total, note=f"missing-only start; pending={len(pending)}")
    for dataset, method_condition, replicate_id, stimulus in pending:
        seed = options.base_seed + replicate_id
        if args.dry_run:
            method_data = _dry_run_method_payload(method_condition)
        else:
            method_data = run_method_trial(generator, stimulus, method_condition, seed, method_config)
        rows.append(
            _make_row(
                stimulus=stimulus,
                method_condition=method_condition,
                replicate_id=replicate_id,
                seed=seed,
                method_data=method_data,
            )
        )
        if len(rows) % options.checkpoint_every == 0:
            _write_checkpoint(rows, output_dir, assigned_total, note=f"checkpoint after {len(rows)} completed assigned trials")

    _write_checkpoint(rows, output_dir, assigned_total, note="run complete")
    print(f"Run complete: {output_dir}")


if __name__ == "__main__":
    main()
