"""EXPLORATORY A1: port builder expressions, validate and seal once."""
from __future__ import annotations

import ast
import copy
import hashlib
import inspect
import json
import random
import sys
from collections import Counter
from pathlib import Path

import build_phase2b_data as b2
import build_phase3a_data as b3
from self_learning_ai.explore.pools import load_dev_pool, write_json
from self_learning_ai.explore.runlog import append_run
from self_learning_ai.explore.scoring import score_program

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/explore/a1"
SEED = 20291015
CHARS = "abcdefghijklmno"
STAGES = {
    1: dict(name="numeric loops", templates=["square_stride", "affine_recurrence", "odd_cube_sum", "descending_product",
                                           "linear_term_sum", "nonmultiple_count", "even_minus_odd", "cubic_offset_sum"],
            reserves=["shifted_product", "include_exclude_sum"]),
    2: dict(name="strings", templates=["upper_reverse", "replace_lower", "trim_lower_suffix", "reverse_replace",
                                      "replace_vowel", "count_letter", "char_at", "contains_label"], reserves=["string_length_class"]),
    3: dict(name="arrays", templates=["threshold_weighted", "indexed_difference", "negative_square", "pairwise_products",
                                     "weighted_four", "count_even_five", "absolute_sum_three", "range_three"],
            reserves=["dot_three", "array_positive_sum"]),
    4: dict(name="delimited fields", templates=["swap_tag", "count_fields", "case_join", "contains_branch",
                                               "tagged_pair", "two_labeled_lines", "case_pair", "length_product"], reserves=["reversed_fields"]),
}
LONG_TEXTS = ["abcdefghijklmnopq", "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "0123456789ABCDEFG",
              "seventeen letters here", "GOCO text sample 12345"]


def expression(node, environment):
    # Extract Python builder expressions only; no GOCO AST or coverage analysis.
    return eval(compile(ast.Expression(node), "<ported-builder-expression>", "eval"), environment)


def definitions():
    three = {}
    for node in ast.walk(ast.parse(inspect.getsource(b3.build))):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "emit":
            three[node.args[6].value] = node.args[8:11]
    two = {}
    for node in ast.walk(ast.parse(inspect.getsource(b2.build_training))):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.List):
            for value in node.value.elts:
                if isinstance(value, ast.Tuple) and isinstance(value.elts[0], ast.Constant):
                    two[value.elts[0].value] = value
    return three, two


THREE, TWO = definitions()


def port(template, k):
    """Use the source builder's unchanged prompt, source and expected formula."""
    if template in THREE:
        env = vars(b3) | dict(k=k, p=k + 2, ch=CHARS[k - 1])
        prompt, source, samples = [expression(node, env) for node in THREE[template]]
        return prompt, source.strip(), samples, "3A:build", []
    env = vars(b2) | dict(k=k, char=CHARS[k - 1])
    spec = expression(TWO[template], env)
    _, prompt, source, solver, *_ = spec
    additions = []
    if template in ("linear_term_sum", "nonmultiple_count", "even_minus_odd", "cubic_offset_sum", "shifted_product"):
        own, added = [0, 2, 5], [1, 3]
        samples = [(str(n), solver(n)) for n in own + added]
    elif template == "include_exclude_sum":
        own, added = [0, 3, 7], [1, 5]
        samples = [(str(n), solver(n)) for n in own + added]
    elif template in ("weighted_four", "count_even_five", "absolute_sum_three", "range_three", "dot_three"):
        width = spec[-1]
        own = {3: [[1, 2, 3], [-2, 0, 5], [4, -1, 2]],
               4: [[1, 2, 3, 4], [-2, 0, 5, 1], [4, -1, 2, -3]],
               5: [[1, 2, 3, 4, 5], [-2, 0, 5, 1, -4], [4, -1, 2, -3, 8]],
               6: [[1, 2, 3, 4, 5, 6], [-2, 0, 5, 1, -4, 2], [4, -1, 2, -3, 8, 1]]}[width]
        added = [[0] * width, [2] * width]
        samples = [("|".join(map(str, xs)), solver(xs)) for xs in own + added]
    elif template == "array_positive_sum":
        own, added = [[1, -2, 3, 0], [-1, -2, -3, -4], [2, 4, 6, 8]], [[0] * 4, [2] * 4]
        samples = [("|".join(map(str, xs)), solver(xs)) for xs in own + added]
    elif template in ("replace_vowel", "count_letter", "contains_label", "char_at", "string_length_class"):
        own = ["GoCo", "alpha beta", "XyZ"] if template == "string_length_class" else ["seaside", "bananas", "uvwxyzABC"]
        added = ["Mixed CASE", "abcdefghijklmno"]
        inputs = LONG_TEXTS if template == "char_at" else own + added
        samples = [(s, solver(s)) for s in inputs]
        if template == "char_at":
            additions.append(dict(kind="char_at_input_replacement", original=own, replacement=LONG_TEXTS))
    else:
        own, added = [("A", "B"), ("Red", "BLUE"), ("hello world", "ok")], [("x", "y"), ("Cat", "Dog")]
        source = b2.split_sentences(["first", "second"]) + source
        samples = [(a + "|" + b, solver(a, b)) for a, b in own + added]
    if template != "char_at":
        additions.append(dict(kind="case_extension", original=own, added=added))
    if template in ("replace_vowel", "count_letter", "contains_label"):
        additions.append(dict(kind="character_substitution", original='["a","e","i","o","u"][k-1]', replacement='"abcdefghijklmno"[k-1]'))
    return prompt, source.strip(), samples, "2B:build_training", additions


