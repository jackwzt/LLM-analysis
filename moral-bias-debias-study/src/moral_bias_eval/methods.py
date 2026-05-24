from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

import pandas as pd

from .generation import GenerationResult
from .prompts import (
    build_checklist_messages,
    build_anti_sycophancy_truth_first_messages,
    build_constitutional_critic_messages,
    build_counterfactual_probe_messages,
    build_counterfactual_resolution_messages,
    build_critique_messages,
    build_debate_messages,
    build_frame_invariant_rationale_messages,
    build_initial_answer_messages,
    build_invariance_probe_messages,
    build_revised_answer_messages,
    build_self_debias_reprompt_messages,
    build_standard_messages,
    build_structured_cr_messages,
)


FINAL_ANSWER_PATTERN = re.compile(r"(?im)^\s*Final answer\s*:\s*(Yes|No)\s*$")


@dataclass(frozen=True)
class MethodRunConfig:
    standard_max_new_tokens: int
    debate_role_max_new_tokens: int
    debate_moderator_max_new_tokens: int


def _empty_legacy_outputs() -> dict[str, str]:
    return {
        "rational_analyst_output": "",
        "intuitive_humanist_output": "",
        "devils_advocate_output": "",
        "moderator_raw_output": "",
    }


def _trace_payload(step_name: str, result: GenerationResult) -> dict[str, Any]:
    return result.to_trace_dict(step_name)


def _summarize_trace(trace: list[dict[str, Any]]) -> tuple[float, int | None, int | None, int | None]:
    total_latency = sum(float(item.get("latency_seconds") or 0.0) for item in trace)
    prompt_tokens = [item.get("prompt_tokens") for item in trace if item.get("prompt_tokens") is not None]
    completion_tokens = [item.get("completion_tokens") for item in trace if item.get("completion_tokens") is not None]
    total_tokens = [item.get("total_tokens") for item in trace if item.get("total_tokens") is not None]
    return (
        total_latency,
        sum(prompt_tokens) if prompt_tokens else None,
        sum(completion_tokens) if completion_tokens else None,
        sum(total_tokens) if total_tokens else None,
    )


def _parse_final_answer(raw_text: str) -> str | None:
    matches = FINAL_ANSWER_PATTERN.findall(raw_text or "")
    if len(matches) != 1:
        return None
    answer = matches[0].strip().title()
    return answer if answer in {"Yes", "No"} else None


def _answer_to_endorsement(answer: str | None, yes_means_invariant: bool) -> int | None:
    if answer == "Yes":
        return int(yes_means_invariant)
    if answer == "No":
        return int(not yes_means_invariant)
    return None


def _endorsement_to_current_answer(endorsement: int, yes_means_invariant: bool) -> str:
    if bool(endorsement) == bool(yes_means_invariant):
        return "Yes"
    return "No"


def _result_payload(
    *,
    method_condition: str,
    final_output: str,
    trace: list[dict[str, Any]],
    legacy_outputs: dict[str, str] | None = None,
) -> dict[str, Any]:
    latency_seconds, prompt_tokens, completion_tokens, total_tokens = _summarize_trace(trace)
    payload = {
        "method_condition": method_condition,
        "final_raw_output": final_output,
        "method_trace_json": json.dumps(trace, ensure_ascii=True),
        "latency_seconds": latency_seconds,
        "prompt_tokens": prompt_tokens if prompt_tokens is not None else "",
        "completion_tokens": completion_tokens if completion_tokens is not None else "",
        "total_tokens": total_tokens if total_tokens is not None else "",
    }
    payload.update(_empty_legacy_outputs())
    if legacy_outputs:
        payload.update(legacy_outputs)
    if method_condition == "debate":
        payload["moderator_raw_output"] = final_output
    return payload


def run_standard_trial(generator, stimulus: pd.Series, seed: int, config: MethodRunConfig) -> dict[str, Any]:
    result = generator.generate(
        build_standard_messages(stimulus["participant_prompt"], stimulus["scenario_text"]),
        seed=seed,
        max_new_tokens=config.standard_max_new_tokens,
    )
    return _result_payload(
        method_condition="standard",
        final_output=result.content,
        trace=[_trace_payload("standard_answer", result)],
    )


def run_structured_cr_trial(generator, stimulus: pd.Series, seed: int, config: MethodRunConfig) -> dict[str, Any]:
    result = generator.generate(
        build_structured_cr_messages(stimulus["participant_prompt"], stimulus["scenario_text"]),
        seed=seed,
        max_new_tokens=config.standard_max_new_tokens,
    )
    return _result_payload(
        method_condition="structured_cr",
        final_output=result.content,
        trace=[_trace_payload("structured_cr_answer", result)],
    )


