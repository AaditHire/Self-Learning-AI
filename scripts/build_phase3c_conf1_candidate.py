"""CLI for separately authorized CONF1 construction or a synthetic rehearsal."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from self_learning_ai.conf1_r1 import candidate
from self_learning_ai.conf1_r1.gates_primary import GateStop


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--seed", type=int, required=True)
    result.add_argument("--out", type=Path, required=True)
    result.add_argument("--workers", type=int, default=8)
    result.add_argument("--authorized-construction", action="store_true")
    return result


def validate_cli(args):
    """CLI's refusal path, independently testable without invoking the builder."""
    label = ("CONF1_CONSTRUCTION" if args.seed == candidate.CONSTRUCTION_SEED else candidate.SYNTHETIC_LABEL)
    candidate.validate_request(args.seed, label=label, authorized_construction=args.authorized_construction,
                               workers=args.workers)
    if args.out.exists() or args.out.is_symlink():
        raise GateStop("refusing an existing output path", {"out_dir": str(args.out)})
    return label


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        label = validate_cli(args)
        candidate.build_candidate(args.seed, args.out, label=label,
                                  authorized_construction=args.authorized_construction, workers=args.workers)
    except GateStop as exc:
        print(str(exc), file=sys.stderr, flush=True)
        return 2
    print(args.out.resolve() / "candidate_manifest.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
