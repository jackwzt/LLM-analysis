from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from moral_bias_eval.experiment import ALL_METHODS, DEFAULT_METHODS, RunOptions, load_config, run_experiment


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the moral bias experiment with a local or API-backed model.")
    parser.add_argument("--phase", choices=["smoke", "pilot", "full"], required=True)
    parser.add_argument(
        "--datasets",
        nargs="+",
        default=["exp2"],
        choices=["exp2", "exp3", "sycophancy", "generated_moral", "generated_sycophancy"],
    )
    parser.add_argument("--methods", nargs="+", default=DEFAULT_METHODS, choices=ALL_METHODS)
    parser.add_argument("--repetitions-override", type=int, default=None, help="Optional override for repetitions per cell.")
    parser.add_argument("--config", type=Path, default=PROJECT_ROOT / "configs" / "experiment.default.json")
    parser.add_argument("--dry-run", action="store_true", help="Skip model loading and emit deterministic placeholder outputs.")
    parser.add_argument("--output-name", type=str, default=None, help="Optional fixed run directory name.")
    parser.add_argument("--resume", action="store_true", help="Resume an existing run directory by skipping completed trials in raw_trials.csv.")
    parser.add_argument("--provider", choices=["qwen", "gemma", "deepseek", "openai_compatible"], default="qwen")
    parser.add_argument("--deepseek-api-key", type=str, default=None, help="Optional DeepSeek API key. Prefer using the DEEPSEEK_API_KEY environment variable.")
    parser.add_argument("--api-key", type=str, default=None, help="Optional API key for the openai_compatible provider. Prefer environment variables.")
    parser.add_argument("--api-base-url", type=str, default=None, help="Base URL for the openai_compatible provider.")
    parser.add_argument("--api-model-id", type=str, default=None, help="Model ID for the openai_compatible provider.")
    parser.add_argument("--api-extra-body", type=str, default=None, help="Optional JSON object merged into the request body for the openai_compatible provider.")
    parser.add_argument("--api-extra-body-file", type=Path, default=None, help="Optional path to a JSON file merged into the request body for the openai_compatible provider.")
    parser.add_argument("--api-disable-thinking", action="store_true", help="Set enable_thinking=false for providers that support this flag.")
    parser.add_argument("--filter-groups-jsonl", type=Path, default=None, help="Optional distillation JSONL split used to restrict evaluation stimuli.")
    parser.add_argument("--filter-group-by", choices=["item", "item_frame"], default="item", help="Granularity for --filter-groups-jsonl.")
    args = parser.parse_args()

    config = load_config(args.config)
    if args.api_extra_body and args.api_extra_body_file:
        parser.error("--api-extra-body and --api-extra-body-file are mutually exclusive.")
    if args.api_extra_body_file:
        api_extra_body = json.loads(args.api_extra_body_file.read_text(encoding="utf-8"))
    else:
        api_extra_body = json.loads(args.api_extra_body) if args.api_extra_body else None
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
        deepseek_api_key=args.deepseek_api_key,
        api_key=args.api_key,
        api_base_url=args.api_base_url,
        api_model_id=args.api_model_id,
        api_extra_body=api_extra_body,
        api_disable_thinking=bool(args.api_disable_thinking),
        filter_groups_jsonl=args.filter_groups_jsonl,
        filter_group_by=args.filter_group_by,
    )

    output_dir = run_experiment(config, options)
    print(f"Run complete: {output_dir}")


if __name__ == "__main__":
    main()
