"""New classifier-free canonical-transport disposable inputs and overlap guard."""
from pathlib import Path
import hashlib
import json
ROOT = Path(__file__).resolve().parents[1]
START = "97c7a1679004a4682beebea8bccf58781d147a84"
RAW = ("000000000", "0000000007", "00000000015", "00000000021", "00000000033")
P, Q = "ct903Item%2==1", "ct903Item%3==2"
HEADER = "NUMBER ct903Limit. INPUT(ct903Limit). NUMBER ct903Total=211. NUMBER ct903P=0. NUMBER ct903Q=0. "
PRELUDE = f"ct903P=0. ct903Q=0. IF ({P}) {{ ct903P=1. }} IF ({Q}) {{ ct903Q=1. }} "
AND = f"IF (({P})&&({Q})) {{ ct903Total+=1. }}"
OR = f"IF (({P})||({Q})) {{ ct903Total+=1. }}"
PRODUCT = "ct903Total+=(ct903P*ct903Q)."
SUM = "IF (ct903P+ct903Q>0) { ct903Total+=1. }"
def source(body):
    return HEADER + "LOOP (NUMBER ct903Item=1 TILL ct903Item<=ct903Limit, ct903Item++) { " + body + " } DISPLAYNL(ct903Total)."
SOURCES = {
    "AND": source(PRELUDE + AND), "PRODUCT": source(PRELUDE + PRODUCT),
    "OR": source(PRELUDE + OR), "SUM": source(PRELUDE + SUM),
    "REPEATED_AND": source(PRELUDE + AND + AND),
    "REPEATED_PRODUCT": source(PRELUDE + PRODUCT + " " + PRODUCT),
    "NON_BOOLEAN_MUL": source(PRELUDE.replace("ct903P=0.", "ct903P=2.") + PRODUCT).replace("NUMBER ct903P=0.", "NUMBER ct903P=2."),
    "EXTRA_SUM": source(PRELUDE + "IF (ct903P+ct903Q+ct903P>0) { ct903Total+=1. }"),
    "ARITY": source(PRELUDE + "ct903Total+=(ct903P*ct903Q*ct903P)."),
    "WRONG_PREDICATE": source(PRELUDE.replace(Q, "ct903Item%3==1") + PRODUCT),
    "STALE": source(PRODUCT + " " + PRELUDE),
    "TARGET": source(PRELUDE + "ct903Q+=(ct903P*ct903Q)."),
    "INCREMENT": source(PRELUDE + SUM.replace("+=1", "+=2")),
    "DOWNSTREAM": source(PRELUDE + PRODUCT).replace("DISPLAYNL(ct903Total)", "DISPLAYNL(ct903P)"),
    "MATCHING_OUTPUT_INVALID": source(PRELUDE + PRODUCT + " IF (ct903Item>223) { ct903Total+=1. }"),
    "WRONG_LOOP": HEADER + "LOOP (NUMBER ct903Item=1 TILL ct903Item<=ct903Limit, ct903Item++) { " + PRELUDE + AND + " } LOOP (NUMBER ct903Later=1 TILL ct903Later<=ct903Limit, ct903Later++) { " + PRODUCT + " } DISPLAYNL(ct903Total).",
}
for name in ("PRODUCT", "SUM", "REPEATED_PRODUCT", "AND", "OR"):
    SOURCES["ALPHA_" + name] = SOURCES[name].replace("ct903", "carrier913")
PAIRS = (("AND", "PRODUCT", "LOCAL_PAIR_JOINT"), ("OR", "SUM", "BOOLEAN_OR"), ("AND", "ALPHA_PRODUCT", "LOCAL_PAIR_JOINT"), ("OR", "ALPHA_SUM", "BOOLEAN_OR"), ("REPEATED_AND", "REPEATED_PRODUCT", "LOCAL_PAIR_JOINT"), ("REPEATED_AND", "ALPHA_REPEATED_PRODUCT", "LOCAL_PAIR_JOINT"))
def expected(name, raw):
    is_or = "OR" in name or "SUM" in name
    count = sum(int((i % 2 == 1 or i % 3 == 2) if is_or else (i % 2 == 1 and i % 3 == 2)) for i in range(1, int(raw) + 1))
    return str(211 + count * (2 if "REPEATED" in name else 1))
def inventory():
    expressions = (P, Q, f"({P})&&({Q})", f"({P})||({Q})", "ct903P*ct903Q", "ct903P+ct903Q>0", "ct903P+ct903Q+ct903P>0", "ct903P*ct903Q*ct903P", "ct903Item%3==1", "ct903Item>223")
    expressions += tuple(x.replace("ct903", "carrier913") for x in expressions)
    values = {"ids": tuple("CTRANSPORT903-" + n for n in SOURCES) + tuple("CTRANSPORT903-CASE-" + str(i) for i in range(5)) + ("CTRANSPORT903-SOURCE-ARTIFACT", "CTRANSPORT903-CASE-ARTIFACT"), "sources": tuple(SOURCES.values()), "expressions": expressions, "raw_inputs": RAW}
    return {k: [{"value": v, "sha256_utf8": hashlib.sha256(v.encode()).hexdigest()} for v in rows] for k, rows in values.items()}
def overlap():
    def strings(v):
        if isinstance(v, str): yield v
        elif isinstance(v, list):
            for x in v: yield from strings(x)
        elif isinstance(v, dict):
            for k, x in v.items(): yield k; yield from strings(x)
    paths = sorted((ROOT / "research/protocols/phase3c_conf1_v3_synthetic_fixtures").glob("*.json"))
    if len(paths) != 13: raise RuntimeError("historical corpus changed")
    historical = set()
    for path in (*paths, ROOT / "research/protocols/phase3c_conf1_v3_synthetic_fixture_manifest.json"):
        historical.update(strings(json.loads(path.read_bytes())))
    new = {r["value"] for rows in inventory().values() for r in rows}
    hashes = {hashlib.sha256(v.encode()).hexdigest() for v in new}
    counts = {"exact_string_overlap": len(new & historical), "recorded_hash_overlap": len(hashes & historical), "recomputed_string_hash_overlap": len(hashes & {hashlib.sha256(v.encode()).hexdigest() for v in historical})}
    if any(counts.values()): raise RuntimeError("disposable overlap")
    return {"starting_head": START, "historical_fixture_files": 13, "expected_labels_parsed": False, **counts, "inventory": inventory()}
