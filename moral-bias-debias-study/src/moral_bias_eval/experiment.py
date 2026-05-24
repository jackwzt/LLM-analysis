from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from .methods import MethodRunConfig, run_method_trial
from .stimuli import get_phase_stimuli, write_stimuli_csv


FINAL_ANSWER_PATTERN = re.compile(r"(?im)^\s*Final answer\s*:\s*(Yes|No)\s*$")
DEFAULT_METHODS = ["standard", "debate"]
ALL_METHODS = [
    "standard",
    "structured_cr",
    "self_debias_reprompt",
    "counterfactual_consistency_vote",
    "constitutional_critic",
    "anti_sycophancy_truth_first",
    "frame_invariant_rationale",
    "debate",
    "checklist",
    "critique_revise",
    "invariance_vote",
]


@dataclass(frozen=True)
class RunOptions:
    project_root: Path
    workspace_root: Path
    phase: str
    datasets: list[str]
    methods: list[str]
    repetitions_override: int | None
    base_seed: int
    checkpoint_every: int
    standard_max_new_tokens: int
    debate_role_max_new_tokens: int
    debate_moderator_max_new_tokens: int
    dry_run: bool
    output_name: str | None
    resume: bool
    provider: str
    deepseek_api_key: str | None
    api_key: str | None
    api_base_url: str | None
    api_model_id: str | None
    api_extra_body: dict[str, Any] | None
    api_disable_thinking: bool
    filter_groups_jsonl: Path | None
    filter_group_by: str


def load_config(config_path: Path) -> dict[str, Any]:
    return json.loads(config_path.read_text(encoding="utf-8"))


def phase_repetitions(phase: str, dataset: str, repetitions_override: int | None = None) -> int:
    if repetitions_override is not None:
        return int(repetitions_override)
    if dataset in {"sycophancy", "generated_sycophancy"}:
        mapping = {"smoke": 2, "pilot": 8, "full": 24}
    else:
        mapping = {"smoke": 2, "pilot": 8, "full": 56}
    if phase not in mapping:
        raise ValueError(f"Unsupported phase: {phase}")
    return mapping[phase]


def parse_final_answer(raw_text: str) -> tuple[str | None, bool]:
    matches = FINAL_ANSWER_PATTERN.findall(raw_text or "")
    if len(matches) != 1:
        return None, False
    answer = matches[0].strip().title()
    return answer, answer in {"Yes", "No"}


def compute_endorsement(answer: str | None, yes_means_invariant: bool) -> int | None:
    if answer == "Yes":
        return int(yes_means_invariant)
    if answer == "No":
        return int(not yes_means_invariant)
    return None


def _trial_key_from_values(
    dataset: str,
    dilemma: str,
    framing_condition: str,
    method_condition: str,
    replicate_id: int,
) -> tuple[str, str, str, str, int]:
    return (dataset, dilemma, framing_condition, method_condition, int(replicate_id))


def _load_existing_rows(raw_trials_path: Path) -> list[dict[str, Any]]:
    if not raw_trials_path.exists():
        return []
    frame = pd.read_csv(raw_trials_path, on_bad_lines="skip")
    if frame.empty:
        return []
    subset_cols = ["dataset", "dilemma", "framing_condition", "method_condition", "replicate_id"]
    if "method_condition" not in frame.columns and "prompt_condition" in frame.columns:
        frame["method_condition"] = frame["prompt_condition"]
    frame = frame.drop_duplicates(subset=subset_cols, keep="last")
    return frame.to_dict(orient="records")


def _load_allowed_groups(groups_jsonl_path: Path, group_by: str) -> set[tuple[str, ...]]:
    if group_by not in {"item", "item_frame"}:
        raise ValueError(f"Unsupported filter_group_by: {group_by}")

    allowed: set[tuple[str, ...]] = set()
    with groups_jsonl_path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            sample = json.loads(line)
            metadata = sample.get("metadata", {})
            if group_by == "item":
                allowed.add((str(metadata["dataset"]), str(metadata["dilemma"])))
            else:
                allowed.add(
                    (
                        str(metadata["dataset"]),
                        str(metadata["dilemma"]),
                        str(metadata["framing_condition"]),
                    )
                )
    return allowed


