"""New disposable development inputs, never an independent scientific corpus.

All exact source/expression/input variants used by the core tests are declared
here so a separate, classifier-free preflight can check them before collection.
"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
FORWARD = "NUMBER devLimit. INPUT(devLimit). NUMBER devLedger=17. LOOP (NUMBER devCursor=1 TILL devCursor<=devLimit, devCursor++) { devLedger+=(devCursor). devLedger+=(devCursor). } DISPLAYNL(devLedger)."
REVERSE = "NUMBER reverseLimit. INPUT(reverseLimit). NUMBER reverseLedger=17. NUMBER reverseCursor=(reverseLimit). LOOP (reverseCursor>=1) { reverseLedger+=(reverseCursor). reverseCursor-=1. } DISPLAYNL(reverseLedger)."
PAIR_ADD = "NUMBER pairLimit. INPUT(pairLimit). NUMBER pairLedger=17. NUMBER fifthHit=0. NUMBER seventhHit=0. LOOP (NUMBER pairCursor=1 TILL pairCursor<=pairLimit, pairCursor++) { fifthHit=0. seventhHit=0. IF (pairCursor%5==0) { fifthHit=1. } IF (pairCursor%7==0) { seventhHit=1. } pairLedger+=(fifthHit+seventhHit). } DISPLAYNL(pairLedger)."
PAIR_MUL = PAIR_ADD.replace("fifthHit+seventhHit", "fifthHit*seventhHit")
RENAMED = FORWARD.replace("devLimit", "aliasLimit").replace("devLedger", "aliasLedger").replace("devCursor", "aliasCursor")
CHANGED_VALUE = FORWARD.replace("=17.", "=19.")
CHANGED_PAIR = PAIR_MUL.replace("%7", "%11")
TRIVIA = "// disposable DevCore comment\n" + RENAMED.replace("NUMBER", "  NUMBER")
ZERO_EVENT = FORWARD.replace("+=(devCursor)", "+=0")
ARRAY_SOURCE = 'IMPORT strings. SENTENCE devRaw. INPUT(devRaw). SENTENCE[] devFields=strings.SPLIT(devRaw,"|"). NUMBER decodedNorth=strings.TO_NUMBER(devFields[0]). NUMBER decodedEast=strings.TO_NUMBER(devFields[1]). NUMBER decodedSouth=strings.TO_NUMBER(devFields[2]). NUMBER decodedWest=strings.TO_NUMBER(devFields[3]). NUMBER[] devValues=[decodedNorth,decodedEast,decodedSouth,decodedWest]. NUMBER arrayLedger=17. LOOP (NUMBER arrayCursor=0 TILL arrayCursor<4, arrayCursor++) { arrayLedger+=(devValues[arrayCursor]). } DISPLAYNL(arrayLedger).'
UNKNOWN = ("IMPORT unknownDevCore.", "WHILE (devCoreTruth) { DISPLAYNL(29). }", "devCallback(31)")
SOURCES = (FORWARD, REVERSE, PAIR_ADD, PAIR_MUL, RENAMED, CHANGED_VALUE, CHANGED_PAIR, TRIVIA, ZERO_EVENT, ARRAY_SOURCE, *UNKNOWN)
EXPRESSIONS = ("devLeft+devRight", "otherRight+otherLeft", "(devLeft+devRight)+devThird", "devLeft+(devRight+devThird)", "devLeft<=devRight", "otherRight>=otherLeft", "-(23+6)*3", "-87", "!(devLeft<devRight)", "devLeft>=devRight", "devLeft*devRight", "devLeft&&devRight")
RAW_INPUTS = ("000", "006", "008", "010", "016", "-7|0|11|2")
ARRAY_INPUTS = (RAW_INPUTS[-1], "-9|5|0|13", "4|-8|0|17", "0|0|-6|29", "-12|7|3|0")
PROGRAM_IDS = ("DEVCORE-NUMERIC-DOUBLE-20260930", "DEVCORE-PAIR-20260930", "DEVCORE-REVERSE-20260930", "DEVCORE-ZERO-20260930", "DEVCORE-ARRAY-20260930")
CASE_IDS = tuple("DEVCORE-CASE-" + suffix for suffix in ("Z", "A", "C", "B", "D"))
IDENTIFIERS = (*PROGRAM_IDS, *CASE_IDS, "DEVCORE-CANDIDATE", "DEVCORE-INDEX", "DEVCORE-ROW-ONE", "DEVCORE-ROW-TWO", "DEVCORE-SOURCE", "DEVCORE-CASES", "DEVCORE-INVENTORY", "DEVCORE-INDEX-ARTIFACT")

# Additional pass-specific inputs. They are independent toy data, not derived
# from a preregistered scientific fixture or its labels. No case is executed by
# the population-guard tests; the strings remain in the complete preflight.
CLOSURE_PROGRAM_ID = "DEV-CLOSURE-LEDGER-20260930-B"
CLOSURE_SOURCE = "NUMBER closureLimit. INPUT(closureLimit). NUMBER closureTally=37. LOOP (NUMBER closureCursor=1 TILL closureCursor<=closureLimit, closureCursor++) { closureTally+=(closureCursor%11). } DISPLAYNL(closureTally)."
IDENTIFIERS = (*IDENTIFIERS, CLOSURE_PROGRAM_ID, "DEV-CLOSURE-UNKNOWN-OCCURRENCE-20260930")
SOURCES = (*SOURCES, CLOSURE_SOURCE)


def disposable_inventory():
    groups = {"ids": IDENTIFIERS, "sources": SOURCES, "expressions": EXPRESSIONS,
              "raw_inputs": tuple(dict.fromkeys((*RAW_INPUTS, *ARRAY_INPUTS)))}
    return {name: [{"value": value, "sha256_utf8": hashlib.sha256(value.encode("utf-8")).hexdigest(),
                    "size_bytes_utf8": len(value.encode("utf-8"))} for value in values]
            for name, values in groups.items()}


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)


def assert_zero_historical_overlap():
    """Read raw fixture strings only; never read labels or invoke core code."""
    folder = ROOT / "research/protocols/phase3c_conf1_v3_synthetic_fixtures"
    paths = sorted(folder.glob("*.json"))
    if len(paths) != 13:
        raise RuntimeError("historical comparison population changed")
    historical = set()
    for path in paths:
        historical.update(_strings(json.loads(path.read_text(encoding="utf-8"))))
    manifest = ROOT / "research/protocols/phase3c_conf1_v3_synthetic_fixture_manifest.json"
    historical.update(_strings(json.loads(manifest.read_text(encoding="utf-8"))))
    new = set((*IDENTIFIERS, *SOURCES, *EXPRESSIONS, *RAW_INPUTS, *ARRAY_INPUTS))
    collisions = sorted(new & historical)
    hashes = {hashlib.sha256(value.encode("utf-8")).hexdigest() for value in new}
    hash_collisions = sorted(hashes & historical)
    computed_hash_collisions = sorted(hashes & {hashlib.sha256(value.encode("utf-8")).hexdigest() for value in historical})
    if collisions or hash_collisions or computed_hash_collisions:
        raise RuntimeError(f"development overlap: strings={collisions!r}, hashes={hash_collisions!r}")
    return {"historical_files_compared": len(paths), "new_ids": len(IDENTIFIERS), "new_sources": len(SOURCES),
            "new_expressions": len(EXPRESSIONS), "new_inputs": len(set((*RAW_INPUTS,*ARRAY_INPUTS))), "exact_string_overlap": 0, "recorded_fixture_hash_overlap": 0,
            "computed_historical_string_hash_overlap": 0,
            "historical_fixture_filenames": [path.name for path in paths],
            "comparison_scope": "all recursive raw strings and recorded hashes in 13 fixture files plus manifest; labels excluded",
            "expected_labels_loaded": False, "classifiers_invoked": False}


if __name__ == "__main__":
    print(json.dumps(assert_zero_historical_overlap(), sort_keys=True))
