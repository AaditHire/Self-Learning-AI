"""CONF1 analysis wrapper. No model imports or model calls."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from self_learning_ai.conf1_r1.execution import GateStop, require_execution_authorization, run_analysis


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--check-authorization-only", action="store_true")
    args = parser.parse_args()
    try:
        require_execution_authorization(args.candidate_dir)
        if args.check_authorization_only:
            print("CONF1 authorization PASS; no model imported")
            return
        report = run_analysis(args.candidate_dir)
        print(json.dumps({"label": report["label"], "acquisition": report["acquisition"]["passed"]}))
    except GateStop as exc:
        parser.exit(2, str(exc) + "\n")


if __name__ == "__main__":
    main()
