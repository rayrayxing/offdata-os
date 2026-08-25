"""Small transactional PostgreSQL layer for OFF/DATA Venture Brain."""
from __future__ import annotations
import json, os, hashlib
from contextlib import contextmanager

class DBUnavailable(RuntimeError): pass

def _psycopg():
    try:
        import psycopg
        from psycopg.rows import dict_row
        return psycopg, dict_row
    except Exception as exc:
        raise DBUnavailable("psycopg is required. Run scripts/offdata_setup.py prepare-python") from exc

def dsn():
    value=os.getenv("OFFDATA_DATABASE_URL")
    if not value: raise DBUnavailable("OFFDATA_DATABASE_URL is not configured")
    return value

@contextmanager
def tx():
    psycopg, dict_row=_psycopg()
    with psycopg.connect(dsn(), row_factory=dict_row) as conn:
        with conn.transaction():
            yield conn

def one(sql, params=()):
    with tx() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()

def all_rows(sql, params=()):
    with tx() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()

def stable_hash(value)->str:
    raw=json.dumps(value,sort_keys=True,separators=(",",":"),default=str).encode()
    return hashlib.sha256(raw).hexdigest()

def begin_operation(conn, operation_id:str, correlation_id:str, actor_profile:str, action:str, payload:dict, environment:str="TEST"):
    """Claim logical operation id. Returns prior result if this exact operation already completed."""
    fingerprint=stable_hash(payload)
    with conn.cursor() as cur:
        cur.execute("SELECT input_fingerprint,result_json,status FROM od_operations WHERE operation_id=%s FOR UPDATE",(operation_id,))
        row=cur.fetchone()
        if row:
            if row["input_fingerprint"] != fingerprint:
                raise ValueError("IDEMPOTENCY_CONFLICT")
            if row["status"] == "COMPLETED":
                return row["result_json"]
            raise ValueError("OPERATION_IN_PROGRESS_OR_FAILED")
        cur.execute("""INSERT INTO od_operations(operation_id,correlation_id,actor_profile,action,input_fingerprint,environment,status)
                       VALUES(%s,%s,%s,%s,%s,%s,'RUNNING')""",
                    (operation_id,correlation_id,actor_profile,action,fingerprint,environment))
    return None

def complete_operation(conn, operation_id:str, result:dict):
    with conn.cursor() as cur:
        cur.execute("UPDATE od_operations SET status='COMPLETED',result_json=%s::jsonb,completed_at=now() WHERE operation_id=%s",
                    (json.dumps(result,default=str),operation_id))

def fail_operation(operation_id:str, error:str):
    try:
        with tx() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE od_operations SET status='FAILED',error=%s,completed_at=now() WHERE operation_id=%s",(error[:2000],operation_id))
    except Exception:
        pass

def audit(conn, *, venture_id=None, operation_id, correlation_id, actor_profile, action, environment, before_fingerprint=None, after_fingerprint=None, input_refs=None, policy_version=None, metadata=None):
    with conn.cursor() as cur:
        cur.execute("""INSERT INTO audit_events(id,venture_id,operation_id,correlation_id,actor_profile,action,before_fingerprint,after_fingerprint,input_refs,policy_version,environment,metadata)
                       VALUES(gen_random_uuid(),%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s::jsonb)""",
                    (venture_id,operation_id,correlation_id,actor_profile,action,before_fingerprint,after_fingerprint,
                     json.dumps(input_refs or []),policy_version,environment,json.dumps(metadata or {})))

def json_result(fn):
    """Hermes handlers must always return JSON strings and never leak exceptions."""
    def wrapped(args, **kwargs):
        try:
            result=fn(args, **kwargs)
            return json.dumps(result,default=str)
        except Exception as exc:
            operation_id=(args or {}).get("operation_id") if isinstance(args,dict) else None
            if operation_id: fail_operation(operation_id,f"{type(exc).__name__}: {exc}")
            return json.dumps({"ok":False,"error":type(exc).__name__,"message":str(exc)})
    wrapped.__name__=fn.__name__
    return wrapped
