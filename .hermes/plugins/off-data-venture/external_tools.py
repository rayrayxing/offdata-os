"""Guarded outbound email and Stripe adapters. All provider effects are idempotency-reserved and audited."""
from __future__ import annotations
import os,json,base64,smtplib,urllib.parse,urllib.request
from email.message import EmailMessage
from decimal import Decimal
from . import db,policy
D=lambda x:Decimal(str(x or 0))
def _reserve(conn,args,actor,provider,effect,env):
    prior=db.begin_operation(conn,args["operation_id"],args["correlation_id"],actor,effect,args,env)
    if prior is not None:return prior
    h=db.stable_hash(args)
    with conn.cursor() as cur:
        cur.execute("SELECT state,provider_id,response_json FROM external_effects WHERE operation_id=%s FOR UPDATE",(args["operation_id"],)); row=cur.fetchone()
        if row:
            if row["state"]=="COMPLETED":return row["response_json"]
            raise ValueError("EXTERNAL_EFFECT_ALREADY_RESERVED_RECONCILE_BEFORE_RETRY")
        cur.execute("INSERT INTO external_effects(operation_id,venture_id,provider,effect_type,request_hash,state) VALUES(%s,%s,%s,%s,%s,'RESERVED')",
                    (args["operation_id"],args.get("venture_id"),provider,effect,h))
    return None
def _finish(args,actor,provider_id,result,env):
    with db.tx() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE external_effects SET state='COMPLETED',provider_id=%s,response_json=%s::jsonb,updated_at=now() WHERE operation_id=%s",(provider_id,json.dumps(result),args["operation_id"]))
        db.audit(conn,venture_id=args.get("venture_id"),operation_id=args["operation_id"],correlation_id=args["correlation_id"],actor_profile=actor,action="external_effect_completed",environment=env,after_fingerprint=db.stable_hash(result),metadata={"provider_id":provider_id})
        db.complete_operation(conn,args["operation_id"],result)
def _unknown(args,error):
    try:
        with db.tx() as conn:
            with conn.cursor() as cur: cur.execute("UPDATE external_effects SET state='UNKNOWN',error=%s,updated_at=now() WHERE operation_id=%s",(str(error)[:2000],args["operation_id"]))
    finally: db.fail_operation(args["operation_id"],str(error))
def _require(conn,actor,args,tool,amount=0):
    ok,reason,auth=policy.action_policy_check(conn,profile=actor,venture_id=args["venture_id"],tool_name=tool,environment=args["environment"],amount_sgd=float(amount),target=args)
    if not ok: raise ValueError(reason)
    return auth
def _contact_guard(conn,venture_id,contact_id):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM contacts WHERE id=%s AND venture_id=%s FOR UPDATE",(contact_id,venture_id)); c=cur.fetchone()
    if not c: raise ValueError("CONTACT_NOT_FOUND")
    if c["opt_out"]: raise ValueError("CONTACT_OPTED_OUT")
    if c.get("bounce_state") in ("HARD_BOUNCE","SUPPRESSED"): raise ValueError("CONTACT_BOUNCED")
    if c.get("complaint_state") in ("COMPLAINT","SUPPRESSED"): raise ValueError("CONTACT_COMPLAINT")
    if c.get("next_allowed_contact_at"):
        with conn.cursor() as cur:
            cur.execute("SELECT now() < %s blocked",(c["next_allowed_contact_at"],));
            if cur.fetchone()["blocked"]: raise ValueError("CONTACT_FREQUENCY_GUARD")
    if not c.get("email"): raise ValueError("CONTACT_EMAIL_MISSING")
    return c
def _gmail_token():
    data=urllib.parse.urlencode({"client_id":os.environ["GOOGLE_WORKSPACE_CLIENT_ID"],"client_secret":os.environ["GOOGLE_WORKSPACE_CLIENT_SECRET"],"refresh_token":os.environ["GOOGLE_WORKSPACE_REFRESH_TOKEN"],"grant_type":"refresh_token"}).encode()
    with urllib.request.urlopen(urllib.request.Request("https://oauth2.googleapis.com/token",data=data),timeout=30) as r:return json.loads(r.read())["access_token"]
