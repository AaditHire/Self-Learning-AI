"""Narrow DEVELOPMENT expected-zero exception, NEVER a scientific overlap API."""
from .attribute_reference import digest_text, output_plan, AUTHORITY
from .projection_grammar import require, development_identity
from .projection_binding_verifier import equal

ZERO_HASH="5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9"
EXCEPTION="FROZEN_CANONICAL_ZERO_OUTPUT"


def strings(v):
    if isinstance(v,str):yield v
    elif isinstance(v,list):
        for x in v:yield from strings(x)
    elif isinstance(v,dict):
        for k,x in v.items():yield k;yield from strings(x)


def permitted_corpus(root):
    import json
    paths=sorted((root/"research/protocols/phase3c_conf1_v3_synthetic_fixtures").glob("*.json"))
    require(len(paths)==13,"ATTRIBUTE_OVERLAP_CORPUS_CHANGED")
    old=set()
    for p in (*paths,root/"research/protocols/phase3c_conf1_v3_synthetic_fixture_manifest.json"):
        old.update(strings(json.loads(p.read_bytes())))
    return old


def compare(inventory,prospective,old):
    require(digest_text("0")==ZERO_HASH,"ZERO_CANONICAL_HASH_CHANGED")
    expected={};zero={}
    for p in prospective:
        development_identity(p)
        rebuilt=output_plan(p["declaration"],p["operations"],p["raw_inputs"],digest_text(p["source"]))
        require(equal(rebuilt,p["output_plan"]),"OVERLAP_PROSPECTIVE_OUTPUT_CHANGED")
        for r in rebuilt["expected_records"]:
            k=(r["program_id"],r["case_id"]);expected[k]=r
            z=[q for q in rebuilt["requirements"] if q["operation"]=="OUTPUT_ZERO"]
            if r["expected_output"]=="0" and len(z)==1:zero[k]=z[0]
    old_hashes={digest_text(x) for x in old};prohibited=[];permitted=[];counts=dict(exact_string_overlap=0,recorded_hash_overlap=0,recomputed_string_hash_overlap=0)
    seen_outputs=set();by_field={k:dict(exact_string_overlap=0,recorded_hash_overlap=0,recomputed_string_hash_overlap=0) for k in inventory}
    for field,rows in inventory.items():
        for r in rows:
            require(set(r)==({"value","sha256_utf8","program_id","case_id","requirement_id"} if field=="expected_outputs" else {"value","sha256_utf8"}),"OVERLAP_FIELD_SCHEMA")
            require(digest_text(r["value"])==r["sha256_utf8"],"OVERLAP_LITERAL_HASH_MISMATCH")
            if field=="expected_outputs":
                k=(r["program_id"],r["case_id"]);require(k in expected and k not in seen_outputs,"OVERLAP_WRONG_CASE")
                require(r["value"]==expected[k]["expected_output"],"OVERLAP_EXPECTED_OUTPUT_NOT_INDEPENDENT")
                seen_outputs.add(k)
                if r["value"]=="0":require(k in zero and r["requirement_id"]==zero[k]["requirement_id"],"ZERO_WITHOUT_PROSPECTIVE_REQUIREMENT")
                else:require(r["requirement_id"] is None,"OVERLAP_FORGED_EXCEPTION")
            hit=[r["value"] in old,r["sha256_utf8"] in old,r["sha256_utf8"] in old_hashes]
            for name,h in zip(counts,hit):counts[name]+=int(h);by_field[field][name]+=int(h)
            if not any(hit):continue
            if field=="expected_outputs" and r["value"]=="0" and r["sha256_utf8"]==ZERO_HASH:
                permitted.append(dict(literal="0",sha256_utf8=ZERO_HASH,artifact_field="expected_outputs",category="OUTPUT_ZERO",scope="DEVELOPMENT_ONLY",
                    justification=EXCEPTION,authority=AUTHORITY,prospective_requirement_id=r["requirement_id"],development_case_id=r["case_id"],
                    program_id=r["program_id"],requirement_existed_before_overlap=True,observed_exact_string=hit[0],observed_recorded_hash=hit[1],observed_recomputed_hash=hit[2]))
            else:prohibited.append(dict(field=field,**r,exact_string=hit[0],recorded_hash=hit[1],recomputed_hash=hit[2]))
    require(seen_outputs==set(expected),"OVERLAP_EXPECTED_OUTPUT_INVENTORY_INCOMPLETE")
    require(not prohibited,"PROHIBITED_ATTRIBUTE_OVERLAP")
    require(len(permitted)<=1,"ZERO_EXCEPTION_NOT_SINGLE_WITNESS")
    return dict(scope="DEVELOPMENT_ONLY",inventory=inventory,prospective=prospective,expected_labels_parsed=False,fixture_files=13,
                prohibited_collisions=prohibited,permitted_normative_collisions=permitted,by_field=by_field,**counts)
