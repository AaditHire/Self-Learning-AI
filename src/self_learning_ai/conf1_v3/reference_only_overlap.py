"""DEVELOPMENT_ONLY RO overlap preflight; not a scientific overlap permission.

Witness generation has no corpus argument. The only boundary permission is the
three-entry prospective adjudication. VALUE/OUTPUT's zero policy is not imported.
This module does not implement RO semantic admission or certify a candidate.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import time


SEED = "RO_REFERENCE_ONLY_DEV_CONSTANTS_V1|7df2a31df6c995d0105e5547aa1d235c6046e9cf141f92321faf92cce3bac682"
SCHEDULE_NAME = "predetermined_witness_schedule.json"
SCOPE = "DEVELOPMENT_ONLY"
FIELD = "isolated_constant_expression"
BOUNDARIES = (
    ("ZERO", "0", "5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9", "FROZEN_RO_INTEGER_ZERO_BOUNDARY"),
    ("MAX", "2147483647", "972dcafa6fb4c2c88bce752fca4ab18c6bd88599330a4ad9813915b05bfbe76d", "FROZEN_RO_INTEGER_MAX_BOUNDARY"),
    ("OVERFLOW", "2147483648", "39f8d58187887b481fe709f7b323f2b876d9f522e9f7afef815c2089084a36d7", "FROZEN_RO_INTEGER_OVERFLOW_BOUNDARY"),
)
# Ordered labels/ranges are fixed before the first corpus consultation. Never
# change this list/ranges in response to an observed collision.
ATOM_LABELS = (
    "ATOM_A", "ATOM_B", "ATOM_C", "ATOM_D", "PU_CONSTANT", "BODY_CONSTANT",
    "INITIAL_OFFSET", "LOOP_CONTRIBUTION", "NESTED_BODY", "EXTRA_WRITE",
    "LIVE_UNMATCHED", "COMPARISON_OTHER", "FALSE_GUARD_LEFT", "FALSE_GUARD_RIGHT",
    "ARRAY_OFFSET", "NEGATIVE_ATOM", "UNSUPPORTED_MODULUS", "ALPHA_CONSTANT",
)
LABELS = (*ATOM_LABELS, *(f"CASE_{i}_NUMERIC" for i in range(5)),
          *(f"CASE_{i}_ARRAY_{j}" for i in range(5) for j in range(4)))
MEDIUM_LABELS = frozenset(("PU_CONSTANT", "INITIAL_OFFSET", "ARRAY_OFFSET"))
PURPOSES = {
    "ATOM_A": "ordered nested constant-tree arithmetic first operand",
    "ATOM_B": "ordered nested constant-tree arithmetic second operand",
    "ATOM_C": "ordered nested constant-tree arithmetic third operand",
    "ATOM_D": "ordered nested constant-tree arithmetic fourth operand",
    "PU_CONSTANT": "fresh unused top-level scalar initializer",
    "BODY_CONSTANT": "restricted constant-false body scalar initializer",
    "INITIAL_OFFSET": "prospectively required development accumulator initializer",
    "LOOP_CONTRIBUTION": "prospectively required development loop contribution",
    "NESTED_BODY": "nested independently false body initializer",
    "EXTRA_WRITE": "extra-write rejection and false-owner boundary event",
    "LIVE_UNMATCHED": "unmatched live-source rejection witness",
    "COMPARISON_OTHER": "comparison operand and false-only-on-samples adversary",
    "FALSE_GUARD_LEFT": "static comparison first constant operand",
    "FALSE_GUARD_RIGHT": "static comparison second constant operand",
    "ARRAY_OFFSET": "array-development required accumulator initializer",
    "NEGATIVE_ATOM": "unary-negation constant-tree operand",
    "UNSUPPORTED_MODULUS": "unsupported nonzero modulo rejection operand",
    "ALPHA_CONSTANT": "alpha-renaming development constant initializer",
}


class OverlapIssue(ValueError):
    pass


def digest(value):
    return sha256(value.encode("utf-8")).hexdigest()


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def witness_schedule():
    """Pure, closed generation: no metadata/corpus, retries, or alternative seed."""
    boundaries = [dict(label=name, literal=literal, sha256_utf8=h,
                       boundary_rule=rule, field=FIELD,
                       development_case_id=f"DEVELOPMENT_ONLY_RO_BOUNDARY_{name}",
                       intended_semantic_purpose={
                           "ZERO": "zero token satisfies frozen N grammar and inclusive lower bound",
                           "MAX": "maximum token satisfies frozen N grammar and inclusive upper bound",
                           "OVERFLOW": "first above-bound token fails frozen N safety bound",
                       }[name]) for name, literal, h, rule in BOUNDARIES]
    constants = []
    for label in LABELS:
        low, high = (100003, 999983) if label in MEDIUM_LABELS or "_ARRAY_" in label else (101, 997)
        h = digest(SEED + "|" + label)
        literal = str(low + int(h, 16) % (high - low + 1))
        purpose = PURPOSES.get(label)
        if purpose is None:
            purpose = ("disposable numeric domain input" if label.endswith("_NUMERIC")
                       else "disposable four-field array input component")
        constants.append(dict(label=label, digest=h, derivation_rule="low + uint256(digest) modulo (high - low + 1)",
                              low=low, high=high, literal=literal, sha256_utf8=digest(literal),
                              intended_semantic_purpose=purpose))
    return dict(schema_version=1, scope=SCOPE,
                artifact_kind="DEVELOPMENT_ONLY_RO_PREDETERMINED_WITNESS_SCHEDULE",
                seed=SEED, boundaries=boundaries, non_boundary=constants,
                resampling_allowed=False, selected_before_overlap_consultation=True)


@dataclass(frozen=True)
class SavedSchedule:
    path: Path
    payload: bytes
    sha256_utf8: str

    def value(self):
        # Return a new object; mutation cannot change the sealed bytes.
        if self.payload != canonical(witness_schedule()) or self.sha256_utf8 != sha256(self.payload).hexdigest():
            raise OverlapIssue("RO_FORGED_SCHEDULE_SNAPSHOT")
        return json.loads(self.payload)


def load_schedule(path):
    """Require a previously serialized exact schedule, not a caller's flags."""
    path = Path(path).resolve(strict=True)
    payload = path.read_bytes()
    if path.name != SCHEDULE_NAME or payload != canonical(witness_schedule()):
        raise OverlapIssue("RO_PREDETERMINED_SCHEDULE_CHANGED")
    return SavedSchedule(path, payload, sha256(payload).hexdigest())