def template_rows(stage, template):
    rows, details = [], dict(source=None, adjustments=[], case_inputs={})
    ports = [port(template, k) for k in range(1, 16)]
    swaps = {}
    for index in range(5):
        if any(isinstance(p[2][index][1], (int, float)) and abs(p[2][index][1]) >= 10_000_000 for p in ports):
            original = [p[2][index][0] for p in ports]
            if not all(x.isdigit() for x in original):
                raise ValueError(f"STOP unsupported numeric size swap: {template}: {original}")
            for candidate in range(min(map(int, original))):
                text = str(candidate)
                if any(text in [x for j, (x, _) in enumerate(p[2]) if j != index] for p in ports):
                    continue
                values = []
                for k in range(1, 16):
                    env = vars(b3 if template in THREE else b2) | dict(k=k, p=k + 2, ch=CHARS[k - 1], char=CHARS[k - 1])
                    if template in THREE:
                        node = copy.deepcopy(THREE[template][2])
                        node.generators[0].iter = ast.List(elts=[ast.Constant(candidate)], ctx=ast.Load())
                        values.append(expression(ast.fix_missing_locations(node), env)[0][1])
                    else:
                        values.append(expression(TWO[template], env)[3](candidate))
                if all(abs(value) < 10_000_000 for value in values):
                    swaps[index] = dict(kind="number_size_swap", original=original, replacement=text)
                    for k, value in enumerate(values):
                        ports[k][2][index] = (text, value)
                    break
            else:
                raise ValueError(f"STOP cannot find smaller numeric input: {template}: {original}")
    for k in range(1, 16):
        prompt, source, samples, provenance, adjustments = ports[k - 1]
        details["source"] = provenance
        details["adjustments"] = adjustments + list(swaps.values())
        if len(samples) != 5:
            return None, dict(reason="cannot supply five cases", k=k)
        cases = [b2.case(j + 1, stdin, value) for j, (stdin, value) in enumerate(samples)]
        score = score_program(source, cases)
        if not score["all_pass"]:
            return None, dict(reason="reference failure", k=k, score=score)
        rows.append(dict(stage=stage, template=template, k=k, prompt=prompt, target=source, cases=cases))
        details["case_inputs"][str(k)] = [stdin for stdin, _ in samples]
        print(f"A1 reference PASS S{stage} {template} k={k}", flush=True)
    return rows, details


