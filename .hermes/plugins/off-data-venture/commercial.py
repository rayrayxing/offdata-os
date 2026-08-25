"""Commercial commitments, delivery, provider finance records and calibration."""
from __future__ import annotations
import json
from decimal import Decimal
from . import db
from .tools import _mutate, _actor

D=lambda x: Decimal(str(x or 0))

@db.json_result
def offdata_offer_create(args, **kwargs):
    def fn(conn):
        lp=D(args["list_price"]); op=D(args["offered_price"])
        if op>lp: discount=Decimal("0")
        elif lp>0: discount=(lp-op)/lp*Decimal("100")
        else: discount=Decimal("0")
        with conn.cursor() as cur:
            cur.execute("SELECT owner_policy FROM portfolios p JOIN ventures v ON v.portfolio_id=p.id WHERE v.id=%s",(args["venture_id"],)); row=cur.fetchone(); pol=(row or {}).get("owner_policy") or {}
            maxdisc=D(((pol.get("commercial") or {}).get("max_discount_pct")) or 0)
            if discount>maxdisc: raise ValueError(f"DISCOUNT_EXCEEDS_OWNER_POLICY {discount}>{maxdisc}")
            cur.execute("""INSERT INTO commercial_offers(id,venture_id,contact_id,offer_type,currency,list_price,offered_price,discount_pct,terms,status,expires_at,operation_id)
                           VALUES(gen_random_uuid(),%s,NULLIF(%s,'')::uuid,%s,%s,%s,%s,%s,%s::jsonb,'DRAFT',NULLIF(%s,'')::timestamptz,%s) RETURNING id""",
                        (args["venture_id"],args.get("contact_id",""),args["offer_type"],args["currency"],lp,op,discount,json.dumps(args.get("terms") or {}),args.get("expires_at",""),args["operation_id"]))
            oid=cur.fetchone()["id"]
            owner_required=args["offer_type"].upper() in {"LOI","PILOT"} or bool((args.get("terms") or {}).get("binding"))
            return {"ok":True,"type":"CommercialOffer","offer_id":str(oid),"discount_pct":float(discount),"status":"DRAFT","owner_approval_required_before_binding":owner_required}
    return _mutate(args,kwargs,"offer_create",fn)

