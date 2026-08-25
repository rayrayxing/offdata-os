"""Hermes handlers for OFF/DATA Venture Brain. Every authoritative write is transactional and idempotent."""
from __future__ import annotations
import json, uuid, datetime as dt
from decimal import Decimal
from . import db, policy

D=lambda x: Decimal(str(x or 0))
def _env(args, default="TEST"): return args.get("environment") or default
def _actor(kwargs): return kwargs.get("actor_profile") or "unknown-profile"
def _mutate(args, kwargs, action, fn, venture_id=None, environment=None, policy_version=None):
    op=args["operation_id"]; corr=args["correlation_id"]; actor=_actor(kwargs); env=environment or _env(args)
    with db.tx() as conn:
        prior=db.begin_operation(conn,op,corr,actor,action,args,env)
        if prior is not None: return prior
        result=fn(conn)
        db.audit(conn,venture_id=venture_id or args.get("venture_id"),operation_id=op,correlation_id=corr,actor_profile=actor,
                 action=action,environment=env,after_fingerprint=db.stable_hash(result),policy_version=policy_version,
                 input_refs=args.get("input_refs"),metadata={"result_type":result.get("type") if isinstance(result,dict) else None})
        db.complete_operation(conn,op,result)
        return result

@db.json_result
def offdata_status(args, **kwargs):
    with db.tx() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT version,applied_at FROM schema_migrations ORDER BY applied_at"); migrations=cur.fetchall()
            cur.execute("SELECT policy_type,version,status FROM policy_registry ORDER BY policy_type,version"); policies=cur.fetchall()
            cur.execute("SELECT count(*) n FROM ventures WHERE status='ACTIVE'"); ventures=cur.fetchone()["n"]
            cur.execute("SELECT count(*) n FROM capability_catalogue WHERE status='AVAILABLE'"); caps=cur.fetchone()["n"]
        return {"ok":True,"type":"OffDataStatus","migrations":migrations,"policies":policies,"active_ventures":ventures,"available_capabilities":caps}

@db.json_result
def offdata_venture_create(args, **kwargs):
    def fn(conn):
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM opportunities WHERE portfolio_id=%s AND slug=%s",(args["portfolio_id"],args["slug"])); opp=cur.fetchone()
            if not opp:
                cur.execute("""INSERT INTO opportunities(id,portfolio_id,slug,name,stage,environment,is_provisional,payload)
                               VALUES(gen_random_uuid(),%s,%s,%s,%s,%s,true,%s::jsonb) RETURNING id""",
                            (args["portfolio_id"],args["slug"],args["name"],args.get("stage","DISCOVERED"),args["environment"],json.dumps(args.get("payload") or {})))
                opp=cur.fetchone()
            cur.execute("SELECT id FROM ventures WHERE portfolio_id=%s AND slug=%s",(args["portfolio_id"],args["slug"])); v=cur.fetchone()
            if not v:
                cur.execute("""INSERT INTO ventures(id,portfolio_id,opportunity_id,slug,name,environment,is_provisional,phase,status)
                               VALUES(gen_random_uuid(),%s,%s,%s,%s,%s,true,%s,'ACTIVE') RETURNING id""",
                            (args["portfolio_id"],opp["id"],args["slug"],args["name"],args["environment"],args.get("stage","DISCOVERED")))
                v=cur.fetchone()
            return {"ok":True,"type":"Venture","venture_id":str(v["id"]),"opportunity_id":str(opp["id"]),"stage":args.get("stage","DISCOVERED")}
    return _mutate(args,kwargs,"venture_create",fn,environment=args["environment"])

@db.json_result
def offdata_venture_get(args, **kwargs):
    with db.tx() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM ventures WHERE id=%s",(args["venture_id"],)); v=cur.fetchone()
            if not v: return {"ok":False,"error":"VENTURE_NOT_FOUND"}
            cur.execute("SELECT * FROM concerns WHERE venture_id=%s AND status='OPEN' ORDER BY severity,created_at",(args["venture_id"],)); concerns=cur.fetchall()
            cur.execute("SELECT gate,result,state,policy_version,created_at FROM gate_snapshots WHERE venture_id=%s ORDER BY created_at",(args["venture_id"],)); gates=cur.fetchall()
            cur.execute("SELECT purpose,admissibility,count(*) n FROM evidence_artifacts WHERE venture_id=%s GROUP BY purpose,admissibility",(args["venture_id"],)); evidence=cur.fetchall()
            return {"ok":True,"venture":v,"open_concerns":concerns,"gate_history":gates,"evidence_counts":evidence}

