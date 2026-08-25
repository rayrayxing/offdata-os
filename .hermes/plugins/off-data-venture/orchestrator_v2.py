"""Outcome-aware OFF/DATA -> Hermes Kanban bridge."""
from __future__ import annotations
import json
from pathlib import Path
from . import db

_PLUGIN=Path(__file__).resolve().parent

def graph(): return json.loads((_PLUGIN/"data"/"workflow.json").read_text())

def bind_task(task_id, *, board=None, venture_id=None, opportunity_id=None, node_id, environment="TEST", operation_prefix, metadata=None):
    with db.tx() as conn:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO kanban_task_contexts(task_id,board,venture_id,opportunity_id,stage,environment,operation_prefix,metadata)
                           VALUES(%s,%s,NULLIF(%s,'')::uuid,NULLIF(%s,'')::uuid,%s,%s,%s,%s::jsonb)
                           ON CONFLICT(task_id) DO UPDATE SET board=excluded.board,venture_id=excluded.venture_id,opportunity_id=excluded.opportunity_id,stage=excluded.stage,environment=excluded.environment,metadata=excluded.metadata,updated_at=now()""",
                        (task_id,board,venture_id or '',opportunity_id or '',node_id,environment,operation_prefix,json.dumps({"workflow_node":node_id,"workflow_revision":"0.2-final",**(metadata or {})})))

def _json(x):
    if isinstance(x,dict): return x
    try: return json.loads(x)
    except Exception: return {}

def _find_metadata(obj):
    if isinstance(obj,dict):
        if isinstance(obj.get("metadata"),dict) and obj["metadata"].get("offdata_outcome"): return obj["metadata"]
        for key in ("latest_run","run","task"):
            found=_find_metadata(obj.get(key));
            if found: return found
        for key in ("runs","attempts"):
            vals=obj.get(key) or []
            if isinstance(vals,list):
                for item in reversed(vals):
                    found=_find_metadata(item)
                    if found: return found
    return {}

def _task_id(result):
    o=_json(result)
    return o.get("task_id") or o.get("id") or ((o.get("task") or {}).get("id") if isinstance(o.get("task"),dict) else None)

def _create(ctx, tc, parent_task_id, node_id, parent_metadata, board):
    g=graph(); node=g["nodes"][node_id]
    venture=str(tc.get("venture_id") or ""); opportunity=str(tc.get("opportunity_id") or "")
    idem=f"offdata:{venture or opportunity}:{node_id}:{parent_metadata.get('artifact_revision','1')}"
    body={"offdata_work_contract_version":"1.0","venture_id":venture,"opportunity_id":opportunity,"stage":node_id,
          "objective":node["objective"],"required_output":node.get("output"),"acceptance":node.get("acceptance",[]),
          "authority_scope":node.get("authority_scope",{}),"required_completion_metadata":{"offdata_outcome":"one of workflow transitions","artifact_refs":"array","residual_risk":"array"}}
    assignee=node["profile"]
    if assignee=="venture-gm-dynamic": assignee=(tc.get("metadata") or {}).get("venture_gm") or "portfolio-director"
    args={"title":node["title"],"body":json.dumps(body,indent=2),"assignee":assignee,"parents":[parent_task_id],
          "skills":node.get("skills",[]),"idempotency_key":idem,"max_retries":node.get("max_retries",2)}
    result=ctx.dispatch_tool("kanban_create",args); tid=_task_id(result)
    if tid: bind_task(tid,board=board,venture_id=venture,opportunity_id=opportunity,node_id=node_id,environment=str(tc["environment"]),operation_prefix=idem,metadata={"venture_gm":(tc.get("metadata") or {}).get("venture_gm")})
    return tid

def on_completed(ctx, *, task_id, board=None, summary=None, **kwargs):
    with db.tx() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM kanban_task_contexts WHERE task_id=%s",(task_id,)); tc=cur.fetchone()
    if not tc: return
    node_id=(tc.get("metadata") or {}).get("workflow_node") or tc.get("stage"); node=(graph().get("nodes") or {}).get(node_id)
    if not node: return
    handoff={}
    try: handoff=_find_metadata(_json(ctx.dispatch_tool("kanban_show",{})))
    except Exception: handoff={}
    transitions=node.get("transitions") or {}
    outcome=str(handoff.get("offdata_outcome") or "").upper()
    if not outcome and len(transitions)==1: outcome=next(iter(transitions))
    if outcome not in transitions:
        ctx.dispatch_tool("kanban_comment",{"task_id":task_id,"comment":f"[OFF/DATA] No valid offdata_outcome for node {node_id}; expected one of {list(transitions)}. Workflow paused safely."})
        return
    for child in transitions.get(outcome) or []: _create(ctx,tc,task_id,child,handoff,board)

def on_blocked(ctx, *, task_id, reason=None, **kwargs):
    try: ctx.dispatch_tool("kanban_comment",{"task_id":task_id,"comment":f"[OFF/DATA] BLOCKED safely: {reason or 'unspecified'}"})
    except Exception: pass
