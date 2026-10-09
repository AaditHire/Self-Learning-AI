"""CONF1 one-pass execution. Model access is exclusively through callables.

Candidate arguments are directories; runtime_root is explicit in fixtures.
generate(seed, condition, task, messages) returns raw text. reset(rng_seed)
is mandatory. score(raw, task, cases, target, checkpoint_dir) returns analyzer
flags. train_cell(seed, condition, schedule, examples) returns exposures,
optimizer_steps and a nonempty losses list, plus optional lineage diagnostics.
"""
from __future__ import annotations

import errno
import hashlib
import json
import math
import os
import time
import uuid
from pathlib import Path
from types import FunctionType

from self_learning_ai.conf1_r1.gates_primary import GateStop
from self_learning_ai.conf1_r1 import analysis, schedule

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RUNTIME = ROOT / ".runtime/phase3c_conf1"
C15_REVIEWED_INCIDENT = "research/protocols/phase3c_conf1_c15_reviewed_incident.json"
AUTHORIZED_STATUSES = frozenset({"CANDIDATE_FROZEN"})
AUTHORIZED_CONSTRUCTION_SEEDS = frozenset({20290123})
EXECUTION_BOUND_FILES = frozenset({
    "scripts/train_phase3c_conf1.py", "scripts/evaluate_phase3c_conf1.py",
    "scripts/analyze_phase3c_conf1.py", "scripts/train_phase2a_qlora.py",
    "scripts/validate_phase2b_data.py", "src/self_learning_ai/dev2r_evaluation.py",
    "src/self_learning_ai/benchmark.py", "src/self_learning_ai/compiler.py",
    "research/protocols/phase3c_conf1_config_proposed.json",
    "prompts/phase1t_system.txt", "prompts/phase1t_user_template.txt",
} | {p.relative_to(ROOT).as_posix() for p in (ROOT / "src/self_learning_ai/conf1_r1").glob("*.py")})


def execution_bound_files():
    """Resolve the full binding set at each call, including newly added modules."""
    return EXECUTION_BOUND_FILES | frozenset(
        p.relative_to(ROOT).as_posix() for p in (ROOT / "src/self_learning_ai/conf1_r1").glob("*.py"))


class AcquisitionFailed(GateStop):
    """Terminal insufficient-acquisition outcome; not an infrastructure incident."""


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def _contained(root, name):
    path = (root / name).resolve()
    if Path(name).is_absolute() or not path.is_relative_to(root) or path == root:
        raise GateStop("manifest path escapes its root", {"path": name})
    return path