@db.json_result
def offdata_research_mission_create(args, **kwargs):
    def fn(conn):
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO research_missions(id,venture_id,objective,questions,freshness_days,max_cost_sgd,min_source_diversity,require_contrary,operation_id)
                           VALUES(gen_random_uuid(),%s,%s,%s::jsonb,%s,%s,%s,%s,%s) RETURNING id""",
                        (args["venture_id"],args["objective"],json.dumps(args["questions"]),args.get("freshness_days",30),args.get("max_cost_sgd",0),args.get("min_source_diversity",3),args.get("require_contrary",True),args["operation_id"]))
            rid=cur.fetchone()["id"]
            return {"ok":True,"type":"ResearchMission","mission_id":str(rid),"status":"OPEN"}
    return _mutate(args,kwargs,"research_mission_create",fn)

@db.json_result
def offdata_research_record(args, **kwargs):
    def fn(conn):
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM research_artifacts WHERE venture_id=%s AND raw_hash=%s LIMIT 1",(args["venture_id"],args["content_hash"])); dup=cur.fetchone()
            if dup: return {"ok":True,"type":"ResearchArtifact","artifact_id":str(dup["id"]),"deduplicated":True}
            cur.execute("""INSERT INTO research_artifacts(id,venture_id,mission_id,source_url,source_type,provider,source_occurred_at,retrieved_at,raw_artifact_ref,raw_hash,role,extracted_claims,receipt,environment,operation_id)
                           VALUES(gen_random_uuid(),%s,%s,%s,%s,%s,NULLIF(%s,'')::timestamptz,%s::timestamptz,%s,%s,%s,%s::jsonb,%s::jsonb,%s,%s) RETURNING id""",
                        (args["venture_id"],args["mission_id"],args.get("source_url"),args["source_type"],args["provider"],args.get("occurred_at",""),args["retrieved_at"],args.get("raw_ref"),args["content_hash"],args["role"],json.dumps(args.get("claims") or []),json.dumps(args.get("receipt") or {}),args["environment"],args["operation_id"]))
            aid=cur.fetchone()["id"]
            return {"ok":True,"type":"ResearchArtifact","artifact_id":str(aid),"deduplicated":False}
    return _mutate(args,kwargs,"research_record",fn,environment=args["environment"])

@db.json_result
def offdata_claim_record(args, **kwargs):
    def fn(conn):
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO claims(id,venture_id,statement,claim_class,confidence,disclosure_policy,supporting_refs,contrary_refs,operation_id)
                           VALUES(gen_random_uuid(),%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s::jsonb,%s) RETURNING id""",
                        (args["venture_id"],args["statement"],args["claim_class"],args.get("confidence"),json.dumps(args.get("disclosure_policy") or {}),json.dumps(args.get("supporting_refs") or []),json.dumps(args.get("contrary_refs") or []),args["operation_id"]))
            return {"ok":True,"type":"Claim","claim_id":str(cur.fetchone()["id"])}
    return _mutate(args,kwargs,"claim_record",fn)

