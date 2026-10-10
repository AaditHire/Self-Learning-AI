"""Build dev and sealed B0 pools together; no model use."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from self_learning_ai.explore.pools import build_pools
from self_learning_ai.explore.runlog import append_run

if __name__ == "__main__":
    try:
        manifest = build_pools()
        append_run(dict(run="b0_pool_build", status="PASS", manifest=manifest))
    except Exception as exc:
        append_run(dict(run="b0_pool_build", status="FAIL", error=repr(exc)))
        raise
