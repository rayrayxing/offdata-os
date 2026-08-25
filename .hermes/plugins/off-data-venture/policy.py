"""Deterministic evidence, gate, finance and authority policy."""
from __future__ import annotations
import json, hashlib, operator
from .db import stable_hash

DIRECT_FIELDS=("account_identity","actor_identity","counterparty_role","interaction_type","occurred_at","channel","receipt_ref")

def direct_g3_admissible(row:dict)->tuple[bool,str|None]:
    if str(row.get("purpose"))!="DIRECT_BUYER": return False,"PURPOSE_NOT_DIRECT_BUYER"
    if str(row.get("admissibility"))!="ADMISSIBLE": return False,"NOT_ADMISSIBLE"
    if str(row.get("environment"))!="LIVE": return False,"NOT_LIVE"
    if bool(row.get("is_provisional")): return False,"PROVISIONAL"
    missing=[f for f in DIRECT_FIELDS if not row.get(f)]
    if missing: return False,"MISSING_DIRECT_TUPLE:"+",".join(missing)
    return True,None

def evidence_fingerprint(row:dict)->str:
    return stable_hash({k:row.get(k) for k in ("id","purpose","admissibility",*DIRECT_FIELDS,"content_hash","environment","is_provisional")})

def _get_path(obj,path):
    cur=obj
    for part in path.split("."):
        if not isinstance(cur,dict) or part not in cur: return None
        cur=cur[part]
    return cur

OPS={">=":operator.ge,">":operator.gt,"<=":operator.le,"<":operator.lt,"==":operator.eq,"!=":operator.ne}

def evaluate_gate(conn, venture_id:str, gate:str, policy_version:str):
    with conn.cursor() as cur:
        cur.execute("SELECT policy,policy_hash,status FROM policy_registry WHERE policy_type='GATES' AND version=%s",(policy_version,))
        p=cur.fetchone()
        if not p or p["status"] not in ("RATIFIED","ACTIVE"): return {"result":"FAIL","reason":"POLICY_NOT_RATIFIED"}
        spec=(p["policy"] or {}).get("gates",{}).get(gate)
        if not spec: return {"result":"FAIL","reason":"GATE_NOT_DEFINED"}
        cur.execute("SELECT environment,kill_switch FROM ventures WHERE id=%s",(venture_id,)); venture=cur.fetchone()
        if not venture: return {"result":"FAIL","reason":"VENTURE_NOT_FOUND"}
        if venture["kill_switch"]: return {"result":"FAIL","reason":"KILL_SWITCH"}
        predecessor=spec.get("predecessor")
        predecessor_id=None
        if predecessor:
            cur.execute("""SELECT id,result,state,input_fingerprint FROM gate_snapshots
                           WHERE venture_id=%s AND gate=%s ORDER BY created_at DESC LIMIT 1""",(venture_id,predecessor))
            pred=cur.fetchone()
            if not pred or pred["result"]!="PASS" or pred["state"]!="CURRENT":
                return {"result":"NOT_YET_PROVEN","reason":"CURRENT_PREDECESSOR_REQUIRED","predecessor":predecessor}
            predecessor_id=str(pred["id"])
        if spec.get("forbid_open_blocking_concerns",True):
            cur.execute("SELECT count(*) n FROM concerns WHERE venture_id=%s AND severity='BLOCKING' AND status='OPEN'",(venture_id,))
            if cur.fetchone()["n"]>0: return {"result":"NOT_YET_PROVEN","reason":"OPEN_BLOCKING_CONCERN"}
        cur.execute("SELECT * FROM evidence_artifacts WHERE venture_id=%s AND admissibility='ADMISSIBLE' ORDER BY created_at",(venture_id,))
        evidence=list(cur.fetchall())
        contributing=[]
        if gate=="G3":
            contributing=[e for e in evidence if direct_g3_admissible(e)[0]]
            min_direct=int(spec.get("min_direct_buyer_items",1))
            if len(contributing)<min_direct:
                return {"result":"NOT_YET_PROVEN","reason":"STRICT_G3_DIRECT_BUYER_EVIDENCE_INSUFFICIENT","count":len(contributing),"required":min_direct}
        for purpose,min_count in (spec.get("min_admissible_by_purpose") or {}).items():
            matches=[e for e in evidence if str(e.get("purpose"))==purpose]
            if len(matches)<int(min_count): return {"result":"NOT_YET_PROVEN","reason":f"EVIDENCE_{purpose}_INSUFFICIENT","count":len(matches),"required":min_count}
            contributing.extend(matches)
        # de-duplicate while preserving deterministic order
        seen=set(); contributing=[e for e in contributing if not (str(e['id']) in seen or seen.add(str(e['id'])))]
        financial_snapshot_id=None; financial_payload=None
        fin=spec.get("financial") or {}
        if fin:
            cur.execute("SELECT id,snapshot FROM financial_snapshots WHERE venture_id=%s ORDER BY period_end DESC,created_at DESC LIMIT 1",(venture_id,))
            fs=cur.fetchone()
            if not fs: return {"result":"NOT_YET_PROVEN","reason":"FINANCIAL_SNAPSHOT_REQUIRED"}
            financial_snapshot_id=str(fs["id"]); financial_payload=fs["snapshot"] or {}
            for rule in fin.get("rules",[]):
                value=_get_path(financial_payload,rule["path"]); expected=rule["value"]; op=OPS[rule["op"]]
                if value is None or not op(float(value),float(expected)):
                    return {"result":"NOT_YET_PROVEN","reason":"FINANCIAL_RULE_FAILED","rule":rule,"actual":value}
        cur.execute("SELECT id,severity,status FROM concerns WHERE venture_id=%s AND status='OPEN' ORDER BY id",(venture_id,)); concerns=cur.fetchall()
        fp=stable_hash({"gate":gate,"policy_hash":p["policy_hash"],"predecessor":predecessor_id,
                        "evidence":[evidence_fingerprint(e) for e in contributing],"financial_snapshot_id":financial_snapshot_id,
                        "concerns":[str(c['id'])+':'+str(c['severity']) for c in concerns],"environment":str(venture['environment'])})
        return {"result":"PASS","reason":"POLICY_SATISFIED","predecessor_snapshot_id":predecessor_id,
                "evidence":contributing,"financial_snapshot_id":financial_snapshot_id,"input_fingerprint":fp,
                "policy_hash":p["policy_hash"],"environment":str(venture["environment"])}

