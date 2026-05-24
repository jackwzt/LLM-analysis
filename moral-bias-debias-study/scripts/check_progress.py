from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_ROOT = PROJECT_ROOT / "results"


def load_progress(run_dir: Path) -> tuple[int, int]:
    progress_path = run_dir / "progress.json"
    if progress_path.exists():
        progress = json.loads(progress_path.read_text(encoding="utf-8"))
        return int(progress.get("completed_trials", 0)), int(progress.get("expected_trials", 0))

    raw_trials_path = run_dir / "raw_trials.csv"
    if not raw_trials_path.exists():
        return 0, 0

    frame = pd.read_csv(raw_trials_path, on_bad_lines="skip")
    return len(frame), 0


def load_state(state_path: Path) -> dict:
    if not state_path.exists():
        return {"last_reported_milestone": 0}
    return json.loads(state_path.read_text(encoding="utf-8"))


def save_state(state_path: Path, state: dict) -> None:
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def build_report(completed: int, expected: int, milestone: int) -> str:
    completion = 0.0 if expected <= 0 else completed / expected
    return (
        f"Milestone reached: {milestone} trials\n"
        f"Completed: {completed} / {expected if expected > 0 else '?'}\n"
        f"Completion rate: {completion:.2%}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Report experiment progress only when a new milestone is reached.")
    parser.add_argument("--run-name", required=True, help="Run directory name under results/.")
    parser.add_argument("--milestone-size", type=int, default=200, help="Milestone interval. Default: 200.")
    parser.add_argument(
        "--state-file",
        type=Path,
        default=None,
        help="Optional explicit milestone state file. Defaults to results/<run>/milestone_state.json.",
    )
    parser.add_argument(
        "--print-current",
        action="store_true",
        help="Print current progress even if no new milestone was reached.",
    )
    args = parser.parse_args()

    run_dir = RESULTS_ROOT / args.run_name
    if not run_dir.exists():
        raise FileNotFoundError(f"Run directory not found: {run_dir}")
    if args.milestone_size <= 0:
        raise ValueError("--milestone-size must be positive")

    state_path = args.state_file or (run_dir / "milestone_state.json")
    completed, expected = load_progress(run_dir)
    state = load_state(state_path)
    last_reported = int(state.get("last_reported_milestone", 0))
    current_milestone = (completed // args.milestone_size) * args.milestone_size

    if current_milestone > last_reported:
        state["last_reported_milestone"] = current_milestone
        save_state(state_path, state)
        print(build_report(completed, expected, current_milestone))
        return 0

    if args.print_current:
        completion = 0.0 if expected <= 0 else completed / expected
        print(
            f"No new milestone. Current progress: {completed} / {expected if expected > 0 else '?'} "
            f"({completion:.2%})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