def require_execution_authorization(candidate_dir):
    """Strict JSON boolean, explicit statuses, byte hashes before heavy import."""
    candidate = Path(candidate_dir).resolve()
    try:
        manifest = read(candidate / "candidate_manifest.json")
        if (not isinstance(manifest, dict) or manifest.get("model_execution_authorized") is not True
                or manifest.get("status") not in AUTHORIZED_STATUSES
                or manifest.get("phase") != "PHASE_3C_CONF1"
                or type(manifest.get("construction_seed")) is not int
                or manifest["construction_seed"] not in AUTHORIZED_CONSTRUCTION_SEEDS):
            raise GateStop("CONF1 model execution is not explicitly authorized")
        for field in ("code_hashes", "authority_hashes", "tokenizer_hashes", "file_sha256"):
            if not isinstance(manifest.get(field), dict) or not manifest[field]:
                raise GateStop("missing mandatory manifest hashes", {"field": field})
        if not isinstance(manifest.get("compiler_sha256"), str) or not manifest["compiler_sha256"]:
            raise GateStop("missing mandatory manifest hashes", {"field": "compiler_sha256"})
        missing = execution_bound_files() - (manifest["code_hashes"].keys() | manifest["authority_hashes"].keys())
        if missing:
            raise GateStop("missing execution bindings", {"paths": sorted(missing)})
        files = manifest.get("file_sha256")
        if not isinstance(files, dict) or not files:
            raise GateStop("candidate manifest has no payload hashes")
        groups = [(candidate, files)]
        actual_hashes = {}

        def verify(root, name, expected, lf=False):
            if not isinstance(name, str) or not isinstance(expected, str):
                raise GateStop("malformed manifest hash")
            path = _contained(root, name)
            key = (path, lf)
            if key not in actual_hashes:
                actual_hashes[key] = (hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
                                      if lf else sha256(path))
            actual = actual_hashes[key]
            if actual != expected:
                raise GateStop("manifest file hash mismatch", {"path": name, "expected": expected, "actual": actual})

        if "code_hashes" in manifest:
            groups.append((ROOT, manifest["code_hashes"]))
        if "authority_hashes" in manifest:
            groups.append((ROOT, {p: v["sha256"] for p, v in manifest["authority_hashes"].items()}))
        for root, hashes in groups:
            for name, expected in hashes.items():
                verify(root, name, expected)
        for name, info in manifest.get("authority_hashes", {}).items():
            if "verified_sha256" in info:
                if info.get("verification") not in ("byte-exact", "LF-normalized"):
                    raise GateStop("unknown authority hash policy", {"path": name})
                verify(ROOT, name, info["verified_sha256"], info["verification"] == "LF-normalized")
        if "compiler_sha256" in manifest:
            verify(ROOT, ".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar", manifest["compiler_sha256"])
        for name, expected in manifest.get("tokenizer_hashes", {}).items():
            verify(ROOT / ".models/Qwen2.5-Coder-3B-Instruct-488639f", name, expected)
        return manifest
    except GateStop:
        raise
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        raise GateStop("invalid or missing candidate manifest", {"fault": str(exc)}) from exc


class CheckpointStore:
    """Atomic, durable create-only JSON, with exclusive per-target reservation."""
    def __init__(self, root):
        self.root = Path(root).resolve()

    def path(self, name):
        return _contained(self.root, name)

    def write(self, name, value):
        target = self.path(name)
        target.parent.mkdir(parents=True, exist_ok=True)
        lock = target.with_name(target.name + ".lock")
        temp = target.with_name(target.name + ".tmp-" + uuid.uuid4().hex)
        locked = False
        try:
            if target.exists():
                raise GateStop("existing checkpoint; retry forbidden", {"path": str(target)})
            with lock.open("xb"):
                locked = True
            raw = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
            with temp.open("xb") as handle:
                handle.write(raw)
                handle.flush()
                os.fsync(handle.fileno())
            if target.exists():
                raise GateStop("existing checkpoint; retry forbidden", {"path": str(target)})
            os.replace(temp, target)
            if os.name != "nt":
                fd = os.open(target.parent, os.O_RDONLY)
                try:
                    os.fsync(fd)
                finally:
                    os.close(fd)
            return sha256(target)
        except FileExistsError as exc:
            fault = GateStop("existing checkpoint reservation; retry forbidden", {"path": str(target)})
            if not name.startswith("incidents/"):
                self.incident("checkpoint_write", fault)
            raise fault from exc
        except Exception as exc:
            if not name.startswith("incidents/"):
                self.incident("checkpoint_write", exc)
            raise
        finally:
            temp.unlink(missing_ok=True)
            if locked:
                lock.unlink(missing_ok=True)

    def incident(self, stage, exc):
        def safe(value):
            if isinstance(value, float) and not math.isfinite(value):
                return repr(value)
            if isinstance(value, dict):
                return {str(k): safe(v) for k, v in value.items()}
            if isinstance(value, (list, tuple)):
                return [safe(v) for v in value]
            return value
        return self.write("incidents/" + uuid.uuid4().hex + ".json",
                          {"status": "STOP", "stage": stage, "error_type": type(exc).__name__,
                           "reason": str(exc), "evidence": safe(getattr(exc, "report", {}))})

    def fresh(self, prefix):
        if self.path(prefix).exists() or self.path("incidents").exists():
            raise GateStop("existing checkpoint or incident; retry forbidden", {"prefix": prefix})


