"""Dispatch only the frozen Phase 3B train/evaluation scripts; never alter their inputs."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


CONFIG=Path("research/protocols/phase3b_config.json")
ROOT=Path(".runtime/phase3b")
JAVA=".tools/jdk-25.0.1+8/bin/java.exe"
JAR=".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar"


def dispatch(label: str, output: Path, args: list[str]) -> None:
    if output.exists():
        obj=json.loads(output.read_text(encoding="utf-8"))
        if obj.get("config_sha256")!="52cc6c8400e5675389a9ca151137a179442af6e6021859aa8572a819855e907f":
            raise ValueError(f"Completed output config mismatch: {output}")
        print(f"SKIP completed {label}",flush=True)
        return
    print(f"START {label}",flush=True)
    env=os.environ.copy(); env["PYTHONPATH"]="src;scripts"
    subprocess.run([sys.executable,*args],env=env,check=True)
    if not output.is_file(): raise RuntimeError(f"Missing output after {label}: {output}")
    print(f"DONE {label}",flush=True)


def main() -> None:
    cfg=json.loads(CONFIG.read_text(encoding="utf-8"))
    if cfg["seeds"]!=[20260924,20261012,20261118] or cfg["runtime_root"]!=str(ROOT).replace('\\','/'):
        raise ValueError("Unexpected Phase 3B configuration")
    common=["--config",str(CONFIG),"--java",JAVA,"--jar",JAR]
    for suite in ("A","B","regression"):
        path=ROOT/"evaluations"/"base"/f"base_{suite.lower()}.json"
        dispatch(f"base {suite}",path,["scripts/run_phase3b_evaluation.py",*common,"--suite",suite,"--condition","base"])
    for seed in cfg["seeds"]:
        label=str(seed)
        path=ROOT/"training"/label/"A.json"
        dispatch(f"A train {seed}",path,["scripts/train_phase3b_qlora.py","--config",str(CONFIG),"--seed",label,"--condition","A"])
        for suite in ("A","B","regression"):
            path=ROOT/"evaluations"/label/f"A_{suite.lower()}.json"
            dispatch(f"A {seed} {suite}",path,["scripts/run_phase3b_evaluation.py",*common,"--seed",label,"--suite",suite,"--condition","A"])
        for condition in ("naive","replay"):
            path=ROOT/"training"/label/f"{condition}.json"
            dispatch(f"{condition} train {seed}",path,["scripts/train_phase3b_qlora.py","--config",str(CONFIG),"--seed",label,"--condition",condition])
            for suite in ("A","B","regression"):
                path=ROOT/"evaluations"/label/f"{condition}_{suite.lower()}.json"
                dispatch(f"{condition} {seed} {suite}",path,["scripts/run_phase3b_evaluation.py",*common,"--seed",label,"--suite",suite,"--condition",condition])


if __name__=="__main__": main()