@db.json_result
def offdata_evidence_record(args, **kwargs):
    def fn(conn):
        direct_required=args["purpose"]=="DIRECT_BUYER"
        provisional=bool(args.get("is_provisional",True))
        initial="PROVISIONAL"
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO evidence_artifacts(id,venture_id,purpose,admissibility,account_identity,actor_identity,counterparty_role,interaction_type,occurred_at,channel,receipt_ref,source_ref,content_hash,payload,environment,is_provisional,operation_id)
                           VALUES(gen_random_uuid(),%s,%s,%s,%s,%s,%s,%s,NULLIF(%s,'')::timestamptz,%s,%s,%s,%s,%s::jsonb,%s,%s,%s) RETURNING *""",
                        (args["venture_id"],args["purpose"],initial,args.get("account_identity"),args.get("actor_identity"),args.get("counterparty_role"),args.get("interaction_type"),args.get("occurred_at",""),args.get("channel"),args.get("receipt_ref"),args.get("source_ref"),args["content_hash"],json.dumps(args.get("payload") or {}),args["environment"],provisional,args["operation_id"]))
            row=cur.fetchone(); ok,reason=policy.direct_g3_admissible({**row,"admissibility":"ADMISSIBLE"}) if direct_required else (True,None)
            if args["purpose"]=="MARKET_RESEARCH": adm="ADMISSIBLE" if args["environment"] in ("TEST","SIMULATION","LIVE") else "PROVISIONAL"
            elif direct_required: adm="ADMISSIBLE" if ok else "INADMISSIBLE"
            else: adm="PROVISIONAL" if provisional else "ADMISSIBLE"
            cur.execute("UPDATE evidence_artifacts SET admissibility=%s,inadmissible_reason=%s,is_provisional=%s WHERE id=%s",(adm,reason,provisional,row["id"]))
            return {"ok":True,"type":"EvidenceArtifact","evidence_id":str(row["id"]),"admissibility":adm,"reason":reason}
    return _mutate(args,kwargs,"evidence_record",fn,environment=args["environment"])

@db.json_result
def offdata_evidence_validate(args, **kwargs):
    with db.tx() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM evidence_artifacts WHERE id=%s",(args["evidence_id"],)); row=cur.fetchone()
            if not row: return {"ok":False,"error":"EVIDENCE_NOT_FOUND"}
            if str(row["purpose"])=="DIRECT_BUYER": ok,reason=policy.direct_g3_admissible(row)
            else: ok=str(row["admissibility"])=="ADMISSIBLE"; reason=None if ok else str(row["admissibility"])
            return {"ok":True,"evidence_id":args["evidence_id"],"authoritative":ok,"reason":reason}

@db.json_result
def offdata_concern_record(args, **kwargs):
    def fn(conn):
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO concerns(id,venture_id,description,severity,confidence,source_refs,mitigation,operation_id)
                           VALUES(gen_random_uuid(),%s,%s,%s,%s,%s::jsonb,%s,%s) RETURNING id""",
                        (args["venture_id"],args["description"],args["severity"],args.get("confidence"),json.dumps(args.get("source_refs") or []),args.get("mitigation"),args["operation_id"]))
            cid=cur.fetchone()["id"]
            return {"ok":True,"type":"Concern","concern_id":str(cid),"severity":args["severity"],"automatically_blocks":args["severity"]=="BLOCKING"}
    return _mutate(args,kwargs,"concern_record",fn)