def _candidate(candidate):
    candidate = Path(candidate).resolve()
    manifest = require_execution_authorization(candidate)
    tasks = read(candidate / "evaluation/tasks.json")
    # Secondary payloads omit structure; identity metadata supplies it.
    catalog = {t["task_id"]: t for t in schedule.EVALUATION_TASKS}
    tasks = [dict(t, **{k: v for k, v in catalog[t["task_id"]].items() if k not in t}) for t in tasks]
    analysis._catalog(tasks)
    examples, cases = {}, {}
    for condition in schedule.CONDITIONS:
        rows = read(candidate / f"training/{condition}_examples.json")
        if len(rows) != 60 or {r["model_task_id"] for r in rows} != set(schedule.SLOT_IDS):
            raise GateStop("training slot population mismatch")
        examples[condition] = {r["model_task_id"]: dict(r, messages=messages(r["model_task_id"], r["prompt"])) for r in rows}
        cases[condition] = read(candidate / f"training/{condition}_cases.json")
    return candidate, manifest, tasks, examples, cases


def messages(task_id, prompt):
    system = (ROOT / "prompts/phase1t_system.txt").read_text(encoding="utf-8").strip()
    template = (ROOT / "prompts/phase1t_user_template.txt").read_text(encoding="utf-8").strip()
    return [{"role": "system", "content": system},
            {"role": "user", "content": template.format(task_id=task_id, task_prompt=prompt)}]


def training_rows(examples, slot_ids):
    """C9 rows for the unchanged TokenDataset prompt construction."""
    by_slot = {row["model_task_id"]: row for row in examples}
    system = (ROOT / "prompts/phase1t_system.txt").read_text(encoding="utf-8").strip()
    return system, [dict(by_slot[tid], example_id=tid) for tid in slot_ids]


def encode_prompt(tokenizer, messages):
    """C13/DEV2R generation prefix with default special-token handling."""
    rendered = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    return tokenizer(rendered, truncation=False)["input_ids"]


def _fault(store, stage, exc):
    store.incident(stage, exc)
    if isinstance(exc, GateStop):
        raise exc
    raise GateStop("execution fault", {"stage": stage, "fault": str(exc)}) from exc


def run_training_cells(candidate, train_cell, *, runtime_root=DEFAULT_RUNTIME):
    store = CheckpointStore(runtime_root)
    try:
        _, _, _, examples, _ = _candidate(candidate)
        store.fresh("training")
        results = []
        for cell in schedule.cell_order():
            seed, condition = cell["seed"], cell["condition"]
            stem = f"training/{seed}/{condition}"
            store.write(stem + ".started.json", cell)
            result = train_cell(seed, condition, schedule.training_schedule(seed), list(examples[condition].values()))
            if (type(result.get("exposures")) is not int or result["exposures"] != 180
                    or type(result.get("optimizer_steps")) is not int or result["optimizer_steps"] != 24
                    or not isinstance(result.get("losses"), list) or not result["losses"]
                    or any(type(v) not in (int, float) or not math.isfinite(v) for v in result["losses"])):
                raise GateStop("training exposure, optimizer-step or finite-loss contract failed", result)
            result = dict(result, **cell)
            digest = store.write(stem + ".json", result)
            store.write(stem + ".sha256.json", {"sha256": digest})
            results.append(result)
        return results
    except Exception as exc:
        _fault(store, "training", exc)


def _score_row(seed, condition, suite, tid, flags, raw_hash, rng_seed):
    metadata = analysis.TRAINING[tid] if suite == "training" else analysis.CANONICAL[tid]
    row = {k: metadata[k] for k in ("task_id", "family", "group", "graph", "block_id") if k in metadata}
    row.update(flags)
    row.update(seed=seed, condition=condition, suite=suite, task_id=tid, raw_sha256=raw_hash, rng_seed=rng_seed)
    analysis._row(row, analysis.TRAINING | analysis.CANONICAL)
    return row