@db.json_result
def offdata_commitment_record(args, **kwargs):
    def fn(conn):
        if args["commitment_type"].upper() in {"LOI","PILOT_AGREEMENT","CONTRACT"} and not kwargs.get("owner_authenticated",False):
            raise ValueError("OWNER_APPROVAL_REQUIRED_FOR_BINDING_COMMITMENT")
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO customer_commitments(id,venture_id,contact_id,offer_id,commitment_type,amount_sgd,evidence_ref,status,occurred_at)
                           VALUES(gen_random_uuid(),%s,NULLIF(%s,'')::uuid,NULLIF(%s,'')::uuid,%s,%s,%s,%s,%s::timestamptz) RETURNING id""",
                        (args["venture_id"],args.get("contact_id",""),args.get("offer_id",""),args["commitment_type"],args.get("amount_sgd"),args["evidence_ref"],args["status"],args["occurred_at"]))
            cid=cur.fetchone()["id"]
            return {"ok":True,"type":"CustomerCommitment","commitment_id":str(cid),"status":args["status"]}
    return _mutate(args,kwargs,"commitment_record",fn)

@db.json_result
def offdata_delivery_obligation_record(args, **kwargs):
    def fn(conn):
        with conn.cursor() as cur:
            cur.execute("INSERT INTO delivery_obligations(id,venture_id,commitment_id,obligation,due_at,status) VALUES(gen_random_uuid(),%s,NULLIF(%s,'')::uuid,%s,NULLIF(%s,'')::timestamptz,'OPEN') RETURNING id",
                        (args["venture_id"],args.get("commitment_id",""),args["obligation"],args.get("due_at","")))
            return {"ok":True,"type":"DeliveryObligation","obligation_id":str(cur.fetchone()["id"]),"status":"OPEN"}
    return _mutate(args,kwargs,"delivery_obligation_record",fn)

@db.json_result
def offdata_delivery_obligation_update(args, **kwargs):
    def fn(conn):
        with conn.cursor() as cur:
            cur.execute("SELECT status FROM delivery_obligations WHERE id=%s AND venture_id=%s FOR UPDATE",(args["obligation_id"],args["venture_id"])); old=cur.fetchone()
            if not old: raise ValueError("DELIVERY_OBLIGATION_NOT_FOUND")
            if args["status"] in ("DELIVERED","ACCEPTED") and not args.get("delivery_receipt_ref"): raise ValueError("DELIVERY_RECEIPT_REQUIRED")
            cur.execute("UPDATE delivery_obligations SET status=%s,delivery_receipt_ref=COALESCE(%s,delivery_receipt_ref) WHERE id=%s",(args["status"],args.get("delivery_receipt_ref"),args["obligation_id"]))
            return {"ok":True,"type":"DeliveryObligation","obligation_id":args["obligation_id"],"previous_status":old["status"],"status":args["status"]}
    return _mutate(args,kwargs,"delivery_obligation_update",fn)

@db.json_result
def offdata_invoice_record(args, **kwargs):
    def fn(conn):
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM invoices WHERE provider=%s AND provider_invoice_id=%s LIMIT 1",(args["provider"],args["provider_invoice_id"])); old=cur.fetchone()
            if old: return {"ok":True,"type":"Invoice","invoice_id":str(old["id"]),"deduplicated":True}
            cur.execute("""INSERT INTO invoices(id,venture_id,contact_id,provider,provider_invoice_id,currency,amount,status,due_at,receipt_ref,operation_id)
                           VALUES(gen_random_uuid(),%s,NULLIF(%s,'')::uuid,%s,%s,%s,%s,%s,NULLIF(%s,'')::timestamptz,%s,%s) RETURNING id""",
                        (args["venture_id"],args.get("contact_id",""),args["provider"],args["provider_invoice_id"],args["currency"],args["amount"],args["status"],args.get("due_at",""),args.get("receipt_ref"),args["operation_id"]))
            return {"ok":True,"type":"Invoice","invoice_id":str(cur.fetchone()["id"]),"deduplicated":False}
    return _mutate(args,kwargs,"invoice_record",fn)

@db.json_result
def offdata_payment_record(args, **kwargs):
    def fn(conn):
        with conn.cursor() as cur:
            cur.execute("SELECT id,environment,amount FROM payments WHERE provider=%s AND provider_payment_id=%s",(args["provider"],args["provider_payment_id"])); old=cur.fetchone()
            if old:
                if str(old["environment"])!=args["environment"] or D(old["amount"])!=D(args["amount"]): raise ValueError("PAYMENT_IDEMPOTENCY_CONFLICT")
                return {"ok":True,"type":"Payment","payment_id":str(old["id"]),"deduplicated":True,"authoritative_revenue":str(old["environment"])=="LIVE"}
            cur.execute("""INSERT INTO payments(id,venture_id,invoice_id,provider,provider_payment_id,currency,amount,status,receipt_ref,occurred_at,environment,operation_id)
                           VALUES(gen_random_uuid(),%s,NULLIF(%s,'')::uuid,%s,%s,%s,%s,%s,%s,%s::timestamptz,%s,%s) RETURNING id""",
                        (args["venture_id"],args.get("invoice_id",""),args["provider"],args["provider_payment_id"],args["currency"],args["amount"],args["status"],args["receipt_ref"],args["occurred_at"],args["environment"],args["operation_id"]))
            pid=cur.fetchone()["id"]
            authoritative=args["environment"]=="LIVE" and args["status"].upper() in {"SUCCEEDED","PAID","SETTLED"}
            return {"ok":True,"type":"Payment","payment_id":str(pid),"deduplicated":False,"authoritative_revenue":authoritative}
    return _mutate(args,kwargs,"payment_record",fn,environment=args["environment"])

@db.json_result
def offdata_refund_record(args, **kwargs):
    def fn(conn):
        if not kwargs.get("owner_authenticated",False): raise ValueError("OWNER_APPROVAL_REQUIRED_FOR_REFUND")
        with conn.cursor() as cur:
            cur.execute("SELECT environment,amount FROM payments WHERE id=%s",(args["payment_id"],)); pay=cur.fetchone()
            if not pay: raise ValueError("PAYMENT_NOT_FOUND")
            if D(args["amount"])>D(pay["amount"]): raise ValueError("REFUND_EXCEEDS_PAYMENT")
            cur.execute("SELECT id FROM refunds WHERE provider_refund_id=%s",(args["provider_refund_id"],)); old=cur.fetchone()
            if old: return {"ok":True,"type":"Refund","refund_id":str(old["id"]),"deduplicated":True}
            cur.execute("INSERT INTO refunds(id,venture_id,payment_id,provider_refund_id,amount,status,receipt_ref,operation_id) VALUES(gen_random_uuid(),%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                        (args["venture_id"],args["payment_id"],args["provider_refund_id"],args["amount"],args["status"],args["receipt_ref"],args["operation_id"]))
            return {"ok":True,"type":"Refund","refund_id":str(cur.fetchone()["id"]),"deduplicated":False}
    return _mutate(args,kwargs,"refund_record",fn)

@db.json_result
def offdata_forecast_record(args, **kwargs):
    def fn(conn):
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO forecasts(id,venture_id,decision_id,actor_profile,model_provider,model_name,outcome_definition,probability,resolve_after)
                           VALUES(gen_random_uuid(),NULLIF(%s,'')::uuid,NULLIF(%s,'')::uuid,%s,%s,%s,%s,%s,NULLIF(%s,'')::timestamptz) RETURNING id""",
                        (args.get("venture_id",""),args.get("decision_id",""),_actor(kwargs),args.get("model_provider"),args.get("model_name"),args["outcome_definition"],args["probability"],args.get("resolve_after","")))
            return {"ok":True,"type":"Forecast","forecast_id":str(cur.fetchone()["id"]),"probability":args["probability"]}
    return _mutate(args,kwargs,"forecast_record",fn,environment="TEST")

