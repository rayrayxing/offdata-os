"""OFF/DATA VENTURE Hermes-native registration."""
from __future__ import annotations
import json, os, uuid
from pathlib import Path
from . import schemas, tools, commercial_schemas, commercial, db, policy, orchestrator_v2

CORE_TOOL_NAMES=list(schemas.S.keys())
COMMERCIAL_TOOL_NAMES=list(commercial_schemas.S.keys())

def _bound(fn, profile_name):
    def handler(args, **kwargs):
        kwargs.setdefault("actor_profile",profile_name)
        return fn(args,**kwargs)
    return handler

def _guard(ctx):
    def pre_tool_call(tool_name, args, task_id, **kwargs):
        if tool_name.startswith("offdata_"): return None
        try:
            with db.tx() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT action_class,effect_class,metadata FROM tool_policies WHERE tool_name=%s AND enabled=true",(tool_name,)); tp=cur.fetchone()
                    if not tp or tp["effect_class"]=="READ": return None
                    cur.execute("SELECT * FROM kanban_task_contexts WHERE task_id=%s",(task_id,)); tc=cur.fetchone()
                    if not tc: return {"action":"block","message":f"OFF/DATA guard: {tool_name} is consequential but this task has no bound venture context."}
                    amount_field=((tp.get("metadata") or {}).get("amount_field") or "amount_sgd")
                    amount=float((args or {}).get(amount_field) or 0)
                    ok,reason,auth_id=policy.action_policy_check(conn,profile=ctx.profile_name,venture_id=str(tc["venture_id"]),tool_name=tool_name,environment=str(tc["environment"]),amount_sgd=amount,target=args)
                    if not ok: return {"action":"block","message":f"OFF/DATA guard blocked {tool_name}: {reason}. Request/resolve explicit authorization first."}
                    return None
        except Exception as exc:
            try: guarded=json.loads(os.getenv("OFFDATA_GUARDED_TOOLS_JSON","{}"))
            except Exception: guarded={}
            if tool_name in guarded: return {"action":"block","message":f"OFF/DATA guard unavailable; fail closed for consequential tool {tool_name}: {exc}"}
            return None
    return pre_tool_call

def _receipt_hook(ctx):
    def post_tool_call(tool_name, args, result, task_id, duration_ms=0, **kwargs):
        if tool_name.startswith("offdata_"): return
        try:
            with db.tx() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT action_class,effect_class FROM tool_policies WHERE tool_name=%s AND enabled=true",(tool_name,)); tp=cur.fetchone()
                    if not tp or tp["effect_class"]=="READ": return
                    cur.execute("SELECT * FROM kanban_task_contexts WHERE task_id=%s",(task_id,)); tc=cur.fetchone()
                    if not tc: return
                    req_hash=db.stable_hash(args or {}); resp_hash=db.stable_hash(result or "")
                    op=f"{tc['operation_prefix']}:{tool_name}:{req_hash[:12]}"
                    cur.execute("""INSERT INTO action_receipts(id,venture_id,operation_id,tool_name,action_class,request_hash,response_hash,status,latency_ms,environment,task_id)
                                   VALUES(gen_random_uuid(),%s,%s,%s,%s,%s,%s,'COMPLETED',%s,%s,%s)
                                   ON CONFLICT(operation_id,tool_name,request_hash) DO NOTHING""",
                                (tc["venture_id"],op,tool_name,tp["action_class"],req_hash,resp_hash,int(duration_ms or 0),tc["environment"],task_id))
        except Exception:
            return
    return post_tool_call

def _offdata_command(ctx):
    def handle(raw):
        parts=(raw or "").strip().split()
        if not parts or parts[0]=="status": return ctx.dispatch_tool("offdata_status",{})
        if parts[0] in ("approve","deny","revoke") and len(parts)>=2:
            decision={"approve":"APPROVED","deny":"DENIED","revoke":"REVOKED"}[parts[0]]
            return ctx.dispatch_tool("offdata_action_resolve",{
                "operation_id":f"telegram:{decision.lower()}:{parts[1]}:{uuid.uuid4()}","correlation_id":f"telegram:{parts[1]}",
                "authorization_id":parts[1],"decision":decision,"resolver_identity":"telegram-owner","note":"Owner command through authenticated Hermes gateway"})
        if parts[0]=="capital-approve" and len(parts)>=3:
            return ctx.dispatch_tool("offdata_capital_authorize",{
                "operation_id":f"telegram:capital:{parts[1]}:{uuid.uuid4()}","correlation_id":f"telegram:capital:{parts[1]}",
                "request_id":parts[1],"decision":"APPROVED","authorized_amount_sgd":float(parts[2]),"resolver_identity":"telegram-owner"})
        if parts[0]=="capital-deny" and len(parts)>=2:
            return ctx.dispatch_tool("offdata_capital_authorize",{
                "operation_id":f"telegram:capital-deny:{parts[1]}:{uuid.uuid4()}","correlation_id":f"telegram:capital:{parts[1]}",
                "request_id":parts[1],"decision":"DENIED","authorized_amount_sgd":0,"resolver_identity":"telegram-owner"})
        return "Usage: /offdata status | approve <authorization_id> | deny <authorization_id> | revoke <authorization_id> | capital-approve <request_id> <SGD> | capital-deny <request_id>"
    return handle

def register(ctx):
    for name in CORE_TOOL_NAMES:
        ctx.register_tool(name=name,toolset="offdata_venture",schema=schemas.S[name],handler=_bound(getattr(tools,name),ctx.profile_name))
    for name in COMMERCIAL_TOOL_NAMES:
        ctx.register_tool(name=name,toolset="offdata_commercial",schema=commercial_schemas.S[name],handler=_bound(getattr(commercial,name),ctx.profile_name))
    ctx.register_hook("pre_tool_call",_guard(ctx))
    ctx.register_hook("post_tool_call",_receipt_hook(ctx))
    ctx.register_hook("kanban_task_completed",lambda **kw: orchestrator_v2.on_completed(ctx,**kw))
    ctx.register_hook("kanban_task_blocked",lambda **kw: orchestrator_v2.on_blocked(ctx,**kw))
    ctx.register_command("offdata",handler=_offdata_command(ctx),description="OFF/DATA status and owner approvals",args_hint="status|approve|deny|revoke|capital-approve|capital-deny")
    skills_dir=Path(__file__).parent/"skills"
    if skills_dir.exists():
        for child in sorted(skills_dir.iterdir()):
            if child.is_dir() and (child/"SKILL.md").exists(): ctx.register_skill(child.name,child/"SKILL.md")