def _filter_frame_to_allowed_groups(
    frame: pd.DataFrame,
    groups_jsonl_path: Path | None,
    group_by: str,
) -> pd.DataFrame:
    if groups_jsonl_path is None:
        return frame

    allowed = _load_allowed_groups(groups_jsonl_path, group_by)
    if not allowed:
        raise ValueError(f"No allowed groups found in {groups_jsonl_path}")

    if group_by == "item":
        mask = frame.apply(lambda row: (str(row["dataset"]), str(row["dilemma"])) in allowed, axis=1)
    else:
        mask = frame.apply(
            lambda row: (
                str(row["dataset"]),
                str(row["dilemma"]),
                str(row["framing_condition"]),
            )
            in allowed,
            axis=1,
        )
    filtered = frame[mask].reset_index(drop=True)
    if filtered.empty:
        raise ValueError(f"Filtering by {groups_jsonl_path} removed all stimuli.")
    return filtered


def attach_frame_bundles(frame: pd.DataFrame) -> pd.DataFrame:
    """Attach same-item framing variants for counterfactual consistency methods."""
    enriched = frame.copy()
    bundle_by_key: dict[tuple[str, str], str] = {}
    for (dataset, dilemma), group in enriched.groupby(["dataset", "dilemma"], dropna=False):
        variants = []
        for _, row in group.sort_values("framing_condition").iterrows():
            variants.append(
                {
                    "framing_condition": str(row["framing_condition"]),
                    "scenario_text": str(row["scenario_text"]),
                    "yes_means_invariant": bool(row.get("yes_means_invariant", True)),
                }
            )
        bundle_by_key[(str(dataset), str(dilemma))] = json.dumps(variants, ensure_ascii=True)
    enriched["frame_bundle_json"] = enriched.apply(
        lambda row: bundle_by_key[(str(row["dataset"]), str(row["dilemma"]))],
        axis=1,
    )
    return enriched