def run_self_debias_reprompt_trial(generator, stimulus: pd.Series, seed: int, config: MethodRunConfig) -> dict[str, Any]:
    initial_result = generator.generate(
        build_initial_answer_messages(stimulus["participant_prompt"], stimulus["scenario_text"]),
        seed=seed,
        max_new_tokens=config.debate_moderator_max_new_tokens,
    )
    revised_result = generator.generate(
        build_self_debias_reprompt_messages(
            stimulus["participant_prompt"],
            stimulus["scenario_text"],
            initial_result.content,
        ),
        seed=seed + 1,
        max_new_tokens=config.debate_moderator_max_new_tokens,
    )
    return _result_payload(
        method_condition="self_debias_reprompt",
        final_output=revised_result.content,
        trace=[
            _trace_payload("initial_answer", initial_result),
            _trace_payload("self_debias_reprompt", revised_result),
        ],
    )


def _load_frame_bundle(stimulus: pd.Series) -> list[dict[str, Any]]:
    raw_bundle = stimulus.get("frame_bundle_json", "")
    if isinstance(raw_bundle, str) and raw_bundle.strip():
        try:
            bundle = json.loads(raw_bundle)
        except json.JSONDecodeError:
            bundle = []
    else:
        bundle = []
    if bundle:
        return bundle
    return [
        {
            "framing_condition": str(stimulus["framing_condition"]),
            "scenario_text": str(stimulus["scenario_text"]),
            "yes_means_invariant": bool(stimulus.get("yes_means_invariant", True)),
        }
    ]


def _current_answer_from_counterfactual_votes(stimulus: pd.Series, votes: list[dict[str, Any]]) -> str | None:
    task_family = str(stimulus.get("task_family", ""))
    valid_votes = [vote for vote in votes if vote.get("answer") in {"Yes", "No"}]
    if not valid_votes:
        return None

    if task_family == "moral":
        endorsements: list[int] = []
        for vote in valid_votes:
            endorsement = _answer_to_endorsement(
                vote.get("answer"),
                bool(vote.get("yes_means_invariant", True)),
            )
            if endorsement is not None:
                endorsements.append(endorsement)
        if not endorsements:
            return None
        yes_count = sum(endorsements)
        no_count = len(endorsements) - yes_count
        if yes_count == no_count:
            return None
        majority_endorsement = int(yes_count > no_count)
        return _endorsement_to_current_answer(majority_endorsement, bool(stimulus["yes_means_invariant"]))

    yes_count = sum(1 for vote in valid_votes if vote.get("answer") == "Yes")
    no_count = sum(1 for vote in valid_votes if vote.get("answer") == "No")
    if yes_count == no_count:
        return None
    return "Yes" if yes_count > no_count else "No"


def run_counterfactual_consistency_vote_trial(
    generator,
    stimulus: pd.Series,
    seed: int,
    config: MethodRunConfig,
) -> dict[str, Any]:
    trace: list[dict[str, Any]] = []
    votes: list[dict[str, Any]] = []
    for offset, variant in enumerate(_load_frame_bundle(stimulus)):
        result = generator.generate(
            build_counterfactual_probe_messages(
                stimulus["participant_prompt"],
                str(variant["scenario_text"]),
                str(variant["framing_condition"]),
            ),
            seed=seed + offset,
            max_new_tokens=config.standard_max_new_tokens,
        )
        answer = _parse_final_answer(result.content)
        votes.append(
            {
                "framing_condition": variant.get("framing_condition"),
                "answer": answer,
                "yes_means_invariant": bool(variant.get("yes_means_invariant", True)),
            }
        )
        trace.append(_trace_payload(f"probe_{variant.get('framing_condition', offset)}", result))

    current_answer = _current_answer_from_counterfactual_votes(stimulus, votes)
    vote_summary = "; ".join(
        f"{vote.get('framing_condition')}={vote.get('answer') or 'Invalid'}" for vote in votes
    )
    if current_answer:
        final_output = f"Reason: Counterfactual variants support the invariant judgment ({vote_summary}).\nFinal answer: {current_answer}"
        trace.append(
            {
                "step_name": "vote_aggregation",
                "content": final_output,
                "latency_seconds": 0.0,
                "prompt_tokens": None,
                "completion_tokens": None,
                "total_tokens": None,
                "raw_response": {"votes": votes},
            }
        )
    else:
        resolution_result = generator.generate(
            build_counterfactual_resolution_messages(
                stimulus["participant_prompt"],
                stimulus["scenario_text"],
                vote_summary,
            ),
            seed=seed + 99,
            max_new_tokens=config.debate_moderator_max_new_tokens,
        )
        final_output = resolution_result.content
        trace.append(_trace_payload("consistency_resolution", resolution_result))

    return _result_payload(
        method_condition="counterfactual_consistency_vote",
        final_output=final_output,
        trace=trace,
    )


