"""Translate OFF/DATA workflow transitions into durable Hermes Kanban tasks.
Hermes owns scheduling/lifecycle; this module only creates typed successor cards.
"""
from __future__ import annotations
import json, os
from pathlib import Path
from . import db

_PLUGIN=Path(__file__).resolve().parent

def _load_graph():
    p=_PLUGIN/"data"/"workflow.json"
    return json.loads(p.read_text())

def bind_task_context(task_id, *, board=None, venture_id=None, opportunity_id=None, stage, environment, operation_prefix, authority_scope=None, metadata=None):
    with db.tx() as conn:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO kanban_task_contexts(task_id,board,venture_id,opportunity_id,stage,environment,operation_prefix,authority_scope,metadata)
                           VALUES(%s,%s,NULLIF(%s,'')::uuid,NULLIF(%s,'')::uuid,%s,%s,%s,%s::jsonb,%s::jsonb)
                           ON CONFLICT(task_id) DO UPDATE SET board=excluded.board,venture_id=excluded.venture_id,opportunity_id=excluded.opportunity_id,stage=excluded.stage,environment=excluded.environment,authority_scope=excluded.authority_scope,metadata=excluded.metadata,updated_at=now()""",
                        (task_id,board,venture_id or '',opportunity_id or '',stage,environment,operation_prefix,json.dumps(authority_scope or {}),json.dumps(metadata or {})))

def _parse_task_id(result):
    if isinstance(result,dict): obj=result
    else:
        try: obj=json.loads(result)
        except Exception: return None
    for key in ("task_id","id"):
        if obj.get(key): return str(obj[key])
    if isinstance(obj.get("task"),dict) and obj["task"].get("id"): return str(obj["task"]["id"])
    return None

def handle_completed(ctx, *, task_id, board=None, summary=None, **kwargs):
    graph=_load_graph()
    with db.tx() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM kanban_task_contexts WHERE task_id=%s",(task_id,)); tc=cur.fetchone()
    if not tc: return
    metadata=tc.get("metadata") or {}; node_id=metadata.get("workflow_node")
    if not node_id: return
    node=(graph.get("nodes") or {}).get(node_id) or {}
    for edge in node.get("on_success",[]):
        target=(graph.get("nodes") or {}).get(edge) or {}
        if not target: continue
        idem=f"offdata:{tc.get('venture_id') or tc.get('opportunity_id')}:{edge}:{metadata.get('workflow_revision','1')}"
        body={
            "offdata_work_contract_version":"1.0",
            "venture_id":str(tc.get("venture_id") or ""),
            "opportunity_id":str(tc.get("opportunity_id") or ""),
            "stage":edge,
            "objective":target.get("objective",edge),
            "required_output":target.get("output"),
            "acceptance":target.get("acceptance",[]),
            "parent_summary":summary,
            "authority_scope":target.get("authority_scope",{}),
        }
        args={"title":target.get("title",edge),"body":json.dumps(body,indent=2),"assignee":target["profile"],
              "parents":[task_id],"skills":target.get("skills",[]),"idempotency_key":idem,"max_retries":target.get("max_retries",2)}
        if target.get("max_runtime"): args["max_runtime"]=target["max_runtime"]
        result=ctx.dispatch_tool("kanban_create",args)
        new_id=_parse_task_id(result)
        if new_id:
            bind_task_context(new_id,board=board,venture_id=str(tc.get("venture_id") or ""),opportunity_id=str(tc.get("opportunity_id") or ""),
                              stage=edge,environment=str(tc["environment"]),operation_prefix=idem,authority_scope=target.get("authority_scope",{}),
                              metadata={"workflow_node":edge,"workflow_revision":metadata.get("workflow_revision","1")})

def handle_blocked(ctx, *, task_id, reason=None, **kwargs):
    try:
        ctx.dispatch_tool("kanban_comment",{"task_id":task_id,"comment":f"[OFF/DATA] blocked safely: {reason or 'unspecified'}"})
    except Exception:
        pass
