from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from moral_bias_eval.stimuli import write_stimuli_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract Exp2 and Exp3 stimuli from the OSF archive.")
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Path to the OSF archive workspace root.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "data" / "derived" / "stimuli.csv",
        help="Output CSV path.",
    )
    args = parser.parse_args()

    frame = write_stimuli_csv(args.workspace_root, args.output)
    print(f"Wrote {len(frame)} rows to {args.output}")


if __name__ == "__main__":
    main()
