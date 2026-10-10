"""Append-only EXPLORATORY run ledger."""
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def append_run(record: dict):
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip())
    path = ROOT / "research/explore/run_log.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    row = dict(record, label="EXPLORATORY", utc_time=datetime.now(timezone.utc).isoformat(),
               git_head=head, dirty_tree=dirty)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