@db.json_result
def offdata_experiment_create(args, **kwargs):
    def fn(conn):
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO experiments(id,venture_id,concept_revision,principal_uncertainty,hypothesis,experiment_type,target,method,success_signal,failure_signal,stopping_rule,budget_sgd,deadline,evidence_requirement,analysis_method,operation_id)
                           VALUES(gen_random_uuid(),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NULLIF(%s,'')::timestamptz,%s::jsonb,%s::jsonb,%s) RETURNING id""",
                        (args["venture_id"],args.get("concept_revision"),args["principal_uncertainty"],args["hypothesis"],args["experiment_type"],args["target"],args["method"],args["success_signal"],args["failure_signal"],args["stopping_rule"],args["budget_sgd"],args.get("deadline",""),json.dumps(args.get("evidence_requirement") or {}),json.dumps(args.get("analysis_method") or {}),args["operation_id"]))
            return {"ok":True,"type":"Experiment","experiment_id":str(cur.fetchone()["id"]),"status":"PLANNED"}
    return _mutate(args,kwargs,"experiment_create",fn)

@db.json_result
def offdata_prototype_record(args, **kwargs):
    def fn(conn):
        if not args["isolation_verified"]: raise ValueError("PROTOTYPE_ISOLATION_REQUIRED")
        with conn.cursor() as cur:
            cur.execute("SELECT COALESCE(max(revision),0)+1 r FROM prototypes WHERE venture_id=%s",(args["venture_id"],)); rev=cur.fetchone()["r"]
            cur.execute("""INSERT INTO prototypes(id,venture_id,experiment_id,revision,artifact_ref,artifact_hash,is_simulation,critical_workflow,isolation_verified,limitations,operation_id)
                           VALUES(gen_random_uuid(),%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s) RETURNING id""",
                        (args["venture_id"],args["experiment_id"],rev,args["artifact_ref"],args["artifact_hash"],args["is_simulation"],args["critical_workflow"],args["isolation_verified"],json.dumps(args.get("limitations") or []),args["operation_id"]))
            return {"ok":True,"type":"Prototype","prototype_id":str(cur.fetchone()["id"]),"revision":rev}
    return _mutate(args,kwargs,"prototype_record",fn)

@db.json_result
def offdata_validation_record(args, **kwargs):
    def fn(conn):
        with conn.cursor() as cur:
            if args["kind"]=="PACKAGE":
                cur.execute("SELECT COALESCE(max(revision),0)+1 r FROM validation_packages WHERE venture_id=%s",(args["venture_id"],)); rev=cur.fetchone()["r"]
                cur.execute("INSERT INTO validation_packages(id,venture_id,revision,package,operation_id) VALUES(gen_random_uuid(),%s,%s,%s::jsonb,%s) RETURNING id",(args["venture_id"],rev,json.dumps(args["payload"]),args["operation_id"])); rid=cur.fetchone()["id"]
                return {"ok":True,"type":"ValidationPackage","id":str(rid),"revision":rev}
            raise ValueError("OBSERVATION must be recorded through offdata_interaction_record/offdata_evidence_record")
    return _mutate(args,kwargs,"validation_record",fn)

@db.json_result
def offdata_gate_evaluate(args, **kwargs):
    def fn(conn):
        result=policy.evaluate_gate(conn,args["venture_id"],args["gate"],args["policy_version"])
        if result["result"]!="PASS": return {"ok":True,"type":"GateEvaluation",**result}
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO gate_snapshots(id,venture_id,gate,policy_version,predecessor_snapshot_id,input_fingerprint,financial_snapshot_id,result,state,environment,operation_id)
                           VALUES(gen_random_uuid(),%s,%s,%s,%s,%s,%s,'PASS','CURRENT',%s,%s) RETURNING id""",
                        (args["venture_id"],args["gate"],args["policy_version"],result.get("predecessor_snapshot_id"),result["input_fingerprint"],result.get("financial_snapshot_id"),result["environment"],args["operation_id"]))
            sid=cur.fetchone()["id"]
            for e in result.get("evidence") or []:
                cur.execute("INSERT INTO gate_snapshot_evidence(gate_snapshot_id,evidence_id,evidence_fingerprint) VALUES(%s,%s,%s)",(sid,e["id"],policy.evidence_fingerprint(e)))
            cur.execute("UPDATE ventures SET current_gate=%s,updated_at=now() WHERE id=%s",(args["gate"],args["venture_id"]))
            return {"ok":True,"type":"GateSnapshot","gate_snapshot_id":str(sid),"gate":args["gate"],"result":"PASS","input_fingerprint":result["input_fingerprint"]}
    return _mutate(args,kwargs,"gate_evaluate",fn,policy_version=args["policy_version"])