def _task(store, seed, condition, suite, task, cases, target, generate, score, reset):
    tid = task["task_id"]
    stem = f"evaluations/{seed}/{condition}/{suite}/{tid}"
    if any(store.path(stem + suffix).exists() for suffix in (".raw.json", ".score.json", ".started.json")):
        raise GateStop("existing task checkpoint; retry forbidden", {"task_id": tid})
    store.write(stem + ".started.json", {"seed": seed, "condition": condition, "task_id": tid})
    rng_seed = schedule.task_rng_seed(seed, tid)
    chat = messages(tid, task["prompt"])
    reset(rng_seed)
    raw = generate(seed, condition, task, chat)
    if not isinstance(raw, str):
        raise GateStop("generation must be raw text")
    raw_hash = store.write(stem + ".raw.json", {"raw_generation": raw, "rng_seed": rng_seed,
                                                "seed": seed, "condition": condition, "task_id": tid})
    flags = score(raw, task, cases, target, store.path(stem + ".compiler"))
    row = _score_row(seed, condition, suite, tid, flags, raw_hash, rng_seed)
    digest = store.write(stem + ".score.json", row)
    store.write(stem + ".score.sha256.json", {"sha256": digest})
    return row


def _score_records(store, suite):
    records = []
    for path in sorted(store.root.glob(f"evaluations/*/*/{suite}/*.score.json")):
        stem = str(path).removesuffix(".score.json")
        if sha256(path) != read(stem + ".score.sha256.json")["sha256"]:
            raise GateStop("score checkpoint hash mismatch", {"path": str(path)})
        row = read(path)
        if sha256(stem + ".raw.json") != row["raw_sha256"]:
            raise GateStop("raw checkpoint hash mismatch", {"path": stem})
        records.append(row)
    return records


def run_own_training(candidate, generate, score, *, reset, runtime_root=DEFAULT_RUNTIME):
    store = CheckpointStore(runtime_root)
    try:
        _, _, _, examples, cases = _candidate(candidate)
        store.fresh("evaluations")
        records = []
        for cell in schedule.cell_order():
            seed, condition = cell["seed"], cell["condition"]
            for tid in schedule.own_training_order(examples[condition]):
                row = examples[condition][tid]
                task = dict(analysis.TRAINING[tid], prompt=row["prompt"])
                records.append(_task(store, seed, condition, "training", task, cases[condition][row["example_id"]],
                                     row["target"], generate, score, reset))
        gate = analysis.acquisition_gate(records)
        if not gate["passed"]:
            gate = dict(gate, outcome=analysis.INDETERMINATE)
        store.write("acquisition_gate.json", gate)
        if not gate["passed"]:
            raise AcquisitionFailed(analysis.INDETERMINATE, gate)
        return gate
    except AcquisitionFailed:
        raise
    except Exception as exc:
        _fault(store, "own_training", exc)


def run_confirmatory(candidate, generate, score, *, reset, runtime_root=DEFAULT_RUNTIME):
    store = CheckpointStore(runtime_root)
    try:
        path, _, tasks, _, _ = _candidate(candidate)
        store.fresh("confirmatory.started.json")
        gate = read(store.path("acquisition_gate.json"))
        verified_gate = analysis.acquisition_gate(_score_records(store, "training"))
        if not gate["passed"] or gate != verified_gate:
            raise GateStop("confirmatory execution requires a verified acquisition PASS")
        if any(store.root.glob("evaluations/*/*/confirmatory/*")):
            raise GateStop("existing confirmatory checkpoint; retry forbidden")
        store.write("confirmatory.started.json", {"status": "STARTED"})
        cases = read(path / "evaluation/hidden_cases.json")
        catalog = {t["task_id"]: t for t in tasks}
        order = schedule.confirmatory_order({g: [t["task_id"] for t in tasks if t["group"] == g] for g in schedule.GROUPS})
        records = []
        for cell in schedule.cell_order():
            for tid in order:
                records.append(_task(store, cell["seed"], cell["condition"], "confirmatory", catalog[tid],
                                     cases[tid], None, generate, score, reset))
        analysis.validate_records(_score_records(store, "training") + records, tasks)
        store.write("confirmatory_complete.json", {"records": len(records), "tasks_per_cell": len(tasks)})
        return records
    except Exception as exc:
        _fault(store, "confirmatory", exc)