@dataclass(frozen=True)
class CorpusString:
    artifact_path: str
    json_pointer: str
    kind: str
    value: str


def _pointer(value):
    return str(value).replace("~", "~0").replace("/", "~1")


def _raw_strings(value, path, pointer=""):
    if isinstance(value, str):
        yield CorpusString(path, pointer, "VALUE", value)
    elif isinstance(value, list):
        for i, item in enumerate(value):
            yield from _raw_strings(item, path, pointer + "/" + str(i))
    elif isinstance(value, dict):
        for key, item in value.items():
            child = pointer + "/" + _pointer(key)
            yield CorpusString(path, child, "KEY", key)
            yield from _raw_strings(item, path, child)


def load_raw_corpus(root):
    """Only 13 historical synthetic fixtures and manifest; NEVER label files."""
    root = Path(root)
    folder = root / "research/protocols/phase3c_conf1_v3_synthetic_fixtures"
    paths = sorted(folder.glob("*.json"))
    if len(paths) != 13:
        raise OverlapIssue("RO_COMPARISON_CORPUS_CHANGED")
    paths.append(root / "research/protocols/phase3c_conf1_v3_synthetic_fixture_manifest.json")
    rows, identities = [], []
    for path in paths:
        raw = path.read_bytes()
        relative = path.relative_to(root).as_posix()
        identities.append(dict(path=relative, sha256_utf8=sha256(raw).hexdigest(), size_bytes_utf8=len(raw)))
        rows.extend(_raw_strings(json.loads(raw), relative))
    return tuple(rows), identities


def scheduled_inventory(saved):
    """All selected atomic witnesses, not a claim of complete executable fixtures."""
    schedule = saved.value()
    rows = [dict(scope=SCOPE, implementation_test="REFERENCE_ONLY", field=FIELD,
                 path=f"boundaries/{i}/literal", value=r["literal"],
                 sha256_utf8=r["sha256_utf8"], boundary_rule=r["boundary_rule"],
                 development_case_id=r["development_case_id"])
            for i, r in enumerate(schedule["boundaries"])]
    rows.extend(dict(scope=SCOPE, implementation_test="REFERENCE_ONLY", field=FIELD,
                     path=f"non_boundary/{i}/literal", value=r["literal"],
                     sha256_utf8=r["sha256_utf8"], boundary_rule=None,
                     development_case_id=f"DEVELOPMENT_ONLY_RO_{r['label']}")
                for i, r in enumerate(schedule["non_boundary"]))
    return rows


