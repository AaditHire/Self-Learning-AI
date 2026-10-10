import random
import re

import pytest
from self_learning_ai.explore.pools import (
    CATEGORIES, ROOT, assign_model_ids, enumerate_candidates, expected, load_dev_pool, probes, signature, split_candidates,
)
from self_learning_ai.explore.scoring import score_program


def test_sealed_path_guard():
    for path in (ROOT / "research/explore/b0/sealed/sealed_pool.json",
                 ROOT / "research/explore/other/sealed/never_exists.json"):
        with pytest.raises(ValueError, match="sealed"):
            load_dev_pool(path)


def test_disjoint_and_primary_exclusions():
    survivors, _, primary = enumerate_candidates()
    dev, sealed_candidates, _ = split_candidates(survivors)
    # Regenerate candidate metadata in memory; never read the sealed file.
    for category in CATEGORIES:
        a = {tuple(r["signature"]) for r in dev if r["category"] == category}
        b = {tuple(r["signature"]) for r in sealed_candidates if r["category"] == category}
        assert not a & b
        assert len(a) == sum(r["category"] == category for r in dev)
    for row in survivors["graph"]:
        assert tuple(row["signature"]) not in primary[row["slot"]["family"]]
    pool = load_dev_pool()
    inputs = probes()
    assert {r["task_id"] for r in pool} == {f"EXPL-B0-{r['category'].upper()}-{r['slot']['family'].upper()}-{i:03d}" for i, r in enumerate(dev)}
    for row in pool:
        assert tuple(row["signature"]) == signature(row["category"], row["slot"], inputs)


def independent_expected(row, stdin):
    slot, category = row["slot"], row["category"]
    if row["family"] == "numeric_iteration":
        n = int(stdin)
        items = [(i, {"odd_index": i % 2 == 1, "residue_two": i % 3 == 2,
                      "divisor_index": n % i == 0, "first_half": 2 * i <= n}) for i in range(1, n + 1)]
    else:
        items = [(i, {"negative_value": x < 0, "even_value": x % 2 == 0,
                      "large_magnitude": x * x > 4, "value_exceeds_index": x > i})
                 for i, x in enumerate(map(int, stdin.split("|")))]
    total = slot.get("offset", 0)
    for _, truth in items:
        if category == "atom_single":
            total += truth[slot["primitive"]]
        elif category == "atom_isolated":
            total += int(truth[slot["P"]]) + int(truth[slot["Q"]])
        elif category == "pair_and":
            total += truth[slot["P"]] and truth[slot["Q"]]
        else:
            p, q, r, s = (truth[slot["role_predicates"][role]] if role in slot["role_predicates"] else False for role in "PQRS")
            graph = slot["graph"]
            if graph == "G1":
                total += p and (q or r)
            elif graph == "G2":
                total += int(p and q) + int(q and r) + int(r and s)
            elif graph == "G3P":
                total += int(p and q) + int(p and r)
            else:
                total += int((p or q) and r) + int(q and s)
    return total


@pytest.mark.parametrize("category", CATEGORIES)
def test_three_independent_rechecks(category):
    rows = [r for r in load_dev_pool() if r["category"] == category]
    for row in random.Random(20291012).sample(rows, 3):
        for case in row["cases"]:
            assert independent_expected(row, case["stdin"]) == int(float(case["expected_stdout"]))
    print(f"independent re-check {category}: 3 tasks / 15 cases PASS")


def test_dev_references_real_compiler():
    for row in load_dev_pool():
        assert score_program(row["reference_source"], row["cases"])["all_pass"], row["task_id"]


def test_case_format():
    for row in load_dev_pool():
        for j, case in enumerate(row["cases"]):
            value = expected(row["category"], row["slot"], case["stdin"])
            assert case["expected_stdout"] == f"{value}.0"
            assert case["stdin"].endswith("\n")
            assert case["case_id"] == f"case-{j + 1}"


def test_neutral_ids_across_both_pools():
    survivors, _, _ = enumerate_candidates()
    dev, sealed_candidates, _ = split_candidates(survivors)
    assign_model_ids(dev + sealed_candidates)
    ids = [r["model_task_id"] for r in dev + sealed_candidates]
    assert len(set(ids)) == len(ids)
    assert all(re.fullmatch(r"EXPL-B0-\d{4}", ident) for ident in ids)
    assert [r["model_task_id"] for r in load_dev_pool()] == [r["model_task_id"] for r in dev]
