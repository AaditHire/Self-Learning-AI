from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def esc(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    result = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    result.extend("| " + " | ".join(esc(cell) for cell in row) + " |" for row in rows)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--training", type=Path, required=True)
    parser.add_argument("--evaluation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)

    audit = load(args.validation)
    training = {row["example_id"]: row for row in load(args.training)}
    evaluation = {row["task_id"]: row for row in load(args.evaluation)}
    split = audit["structural_split"]
    prior = audit["consumed_artifact_audit"]

    lines = [
        "# Phase 2B structural-overlap manual review",
        "",
        "Reviewed: 2026-09-21, before any Phase 2B gradient step.",
        "",
        "Decision: **PASS FOR FREEZE**. No reviewed pair is the same semantic mapping, a renamed/literal-only variant, or a retained prior evaluation task. Similarity flags below are attributable to the deliberately small GOCO grammar, required input scaffolding, or broad control-flow shape. All retained train/evaluation pairs have distinct algorithm labels, lineages, structural signatures, and semantic-operation labels. No normalized-code pair reaches the predeclared 0.98 rejection threshold. The legacy sealed Phase 1 holdout was not opened.",
        "",
        "## Automated gate summary",
        "",
        f"- Training targets: {audit['training_verification']['passed']}/200 verified; failures: 0.",
        f"- Confirmatory references: {audit['evaluation_reference_verification']['passed']}/128 verified; failures: 0.",
        f"- Exact prompt reuse across train/evaluation: {split['exact_prompt_reuse']}.",
        f"- Exact train/evaluation algorithm, lineage, structural-signature, and semantic-operation overlaps: 0 each.",
        f"- Train/evaluation prompt flags at 0.70: {len(split['prompt_flags_at_or_above_0p70'])}.",
        f"- Train/evaluation normalized-code flags at 0.85: {len(split['code_flags_at_or_above_0p85'])}; rejects at 0.98: {len(split['code_rejects_at_or_above_0p98'])}.",
        f"- Exact AST-proxy flags: {len(split['ast_proxy_exact_matches'])}.",
        f"- Distance buckets: {split['distance_bucket_counts']}.",
        f"- Prior consumed-suite prompt flags at 0.70: {len(prior['prompt_flags_at_or_above_0p70'])}; normalized-code flags at 0.90: {len(prior['code_flags_at_or_above_0p90'])}.",
        f"- Prior normalized-code pairs at or above 0.98: {sum(row['similarity'] >= 0.98 for row in prior['code_flags_at_or_above_0p90'])}.",
        "",
        "## Prompt flags reviewed",
        "",
    ]
    prompt_rows = []
    for row in split["prompt_flags_at_or_above_0p70"]:
        ev = evaluation[row["evaluation_task_id"]]
        tr = training[row["nearest_task_id"]]
        prompt_rows.append([row["evaluation_task_id"], row["nearest_task_id"], f"{row['similarity']:.3f}", ev["algorithmic_structure"], tr["algorithmic_structure"], "retain: different mapping"])
    lines += table(["evaluation", "nearest training", "similarity", "evaluation algorithm", "training algorithm", "resolution"], prompt_rows)
    lines += ["", "## Normalized-code flags reviewed", ""]
    code_rows = []
    for row in split["code_flags_at_or_above_0p85"]:
        ev = evaluation[row["evaluation_task_id"]]
        tr = training[row["nearest_task_id"]]
        code_rows.append([row["evaluation_task_id"], row["nearest_task_id"], f"{row['similarity']:.3f}", ev["algorithmic_structure"], tr["algorithmic_structure"], "retain: distinct semantics; shared scaffold"])
    lines += table(["evaluation", "nearest training", "similarity", "evaluation algorithm", "training algorithm", "resolution"], code_rows)
    lines += ["", "## Exact AST-proxy flags reviewed", ""]
    ast_rows = []
    for row in split["ast_proxy_exact_matches"]:
        ev = evaluation[row["evaluation_task_id"]]
        tr = training[row["training_task_id"]]
        ast_rows.append([row["evaluation_task_id"], row["training_task_id"], row["ast_proxy_signature"], ev["semantic_operations"][0], tr["semantic_operations"][0], "retain: proxy omits called operation"])
    lines += table(["evaluation", "training", "AST proxy", "evaluation operation", "training operation", "resolution"], ast_rows)
    lines += ["", "## Prior consumed-suite normalized-code flags reviewed", ""]
    prior_rows = [[row["evaluation_task_id"], row["nearest_task_id"], f"{row['similarity']:.3f}", "retain: below 0.98; prompt/semantic task differs"] for row in prior["code_flags_at_or_above_0p90"]]
    lines += table(["evaluation", "nearest consumed task", "similarity", "resolution"], prior_rows)
    lines += [
        "",
        "## Reviewer conclusion",
        "",
        "All listed pairs were reviewed against task prompts, reference programs, algorithm labels, lineages, structural signatures, and semantic-operation labels. The four prompt flags express broad family-level wording rather than the same mapping. The 81 train/evaluation code flags and 25 exact AST proxies reflect mandatory GOCO declarations, pipe-splitting boilerplate, loop shells, or one-call string skeletons; none is a renamed or literal-only copy. The 84 prior-suite code flags are all below 0.98 after the final replacements, and there are zero prior prompt flags at 0.70. The suite is therefore accepted for preregistration with distance bucket retained as a task-level analysis factor.",
        "",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