def _send_email(to,subject,text,html=None):
    sender=os.getenv("OFFDATA_EMAIL_ADDRESS") or os.getenv("EMAIL_ADDRESS")
    if not sender: raise ValueError("OFFDATA_EMAIL_ADDRESS_MISSING")
    m=EmailMessage();m["From"]=sender;m["To"]=to;m["Subject"]=subject;m.set_content(text)
    if html:m.add_alternative(html,subtype="html")
    if os.getenv("GOOGLE_WORKSPACE_REFRESH_TOKEN"):
        raw=base64.urlsafe_b64encode(m.as_bytes()).decode().rstrip("=")
        req=urllib.request.Request("https://gmail.googleapis.com/gmail/v1/users/me/messages/send",data=json.dumps({"raw":raw}).encode(),headers={"Authorization":"Bearer "+_gmail_token(),"Content-Type":"application/json"},method="POST")
        with urllib.request.urlopen(req,timeout=45) as r:return json.loads(r.read())
    pw=os.getenv("OFFDATA_EMAIL_APP_PASSWORD") or os.getenv("EMAIL_PASSWORD")
    if not pw: raise ValueError("EMAIL_TRANSPORT_NOT_CONFIGURED")
    with smtplib.SMTP_SSL(os.getenv("EMAIL_SMTP_HOST","smtp.gmail.com"),int(os.getenv("EMAIL_SMTP_PORT","465")),timeout=45) as s:
        s.login(sender,pw); s.send_message(m)
    return {"id":m.get("Message-ID") or db.stable_hash({"to":to,"subject":subject,"body":text})[:24],"transport":"smtp"}
def _stripe(method,path,data=None,idem=None):
    key=os.getenv("STRIPE_SECRET_KEY");
    if not key: raise ValueError("STRIPE_SECRET_KEY_MISSING")
    headers={"Authorization":"Bearer "+key}
    body=None
    if data is not None: body=urllib.parse.urlencode(data,doseq=True).encode(); headers["Content-Type"]="application/x-www-form-urlencoded"
    if idem: headers["Idempotency-Key"]=idem
    req=urllib.request.Request("https://api.stripe.com/v1"+path,data=body,headers=headers,method=method)
    with urllib.request.urlopen(req,timeout=45) as r:return json.loads(r.read())
@db.json_result
def offdata_email_send(args,actor_profile="unknown-profile",**kwargs):
    env=args["environment"]
    with db.tx() as conn:
        prior=_reserve(conn,args,actor_profile,"google-workspace","email_send",env)
        if prior is not None:return prior
        _require(conn,actor_profile,args,"offdata_email_send"); c=_contact_guard(conn,args["venture_id"],args["contact_id"]); to=c["email"]
    try:
        resp=_send_email(to,args["subject"],args["body_text"],args.get("body_html")); pid=str(resp.get("id") or resp.get("threadId") or "unknown")
        result={"ok":True,"type":"EmailSendReceipt","provider":"google-workspace","provider_message_id":pid,"contact_id":args["contact_id"],"receipt_ref":"gmail:"+pid}
        with db.tx() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO interactions(id,venture_id,contact_id,interaction_type,channel,occurred_at,receipt_ref,summary,environment,operation_id) VALUES(gen_random_uuid(),%s,%s,'OUTBOUND_EMAIL','email',now(),%s,%s,%s,%s)",
                            (args["venture_id"],args["contact_id"],result["receipt_ref"],args["subject"],env,args["operation_id"]))
                cur.execute("UPDATE contacts SET last_contact_at=now(),next_allowed_contact_at=now()+interval '48 hours',updated_at=now() WHERE id=%s",(args["contact_id"],))
        _finish(args,actor_profile,pid,result,env); return result
    except Exception as e:_unknown(args,e); raise
@db.json_result
def offdata_stripe_checkout_create(args,actor_profile="unknown-profile",**kwargs):
    env=args["environment"]
    with db.tx() as conn:
        prior=_reserve(conn,args,actor_profile,"stripe","checkout_create",env)
        if prior is not None:return prior
        _require(conn,actor_profile,args,"offdata_stripe_checkout_create",args["amount_sgd"]); c=_contact_guard(conn,args["venture_id"],args["contact_id"])
    try:
        cents=int((D(args["amount_sgd"])*100).quantize(Decimal("1")))
        data={"mode":"payment","customer_email":c["email"],"success_url":args["success_url"],"cancel_url":args["cancel_url"],"line_items[0][quantity]":"1","line_items[0][price_data][currency]":"sgd","line_items[0][price_data][unit_amount]":str(cents),"line_items[0][price_data][product_data][name]":args["description"],"metadata[offdata_venture_id]":args["venture_id"],"metadata[offdata_offer_id]":args["offer_id"],"metadata[offdata_operation_id]":args["operation_id"]}
        resp=_stripe("POST","/checkout/sessions",data,args["operation_id"]);pid=resp["id"]
        result={"ok":True,"type":"StripeCheckout","checkout_session_id":pid,"url":resp.get("url"),"amount_sgd":float(D(args["amount_sgd"])),"environment":env}
        _finish(args,actor_profile,pid,result,env);return result
    except Exception as e:_unknown(args,e);raise
