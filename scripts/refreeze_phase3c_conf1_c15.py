"""One-time C15 re-freeze; no model imports or execution."""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from self_learning_ai.conf1_r1 import execution

COMMIT1 = "611cdc2dd1764723450342b11b7672252eb97d86"
PREVIOUS = "d10895fb3a236e49c82e6bae09b0b5e05a2b62f43d929ab3c9fc80e7e1e1ecfb"
COMPILER = "e10a7bacf43a287d7a180a831842f16eead8d1331bba9f4c3a5cacbceb8beb4c"
SCRIPT = "scripts/refreeze_phase3c_conf1_c15.py"
BASE = "research/results/PHASE_3C_CONF1_PREFREEZE/"
CANDIDATE = ROOT / BASE / "attempt_004"
MANIFEST = CANDIDATE / "candidate_manifest.json"
REPORT = ROOT / BASE / "attempt_004_freeze/c15_refreeze_report.json"
EXTERNAL = Path(r"C:\Users\Admin\conf1-c15-pytest")
IGNORED_BASELINE = EXTERNAL / "ignored-at-commit1.bin"
IGNORED_BASELINE_SHA256 = "63bacc91ac1b3b6b82986bbfc8cb35a271dde09bf7cb7e660194482e0c99b6dc"
CHANGED = {"src/self_learning_ai/conf1_r1/execution.py", "scripts/evaluate_phase3c_conf1.py"}
ADDED = [
    "research/protocols/phase3c_conf1_implementation_clarifications_c15.md",
    "research/protocols/phase3c_conf1_c15_reviewed_incident.json",
    "tests/test_conf1_r1_c15.py",
    SCRIPT,
]
FORBIDDEN_IMPORTS = {"torch", "transformers", "peft", "bitsandbytes", "accelerate"}
REFUSAL = "CONF1 model execution is not explicitly authorized"


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False,
                       allow_nan=False) + "\n").encode("utf-8")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def sha(path):
    return digest(Path(path).read_bytes())


def require(condition, reason):
    if not condition:
        raise execution.GateStop(reason)


def git(*args):
    return subprocess.check_output(["git", "--no-optional-locks", *args], cwd=ROOT)


def ignored_paths(raw):
    return set(raw.split(b"\0")) - {b""}


def check_ignored():
    raw = IGNORED_BASELINE.read_bytes()
    require(digest(raw) == IGNORED_BASELINE_SHA256, "ignored baseline hash mismatch")
    before = ignored_paths(raw)
    current = ignored_paths(git("ls-files", "--others", "--ignored", "--exclude-standard", "-z"))
    require(not (current - before), "new ignored files since COMMIT1")
    return {"passed": True, "baseline_sha256": IGNORED_BASELINE_SHA256,
            "baseline_paths": len(before), "current_paths": len(current),
            "new_ignored_paths": 0}


