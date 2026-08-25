"""Schemas for guarded customer communication and Stripe payment rail."""
from .schemas import _schema, ID, ENV
S={}
def add(n,d,p,r=()): S[n]=_schema(n,d,p,r)
add("offdata_email_send","Send one approved customer email through the controlled OFF/DATA mail rail after contact/authority checks.",{
 "operation_id":ID,"correlation_id":ID,"venture_id":ID,"contact_id":ID,"subject":ID,"body_text":ID,"body_html":{"type":"string"},"environment":ENV
},("operation_id","correlation_id","venture_id","contact_id","subject","body_text","environment"))
add("offdata_stripe_checkout_create","Create an idempotent Stripe Checkout session for an approved commercial offer.",{
 "operation_id":ID,"correlation_id":ID,"venture_id":ID,"contact_id":ID,"offer_id":ID,"description":ID,"amount_sgd":{"type":"number","exclusiveMinimum":0},"success_url":ID,"cancel_url":ID,"environment":ENV
},("operation_id","correlation_id","venture_id","contact_id","offer_id","description","amount_sgd","success_url","cancel_url","environment"))
add("offdata_stripe_invoice_create","Create/finalize a Stripe invoice for an approved commercial offer.",{
 "operation_id":ID,"correlation_id":ID,"venture_id":ID,"contact_id":ID,"offer_id":ID,"description":ID,"amount_sgd":{"type":"number","exclusiveMinimum":0},"days_until_due":{"type":"integer","minimum":0,"maximum":90},"environment":ENV
},("operation_id","correlation_id","venture_id","contact_id","offer_id","description","amount_sgd","environment"))
add("offdata_stripe_sync","Reconcile Stripe invoices and payments carrying OFF/DATA venture metadata into Venture Brain.",{
 "venture_id":ID,"environment":ENV,"limit":{"type":"integer","minimum":1,"maximum":100}
},("venture_id","environment"))