@db.json_result
def offdata_action_request(args, **kwargs):
    def fn(conn):
        actor=_actor(kwargs)
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO action_authorizations(id,venture_id,actor_profile,action_class,tool_scope,target_scope,environment,amount_sgd,reason,status,expires_at,operation_id)
                           VALUES(gen_random_uuid(),%s,%s,%s,%s::jsonb,%s::jsonb,%s,%s,%s,'PENDING',NULLIF(%s,'')::timestamptz,%s) RETURNING id""",
                        (args["venture_id"],actor,args["action_class"],json.dumps(args["tool_scope"]),json.dumps(args["target_scope"]),args["environment"],args["amount_sgd"],args["reason"],args.get("expires_at",""),args["operation_id"]))
            aid=cur.fetchone()["id"]
            return {"ok":True,"type":"ActionAuthorization","authorization_id":str(aid),"status":"PENDING","requires_owner_resolution":True,
                    "telegram_instruction":f"/offdata approve {aid} or /offdata deny {aid}"}
    return _mutate(args,kwargs,"action_request",fn,environment=args["environment"])

@db.json_result
def offdata_action_resolve(args, **kwargs):
    def fn(conn):
        if _actor(kwargs)!="offdata-control" and not kwargs.get("owner_authenticated",False): raise ValueError("OWNER_OR_CONTROL_PROFILE_REQUIRED")
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM action_authorizations WHERE id=%s FOR UPDATE",(args["authorization_id"],)); row=cur.fetchone()
            if not row: raise ValueError("AUTHORIZATION_NOT_FOUND")
            if args["decision"]=="REVOKED": status="REVOKED"
            else: status=args["decision"]
            cur.execute("UPDATE action_authorizations SET status=%s,resolved_by=%s,resolved_at=now(),valid_from=CASE WHEN %s='APPROVED' THEN now() ELSE valid_from END WHERE id=%s",(status,args["resolver_identity"],status,args["authorization_id"]))
            return {"ok":True,"type":"ActionAuthorization","authorization_id":args["authorization_id"],"status":status}
    return _mutate(args,kwargs,"action_resolve",fn)

@db.json_result
def offdata_capital_request(args, **kwargs):
    def fn(conn):
        with conn.cursor() as cur:
            cur.execute("INSERT INTO capital_requests(id,venture_id,purpose,amount_sgd,expected_value,gate_snapshot_id,status,expires_at,operation_id) VALUES(gen_random_uuid(),%s,%s,%s,%s::jsonb,NULLIF(%s,'')::uuid,'PENDING',NULLIF(%s,'')::timestamptz,%s) RETURNING id",
                        (args["venture_id"],args["purpose"],args["amount_sgd"],json.dumps(args.get("expected_value") or {}),args.get("gate_snapshot_id",""),args.get("expires_at",""),args["operation_id"]))
            return {"ok":True,"type":"CapitalRequest","request_id":str(cur.fetchone()["id"]),"status":"PENDING"}
    return _mutate(args,kwargs,"capital_request",fn)

@db.json_result
def offdata_capital_authorize(args, **kwargs):
    def fn(conn):
        if _actor(kwargs)!="offdata-control" and not kwargs.get("owner_authenticated",False): raise ValueError("OWNER_OR_CONTROL_PROFILE_REQUIRED")
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM capital_requests WHERE id=%s FOR UPDATE",(args["request_id"],)); req=cur.fetchone()
            if not req: raise ValueError("CAPITAL_REQUEST_NOT_FOUND")
            amount=D(args.get("authorized_amount_sgd",0))
            if args["decision"]=="APPROVED" and amount>D(req["amount_sgd"]): raise ValueError("AUTHORIZED_AMOUNT_EXCEEDS_REQUEST")
            cur.execute("UPDATE capital_requests SET status=%s WHERE id=%s",(args["decision"],args["request_id"]))
            if args["decision"]=="APPROVED":
                cur.execute("INSERT INTO capital_authorizations(id,request_id,venture_id,purpose,amount_sgd,authorized_by,gate_snapshot_id,operation_id) VALUES(gen_random_uuid(),%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                            (req["id"],req["venture_id"],req["purpose"],amount,args["resolver_identity"],req["gate_snapshot_id"],args["operation_id"])); aid=cur.fetchone()["id"]
            else: aid=None
            return {"ok":True,"type":"CapitalDecision","request_id":args["request_id"],"decision":args["decision"],"authorization_id":str(aid) if aid else None}
    return _mutate(args,kwargs,"capital_authorize",fn)

@db.json_result
def offdata_financial_post(args, **kwargs):
    def fn(conn):
        deb=sum(D(x.get("debit")) for x in args["lines"]); cred=sum(D(x.get("credit")) for x in args["lines"])
        if deb!=cred: raise ValueError(f"UNBALANCED_ENTRY debit={deb} credit={cred}")
        if deb==0: raise ValueError("ZERO_VALUE_ENTRY")
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM financial_periods WHERE venture_id=%s AND %s::date BETWEEN period_start AND period_end AND status='CLOSED'",(args["venture_id"],args["entry_date"]))
            if cur.fetchone(): raise ValueError("FINANCIAL_PERIOD_CLOSED")
            cur.execute("INSERT INTO journal_entries(id,venture_id,entry_date,currency,description,source_receipt_ref,environment,operation_id) VALUES(gen_random_uuid(),%s,%s::date,%s,%s,%s,%s,%s) RETURNING id",
                        (args["venture_id"],args["entry_date"],args["currency"],args["description"],args.get("source_receipt_ref"),args["environment"],args["operation_id"])); eid=cur.fetchone()["id"]
            for line in args["lines"]:
                cur.execute("INSERT INTO journal_lines(id,entry_id,account_code,debit,credit,memo) VALUES(gen_random_uuid(),%s,%s,%s,%s,%s)",(eid,line["account"],line["debit"],line["credit"],line.get("memo")))
            cur.execute("SELECT COALESCE(sum(debit),0) d,COALESCE(sum(credit),0) c FROM journal_lines WHERE entry_id=%s",(eid,)); bal=cur.fetchone()
            if D(bal["d"])!=D(bal["c"]): raise ValueError("UNBALANCED_AFTER_INSERT")
            return {"ok":True,"type":"JournalEntry","entry_id":str(eid),"debit":str(deb),"credit":str(cred)}
    return _mutate(args,kwargs,"financial_post",fn,environment=args["environment"])

@db.json_result
def offdata_financial_snapshot_close(args, **kwargs):
    def fn(conn):
        with conn.cursor() as cur:
            cur.execute("""SELECT a.account_type,a.code,COALESCE(sum(l.debit-l.credit),0) balance
                           FROM accounts a LEFT JOIN journal_lines l ON l.account_code=a.code LEFT JOIN journal_entries j ON j.id=l.entry_id AND j.venture_id=%s AND j.entry_date BETWEEN %s::date AND %s::date
                           GROUP BY a.account_type,a.code ORDER BY a.code""",(args["venture_id"],args["period_start"],args["period_end"])); rows=cur.fetchall()
            balances={r["code"]:float(r["balance"]) for r in rows}
            revenue=max(0,-sum(float(r["balance"]) for r in rows if r["account_type"]=="REVENUE"))
            expenses=max(0,sum(float(r["balance"]) for r in rows if r["account_type"]=="EXPENSE"))
            cor=max(0,balances.get("5000",0)); gross_profit=revenue-cor; gm=(gross_profit/revenue*100) if revenue else None
            snapshot={"balances":balances,"metrics":{"revenue_sgd":revenue,"expenses_sgd":expenses,"gross_profit_sgd":gross_profit,"gross_margin_pct":gm}}
            fp=db.stable_hash(snapshot)
            cur.execute("INSERT INTO financial_snapshots(id,venture_id,period_start,period_end,snapshot,input_fingerprint,closed_at,operation_id) VALUES(gen_random_uuid(),%s,%s::date,%s::date,%s::jsonb,%s,now(),%s) RETURNING id",
                        (args["venture_id"],args["period_start"],args["period_end"],json.dumps(snapshot),fp,args["operation_id"])); sid=cur.fetchone()["id"]
            cur.execute("INSERT INTO financial_periods(id,venture_id,period_start,period_end,status,closed_at) VALUES(gen_random_uuid(),%s,%s::date,%s::date,'CLOSED',now()) ON CONFLICT(venture_id,period_start,period_end) DO UPDATE SET status='CLOSED',closed_at=now()",(args["venture_id"],args["period_start"],args["period_end"]))
            return {"ok":True,"type":"FinancialSnapshot","snapshot_id":str(sid),"input_fingerprint":fp,"snapshot":snapshot}
    return _mutate(args,kwargs,"financial_snapshot_close",fn)

@db.json_result
def offdata_contact_upsert(args, **kwargs):
    def fn(conn):
        with conn.cursor() as cur:
            email=args.get("email")
            if email:
                cur.execute("SELECT id FROM contacts WHERE venture_id=%s AND lower(email)=lower(%s)",(args["venture_id"],email)); row=cur.fetchone()
            else: row=None
            if row:
                cur.execute("UPDATE contacts SET account_identity=COALESCE(%s,account_identity),person_identity=COALESCE(%s,person_identity),opt_out=%s,metadata=metadata||%s::jsonb,updated_at=now() WHERE id=%s",
                            (args.get("account_identity"),args.get("person_identity"),args.get("opt_out",False),json.dumps(args.get("metadata") or {}),row["id"])); cid=row["id"]
            else:
                cur.execute("INSERT INTO contacts(id,venture_id,account_identity,person_identity,email,opt_out,metadata,operation_id) VALUES(gen_random_uuid(),%s,%s,%s,%s,%s,%s::jsonb,%s) RETURNING id",
                            (args["venture_id"],args.get("account_identity"),args.get("person_identity"),email,args.get("opt_out",False),json.dumps(args.get("metadata") or {}),args["operation_id"])); cid=cur.fetchone()["id"]
            return {"ok":True,"type":"Contact","contact_id":str(cid)}
    return _mutate(args,kwargs,"contact_upsert",fn)

@db.json_result
def offdata_interaction_record(args, **kwargs):
    def fn(conn):
        with conn.cursor() as cur:
            if args.get("contact_id"):
                cur.execute("SELECT opt_out,next_allowed_contact_at FROM contacts WHERE id=%s",(args["contact_id"],)); c=cur.fetchone()
                if c and c["opt_out"] and args["interaction_type"].upper() in ("OUTREACH","EMAIL_SEND","DM_SEND"): raise ValueError("CONTACT_OPTED_OUT")
            cur.execute("INSERT INTO interactions(id,venture_id,contact_id,interaction_type,channel,occurred_at,receipt_ref,summary,raw_ref,environment,operation_id) VALUES(gen_random_uuid(),%s,NULLIF(%s,'')::uuid,%s,%s,%s::timestamptz,%s,%s,%s,%s,%s) RETURNING id",
                        (args["venture_id"],args.get("contact_id",""),args["interaction_type"],args["channel"],args["occurred_at"],args.get("receipt_ref"),args.get("summary"),args.get("raw_ref"),args["environment"],args["operation_id"])); iid=cur.fetchone()["id"]
            if args.get("contact_id"): cur.execute("UPDATE contacts SET last_contact_at=%s::timestamptz,updated_at=now() WHERE id=%s",(args["occurred_at"],args["contact_id"]))
            return {"ok":True,"type":"Interaction","interaction_id":str(iid)}
    return _mutate(args,kwargs,"interaction_record",fn,environment=args["environment"])

@db.json_result
def offdata_capability_upsert(args, **kwargs):
    def fn(conn):
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO capability_catalogue(id,capability_key,kind,provider,version,profiles,status,details,tested_at)
                           VALUES(gen_random_uuid(),%s,%s,%s,%s,%s::jsonb,%s,%s::jsonb,CASE WHEN %s='AVAILABLE' THEN now() END)
                           ON CONFLICT(capability_key) DO UPDATE SET kind=excluded.kind,provider=excluded.provider,version=excluded.version,profiles=excluded.profiles,status=excluded.status,details=excluded.details,tested_at=excluded.tested_at,updated_at=now()
                           RETURNING id""",(args["capability_key"],args["kind"],args["provider"],args.get("version"),json.dumps(args.get("profiles") or []),args["status"],json.dumps(args.get("details") or {}),args["status"])); cid=cur.fetchone()["id"]
            return {"ok":True,"type":"Capability","capability_id":str(cid),"status":args["status"]}
    return _mutate(args,kwargs,"capability_upsert",fn,environment="TEST")