def main():
    started = time.perf_counter()
    checks = {}
    require(git("branch", "--show-current").strip() == b"main", "start branch mismatch")
    require(git("rev-parse", "HEAD").strip().decode() == COMMIT1, "HEAD must equal COMMIT1")
    status = git("status", "--porcelain", "--untracked-files=all").decode().splitlines()
    require(status == ["?? " + SCRIPT], "start tree must contain only the untracked re-freeze script")
    checks["start"] = {"passed": True, "head": COMMIT1, "branch": "main", "status": status,
                       "no_modified_paths": True, "no_staged_paths": True, "no_other_untracked_paths": True}
    checks["ignored_at_start"] = check_ignored()
    require(sha(MANIFEST) == PREVIOUS, "previous manifest hash mismatch")
    require(not REPORT.exists(), "C15 re-freeze report already exists")
    original_bytes = MANIFEST.read_bytes()
    original = json.loads(original_bytes)
    require(original["status"] == "CANDIDATE_FROZEN", "candidate status mismatch")
    require(original["model_execution_authorized"] is True, "superseded authorization mismatch")
    require(canonical(original) == original_bytes, "original manifest is not canonical JSON")
    checks["previous_manifest"] = {"passed": True, "sha256": PREVIOUS, "canonical": True,
                                   "status": original["status"], "model_execution_authorized": True}
    frozen = copy.deepcopy(original)
    changed = {}
    code_checks = {}
    for name, old in original["code_hashes"].items():
        new = sha(ROOT / name)
        require(new == old or name in CHANGED, "unapproved code hash change: " + name)
        code_checks[name] = {"old": old, "new": new, "passed": True}
        if new != old:
            changed[name] = {"old": old, "new": new}
            frozen["code_hashes"][name] = new
    require(set(changed) == CHANGED, "expected exactly the two amended code hashes")
    require(sha(ROOT / "src/self_learning_ai/compiler.py") == COMPILER, "compiler.py hash changed")
    checks["code_hashes"] = code_checks
    checks["compiler_unchanged"] = {"passed": True, "sha256": COMPILER}
    authority_checks = {}
    for name, info in original["authority_hashes"].items():
        raw = (ROOT / name).read_bytes()
        require(digest(raw) == info["sha256"], "authority byte hash mismatch: " + name)
        if "verified_sha256" in info:
            policy = info.get("verification")
            require(policy in ("byte-exact", "LF-normalized"), "unknown authority policy: " + name)
            verified = digest(raw.replace(b"\r\n", b"\n") if policy == "LF-normalized" else raw)
            require(verified == info["verified_sha256"], "authority policy hash mismatch: " + name)
        authority_checks[name] = dict(info, passed=True)
    checks["existing_authority_hashes"] = authority_checks
    added_entries = {}
    for name in ADDED:
        require(name not in frozen["authority_hashes"], "authority already present: " + name)
        raw = (ROOT / name).read_bytes()
        require(b"\r\n" not in raw, "new authority must have LF endings: " + name)
        h = digest(raw)
        entry = {"sha256": h, "verification": "byte-exact", "verified_sha256": h}
        frozen["authority_hashes"][name] = entry
        added_entries[name] = entry
    require(execution.execution_bound_files() <=
            (frozen["code_hashes"].keys() | frozen["authority_hashes"].keys()), "missing execution bindings")
    checks["execution_bindings"] = {"passed": True, "paths": sorted(execution.execution_bound_files())}
    frozen["model_execution_authorized"] = False
    frozen["c15_refreeze"] = {
        "previous_manifest_sha256": PREVIOUS,
        "superseded_authorization_commit": "4c1d0b64a21d450f718a9334faefcd336e7ff1d0",
        "implementation_commit": COMMIT1,
        "incident_sha256": "8563276e0f24ad726f9508e15ca449d759a6718748cf6f6cc9e0d7a4fa4d0db9",
        "changed_code_hashes": changed,
        "added_authority": ADDED,
        "utc": datetime.now(timezone.utc).isoformat(),
    }
    comparison = copy.deepcopy(frozen)
    comparison.pop("c15_refreeze")
    comparison["model_execution_authorized"] = original["model_execution_authorized"]
    for name in CHANGED:
        comparison["code_hashes"][name] = original["code_hashes"][name]
    for name in ADDED:
        comparison["authority_hashes"].pop(name)
    require(canonical(comparison) == original_bytes, "other manifest fields changed")
    checks["other_manifest_fields_unchanged"] = {"passed": True, "canonical_bytes_equal": True}
    frozen_bytes = canonical(frozen)
    require(b"\r\n" not in frozen_bytes, "manifest must be LF-only")
    MANIFEST.write_bytes(frozen_bytes)
    require(MANIFEST.read_bytes() == frozen_bytes, "manifest write verification failed")
    validation = {}
    try:
        execution.require_execution_authorization(CANDIDATE)
    except execution.GateStop as exc:
        require(REFUSAL in str(exc), "unexpected V1 refusal: " + str(exc))
        validation["V1"] = {"passed": True, "refusal": str(exc)}
    else:
        raise execution.GateStop("V1 unexpectedly accepted authorization")
    with tempfile.TemporaryDirectory(prefix="conf1-c15-authorization-", dir=EXTERNAL) as temp:
        temp_root = Path(temp).resolve()
        require(not temp_root.is_relative_to(ROOT), "V2 copy must be outside repository")
        target = temp_root / "authorized_copy"
        shutil.copytree(CANDIDATE, target)
        authorized = copy.deepcopy(frozen)
        authorized["model_execution_authorized"] = True
        (target / "candidate_manifest.json").write_bytes(canonical(authorized))
        verified = execution.require_execution_authorization(target)
        require(verified == authorized, "V2 full verification returned different manifest")
    require(not temp_root.exists(), "V2 external copy not deleted")
    validation["V2"] = {"passed": True, "full_verification": "accepted",
                         "repo_files_verified_in_place": True, "external_copy_deleted": True}
    reread = json.loads(MANIFEST.read_bytes())
    require(reread["file_sha256"] == original["file_sha256"], "V3 payload hash values changed")
    validation["V3"] = {"passed": True, "unchanged_file_sha256": original["file_sha256"]}
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    junit = EXTERNAL / ("v4-" + run_id + ".xml")
    log = EXTERNAL / ("v4-" + run_id + ".log")
    basetemp = EXTERNAL / ("v4-" + run_id)
    require(not basetemp.exists() and not junit.exists() and not log.exists(), "V4 paths already exist")
    command = [sys.executable, "-B", "-m", "pytest", "tests/test_conf1_r1_execution.py",
               "-k", "t1 or h2", "-p", "no:cacheprovider", "--basetemp=" + str(basetemp),
               "--junitxml=" + str(junit), "-v"]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
               PYTHONPATH=str(ROOT / "src"), PYTEST_ADDOPTS="-o addopts=")
    with log.open("wb") as output:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=output, stderr=subprocess.STDOUT)
    require(result.returncode == 0, "V4 pytest failed; see " + str(log))
    cases = list(ET.parse(junit).iter("testcase"))
    require(bool(cases) and all(c.find("failure") is None and c.find("error") is None
                              and c.find("skipped") is None for c in cases), "V4 failures, errors or skips")
    validation["V4"] = {"passed": True, "exit_code": result.returncode, "command": command,
                         "environment": {k: env[k] for k in ("PYTHONDONTWRITEBYTECODE",
                             "PYTEST_DISABLE_PLUGIN_AUTOLOAD", "PYTHONPATH", "PYTEST_ADDOPTS")},
                         "tests": [{"id": c.attrib["classname"] + "::" + c.attrib["name"],
                                    "result": "PASS"} for c in cases],
                         "passed_count": len(cases), "failures": 0, "errors": 0, "skips": 0,
                         "junit": str(junit), "log": str(log)}
    checks["ignored_at_end"] = check_ignored()
    require(not (FORBIDDEN_IMPORTS & sys.modules.keys()), "forbidden model import")
    checks["no_model_imports"] = {"passed": True, "forbidden_modules_loaded": []}
    report = {"status": "C15_REFROZEN_MODEL_EXECUTION_NOT_AUTHORIZED", "implementation_commit": COMMIT1,
              "previous_manifest_sha256": PREVIOUS, "new_manifest_sha256": digest(frozen_bytes),
              "changed_code_hashes": changed, "added_authority_entries": added_entries,
              "checks": checks, "validation": validation, "wall_seconds": time.perf_counter() - started}
    REPORT.write_bytes(canonical(report))
    print(json.dumps({"status": report["status"], "new_manifest_sha256": report["new_manifest_sha256"],
                      "V1_V4": "PASS", "V4_passed": len(cases)}, indent=2))


if __name__ == "__main__":
    main()