def c15_reviewed_incident(manifest):
    """Read only the fixed, byte-exact manifest-bound C15 decision."""
    try:
        info = manifest["authority_hashes"].get(C15_REVIEWED_INCIDENT)
        path = ROOT / C15_REVIEWED_INCIDENT
        if (not isinstance(info, dict) or info.get("verification") != "byte-exact"
                or info.get("sha256") != sha256(path)
                or info.get("verified_sha256") != sha256(path)):
            raise GateStop("C15 reviewed incident is missing or not hash-bound")
        return read(path)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise GateStop("C15 reviewed incident is missing or not hash-bound") from exc


def _c15_incident(store, reviewed):
    files = list(store.path("incidents").iterdir())
    incident = store.path(reviewed["incident"])
    if (reviewed.get("amendment") != "C15" or files != [incident]
            or not incident.is_file() or sha256(incident) != reviewed["incident_sha256"]):
        raise GateStop("C15 reviewed incident mismatch")


def _c15_marker(reviewed, raw_hash):
    return {"amendment": "C15", "incident": reviewed["incident"],
            "incident_sha256": reviewed["incident_sha256"], "resume_index": reviewed["resume_index"],
            "resume_task": reviewed["resume_task"], "raw_sha256": raw_hash}


def run_confirmatory_c15_continuation(candidate, generate, score, *, reset, reviewed_incident,
                                     runtime_root=DEFAULT_RUNTIME):
    """One reviewed continuation; reuse the persisted generation at index 128."""
    store = CheckpointStore(runtime_root)
    try:
        path, _, tasks, _, _ = _candidate(candidate)
        reviewed = reviewed_incident
        _c15_incident(store, reviewed)
        if any(p.name.endswith(".lock") or ".tmp-" in p.name for p in store.root.rglob("*")):
            raise GateStop("C15 runtime has a lock or temporary file")
        if read(store.path("confirmatory.started.json")) != {"status": "STARTED"}:
            raise GateStop("C15 confirmatory start marker mismatch")
        gate = read(store.path("acquisition_gate.json"))
        verified_gate = analysis.acquisition_gate(_score_records(store, "training"))
        if not gate["passed"] or gate != verified_gate:
            raise GateStop("confirmatory execution requires a verified acquisition PASS")
        marker = "confirmatory_c15_continuation.started.json"
        if store.path("confirmatory_complete.json").exists() or store.path(marker).exists():
            raise GateStop("C15 continuation already started or complete")
        catalog = {t["task_id"]: t for t in tasks}
        order = schedule.confirmatory_order({g: [t["task_id"] for t in tasks if t["group"] == g]
                                             for g in schedule.GROUPS})
        entries = [(c["seed"], c["condition"], tid) for c in schedule.cell_order() for tid in order]
        resume = reviewed["resume_index"]
        selected = reviewed["resume_task"]
        if (len(entries) != 640 or type(resume) is not int or resume != 128
                or entries[resume] != (selected["seed"], selected["condition"], selected["task_id"])):
            raise GateStop("C15 resume index or frozen task mismatch")
        allowed = set()
        for index, (seed, condition, tid) in enumerate(entries):
            stem = f"evaluations/{seed}/{condition}/confirmatory/{tid}"
            if index > resume:
                continue
            names = [stem + ".started.json", stem + ".raw.json"]
            compiler_dir = stem + ".compiler"
            compiler_names = [compiler_dir + "/" + tid + ".generation.json"]
            if index < resume:
                names += [stem + ".score.json", stem + ".score.sha256.json"]
                compiler_names += [compiler_dir + "/" + tid + ".primary.json"]
            for name in names + compiler_names:
                if not store.path(name).is_file():
                    raise GateStop("C15 missing pre-existing artifact", {"path": name})
                allowed.add(store.path(name))
            if not store.path(compiler_dir).is_dir():
                raise GateStop("C15 missing compiler checkpoint")
            allowed.add(store.path(compiler_dir))
            raw = read(store.path(stem + ".raw.json"))
            if any(raw.get(k) != v for k, v in {"seed": seed, "condition": condition,
                    "task_id": tid, "rng_seed": schedule.task_rng_seed(seed, tid)}.items()):
                raise GateStop("C15 raw metadata mismatch")
            if index < resume:
                scored = store.path(stem + ".score.json")
                if (sha256(scored) != read(store.path(stem + ".score.sha256.json"))["sha256"]
                        or sha256(store.path(stem + ".raw.json")) != read(scored)["raw_sha256"]):
                    raise GateStop("C15 pre-existing score or raw hash mismatch")
        directories = set(store.root.glob("evaluations/*/*/confirmatory"))
        expected_directories = {store.path(f"evaluations/{seed}/{condition}/confirmatory")
                                for seed, condition, _ in entries[:resume + 1]}
        actual = {p for d in directories for p in d.rglob("*")}
        if directories != expected_directories or actual != allowed:
            raise GateStop("C15 unexpected confirmatory artifact")
        seed, condition, tid = entries[resume]
        stem = f"evaluations/{seed}/{condition}/confirmatory/{tid}"
        raw_path = store.path(stem + ".raw.json")
        raw = read(raw_path)
        raw_hash = sha256(raw_path)
        cases = read(path / "evaluation/hidden_cases.json")
        store.write(marker, _c15_marker(reviewed, raw_hash))
        flags = score(raw["raw_generation"], catalog[tid], cases[tid], None,
                      store.path(stem + ".compiler-c15"))
        row = _score_row(seed, condition, "confirmatory", tid, flags, raw_hash, raw["rng_seed"])
        digest = store.write(stem + ".score.json", row)
        store.write(stem + ".score.sha256.json", {"sha256": digest})
        for seed, condition, tid in entries[resume + 1:]:
            _task(store, seed, condition, "confirmatory", catalog[tid], cases[tid], None,
                  generate, score, reset)
        records = _score_records(store, "confirmatory")
        if len(records) != 640:
            raise GateStop("C15 incomplete confirmatory population")
        analysis.validate_records(_score_records(store, "training") + records, tasks)
        store.write("confirmatory_complete.json", {"records": 640, "tasks_per_cell": 64})
        return records
    except Exception as exc:
        _fault(store, "confirmatory_c15", exc)


