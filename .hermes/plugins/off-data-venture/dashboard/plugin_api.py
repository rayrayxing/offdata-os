from fastapi import APIRouter,HTTPException
import os
router=APIRouter()
def q(sql,params=(),many=True):
 try:
  import psycopg
  from psycopg.rows import dict_row
  with psycopg.connect(os.environ["OFFDATA_DATABASE_URL"],row_factory=dict_row) as c:
   with c.cursor() as cur:cur.execute(sql,params);return cur.fetchall() if many else cur.fetchone()
 except Exception as e:raise HTTPException(503,f"Venture Brain unavailable: {e}")
@router.get("/summary")
def summary():
 return {"ventures":q("SELECT phase,count(*) n FROM ventures WHERE status='ACTIVE' GROUP BY phase ORDER BY phase"),"pending_actions":q("SELECT count(*) n FROM action_authorizations WHERE status='PENDING'",many=False)["n"],"pending_capital":q("SELECT count(*) n FROM capital_requests WHERE status='PENDING'",many=False)["n"],"revenue_sgd":float(q("SELECT coalesce(sum(amount),0) n FROM payments WHERE status IN ('succeeded','paid','SUCCEEDED','PAID') AND environment='LIVE'",many=False)["n"])}
@router.get("/ventures")
def ventures():return q("SELECT id,slug,name,phase,current_gate,kill_switch,status,updated_at FROM ventures ORDER BY updated_at DESC LIMIT 100")
@router.get("/approvals")
def approvals():return {"actions":q("SELECT id,venture_id,actor_profile,action_class,amount_sgd,status,reason,requested_at FROM action_authorizations WHERE status='PENDING' ORDER BY requested_at"),"capital":q("SELECT id,venture_id,amount_sgd,purpose,status,created_at FROM capital_requests WHERE status='PENDING' ORDER BY created_at")}
@router.get("/evidence/{venture_id}")
def evidence(venture_id:str):return q("SELECT id,purpose,admissibility,account_identity,actor_identity,counterparty_role,interaction_type,occurred_at,channel,receipt_ref,is_provisional,updated_at FROM evidence_artifacts WHERE venture_id=%s ORDER BY created_at DESC LIMIT 200",(venture_id,))
@router.get("/gates/{venture_id}")
def gates(venture_id:str):return q("SELECT gate,policy_version,result,state,reason,created_at FROM gate_snapshots WHERE venture_id=%s ORDER BY created_at DESC",(venture_id,))
@router.get("/finance/{venture_id}")
def finance(venture_id:str):return {"payments":q("SELECT provider,provider_payment_id,currency,amount,status,occurred_at,environment FROM payments WHERE venture_id=%s ORDER BY occurred_at DESC LIMIT 100",(venture_id,)),"snapshots":q("SELECT period_start,period_end,snapshot,closed_at FROM financial_snapshots WHERE venture_id=%s ORDER BY period_end DESC LIMIT 20",(venture_id,))}