def _write_checkpoint(rows: list[dict[str, Any]], output_dir: Path, expected_trials: int, note: str) -> None:
    raw_trials_path = output_dir / "raw_trials.csv"
    temp_path = output_dir / "raw_trials.tmp.csv"
    frame = pd.DataFrame(rows)
    frame.to_csv(temp_path, index=False)
    temp_path.replace(raw_trials_path)

    completed = 0 if frame.empty else len(frame)
    progress = {
        "completed_trials": completed,
        "expected_trials": expected_trials,
        "completion_rate": 0 if expected_trials == 0 else completed / expected_trials,
        "last_note": note,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    (output_dir / "progress.json").write_text(json.dumps(progress, indent=2), encoding="utf-8")


def _build_qwen_config(config: dict[str, Any]):
    from .qwen import QwenModelConfig

    return QwenModelConfig(
        model_id=config["model"]["model_id"],
        fallback_model_id=config["model"]["fallback_model_id"],
        quantization=config["model"]["quantization"],
        device_map=config["model"]["device_map"],
        temperature=config["generation"]["temperature"],
        top_p=config["generation"]["top_p"],
        top_k=config["generation"]["top_k"],
        enable_thinking=bool(config["generation"]["enable_thinking"]),
        adapter_path=config["model"].get("adapter_path"),
    )


def _build_gemma_config(config: dict[str, Any]):
    from .gemma import GemmaModelConfig

    gemma_config = config.get("gemma", {})
    if not gemma_config.get("model_id"):
        raise ValueError("Gemma provider selected, but no gemma.model_id is configured.")

    return GemmaModelConfig(
        model_id=str(gemma_config["model_id"]),
        quantization=str(gemma_config.get("quantization", "bnb4")),
        device_map=str(gemma_config.get("device_map", "auto")),
        temperature=float(config["generation"]["temperature"]),
        top_p=float(config["generation"]["top_p"]),
        top_k=int(config["generation"]["top_k"]),
        enable_thinking=bool(gemma_config.get("enable_thinking", False)),
        adapter_path=gemma_config.get("adapter_path"),
    )


def _build_deepseek_config(config: dict[str, Any], api_key: str):
    from .deepseek import DeepSeekModelConfig

    api_config = config.get("api", {}).get("deepseek", {})
    return DeepSeekModelConfig(
        api_key=api_key,
        base_url=str(api_config.get("base_url", "https://api.deepseek.com")),
        model_id=str(api_config.get("model_id", "deepseek-chat")),
        temperature=float(config["generation"]["temperature"]),
        top_p=float(config["generation"]["top_p"]),
        max_retries=int(api_config.get("max_retries", 3)),
        timeout_seconds=int(api_config.get("timeout_seconds", 180)),
        retry_base_delay_seconds=float(api_config.get("retry_base_delay_seconds", 2.0)),
        retry_max_delay_seconds=float(api_config.get("retry_max_delay_seconds", 60.0)),
        min_request_interval_seconds=float(api_config.get("min_request_interval_seconds", 0.0)),
        omit_seed=bool(api_config.get("omit_seed", False)),
        extra_body=dict(api_config.get("extra_body", {})),
    )


def _build_openai_compatible_config(config: dict[str, Any], options: RunOptions):
    from .openai_compatible import OpenAICompatibleConfig

    api_config = config.get("api", {}).get("openai_compatible", {})
    api_key = options.api_key or os.environ.get("OPENAI_COMPATIBLE_API_KEY")
    base_url = options.api_base_url or api_config.get("base_url")
    model_id = options.api_model_id or api_config.get("model_id")
    if not api_key:
        raise ValueError("OpenAI-compatible provider selected, but no API key was supplied.")
    if not base_url:
        raise ValueError("OpenAI-compatible provider selected, but no base URL was supplied.")
    if not model_id:
        raise ValueError("OpenAI-compatible provider selected, but no model ID was supplied.")

    merged_extra_body = dict(api_config.get("extra_body", {}))
    if options.api_extra_body:
        merged_extra_body.update(options.api_extra_body)
    if options.api_disable_thinking:
        merged_extra_body["enable_thinking"] = False

    return OpenAICompatibleConfig(
        api_key=str(api_key),
        base_url=str(base_url),
        model_id=str(model_id),
        temperature=float(config["generation"]["temperature"]),
        top_p=float(config["generation"]["top_p"]),
        max_retries=int(api_config.get("max_retries", 3)),
        timeout_seconds=int(api_config.get("timeout_seconds", 180)),
        retry_base_delay_seconds=float(api_config.get("retry_base_delay_seconds", 2.0)),
        retry_max_delay_seconds=float(api_config.get("retry_max_delay_seconds", 60.0)),
        min_request_interval_seconds=float(api_config.get("min_request_interval_seconds", 0.0)),
        omit_seed=bool(api_config.get("omit_seed", False)),
        extra_body=merged_extra_body,
    )


def _resolve_generator(config: dict[str, Any], options: RunOptions):
    if options.provider == "qwen":
        from .qwen import QwenGenerator

        generator = QwenGenerator(_build_qwen_config(config))
        generator.load()
        return generator
    if options.provider == "gemma":
        from .gemma import GemmaGenerator

        generator = GemmaGenerator(_build_gemma_config(config))
        generator.load()
        return generator
    if options.provider == "deepseek":
        api_key = options.deepseek_api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DeepSeek provider selected, but no API key was supplied.")
        from .deepseek import DeepSeekGenerator

        generator = DeepSeekGenerator(_build_deepseek_config(config, api_key))
        generator.load()
        return generator
    if options.provider == "openai_compatible":
        from .openai_compatible import OpenAICompatibleGenerator

        generator = OpenAICompatibleGenerator(_build_openai_compatible_config(config, options))
        generator.load()
        return generator
    raise ValueError(f"Unsupported provider: {options.provider}")


def _dry_run_method_payload(method_condition: str) -> dict[str, Any]:
    final_output = "Reason: Dry-run placeholder.\nFinal answer: Yes"
    return {
        "method_condition": method_condition,
        "final_raw_output": final_output,
        "method_trace_json": json.dumps([{"step_name": "dry_run", "content": final_output}], ensure_ascii=True),
        "latency_seconds": 0.0,
        "prompt_tokens": "",
        "completion_tokens": "",
        "total_tokens": "",
        "rational_analyst_output": "Dry-run rational output." if method_condition == "debate" else "",
        "intuitive_humanist_output": "Dry-run intuitive output." if method_condition == "debate" else "",
        "devils_advocate_output": "Dry-run advocate output." if method_condition == "debate" else "",
        "moderator_raw_output": final_output if method_condition == "debate" else "",
    }


def run_experiment(config: dict[str, Any], options: RunOptions) -> Path:
    stimuli_path = options.project_root / "data" / "derived" / "stimuli.csv"
    frame = write_stimuli_csv(options.workspace_root, stimuli_path)
    frame = get_phase_stimuli(frame, options.phase, options.datasets)
    frame = _filter_frame_to_allowed_groups(frame, options.filter_groups_jsonl, options.filter_group_by)
    frame = attach_frame_bundles(frame)

    run_name = options.output_name or f"{options.phase}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_dir = options.project_root / "results" / run_name
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_trials_path = output_dir / "raw_trials.csv"

    expected_trials = sum(
        len(frame[frame["dataset"] == dataset]) * phase_repetitions(options.phase, dataset, options.repetitions_override) * len(options.methods)
        for dataset in options.datasets
    )

    existing_rows = _load_existing_rows(raw_trials_path) if options.resume else []
    if raw_trials_path.exists() and not options.resume and options.output_name:
        raise FileExistsError(
            f"Output file already exists at {raw_trials_path}. Use --resume to continue this run or choose a new --output-name."
        )

    rows: list[dict[str, Any]] = list(existing_rows)
    completed_keys = {
        _trial_key_from_values(
            str(row["dataset"]),
            str(row["dilemma"]),
            str(row["framing_condition"]),
            str(row.get("method_condition", row.get("prompt_condition", "standard"))),
            int(row["replicate_id"]),
        )
        for row in rows
    }

    generator = None
    if not options.dry_run:
        generator = _resolve_generator(config, options)

    method_config = MethodRunConfig(
        standard_max_new_tokens=options.standard_max_new_tokens,
        debate_role_max_new_tokens=options.debate_role_max_new_tokens,
        debate_moderator_max_new_tokens=options.debate_moderator_max_new_tokens,
    )

    for dataset in options.datasets:
        dataset_frame = frame[frame["dataset"] == dataset].reset_index(drop=True)
        repetitions = phase_repetitions(options.phase, dataset, options.repetitions_override)
        for method_condition in options.methods:
            for replicate_id in range(1, repetitions + 1):
                seed = options.base_seed + replicate_id
                for _, stimulus in dataset_frame.iterrows():
                    trial_key = _trial_key_from_values(
                        dataset,
                        str(stimulus["dilemma"]),
                        str(stimulus["framing_condition"]),
                        method_condition,
                        replicate_id,
                    )
                    if trial_key in completed_keys:
                        continue

                    if options.dry_run:
                        method_data = _dry_run_method_payload(method_condition)
                    else:
                        method_data = run_method_trial(generator, stimulus, method_condition, seed, method_config)

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

                    rows.append(
                        {
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
                    )
                    completed_keys.add(trial_key)
                    if len(rows) % options.checkpoint_every == 0:
                        _write_checkpoint(
                            rows,
                            output_dir,
                            expected_trials,
                            note=f"checkpoint after {len(rows)} completed trials",
                        )

    _write_checkpoint(rows, output_dir, expected_trials, note="run complete")
    return output_dir