@db.json_result
def offdata_forecast_resolve(args, **kwargs):
    def fn(conn):
        with conn.cursor() as cur:
            cur.execute("SELECT probability,realized FROM forecasts WHERE id=%s FOR UPDATE",(args["forecast_id"],)); f=cur.fetchone()
            if not f: raise ValueError("FORECAST_NOT_FOUND")
            if f["realized"] is not None: return {"ok":True,"type":"ForecastResolution","forecast_id":args["forecast_id"],"already_resolved":True}
            y=1.0 if args["realized"] else 0.0; p=float(f["probability"]); brier=(p-y)**2
            cur.execute("UPDATE forecasts SET realized=%s,score=%s,resolved_at=now() WHERE id=%s",(args["realized"],brier,args["forecast_id"]))
            return {"ok":True,"type":"ForecastResolution","forecast_id":args["forecast_id"],"realized":args["realized"],"brier_score":brier}
    return _mutate(args,kwargs,"forecast_resolve",fn,environment="TEST")

@db.json_result
def offdata_owner_policy_apply(args, **kwargs):
    def fn(conn):
        if _actor(kwargs)!="offdata-control" and not kwargs.get("owner_authenticated",False): raise ValueError("OWNER_OR_CONTROL_PROFILE_REQUIRED")
        with conn.cursor() as cur:
            cur.execute("UPDATE portfolios SET owner_policy_version=%s,owner_policy=%s::jsonb,base_currency=%s WHERE id=%s",
                        (args["policy_version"],json.dumps(args["policy"]),args["base_currency"],args["portfolio_id"]))
            if cur.rowcount!=1: raise ValueError("PORTFOLIO_NOT_FOUND")
            return {"ok":True,"type":"OwnerPolicy","portfolio_id":args["portfolio_id"],"policy_version":args["policy_version"],"policy_hash":db.stable_hash(args["policy"])}
    return _mutate(args,kwargs,"owner_policy_apply",fn,environment="TEST")