def run_analysis(candidate, runtime_root=DEFAULT_RUNTIME):
    store = CheckpointStore(runtime_root)
    try:
        if store.path("analysis.json").exists():
            raise GateStop("existing analysis checkpoint; retry forbidden")
        if store.path("incidents").exists():
            try:
                manifest = require_execution_authorization(candidate)
                reviewed = c15_reviewed_incident(manifest)
                _c15_incident(store, reviewed)
                task = reviewed["resume_task"]
                raw_path = store.path(f"evaluations/{task['seed']}/{task['condition']}/confirmatory/"
                                      f"{task['task_id']}.raw.json")
                if read(store.path("confirmatory_c15_continuation.started.json")) != _c15_marker(reviewed, sha256(raw_path)):
                    raise GateStop("C15 continuation marker mismatch")
            except Exception as exc:
                raise GateStop("analysis requires an incident-free, complete runtime or reviewed C15 continuation") from exc
        if any(p.name.endswith(".lock") or ".tmp-" in p.name for p in store.root.rglob("*")):
            raise GateStop("analysis requires an incident-free, complete runtime")
        _, _, tasks, _, _ = _candidate(candidate)
        for cell in schedule.cell_order():
            stem = f"training/{cell['seed']}/{cell['condition']}"
            record = store.path(stem + ".json")
            if sha256(record) != read(store.path(stem + ".sha256.json"))["sha256"]:
                raise GateStop("training cell record hash mismatch", {"path": str(record)})
        training = _score_records(store, "training")
        gate = analysis.acquisition_gate(training)
        if not gate["passed"]:
            gate = dict(gate, outcome=analysis.INDETERMINATE)
        if read(store.path("acquisition_gate.json")) != gate:
            raise GateStop("acquisition gate checkpoint mismatch")
        confirmatory = []
        if not gate["passed"]:
            if store.path("confirmatory.started.json").exists() or any(
                    store.root.glob("evaluations/*/*/confirmatory/*")) or store.path("confirmatory_complete.json").exists():
                raise GateStop("confirmatory checkpoints forbidden after failed acquisition")
        else:
            complete = read(store.path("confirmatory_complete.json"))
            confirmatory = _score_records(store, "confirmatory")
            expected = 10 * len(tasks)
            if len(confirmatory) != expected or complete != {"records": expected, "tasks_per_cell": len(tasks)}:
                raise GateStop("incomplete confirmatory checkpoint population")
        report = analysis.analyze(training + confirmatory, tasks)
        store.write("analysis.json", report)
        inventory = {p.relative_to(store.root).as_posix(): sha256(p) for p in sorted(store.root.rglob("*.json"))}
        store.write("output_inventory.json", inventory)
        return report
    except Exception as exc:
        _fault(store, "analysis", exc)


