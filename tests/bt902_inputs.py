"""Classifier-free, new Boolean-total-mapping disposable inventory."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
START = "43a30343a6a0494de0f55177f714ef93adb3021b"
RAW = ("00000000", "00000006", "000000011", "000000017", "000000029")
ARRAY_RAW = ("-131|14|0|137", "0|-139|16|149", "18|0|-151|157", "-163|20|167|0", "0|22|-173|179")
P, Q = "bt902Item%2==1", "bt902Item%3==2"
HEADER = "NUMBER bt902Limit. INPUT(bt902Limit). NUMBER bt902Total=181. NUMBER bt902P=0. NUMBER bt902Q=0. "
PRELUDE = f"bt902P=0. bt902Q=0. IF ({P}) {{ bt902P=1. }} IF ({Q}) {{ bt902Q=1. }} "
AND = f"IF (({P})&&({Q})) {{ bt902Total+=1. }}"
OR = f"IF (({P})||({Q})) {{ bt902Total+=1. }}"
PRODUCT = "bt902Total+=(bt902P*bt902Q)."
SUM = "IF (bt902P+bt902Q>0) { bt902Total+=1. }"

def source(body):
    return HEADER + "LOOP (NUMBER bt902Item=1 TILL bt902Item<=bt902Limit, bt902Item++) { " + body + " } DISPLAYNL(bt902Total)."

SOURCES = {
    "AND": source(PRELUDE + AND), "PRODUCT": source(PRELUDE + PRODUCT),
    "OR": source(PRELUDE + OR), "SUM": source(PRELUDE + SUM),
    "REPEATED_AND": source(PRELUDE + AND + AND),
    "REPEATED_PRODUCT": source(PRELUDE + PRODUCT + " " + PRODUCT),
    "EXTRA_ARITHMETIC": source(PRELUDE + PRODUCT + "bt902Total+=bt902Item+191."),
    "EXTRA_BOOLEAN": source(PRELUDE + SUM + f"IF ({P}) {{ bt902Total+=1. }}"),
    "MISSING": source(PRELUDE + PRODUCT),
    "DOWNSTREAM": source(PRELUDE + PRODUCT + "bt902Total=181."),
    "EXTRA_INDICATOR": source(PRELUDE + "bt902Total+=bt902P*bt902Q+bt902P."),
    "STATE_MUTATION": source(PRELUDE + PRODUCT + "bt902P=0."),
    "SAME_OUTPUT": source(PRELUDE + PRODUCT + "IF (bt902Item>197) { bt902Total+=1. }"),
    "WRONG_BOUNDARY": source(PRELUDE + "bt902Q+=bt902P*bt902Q."),
    "WRONG_LOOP": HEADER + "LOOP (NUMBER bt902Item=1 TILL bt902Item<=bt902Limit, bt902Item++) { " + PRELUDE + AND + " } LOOP (NUMBER bt902Later=1 TILL bt902Later<=bt902Limit, bt902Later++) { " + PRODUCT + " } DISPLAYNL(bt902Total).",
}
for name in ("AND", "PRODUCT", "OR", "SUM", "REPEATED_PRODUCT"):
    SOURCES["ALPHA_" + name] = SOURCES[name].replace("bt902", "transport907")
for name, predicate in zip(("ODD", "RESIDUE", "DIVISOR", "HALF"), (P, Q, "bt902Limit%bt902Item==0", "2*bt902Item<=bt902Limit")):
    SOURCES[name] = source(PRELUDE + f"IF ({predicate}) {{ bt902Total+=1. }}")
ARRAY_PREDICATES = ("bt902Values[bt902Item]<0", "bt902Values[bt902Item]%2==0", "bt902Values[bt902Item]*bt902Values[bt902Item]>4", "bt902Values[bt902Item]>bt902Item")
SOURCES["ARRAY"] = 'IMPORT strings. SENTENCE bt902Raw. INPUT(bt902Raw). SENTENCE[] bt902Fields=strings.SPLIT(bt902Raw,"|"). NUMBER bt902A=strings.TO_NUMBER(bt902Fields[0]). NUMBER bt902B=strings.TO_NUMBER(bt902Fields[1]). NUMBER bt902C=strings.TO_NUMBER(bt902Fields[2]). NUMBER bt902D=strings.TO_NUMBER(bt902Fields[3]). NUMBER[] bt902Values=[bt902A,bt902B,bt902C,bt902D]. NUMBER bt902Total=181. LOOP (NUMBER bt902Item=0 TILL bt902Item<4, bt902Item++) { ' + " ".join(f"IF ({p}) {{ bt902Total+=1. }}" for p in ARRAY_PREDICATES) + ' } DISPLAYNL(bt902Total).'
PAIRS = (("AND", "PRODUCT", "LOCAL_PAIR_JOINT"), ("OR", "SUM", "BOOLEAN_OR"), ("AND", "ALPHA_PRODUCT", "LOCAL_PAIR_JOINT"), ("OR", "ALPHA_SUM", "BOOLEAN_OR"), ("REPEATED_AND", "REPEATED_PRODUCT", "LOCAL_PAIR_JOINT"), ("REPEATED_AND", "ALPHA_REPEATED_PRODUCT", "LOCAL_PAIR_JOINT"))

def inventory():
    # Include whole source and every expression candidate; no classifier import.
    expressions = (P, Q, "bt902P*bt902Q", "bt902P+bt902Q>0", f"({P})&&({Q})", f"({P})||({Q})", "bt902Item+191", "bt902P*bt902Q+bt902P", "bt902Item>197", "bt902Limit%bt902Item==0", "2*bt902Item<=bt902Limit", *ARRAY_PREDICATES)
    expressions += tuple(e.replace("bt902", "transport907") for e in expressions)
    values = {"ids": tuple("BTOTAL902-" + n for n in SOURCES) + tuple("BTOTAL902-CASE-" + str(i) for i in range(5)), "sources": tuple(SOURCES.values()), "expressions": expressions, "raw_inputs": RAW + ARRAY_RAW}
    return {k: [{"value": v, "sha256_utf8": hashlib.sha256(v.encode()).hexdigest()} for v in rows] for k, rows in values.items()}

def overlap():
    def strings(value):
        if isinstance(value, str): yield value
        elif isinstance(value, list):
            for row in value: yield from strings(row)
        elif isinstance(value, dict):
            for key, row in value.items(): yield key; yield from strings(row)
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