def run_constitutional_critic_trial(generator, stimulus: pd.Series, seed: int, config: MethodRunConfig) -> dict[str, Any]:
    initial_result = generator.generate(
        build_initial_answer_messages(stimulus["participant_prompt"], stimulus["scenario_text"]),
        seed=seed,
        max_new_tokens=config.debate_moderator_max_new_tokens,
    )
    final_result = generator.generate(
        build_constitutional_critic_messages(
            stimulus["participant_prompt"],
            stimulus["scenario_text"],
            initial_result.content,
        ),
        seed=seed + 1,
        max_new_tokens=config.debate_moderator_max_new_tokens,
    )
    return _result_payload(
        method_condition="constitutional_critic",
        final_output=final_result.content,
        trace=[
            _trace_payload("initial_answer", initial_result),
            _trace_payload("constitutional_critic", final_result),
        ],
    )


def run_anti_sycophancy_truth_first_trial(generator, stimulus: pd.Series, seed: int, config: MethodRunConfig) -> dict[str, Any]:
    result = generator.generate(
        build_anti_sycophancy_truth_first_messages(stimulus["participant_prompt"], stimulus["scenario_text"]),
        seed=seed,
        max_new_tokens=config.debate_moderator_max_new_tokens,
    )
    return _result_payload(
        method_condition="anti_sycophancy_truth_first",
        final_output=result.content,
        trace=[_trace_payload("truth_first_answer", result)],
    )


def run_frame_invariant_rationale_trial(generator, stimulus: pd.Series, seed: int, config: MethodRunConfig) -> dict[str, Any]:
    result = generator.generate(
        build_frame_invariant_rationale_messages(stimulus["participant_prompt"], stimulus["scenario_text"]),
        seed=seed,
        max_new_tokens=config.debate_moderator_max_new_tokens,
    )
    return _result_payload(
        method_condition="frame_invariant_rationale",
        final_output=result.content,
        trace=[_trace_payload("frame_invariant_rationale", result)],
    )


def run_checklist_trial(generator, stimulus: pd.Series, seed: int, config: MethodRunConfig) -> dict[str, Any]:
    result = generator.generate(
        build_checklist_messages(stimulus["participant_prompt"], stimulus["scenario_text"]),
        seed=seed,
        max_new_tokens=config.debate_moderator_max_new_tokens,
    )
    return _result_payload(
        method_condition="checklist",
        final_output=result.content,
        trace=[_trace_payload("checklist_answer", result)],
    )


def run_critique_revise_trial(generator, stimulus: pd.Series, seed: int, config: MethodRunConfig) -> dict[str, Any]:
    initial_result = generator.generate(
        build_initial_answer_messages(stimulus["participant_prompt"], stimulus["scenario_text"]),
        seed=seed,
        max_new_tokens=config.debate_moderator_max_new_tokens,
    )
    critique_result = generator.generate(
        build_critique_messages(stimulus["participant_prompt"], stimulus["scenario_text"], initial_result.content),
        seed=seed + 1,
        max_new_tokens=config.debate_role_max_new_tokens,
    )
    revised_result = generator.generate(
        build_revised_answer_messages(
            stimulus["participant_prompt"],
            stimulus["scenario_text"],
            initial_result.content,
            critique_result.content,
        ),
        seed=seed + 2,
        max_new_tokens=config.debate_moderator_max_new_tokens,
    )
    return _result_payload(
        method_condition="critique_revise",
        final_output=revised_result.content,
        trace=[
            _trace_payload("initial_answer", initial_result),
            _trace_payload("self_critique", critique_result),
            _trace_payload("revised_answer", revised_result),
        ],
    )


def _debate_trace(generator, stimulus: pd.Series, seed: int, config: MethodRunConfig) -> tuple[list[dict[str, Any]], dict[str, str]]:
    prior_turns: list[tuple[str, str]] = []
    trace: list[dict[str, Any]] = []
    legacy_outputs = _empty_legacy_outputs()
    role_order = [
        ("Rational Analyst", "rational_analyst_output"),
        ("Intuitive Humanist", "intuitive_humanist_output"),
        ("Devil's Advocate", "devils_advocate_output"),
    ]
    for offset, (role_name, field_name) in enumerate(role_order, start=1):
        result = generator.generate(
            build_debate_messages(
                participant_prompt=stimulus["participant_prompt"],
                scenario_text=stimulus["scenario_text"],
                role_name=role_name,
                prior_turns=prior_turns,
            ),
            seed=seed + offset,
            max_new_tokens=config.debate_role_max_new_tokens,
        )
        legacy_outputs[field_name] = result.content
        trace.append(_trace_payload(role_name.lower().replace(" ", "_"), result))
        prior_turns.append((role_name, result.content))

    moderator_result = generator.generate(
        build_debate_messages(
            participant_prompt=stimulus["participant_prompt"],
            scenario_text=stimulus["scenario_text"],
            role_name="Moderator",
            prior_turns=prior_turns,
        ),
        seed=seed + 99,
        max_new_tokens=config.debate_moderator_max_new_tokens,
    )
    legacy_outputs["moderator_raw_output"] = moderator_result.content
    trace.append(_trace_payload("moderator", moderator_result))
    return trace, legacy_outputs


