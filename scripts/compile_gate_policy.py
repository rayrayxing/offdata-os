#!/usr/bin/env python3
"""Compile/ratify an extracted VentureOS G0-G10 policy into OFF/DATA Gate Engine format.
This compiler does not guess missing source semantics. Hermes/Codex must first extract exact policy from the owner's local VentureOS checkout into the documented JSON contract.
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys
from pathlib import Path

REQ_G3=["accountIdentity","actorIdentity","counterpartyRole","interactionType","occurredAt","channel","receiptRef"]

def canonical(obj): return json.dumps(obj,sort_keys=True,separators=(",",":"))
def sha(obj): return hashlib.sha256(canonical(obj).encode()).hexdigest()

def fail(msg): print("FAIL:",msg,file=sys.stderr); raise SystemExit(2)

def validate_source(d):
    for k in ("source_repo","source_sha","source_dirty","extracted_by","gates"):
        if k not in d: fail(f"missing top-level {k}")
    gates=d["gates"]
    missing=[f"G{i}" for i in range(11) if f"G{i}" not in gates]
    if missing: fail(f"source extraction missing gates {missing}")
    for g,s in gates.items():
        for k in ("purpose","predecessor","requirements"):
            if k not in s: fail(f"{g} missing {k}")
    g3=gates["G3"]
    got=g3.get("required_direct_tuple") or []
    if set(got)!=set(REQ_G3): fail(f"G3 seven-tuple mismatch: {got}")
    if g3.get("allow_url_domain_fallback",False): fail("G3 URL/domain fallback forbidden")
    if g3.get("research_can_pass",False) or g3.get("prototype_can_pass",False) or g3.get("simulation_can_pass",False): fail("G3 non-buyer authority forbidden")
    if gates["G4"].get("predecessor") not in ("G3",None): fail("G4 source conflicts with known current-G3 predecessor floor")
    # Audit-known floors are not invented semantics: source must explicitly reconcile them if those gates use the metrics.
    g8=canonical(gates["G8"]).lower()
    for term in ("retention","billing","cash"):
        if term not in g8: fail(f"G8 extraction does not reconcile audit-known {term} semantics")
    g9=canonical(gates["G9"]).lower()
    if "gross_margin" not in g9 and "margin" not in g9: fail("G9 extraction lacks audited margin semantics")
    g10=canonical(gates["G10"]).lower()
    if "roi" not in g10 and "ratio" not in g10: fail("G10 extraction lacks audited ROI/ratio semantics")
    return True

def compile_policy(src):
    validate_source(src)
    out={"policy_type":"GATES","version":f"VENTUREOS-{src['source_sha'][:12]}","source":{
        "repo":src["source_repo"],"sha":src["source_sha"],"dirty":src["source_dirty"],"extracted_by":src["extracted_by"],"evidence_refs":src.get("evidence_refs",[])},
        "global":{"environment_required":True,"current_predecessor_required":True,"snapshot_identity_required":True,"authority_relevant_change_stales_snapshot":True,"transactional_audit_required":True},"gates":{}}
    for i in range(11):
        name=f"G{i}"; s=src["gates"][name]
        c={"purpose":s["purpose"],"predecessor":s.get("predecessor"),"requirements":s.get("requirements",{}),
           "forbid_open_blocking_concerns":s.get("forbid_open_blocking_concerns",True),"min_admissible_by_purpose":s.get("min_admissible_by_purpose",{}),
           "financial":s.get("financial",{}),"owner_approval":s.get("owner_approval"),"authorized_transition":s.get("authorized_transition"),"source_refs":s.get("source_refs",[])}
        if name=="G3": c.update({"min_direct_buyer_items":int(s.get("min_direct_buyer_items",1)),"required_direct_tuple":REQ_G3,"allow_url_domain_fallback":False,"research_can_pass":False,"prototype_can_pass":False,"simulation_can_pass":False})
        out["gates"][name]=c
    out["policy_hash"]=sha(out)
    return out

def load_db(compiled, activate=False):
    try: import psycopg
    except Exception as e: fail(f"psycopg required to load DB: {e}")
    dsn=os.getenv("OFFDATA_DATABASE_URL")
    if not dsn: fail("OFFDATA_DATABASE_URL required for --load-db")
    status="ACTIVE" if activate else "RATIFIED"
    with psycopg.connect(dsn) as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                if activate:
                    cur.execute("UPDATE policy_registry SET status='SUPERSEDED' WHERE policy_type='GATES' AND status='ACTIVE'")
                cur.execute("""INSERT INTO policy_registry(policy_type,version,policy,policy_hash,status,ratified_by,activated_at)
                               VALUES('GATES',%s,%s::jsonb,%s,%s,%s,CASE WHEN %s='ACTIVE' THEN now() END)
                               ON CONFLICT(policy_type,version) DO UPDATE SET policy=excluded.policy,policy_hash=excluded.policy_hash,status=excluded.status,ratified_by=excluded.ratified_by,activated_at=excluded.activated_at""",
                            (compiled["version"],json.dumps(compiled),compiled["policy_hash"],status,"owner+independent-codex",status))
    print(f"DB policy {compiled['version']} -> {status}")

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--input",required=True); ap.add_argument("--output",default="state/compiled-gate-policy.json"); ap.add_argument("--load-db",action="store_true"); ap.add_argument("--activate",action="store_true")
    ns=ap.parse_args(); src=json.loads(Path(ns.input).read_text()); out=compile_policy(src)
    p=Path(ns.output); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(out,indent=2)+"\n")
    print(f"PASS compiled exact G0-G10 source policy -> {p}; version={out['version']} hash={out['policy_hash']}")
    if ns.load_db or ns.activate: load_db(out,activate=ns.activate)

if __name__=="__main__": main()
