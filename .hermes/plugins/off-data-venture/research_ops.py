"""Research mission query reservation, dedupe, cost and provider-attempt bookkeeping."""
from __future__ import annotations
import hashlib, re, json
from decimal import Decimal
from . import db
D=lambda x: Decimal(str(x or 0))
def norm(q): return re.sub(r"\s+"," ",(q or "").strip().lower())
def qhash(q): return hashlib.sha256(norm(q).encode()).hexdigest()
@db.json_result
def offdata_research_query_reserve(args, actor_profile="unknown-profile", **kwargs):
    op=args["operation_id"]; corr=args["correlation_id"]
    with db.tx() as conn:
        prior=db.begin_operation(conn,op,corr,actor_profile,"research_query_reserve",args,"TEST")
        if prior is not None:return prior
        with conn.cursor() as cur:
            cur.execute("SELECT id,max_cost_sgd,spent_sgd,status FROM research_missions WHERE id=%s FOR UPDATE",(args["mission_id"],)); m=cur.fetchone()
            if not m: raise ValueError("RESEARCH_MISSION_NOT_FOUND")
            if m["status"] not in ("OPEN","RUNNING"): raise ValueError("RESEARCH_MISSION_NOT_OPEN")
            est=D(args.get("estimated_cost_sgd")); available=D(m["max_cost_sgd"])-D(m["spent_sgd"])
            if est>available: raise ValueError(f"RESEARCH_BUDGET_EXCEEDED available={available}")
            h=qhash(args["query"])
            cur.execute("SELECT * FROM research_queries WHERE mission_id=%s AND query_hash=%s AND provider=%s FOR UPDATE",(args["mission_id"],h,args["provider"])); row=cur.fetchone()
            if row and row["status"] in ("RESERVED","RUNNING","COMPLETED","EMPTY"):
                result={"ok":True,"type":"ResearchQueryReservation","query_id":str(row["id"]),"status":row["status"],"deduped":True,"query_hash":h}
            else:
                if row:
                    cur.execute("UPDATE research_queries SET status='RESERVED',attempt_count=attempt_count+1,last_error=NULL,updated_at=now() WHERE id=%s RETURNING id",(row["id"],)); qid=cur.fetchone()["id"]
                else:
                    cur.execute("""INSERT INTO research_queries(id,mission_id,query_hash,normalized_query,provider,status,attempt_count,cost_sgd)
                                   VALUES(gen_random_uuid(),%s,%s,%s,%s,'RESERVED',1,0) RETURNING id""",(args["mission_id"],h,norm(args["query"]),args["provider"])); qid=cur.fetchone()["id"]
                cur.execute("UPDATE research_missions SET status='RUNNING' WHERE id=%s",(args["mission_id"],))
                result={"ok":True,"type":"ResearchQueryReservation","query_id":str(qid),"status":"RESERVED","deduped":False,"query_hash":h,"budget_remaining_sgd":float(available)}
        db.audit(conn,operation_id=op,correlation_id=corr,actor_profile=actor_profile,action="research_query_reserve",environment="TEST",after_fingerprint=db.stable_hash(result))
        db.complete_operation(conn,op,result); return result
@db.json_result
def offdata_research_query_complete(args, actor_profile="unknown-profile", **kwargs):
    op=args["operation_id"]; corr=args["correlation_id"]
    with db.tx() as conn:
        prior=db.begin_operation(conn,op,corr,actor_profile,"research_query_complete",args,"TEST")
        if prior is not None:return prior
        with conn.cursor() as cur:
            cur.execute("SELECT q.*,m.max_cost_sgd,m.spent_sgd FROM research_queries q JOIN research_missions m ON m.id=q.mission_id WHERE q.id=%s FOR UPDATE",(args["query_id"],)); q=cur.fetchone()
            if not q: raise ValueError("RESEARCH_QUERY_NOT_FOUND")
            if q["status"] in ("COMPLETED","EMPTY") and D(q["cost_sgd"])==D(args["actual_cost_sgd"]):
                result={"ok":True,"type":"ResearchQueryResult","query_id":str(q["id"]),"status":q["status"],"deduped":True}
            else:
                actual=D(args["actual_cost_sgd"]); prior_cost=D(q["cost_sgd"]); delta=max(Decimal("0"),actual-prior_cost)
                if D(q["spent_sgd"])+delta>D(q["max_cost_sgd"]): raise ValueError("ACTUAL_RESEARCH_COST_EXCEEDS_MISSION_BUDGET")
                cur.execute("""UPDATE research_queries SET status=%s,cost_sgd=%s,result_count=%s,provider_receipt=%s::jsonb,last_error=%s,updated_at=now() WHERE id=%s""",
                            (args["status"],actual,args["result_count"],json.dumps(args.get("provider_receipt") or {}),args.get("last_error"),args["query_id"]))
                if delta: cur.execute("UPDATE research_missions SET spent_sgd=spent_sgd+%s WHERE id=%s",(delta,q["mission_id"]))
                result={"ok":True,"type":"ResearchQueryResult","query_id":str(q["id"]),"status":args["status"],"actual_cost_sgd":float(actual),"result_count":args["result_count"]}
        db.audit(conn,operation_id=op,correlation_id=corr,actor_profile=actor_profile,action="research_query_complete",environment="TEST",after_fingerprint=db.stable_hash(result))
        db.complete_operation(conn,op,result); return result
