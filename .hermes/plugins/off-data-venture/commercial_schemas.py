"""Additional model-facing schemas for commercial operations and recursive learning."""
from .schemas import _schema, ID, ENV, OBJ
S={}
def add(n,d,p,r=()): S[n]=_schema(n,d,p,r)
add("offdata_offer_create","Create a truthful commercial offer within owner discount/term policy.",{
 "operation_id":ID,"correlation_id":ID,"venture_id":ID,"contact_id":{"type":"string"},"offer_type":ID,"currency":{"type":"string","default":"SGD"},"list_price":{"type":"number","minimum":0},"offered_price":{"type":"number","minimum":0},"terms":OBJ,"expires_at":{"type":"string"}
},("operation_id","correlation_id","venture_id","offer_type","currency","list_price","offered_price"))
add("offdata_commitment_record","Record a real LOI/preorder/paid-pilot/order/subscription commitment with evidence.",{
 "operation_id":ID,"correlation_id":ID,"venture_id":ID,"contact_id":{"type":"string"},"offer_id":{"type":"string"},"commitment_type":ID,"amount_sgd":{"type":"number","minimum":0},"evidence_ref":ID,"status":ID,"occurred_at":ID
},("operation_id","correlation_id","venture_id","commitment_type","evidence_ref","status","occurred_at"))
add("offdata_delivery_obligation_record","Record a customer obligation created by a commercial commitment.",{
 "operation_id":ID,"correlation_id":ID,"venture_id":ID,"commitment_id":{"type":"string"},"obligation":ID,"due_at":{"type":"string"}
},("operation_id","correlation_id","venture_id","obligation"))
add("offdata_delivery_obligation_update","Update delivery status/receipt for an existing obligation.",{
 "operation_id":ID,"correlation_id":ID,"venture_id":ID,"obligation_id":ID,"status":{"type":"string","enum":["OPEN","IN_PROGRESS","DELIVERED","ACCEPTED","CANCELLED","BREACHED"]},"delivery_receipt_ref":{"type":"string"}
},("operation_id","correlation_id","venture_id","obligation_id","status"))
add("offdata_invoice_record","Record an invoice created by an approved provider integration.",{
 "operation_id":ID,"correlation_id":ID,"venture_id":ID,"contact_id":{"type":"string"},"provider":ID,"provider_invoice_id":ID,"currency":ID,"amount":{"type":"number","exclusiveMinimum":0},"status":ID,"due_at":{"type":"string"},"receipt_ref":{"type":"string"}
},("operation_id","correlation_id","venture_id","provider","provider_invoice_id","currency","amount","status"))
add("offdata_payment_record","Record/reconcile a provider payment. TEST/SIM cannot become LIVE revenue.",{
 "operation_id":ID,"correlation_id":ID,"venture_id":ID,"invoice_id":{"type":"string"},"provider":ID,"provider_payment_id":ID,"currency":ID,"amount":{"type":"number","exclusiveMinimum":0},"status":ID,"receipt_ref":ID,"occurred_at":ID,"environment":ENV
},("operation_id","correlation_id","venture_id","provider","provider_payment_id","currency","amount","status","receipt_ref","occurred_at","environment"))
add("offdata_refund_record","Record an owner-authorized refund after provider effect.",{
 "operation_id":ID,"correlation_id":ID,"venture_id":ID,"payment_id":ID,"provider_refund_id":ID,"amount":{"type":"number","exclusiveMinimum":0},"status":ID,"receipt_ref":ID
},("operation_id","correlation_id","venture_id","payment_id","provider_refund_id","amount","status","receipt_ref"))
add("offdata_forecast_record","Record a probabilistic forecast for later calibration.",{
 "operation_id":ID,"correlation_id":ID,"venture_id":{"type":"string"},"decision_id":{"type":"string"},"outcome_definition":ID,"probability":{"type":"number","minimum":0,"maximum":1},"resolve_after":{"type":"string"},"model_provider":{"type":"string"},"model_name":{"type":"string"}
},("operation_id","correlation_id","outcome_definition","probability"))
add("offdata_forecast_resolve","Resolve an observable forecast and calculate Brier score.",{
 "operation_id":ID,"correlation_id":ID,"forecast_id":ID,"realized":{"type":"boolean"}
},("operation_id","correlation_id","forecast_id","realized"))
add("offdata_owner_policy_apply","Apply a versioned owner-policy JSON prepared locally during setup.",{
 "operation_id":ID,"correlation_id":ID,"portfolio_id":ID,"policy_version":ID,"policy":OBJ,"base_currency":{"type":"string","default":"SGD"},"resolver_identity":ID
},("operation_id","correlation_id","portfolio_id","policy_version","policy","base_currency","resolver_identity"))