def boundary_permitted(row, saved):
    # Exact scheduled field/path/case binding, not 'normative=true' or any other
    # caller claim. No expected-output, source, raw-input or metadata exception.
    return any(row.get("scope") == SCOPE
               and row.get("implementation_test") == "REFERENCE_ONLY"
               and row.get("field") == FIELD
               and row.get("path") == f"boundaries/{i}/literal"
               and row.get("development_case_id") == b["development_case_id"]
               and row.get("value") == b["literal"]
               and row.get("sha256_utf8") == b["sha256_utf8"]
               and row.get("boundary_rule") == b["boundary_rule"]
               and digest(row["value"]) == row["sha256_utf8"]
               for i, b in enumerate(saved.value()["boundaries"]))


def compare(rows, saved, corpus):
    """Record every location of exact/recorded/recomputed hash hits, fail closed.

    Injection of synthetic corpus strings here supports adversarial unit tests;
    the real preflight calls load_schedule BEFORE its one raw-corpus read.
    This function cannot change/resample the schedule on any result.
    """
    exact, hashes = {}, {}
    for c in corpus:
        exact.setdefault(c.value, []).append(c)
        hashes.setdefault(digest(c.value), []).append(c)
    permitted, prohibited = [], []
    malformed = []
    for row in rows:
        value, h = row.get("value"), row.get("sha256_utf8")
        if not isinstance(value, str) or not isinstance(h, str) or digest(value) != h:
            malformed.append(dict(row=row, reason="RO_OVERLAP_LITERAL_HASH_MISMATCH"))
        # A forged recorded hash is itself checked, not replaced by the real hash.
        locations = {}
        for mode, matches in (("EXACT_STRING", exact.get(value, [])),
                              ("RECORDED_HASH", exact.get(h, [])),
                              ("RECOMPUTED_STRING_HASH", hashes.get(digest(value), []) if isinstance(value, str) else [])):
            for c in matches:
                key = (c.artifact_path, c.json_pointer, c.kind)
                hit = locations.setdefault(key, dict(artifact_path=c.artifact_path, json_pointer=c.json_pointer,
                                                     string_kind=c.kind, match_modes=[]))
                hit["match_modes"].append(mode)
        if not locations:
            continue
        collision = dict(literal=value, sha256_utf8=h, boundary_rule=row.get("boundary_rule"),
                         field=row.get("field"), path=row.get("path"),
                         development_case_id=row.get("development_case_id"),
                         match_locations=list(locations.values()), match_location_count=len(locations),
                         witness_schedule_sha256_utf8=saved.sha256_utf8,
                         selection_basis="exact serialized predetermined schedule, verified before corpus read")
        (permitted if boundary_permitted(row, saved) else prohibited).append(collision)
    return dict(schema_version=1, scope=SCOPE,
                artifact_kind="DEVELOPMENT_ONLY_RO_OVERLAP_ADJUDICATION",
                witness_schedule_sha256_utf8=saved.sha256_utf8,
                permitted_normative_collisions=permitted, prohibited_collisions=prohibited,
                malformed_inventory=malformed,
                permitted_collision_count=len(permitted), prohibited_collision_count=len(prohibited),
                status="PASS" if not prohibited and not malformed else "STOP",
                expected_labels_parsed=False, scientific_overlap_permissions_changed=False,
                value_output_exception_imported=False, resampling_occurred=False)


def require_clear(result):
    if result["status"] != "PASS" or result["prohibited_collisions"] or result["malformed_inventory"]:
        raise OverlapIssue("STOPPED_COVERAGE_V3_REFERENCE_ONLY_IMPLEMENTATION_ISSUE: PROHIBITED_RO_OVERLAP")


def preflight(root, schedule_path):
    """Actual causal ordering: verify saved bytes, then (and only then) read corpus."""
    saved = load_schedule(schedule_path)
    loaded_at = time.time_ns()
    rows = scheduled_inventory(saved)
    corpus_started_at = time.time_ns()
    corpus, identities = load_raw_corpus(root)
    result = compare(rows, saved, corpus)
    if saved.path.read_bytes() != saved.payload:
        raise OverlapIssue("RO_SCHEDULE_MUTATED_DURING_SCAN")
    result.update(inventory=rows, comparison_inputs=identities,
                  comparison_scope="all recursive raw keys/values and recorded/recomputed hashes in 13 fixtures plus manifest; labels excluded",
                  causal_sequence=[dict(event="SERIALIZED_SCHEDULE_VERIFIED", time_unix_ns=loaded_at,
                                       sha256_utf8=saved.sha256_utf8),
                                   dict(event="PROTECTED_RAW_CORPUS_READ_STARTED", time_unix_ns=corpus_started_at)],
                  schedule_existed_before_scan=True, inventory_scope="selected atomic witnesses only; no executable fixture has run")
    return result
