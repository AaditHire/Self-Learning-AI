"""Fail-closed DEV2 pre-gradient preflight, including composition novelty."""

import hashlib
import importlib.metadata
import json
import platform
import re
import subprocess
from collections import Counter
from pathlib import Path

from transformers import AutoTokenizer

from build_phase3c_dev2_data import PREDICATES

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/protocols/phase3c_dev2_manifest.json"
OUTPUT = ROOT / ".runtime/phase3c_dev2/preflight.json"
FROZEN_HEAD = "886cf3c69c2babb3f735776ab7b28ce36b2de62d"
NOVEL_SIGNATURE = re.compile(r"^count\((\w+) AND (\w+)\)\+count\((\w+) AND (\w+)\)$")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalized_sha256(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def novelty_check(tasks, refs, training):
    vocabulary = {family: {name: entry[0] for name, entry in predicates.items()}
                  for family, predicates in PREDICATES.items()}
    evidence = []
    for task in tasks:
        if task["development_group"] != "novel_composition":
            continue
        tid = task["task_id"]
        match = NOVEL_SIGNATURE.fullmatch(task["composition_signature"])
        if not match:
            raise ValueError(f"Ambiguous composition signature: {tid}")
        p, q, r, s = match.groups()
        if len({p, q, r, s}) != 4 or set((p, q, r, s)) != set(vocabulary[task["family"]]):
            raise ValueError(f"Novel task does not use four distinct covered primitives: {tid}")
        P, Q, R, S = (vocabulary[task["family"]][key] for key in (p, q, r, s))
        body = f"IF ({P}) {{ IF ({Q}) {{ count+=1. }} }} IF ({R}) {{ IF ({S}) {{ count+=1. }} }}"
        if body not in refs[tid] or refs[tid].count("IF (") != 4 or task["semantic_primitives"] != [p, q, r, s]:
            raise ValueError(f"Signature/reference mismatch: {tid}")
        row = {"task_id": tid, "signature": task["composition_signature"],
               "ordered_intersections": [[p, q], [r, s]], "reference_body_verified": True, "conditions": {}}
        for condition, (train_rows, train_refs) in training.items():
            coverage = {op for item in train_rows for op in item["semantic_primitives"]}
            matching = [item["example_id"] for item in train_rows
                        if item["composition_signature"] == task["composition_signature"]]
            # Training references have one nested pair plus one simple guard;
            # the development reference requires two ordered intersections.
            if not {p, q, r, s} <= coverage or matching or any(code.count("IF (") != 3 for code in train_refs.values()):
                raise ValueError(f"Composition novelty/coverage failure: {tid}, {condition}")
            row["conditions"][condition] = {"all_primitives_present": True,
                                             "same_composition_training_ids": matching,
                                             "same_two_intersection_structure_present": False}
        evidence.append(row)
    if len(evidence) != 16:
        raise ValueError(f"Expected 16 novel tasks; got {len(evidence)}")
    return evidence


def main():
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if subprocess.run(["git", "merge-base", "--is-ancestor", FROZEN_HEAD, head], cwd=ROOT).returncode:
        raise ValueError("Frozen design commit is not an ancestor of HEAD")
    status = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True)
    if status:
        raise ValueError(f"Working tree not clean before gradients: {status}")
    manifest = read("research/protocols/phase3c_dev2_manifest.json")
    cfg = read("research/protocols/phase3c_dev2_config.json")
    if manifest["status"] != "FROZEN_DESIGN_PROPOSAL_NO_MODEL_EXECUTION" or cfg["phase"] != "3C-DEV2":
        raise ValueError("Frozen design identity")
    for relative, expected in manifest["file_normalized_sha256"].items():
        path = ROOT / relative
        if not path.is_file() or normalized_sha256(path) != expected:
            raise ValueError(f"Frozen design hash mismatch: {relative}")
    audit = read("research/results/PHASE_3C_DEV2/pre_gradient_audit.json")
    tokens = read("research/results/PHASE_3C_DEV2/token_budget_audit.json")
    pairs = read("research/results/PHASE_3C_DEV2/structural_pairs.json")
    if len(pairs) != 5760 or audit["structural_pair_count"] != 5760 or len(audit["central_coverage_proof"]) != 32:
        raise ValueError("Frozen structural audit incomplete")
    if any(x["passed"] != x["references"] for x in audit["reference_validation"].values()) or sum(x["cases"] for x in audit["reference_validation"].values()) != 840:
        raise ValueError("Frozen reference validation failure")
    if any(audit["historical_exact_reuse"].values()) or any(x["missing_in_isolated"] or x["missing_in_composition"] for x in audit["central_coverage_proof"]):
        raise ValueError("Reuse or missing central primitive")
    if len(audit["primitive_frequency"]) != 8 or len(audit["api_syntax_frequency"]) != 8:
        raise ValueError("Primitive/API audit count")
    for row in audit["primitive_frequency"]:
        a, b = (row["conditions"][c] for c in ("isolated", "composition"))
        if a["examples_containing"] != 15 or b["examples_containing"] != 15 or a["reference_occurrences"] != b["reference_occurrences"]:
            raise ValueError("Primitive frequency mismatch")
    for row in audit["api_syntax_frequency"]:
        counts = row["reference_occurrences"]
        if counts["isolated"] != counts["composition"]:
            raise ValueError("GOCO syntax/API mismatch")
    jar = ROOT / cfg["compiler"]["path"]
    if sha256(jar) != cfg["compiler"]["sha256"] or sha256(jar) != audit["compiler_sha256"]:
        raise ValueError("Compiler hash mismatch")
    model = ROOT / cfg["base_weights"]["local_path"]
    base_hashes = {name: sha256(model / name) for name in cfg["base_weights"]["weight_file_sha256"]}
    if base_hashes != cfg["base_weights"]["weight_file_sha256"]:
        raise ValueError("Immutable base weights changed")
    support = read("research/protocols/phase3c_execution_manifest.json")["model_support_file_sha256"]
    for relative, expected in support.items():
        if sha256(ROOT / relative) != expected:
            raise ValueError(f"Model support file changed: {relative}")
    for name, expected in cfg["tokenizer_file_sha256"].items():
        if sha256(model / name) != expected:
            raise ValueError(f"Tokenizer changed: {name}")
    prior_cfg = read("research/protocols/phase3c_config.json")
    for relative in ("prompts/phase1t_system.txt", "prompts/phase1t_user_template.txt"):
        current = sha256(ROOT / relative)
        if current != prior_cfg["file_sha256"][relative] and normalized_sha256(ROOT / relative) != prior_cfg["git_text_content_sha256"][relative]:
            raise ValueError(f"Frozen prompt changed: {relative}")
    if sha256(ROOT / cfg["prompt_system_template"]) != tokens["prompt_template_sha256"]:
        raise ValueError("DEV2 token-audit prompt hash changed")
    expected_packages = manifest["environment_at_design_freeze"]["packages"]
    packages = {name: platform.python_version() if name == "python" else importlib.metadata.version(name) for name in expected_packages}
    if packages != expected_packages:
        raise ValueError(f"Package/Python contract changed: {packages}")
    rows = {c: read(f"data/phase3c_dev2/a_{c}_training_examples.json") for c in ("isolated", "composition")}
    train_refs = {c: read(f"data/phase3c_dev2/a_{c}_training_references.json") for c in rows}
    eval_rows = read("benchmark/phase3c_dev2/a_development_eval_tasks.json")
    eval_refs = read("benchmark/phase3c_dev2/a_development_eval_references.json")
    if len(eval_rows) != 48 or len(eval_refs) != 48:
        raise ValueError("Development task count")
    novelty = novelty_check(eval_rows, eval_refs, {c: (rows[c], train_refs[c]) for c in rows})
    frozen_novel = {x["task_id"]: x for x in audit["central_coverage_proof"] if x["group"] == "novel_composition"}
    if set(frozen_novel) != {x["task_id"] for x in novelty} or any(x["exact_composition_in_isolated"] or x["exact_composition_in_composition"] for x in frozen_novel.values()):
        raise ValueError("Frozen novelty audit disagrees")
    schedule = read("research/protocols/phase3c_dev2_schedule.json")
    if schedule["seeds"] != cfg["seeds"] or cfg["seeds"] != [20270925, 20271013, 20271119] or schedule["epochs"] != 3 or schedule["slots_per_epoch"] != 60 or schedule["optimizer_steps_per_epoch"] != 8:
        raise ValueError("Seeds/schedule/step contract")
    by_id = {c: {x["example_id"]: x for x in rows[c]} for c in rows}
    eval_ids = {x["task_id"] for x in eval_rows}
    if len(eval_ids) != 48 or any(len(rows[c]) != 60 or len(by_id[c]) != 60 or Counter(x["family"] for x in rows[c]) != {"numeric_iteration": 30, "array_reduction": 30} for c in rows):
        raise ValueError("Dataset count/ID contract")
    for seed in cfg["seeds"]:
        epochs = schedule["by_seed"][str(seed)]
        if len(epochs) != 3:
            raise ValueError("Epoch count")
        for epoch in epochs:
            if len(epoch["slot_families"]) != 60 or Counter(epoch["slot_families"]) != {"numeric_iteration": 30, "array_reduction": 30}:
                raise ValueError("Slot subskill balance")
            for c in rows:
                ids = epoch[f"{c}_example_ids"]
                if len(ids) != 60 or set(ids) != set(by_id[c]) or set(ids) & eval_ids or [by_id[c][x]["family"] for x in ids] != epoch["slot_families"]:
                    raise ValueError("Scheduled IDs/families")
            if any(by_id["isolated"][a]["archetype"] != by_id["composition"][b]["archetype"] for a, b in zip(epoch["isolated_example_ids"], epoch["composition_example_ids"])):
                raise ValueError("Paired archetype schedule mismatch")
    tokenizer = AutoTokenizer.from_pretrained(model, local_files_only=True)
    system = (ROOT / cfg["prompt_system_template"]).read_text(encoding="utf-8").strip()
    exposure = {}
    for c, group in rows.items():
        full_total = target_total = maximum = 0
        for item in group:
            messages = [{"role": "system", "content": system},
                        {"role": "user", "content": f"Task {item['example_id']}\n\n{item['prompt']}"}]
            p = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            f = tokenizer.apply_chat_template(messages + [{"role": "assistant", "content": item["target"]}], tokenize=False, add_generation_prompt=False)
            p_ids = tokenizer(p, add_special_tokens=False)["input_ids"]
            f_ids = tokenizer(f, add_special_tokens=False)["input_ids"]
            if f_ids[:len(p_ids)] != p_ids:
                raise ValueError("Chat prefix mismatch")
            full_total += len(f_ids)
            target_total += len(f_ids) - len(p_ids)
            maximum = max(maximum, len(f_ids))
        exposure[c] = {"one_epoch_full_tokens": full_total, "one_epoch_supervised_tokens": target_total,
                       "three_epoch_full_tokens": 3 * full_total, "three_epoch_supervised_tokens": 3 * target_total,
                       "max_sequence_tokens": maximum}
        frozen = tokens["conditions"][c]
        if (full_total, target_total, maximum) != (frozen["one_epoch_full_tokens"], frozen["one_epoch_supervised_tokens"], frozen["max_full_tokens"]):
            raise ValueError("Token audit mismatch")
    a, b = exposure["isolated"], exposure["composition"]
    full_diff = (b["one_epoch_full_tokens"] - a["one_epoch_full_tokens"]) / a["one_epoch_full_tokens"]
    target_diff = (b["one_epoch_supervised_tokens"] - a["one_epoch_supervised_tokens"]) / a["one_epoch_supervised_tokens"]
    if max(abs(full_diff), abs(target_diff)) > .10 or max(x["max_sequence_tokens"] for x in exposure.values()) > 320 or tokens["compute_gate"] != "PASS":
        raise ValueError("Prospective token STOP rule")
    redundant = {c: [x["example_id"] for x in rows[c] if re.search(r"IF \(([^)]*)\) \{ IF \(\1\)", train_refs[c][x["example_id"]])] for c in rows}
    if len(redundant["isolated"]) != 60 or redundant["composition"]:
        raise ValueError("Unexpected redundant-guard exposure")
    hardware = subprocess.run(["nvidia-smi", "--query-gpu=name,driver_version,memory.total,memory.free", "--format=csv,noheader"], capture_output=True, text=True, check=True).stdout.strip()
    java = subprocess.run([str(ROOT / cfg["compiler"]["java"]), "-version"], capture_output=True, text=True, check=True).stderr.strip()
    payload = {"phase": "3C-DEV2", "status": "PASS_PREGRADIENT_CONTRACT", "frozen_design_commit": FROZEN_HEAD,
               "current_head": head, "git_status_at_preflight": status, "manifest_sha256": sha256(MANIFEST),
               "execution_code_sha256": {name: sha256(ROOT / f"scripts/{name}_phase3c_dev2.py")
                                         for name in ("preflight", "train", "evaluate", "analyze")},
               "compiler_sha256": sha256(jar), "base_weight_sha256": base_hashes, "packages": packages,
               "platform": platform.platform(), "gpu": hardware, "java": java, "seeds": cfg["seeds"],
               "reference_validation": {"references": 168, "cases": 840, "all_pass": True},
               "composition_novelty": {"status": "PASS_ALL_16", "task_records": novelty},
               "primitive_frequency_match": "PASS_EXACT_EIGHT_PRIMITIVES",
               "api_syntax_frequency_match": "PASS_EXACT_EIGHT_CONSTRUCTS",
               "central_primitive_coverage": "PASS_ALL_32_BOTH_CONDITIONS",
               "residual_confound": {"one_epoch_full_tokens": {c: exposure[c]["one_epoch_full_tokens"] for c in exposure},
                                    "composition_minus_isolated_full_tokens": b["one_epoch_full_tokens"] - a["one_epoch_full_tokens"],
                                    "composition_minus_isolated_full_fraction": full_diff,
                                    "one_epoch_supervised_tokens": {c: exposure[c]["one_epoch_supervised_tokens"] for c in exposure},
                                    "supervised_fraction_difference": target_diff,
                                    "redundant_nested_guard_example_ids": redundant,
                                    "other": "Matched audited API counts; different prompt semantics and conditional relation. COMPOSITION has 2.70% more full tokens."},
               "exposure": exposure, "token_gate": "PASS", "no_model_inference_or_gradients": True}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "novel_tasks": len(novelty), "full_tokens": payload["residual_confound"]["one_epoch_full_tokens"], "gpu": hardware}), flush=True)


if __name__ == "__main__":
    main()