def run_debate_trial(generator, stimulus: pd.Series, seed: int, config: MethodRunConfig) -> dict[str, Any]:
    trace, legacy_outputs = _debate_trace(generator, stimulus, seed, config)
    return _result_payload(
        method_condition="debate",
        final_output=legacy_outputs["moderator_raw_output"],
        trace=trace,
        legacy_outputs=legacy_outputs,
    )


def run_invariance_vote_trial(generator, stimulus: pd.Series, seed: int, config: MethodRunConfig) -> dict[str, Any]:
    probes = [
        ("original_probe", "original", seed),
        ("invariant_probe", "invariant", seed + 1),
        ("neutral_probe", "neutral", seed + 2),
    ]
    trace: list[dict[str, Any]] = []
    probe_outputs: list[tuple[str, str]] = []
    for step_name, probe_kind, step_seed in probes:
        result = generator.generate(
            build_invariance_probe_messages(
                participant_prompt=stimulus["participant_prompt"],
                scenario_text=stimulus["scenario_text"],
                neutral_scenario_text=str(stimulus.get("neutral_scenario_text", "") or ""),
                probe_kind=probe_kind,
            ),
            seed=step_seed,
            max_new_tokens=config.standard_max_new_tokens,
        )
        trace.append(_trace_payload(step_name, result))
        probe_outputs.append((probe_kind, result.content))

    parsed_votes: list[tuple[str, str]] = []
    for probe_kind, output_text in probe_outputs:
        normalized = output_text.lower()
        if "final answer: yes" in normalized:
            parsed_votes.append((probe_kind, "Yes"))
        elif "final answer: no" in normalized:
            parsed_votes.append((probe_kind, "No"))

    final_answer = ""
    if len(parsed_votes) >= 2:
        yes_count = sum(1 for _, answer in parsed_votes if answer == "Yes")
        no_count = sum(1 for _, answer in parsed_votes if answer == "No")
        if yes_count > no_count:
            final_answer = "Yes"
        elif no_count > yes_count:
            final_answer = "No"
        else:
            neutral_vote = next((answer for kind, answer in parsed_votes if kind == "neutral"), "")
            final_answer = neutral_vote or parsed_votes[0][1]
    elif len(parsed_votes) == 1:
        final_answer = parsed_votes[0][1]

    rationale = "; ".join(f"{kind}={answer}" for kind, answer in parsed_votes) if parsed_votes else "No valid vote"
    final_output = f"Reason: Invariance vote based on {rationale}.\nFinal answer: {final_answer}" if final_answer else "Reason: Invariance vote failed.\nFinal answer: Unknown"
    trace.append(
        {
            "step_name": "vote_aggregation",
            "content": final_output,
            "latency_seconds": 0.0,
            "prompt_tokens": None,
            "completion_tokens": None,
            "total_tokens": None,
            "raw_response": {"votes": parsed_votes},
        }
    )
    return _result_payload(
        method_condition="invariance_vote",
        final_output=final_output,
        trace=trace,
    )


def run_method_trial(
    generator,
    stimulus: pd.Series,
    method_condition: str,
    seed: int,
    config: MethodRunConfig,
) -> dict[str, Any]:
    if method_condition == "standard":
        return run_standard_trial(generator, stimulus, seed, config)
    if method_condition == "structured_cr":
        return run_structured_cr_trial(generator, stimulus, seed, config)
    if method_condition == "self_debias_reprompt":
        return run_self_debias_reprompt_trial(generator, stimulus, seed, config)
    if method_condition == "counterfactual_consistency_vote":
        return run_counterfactual_consistency_vote_trial(generator, stimulus, seed, config)
    if method_condition == "constitutional_critic":
        return run_constitutional_critic_trial(generator, stimulus, seed, config)
    if method_condition == "anti_sycophancy_truth_first":
        return run_anti_sycophancy_truth_first_trial(generator, stimulus, seed, config)
    if method_condition == "frame_invariant_rationale":
        return run_frame_invariant_rationale_trial(generator, stimulus, seed, config)
    if method_condition == "debate":
        return run_debate_trial(generator, stimulus, seed, config)
    if method_condition == "checklist":
        return run_checklist_trial(generator, stimulus, seed, config)
    if method_condition == "critique_revise":
        return run_critique_revise_trial(generator, stimulus, seed, config)
    if method_condition == "invariance_vote":
        return run_invariance_vote_trial(generator, stimulus, seed, config)
    raise ValueError(f"Unsupported method_condition: {method_condition}")
