from __future__ import annotations

import subprocess
import sys
from pathlib import Path


CONFIG="research/protocols/phase3a_config.json"
JAVA=".tools/jdk-25.0.1+8/bin/java.exe"
JAR=".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar"


def run(*args: str):
    output=Path(args[-1])
    if output.exists(): raise FileExistsError(output)
    print("START", " ".join(args), flush=True)
    completed=subprocess.run([sys.executable,*args],check=True)
    print("DONE", output, completed.returncode, flush=True)


def train(seed: int, stage: str, exp: int):
    run("scripts/train_phase3a_qlora.py","--config",CONFIG,"--seed",str(seed),"--stage",stage,"--output",f"research/results/EXP-{exp:04d}/training.json")


def evaluate(seed: int, condition: str, suite: str):
    exp=35 if suite=="regression" else 34
    run("scripts/run_phase3a_evaluation.py","--config",CONFIG,"--suite",suite,"--condition",condition,"--seed",str(seed),"--java",JAVA,"--jar",JAR,"--output",f"research/results/EXP-{exp:04d}/{condition}_{suite}_seed_{seed}.json")


def main():
    for seed,a_exp,b_exp in ((20261011,30,31),(20261117,32,33)):
        train(seed,"A",a_exp)
        evaluate(seed,"A","A")
        evaluate(seed,"A","B")
        evaluate(seed,"A","regression")
        train(seed,"B",b_exp)
        evaluate(seed,"AtoB","B")
        evaluate(seed,"AtoB","A")
        evaluate(seed,"AtoB","regression")


if __name__=="__main__": main()
