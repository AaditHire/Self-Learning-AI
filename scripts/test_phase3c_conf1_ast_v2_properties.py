"""Deterministic synthetic metamorphic checks derived from the v2 normative rule."""

from __future__ import annotations

import json
import re

from phase3c_conf1_structural_overlap_v2 import adjudicate_v2, canonical_tree


def replace_name(source: str, old: str, new: str) -> str:
    return re.sub(r"\b" + re.escape(old) + r"\b", new, source)


def main() -> None:
    incidental = 0
    structural = 0
    for serial in range(50):
        limit = f"bound{serial}"
        index = f"position{serial}"
        tally = f"tally{serial}"
        divisor = 2 + serial % 7
        source = (f"NUMBER {limit}. INPUT({limit}). NUMBER {tally}=0. "
                  f"LOOP (NUMBER {index}=1 TILL {index}<={limit}, {index}++) "
                  f"{{ IF ({index}%{divisor}==1) {{ {tally}+=1. }} }} DISPLAYNL({tally}).")
        trivial = [
            source.replace(". INPUT", ".INPUT").replace(". NUMBER", ".NUMBER")
                  .replace(". LOOP", ".LOOP").replace(" } DISPLAYNL", " }DISPLAYNL"),
            source.replace("NUMBER", "number").replace("INPUT", "input")
                  .replace("LOOP", "loop").replace("TILL", "till")
                  .replace("IF", "if").replace("DISPLAYNL", "displaynl"),
            replace_name(replace_name(replace_name(source, limit, f"cap{serial}"),
                                      index, f"cursor{serial}"), tally, f"sum{serial}"),
            source.replace(f"%{divisor}==1", f"%{divisor + 11}==4").replace("+=1.", "+=8."),
            source.replace(". LOOP", ". // comment\nLOOP"),
        ]
        for transformed in trivial:
            assert canonical_tree(source) == canonical_tree(transformed)
            assert adjudicate_v2(source, transformed, False) == "PROHIBITED_STRUCTURAL_TEMPLATE_REUSE"
            incidental += 1
        changed = [
            source.replace(f"{tally}+=1.", f"{tally}*=1."),
            source.replace(f"IF ({index}%", f"IF ({limit}%"),
            source.replace(f"DISPLAYNL({tally})", f"DISPLAYNL({limit})"),
            source.replace(f"{{ IF ({index}%", f"{{ IF ({index}<{limit}) {{ {tally}+=1. }} IF ({index}%"),
        ]
        for transformed in changed:
            assert canonical_tree(source) != canonical_tree(transformed)
            structural += 1
    print(json.dumps({"synthetic_base_programs": 50, "incidental_transformations_preserved": incidental,
                      "structural_transformations_distinguished": structural, "status": "PASS"}))


if __name__ == "__main__":
    main()