def owner_policy(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT owner_policy,base_currency FROM portfolios ORDER BY created_at LIMIT 1")
        row=cur.fetchone()
        return (row or {}).get("owner_policy") or {}

def action_policy_check(conn, *, profile:str, venture_id:str, tool_name:str, environment:str, amount_sgd:float=0, target=None):
    with conn.cursor() as cur:
        cur.execute("SELECT kill_switch FROM ventures WHERE id=%s",(venture_id,)); v=cur.fetchone()
        if not v: return False,"VENTURE_NOT_FOUND",None
        if v["kill_switch"]: return False,"KILL_SWITCH",None
        cur.execute("SELECT action_class,effect_class,default_requires_authorization FROM tool_policies WHERE tool_name=%s AND enabled=true",(tool_name,)); tp=cur.fetchone()
        if not tp: return True,"UNCLASSIFIED_TOOL_NOT_GUARDED",None
        if tp["effect_class"]=="READ": return True,"READ_ONLY",None
        cur.execute("""SELECT id FROM authority_grants WHERE profile_name=%s AND (venture_id IS NULL OR venture_id=%s)
                       AND action_class=%s AND environment=%s AND revoked_at IS NULL
                       AND valid_from<=now() AND (expires_at IS NULL OR expires_at>now()) ORDER BY valid_from DESC LIMIT 1""",
                    (profile,venture_id,tp["action_class"],environment))
        grant=cur.fetchone()
        if not grant: return False,"NO_ACTIVE_AUTHORITY_GRANT",None
        cur.execute("""SELECT id,amount_sgd,target_scope FROM action_authorizations WHERE venture_id=%s AND actor_profile=%s
                       AND action_class=%s AND environment=%s AND status='APPROVED'
                       AND (valid_from IS NULL OR valid_from<=now()) AND (expires_at IS NULL OR expires_at>now())
                       ORDER BY resolved_at DESC LIMIT 1""",(venture_id,profile,tp["action_class"],environment))
        auth=cur.fetchone()
        if tp["default_requires_authorization"] and not auth: return False,"ACTION_AUTHORIZATION_REQUIRED",None
        if auth and amount_sgd>float(auth["amount_sgd"] or 0): return False,"ACTION_AMOUNT_EXCEEDS_AUTHORIZATION",str(auth["id"])
        return True,"AUTHORIZED",str(auth["id"]) if auth else None