@db.json_result
def offdata_capability_list(args, **kwargs):
    with db.tx() as conn:
        with conn.cursor() as cur:
            if args.get("status"): cur.execute("SELECT * FROM capability_catalogue WHERE status=%s ORDER BY capability_key",(args["status"],))
            else: cur.execute("SELECT * FROM capability_catalogue ORDER BY capability_key")
            return {"ok":True,"capabilities":cur.fetchall()}

@db.json_result
def offdata_learning_record(args, **kwargs):
    def fn(conn):
        with conn.cursor() as cur:
            cur.execute("INSERT INTO learning_candidates(id,venture_id,learning_type,content,evidence_refs,status,operation_id) VALUES(gen_random_uuid(),NULLIF(%s,'')::uuid,%s,%s::jsonb,%s::jsonb,'CANDIDATE',%s) RETURNING id",
                        (args.get("venture_id",""),args["learning_type"],json.dumps(args["content"]),json.dumps(args.get("evidence_refs") or []),args["operation_id"])); lid=cur.fetchone()["id"]
            return {"ok":True,"type":"LearningCandidate","learning_id":str(lid),"protected_policy_auto_activation":False}
    return _mutate(args,kwargs,"learning_record",fn,environment="TEST")

@db.json_result
def offdata_aar_record(args, **kwargs):
    def fn(conn):
        with conn.cursor() as cur:
            cur.execute("INSERT INTO aars(id,venture_id,aar_type,payload,operation_id) VALUES(gen_random_uuid(),NULLIF(%s,'')::uuid,%s,%s::jsonb,%s) RETURNING id",
                        (args.get("venture_id",""),args["aar_type"],json.dumps(args["payload"]),args["operation_id"])); aid=cur.fetchone()["id"]
            return {"ok":True,"type":"AAR","aar_id":str(aid),"stored_before_delivery":True}
    return _mutate(args,kwargs,"aar_record",fn,environment="TEST")