def compiler_score(compiler):
    """Adapt the existing DEV2R durable evaluator to C13 extraction and C14 flags."""
    from self_learning_ai.benchmark import extract_source
    from self_learning_ai.dev2r_evaluation import evaluate_task
    from self_learning_ai.conf1_r1.overlap import _normalizer
    normalized_code = _normalizer().normalized_code
    # Reuse the historical durable evaluator unchanged, but bind its extractor
    # to C13 in a private namespace. Historical DEV2R keeps its own rule; no
    # module globals are patched, and raw generations remain byte-for-byte raw.
    evaluate = FunctionType(evaluate_task.__code__,
                            dict(evaluate_task.__globals__, extract_source_phase1r=extract_source),
                            evaluate_task.__name__, evaluate_task.__defaults__, evaluate_task.__closure__)
    evaluate.__kwdefaults__ = dict(evaluate_task.__kwdefaults__ or {})

    def score(raw, task, cases, target, checkpoint_dir):
        source = extract_source(raw)
        adapted = dict(task, development_group=task["group"], archetype=task.get("graph", task["group"]),
                       semantic_primitives=["CONF1"], composition_signature=task["group"], required_regex=[])
        from self_learning_ai.dev2r_evaluation import atomic_new_json
        attempts = []
        retried = False

        class SystemRetries:
            case_index = 0

            def run(self, source, stdin):
                nonlocal retried
                index = self.case_index
                self.case_index += 1
                for number in range(1, 4):
                    if number > 1:
                        retried = True
                        time.sleep(2 if number == 2 else 10)
                    try:
                        result = compiler.run(source, stdin)
                    except OSError as exc:
                        if exc.errno != errno.EINVAL:
                            raise
                        attempts.append({"case_index": index, "attempt_number": number, "einval": True})
                        if number == 3:
                            raise
                        continue
                    attempt = {"case_index": index, "attempt_number": number, "einval": False,
                               "is_system": result.phase == "system", "exit_code": result.exit_code,
                               "timed_out": result.timed_out, "elapsed_ms": result.elapsed_ms}
                    if attempt["is_system"]:
                        attempt["stderr"] = result.stderr[:200]
                    attempts.append(attempt)
                    if result.phase != "system":
                        return result
                return result

        try:
            result = evaluate(compiler=SystemRetries(), task=adapted, cases=cases,
                              raw_generation=raw, generation_metadata={},
                              adapter_identity={"condition": "CONF1"}, checkpoint_dir=checkpoint_dir)
        finally:
            if retried:
                atomic_new_json(Path(checkpoint_dir) / "c15_system_retries.json", {"attempts": attempts})
        flags = result["score"]
        if any(c["phase"] == "system" for c in flags["case_results"]):
            raise GateStop("compiler infrastructure fault", flags)
        row = {"passed": flags["hidden_pass"], "compile_ok": flags["compile_success"],
               "case_outcomes": [{"passed": c["passed"], "execution_ok": c["phase"] == "success",
                                   "expected_stdout": c["expected_stdout"]} for c in flags["case_results"]]}
        if target is not None:
            row["exact_target"] = normalized_code(source) == normalized_code(target)
        return row
    return score