def json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def build():
    if OUT.exists():
        raise FileExistsError("A1 output directory already exists")
    splits = dict(train=[], dev=[], sealed=[])
    manifest = dict(label="EXPLORATORY", seed=SEED, stages={}, templates={}, replacements=[], k_splits={})
    for stage, specification in STAGES.items():
        reserves, selected = iter(specification["reserves"]), []
        for original in specification["templates"]:
            template = original
            while True:
                rows, details = template_rows(stage, template)
                if rows is not None:
                    break
                replacement = next(reserves, None)
                if replacement is None:
                    raise ValueError(f"STOP stage {stage} exhausted reserves: {template}: {details}")
                manifest["replacements"].append(dict(stage=stage, original=template, replacement=replacement, failure=details))
                print(f"A1 replacement S{stage}: {template} -> {replacement}: {details}", flush=True)
                template = replacement
            selected.append(template)
            manifest["templates"][template] = details
            ks = list(range(1, 16))
            random.Random(f"{SEED}-{template}").shuffle(ks)
            partition = dict(train=ks[:9], dev=ks[9:12], sealed=ks[12:])
            manifest["k_splits"][template] = partition
            by_k = {r["k"]: r for r in rows}
            for split, values in partition.items():
                splits[split].extend(dict(by_k[k]) for k in values)
        manifest["stages"][str(stage)] = dict(name=specification["name"], templates=selected)
    all_rows = [r for rows in splits.values() for r in rows]
    shuffled = list(all_rows)
    random.Random(SEED).shuffle(shuffled)
    for index, row in enumerate(shuffled):
        row["model_task_id"] = f"EXPL-A1-{index:04d}"
    for split, rows in splits.items():
        for row in rows:
            if split == "train":
                row["example_id"] = row.pop("model_task_id")
            else:
                row["task_id"] = f"EXPL-A1-S{row['stage']}-{row['template']}-{row['k']:02d}"
                del row["target"]
    for field in ("prompt", "template_k"):
        sets = [{r["prompt"] if field == "prompt" else (r["template"], r["k"]) for r in rows} for rows in splits.values()]
        if any(sets[i] & sets[j] for i in range(3) for j in range(i + 1, 3)):
            raise ValueError(f"STOP cross-split overlap: {field}")
    from transformers import AutoTokenizer
    from train_phase2a_qlora import TokenDataset
    tokenizer = AutoTokenizer.from_pretrained(ROOT / ".models/Qwen2.5-Coder-3B-Instruct-488639f", local_files_only=True)
    system = (ROOT / "prompts/phase1t_system.txt").read_text(encoding="utf-8").strip()
    dataset = TokenDataset(splits["train"], tokenizer, system, 320)
    manifest["max_training_tokens"] = max(len(r["input_ids"]) for r in dataset.items)
    manifest["counts"] = {split: dict(Counter(str(r["stage"]) for r in rows)) for split, rows in splits.items()}
    # Publish opaque IDs and prompt hashes as metadata so tests never open sealed data.
    manifest["split_metadata"] = {split: [dict(model_id=r.get("example_id", r.get("model_task_id")),
                                               prompt_sha256=hashlib.sha256(r["prompt"].encode()).hexdigest()) for r in rows]
                                  for split, rows in splits.items()}
    paths = dict(train="stream_train.json", dev="stream_dev.json", sealed="sealed/stream_sealed.json")
    payloads = {split: json_bytes(rows) for split, rows in splits.items()}
    manifest["sha256"] = {paths[split]: hashlib.sha256(raw).hexdigest() for split, raw in payloads.items()}
    for split, raw in payloads.items():
        path = OUT / paths[split]
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(raw)
    write_json(OUT / "manifest.json", manifest)
    append_run(dict(run="a1_build", status="PASS", manifest=manifest))
    print(f"A1 build PASS: train=288 dev=96 sealed=96 max_tokens={manifest['max_training_tokens']}", flush=True)


def main():
    sys.stdout.reconfigure(newline="\n")
    sys.stderr.reconfigure(newline="\n")
    try:
        build()
    except Exception as exc:
        append_run(dict(run="a1_build", status="FAIL", error=repr(exc)))
        raise


if __name__ == "__main__":
    main()