@db.json_result
def offdata_stripe_invoice_create(args,actor_profile="unknown-profile",**kwargs):
    env=args["environment"]
    with db.tx() as conn:
        prior=_reserve(conn,args,actor_profile,"stripe","invoice_create",env)
        if prior is not None:return prior
        _require(conn,actor_profile,args,"offdata_stripe_invoice_create",args["amount_sgd"]); c=_contact_guard(conn,args["venture_id"],args["contact_id"])
    try:
        base=args["operation_id"]
        customer=_stripe("POST","/customers",{"email":c["email"],"metadata[offdata_venture_id]":args["venture_id"]},base+":customer")
        cents=int((D(args["amount_sgd"])*100).quantize(Decimal("1")))
        _stripe("POST","/invoiceitems",{"customer":customer["id"],"currency":"sgd","amount":str(cents),"description":args["description"]},base+":item")
        invoice=_stripe("POST","/invoices",{"customer":customer["id"],"collection_method":"send_invoice","days_until_due":str(args.get("days_until_due",14)),"metadata[offdata_venture_id]":args["venture_id"],"metadata[offdata_offer_id]":args["offer_id"],"metadata[offdata_operation_id]":base},base+":invoice")
        invoice=_stripe("POST",f"/invoices/{invoice['id']}/finalize",{},base+":finalize")
        result={"ok":True,"type":"StripeInvoice","provider_invoice_id":invoice["id"],"hosted_invoice_url":invoice.get("hosted_invoice_url"),"amount_sgd":float(D(args["amount_sgd"])),"status":invoice.get("status"),"environment":env}
        with db.tx() as conn:
            with conn.cursor() as cur:cur.execute("INSERT INTO invoices(id,venture_id,contact_id,provider,provider_invoice_id,currency,amount,status,due_at,receipt_ref,operation_id) VALUES(gen_random_uuid(),%s,%s,'stripe',%s,'SGD',%s,%s,to_timestamp(%s),%s,%s) ON CONFLICT(provider_invoice_id) DO NOTHING",(args["venture_id"],args["contact_id"],invoice["id"],D(args["amount_sgd"]),invoice.get("status") or "open",invoice.get("due_date") or 0,"stripe:"+invoice["id"],args["operation_id"]))
        _finish(args,actor_profile,invoice["id"],result,env);return result
    except Exception as e:_unknown(args,e);raise
@db.json_result
def offdata_stripe_sync(args,actor_profile="unknown-profile",**kwargs):
    lim=int(args.get("limit",100)); venture=args["venture_id"]; env=args["environment"]; out={"invoices":0,"payments":0}
    inv=_stripe("GET",f"/invoices?limit={lim}")
    pay=_stripe("GET",f"/payment_intents?limit={lim}")
    with db.tx() as conn:
        with conn.cursor() as cur:
            for x in inv.get("data",[]):
                if (x.get("metadata") or {}).get("offdata_venture_id")!=venture:continue
                cur.execute("INSERT INTO invoices(id,venture_id,provider,provider_invoice_id,currency,amount,status,due_at,receipt_ref) VALUES(gen_random_uuid(),%s,'stripe',%s,upper(%s),%s,%s,to_timestamp(%s),%s) ON CONFLICT(provider_invoice_id) DO UPDATE SET status=excluded.status,amount=excluded.amount",(venture,x["id"],x.get("currency","sgd"),D(x.get("amount_due",0))/100,x.get("status","unknown"),x.get("due_date") or 0,"stripe:"+x["id"]));out["invoices"]+=1
            for x in pay.get("data",[]):
                if (x.get("metadata") or {}).get("offdata_venture_id")!=venture:continue
                cur.execute("INSERT INTO payments(id,venture_id,provider,provider_payment_id,currency,amount,status,receipt_ref,occurred_at,environment) VALUES(gen_random_uuid(),%s,'stripe',%s,upper(%s),%s,%s,%s,to_timestamp(%s),%s) ON CONFLICT(provider_payment_id) DO UPDATE SET status=excluded.status,amount=excluded.amount",(venture,x["id"],x.get("currency","sgd"),D(x.get("amount_received",x.get("amount",0)))/100,x.get("status","unknown"),"stripe:"+x["id"],x.get("created") or 0,env));out["payments"]+=1
    return {"ok":True,"type":"StripeSync","venture_id":venture,**out}
