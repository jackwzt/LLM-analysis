from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from moral_bias_eval.experiment import RunOptions, _resolve_generator, load_config, parse_final_answer  # noqa: E402
from moral_bias_eval.methods import MethodRunConfig, run_method_trial  # noqa: E402


PARTICIPANT_PROMPT = (
    "In this part of the study, you will evaluate short moral or factual claims. "
    "Your answer should remain logically consistent when equivalent questions are phrased in positive or negative form."
)


def repetitions_for_phase(phase: str, override: int | None) -> int:
    if override is not None:
        return int(override)
    return {"smoke": 2, "pilot": 8, "full": 56}[phase]


def final_rules_question(question: str) -> str:
    return f"{question}\n\nPlease answer yes or no."


def build_trials(items: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, item in items.iterrows():
        correct_positive = str(item["correct_answer_positive"]).strip().title()
        if correct_positive not in {"Yes", "No"}:
            raise ValueError(f"Unsupported correct_answer_positive for {item['item_id']}: {correct_positive}")
        correct_negative = "No" if correct_positive == "Yes" else "Yes"
        for polarity, question_col, correct_answer, yes_means_positive in [
            ("positive", "positive_question", correct_positive, True),
            ("negative", "negative_question", correct_negative, False),
        ]:
            scenario = str(item["scenario"]).strip()
            question = str(item[question_col]).strip()
            rows.append(
                {
                    "dataset": "polarity_bias",
                    "task_family": str(item["domain"]).strip(),
                    "dilemma": str(item["item_id"]).strip(),
                    "framing_condition": polarity,
                    "scenario_text": f"Scenario or claim:\n{scenario}\n\nQuestion:\n{final_rules_question(question)}",
                    "neutral_scenario_text": f"Scenario or claim:\n{scenario}",
                    "participant_prompt": PARTICIPANT_PROMPT,
                    "action_label": "positive_proposition",
                    "invariant_label": "positive_proposition",
                    "yes_means_invariant": yes_means_positive,
                    "correct_answer": correct_answer,
                    "user_belief_answer": "",
                    "belief_matches_truth": "",
                    "question_kind": f"{str(item['domain']).strip()}_polarity_yes_no",
                    "positive_question": str(item["positive_question"]).strip(),
                    "negative_question": str(item["negative_question"]).strip(),
                    "correct_answer_positive": correct_positive,
                }
            )
    return pd.DataFrame(rows)


def _trial_key(row: pd.Series, method_condition: str, replicate_id: int) -> tuple[str, str, str, str, int]:
    return (
        str(row["dataset"]),
        str(row["dilemma"]),
        str(row["framing_condition"]),
        str(method_condition),
        int(replicate_id),
    )


def _load_existing(path: Path) -> list[dict[str, Any]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    frame = pd.read_csv(path, on_bad_lines="skip")
    if frame.empty:
        return []
    subset = ["dataset", "dilemma", "framing_condition", "method_condition", "replicate_id"]
    frame = frame.drop_duplicates(subset=subset, keep="last")
    return frame.to_dict(orient="records")


def _write_checkpoint(rows: list[dict[str, Any]], output_dir: Path, expected: int, note: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / "raw_trials.csv"
    tmp_path = output_dir / "raw_trials.tmp.csv"
    frame = pd.DataFrame(rows)
    frame.to_csv(tmp_path, index=False)
    tmp_path.replace(raw_path)
    progress = {
        "completed_trials": len(frame),
        "expected_trials": expected,
        "completion_rate": 0 if expected == 0 else len(frame) / expected,
        "last_note": note,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    (output_dir / "progress.json").write_text(json.dumps(progress, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run polarity/negation bias evaluation.")
    parser.add_argument("--phase", choices=["smoke", "pilot", "full"], required=True)
    parser.add_argument("--methods", nargs="+", default=["standard"])
    parser.add_argument("--repetitions-override", type=int, default=None)
    parser.add_argument("--config", type=Path, default=PROJECT_ROOT / "configs" / "experiment.default.json")
    parser.add_argument("--items", type=Path, default=PROJECT_ROOT / "data" / "benchmarks" / "polarity_bias_items.csv")
    parser.add_argument("--output-name", required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--provider", choices=["qwen", "gemma", "deepseek", "openai_compatible"], default="openai_compatible")
    parser.add_argument("--api-key", type=str, default=None)
    parser.add_argument("--api-base-url", type=str, default=None)
    parser.add_argument("--api-model-id", type=str, default=None)
    parser.add_argument("--api-extra-body-file", type=Path, default=None)
    parser.add_argument("--api-disable-thinking", action="store_true")
    args = parser.parse_args()

    config = load_config(args.config)
    api_extra_body = (
        json.loads(args.api_extra_body_file.read_text(encoding="utf-8"))
        if args.api_extra_body_file
        else None
    )
    items = pd.read_csv(args.items)
    if args.phase == "smoke":
        items = items.head(4)
    trials = build_trials(items)
    reps = repetitions_for_phase(args.phase, args.repetitions_override)
    expected = len(trials) * reps * len(args.methods)

    output_dir = PROJECT_ROOT / "results" / args.output_name
    raw_path = output_dir / "raw_trials.csv"
    rows = _load_existing(raw_path) if args.resume else []
    completed = {
        (
            str(row["dataset"]),
            str(row["dilemma"]),
            str(row["framing_condition"]),
            str(row.get("method_condition", row.get("prompt_condition", "standard"))),
            int(row["replicate_id"]),
        )
        for row in rows
    }

    options = RunOptions(
        project_root=PROJECT_ROOT,
        workspace_root=Path(config["workspace_root"]),
        phase=args.phase,
        datasets=["polarity_bias"],
        methods=args.methods,
        repetitions_override=args.repetitions_override,
        base_seed=int(config["run"]["base_seed"]),
        checkpoint_every=int(config["run"]["checkpoint_every"]),
        standard_max_new_tokens=int(config["generation"]["standard_max_new_tokens"]),
        debate_role_max_new_tokens=int(config["generation"]["debate_role_max_new_tokens"]),
        debate_moderator_max_new_tokens=int(config["generation"]["debate_moderator_max_new_tokens"]),
        dry_run=False,
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
    generator = _resolve_generator(config, options)
    method_config = MethodRunConfig(
        standard_max_new_tokens=options.standard_max_new_tokens,
        debate_role_max_new_tokens=options.debate_role_max_new_tokens,
        debate_moderator_max_new_tokens=options.debate_moderator_max_new_tokens,
    )

    _write_checkpoint(rows, output_dir, expected, "start")
    for method_condition in args.methods:
        for replicate_id in range(1, reps + 1):
            seed = options.base_seed + replicate_id
            for _, trial in trials.iterrows():
                key = _trial_key(trial, method_condition, replicate_id)
                if key in completed:
                    continue
                method_data = run_method_trial(generator, trial, method_condition, seed, method_config)
                parsed_answer, valid = parse_final_answer(str(method_data["final_raw_output"]))
                if parsed_answer == "Yes":
                    endorse_positive = int(bool(trial["yes_means_invariant"]))
                elif parsed_answer == "No":
                    endorse_positive = int(not bool(trial["yes_means_invariant"]))
                else:
                    endorse_positive = ""
                correct_answer = str(trial["correct_answer"]).strip().title()
                model_correct = parsed_answer == correct_answer if valid else ""
                rows.append(
                    {
                        **trial.to_dict(),
                        "prompt_condition": method_condition,
                        "method_condition": method_condition,
                        "replicate_id": replicate_id,
                        "seed": seed,
                        "parsed_answer": parsed_answer or "",
                        "valid": bool(valid),
                        "endorse_original_action": endorse_positive,
                        "endorse_positive_proposition": endorse_positive,
                        "model_correct": model_correct,
                        "agrees_with_user_belief": "",
                        **method_data,
                    }
                )
                completed.add(key)
                if len(rows) % options.checkpoint_every == 0:
                    _write_checkpoint(rows, output_dir, expected, f"checkpoint after {len(rows)}")
    _write_checkpoint(rows, output_dir, expected, "run complete")
    print(f"Run complete: {output_dir}")


if __name__ == "__main__":
    main()
