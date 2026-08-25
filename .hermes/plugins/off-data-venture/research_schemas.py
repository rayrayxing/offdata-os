"""Schemas for deterministic research budget/query reservation."""
from .schemas import _schema, ID
S={}
def add(n,d,p,r=()): S[n]=_schema(n,d,p,r)
add("offdata_research_query_reserve","Reserve/dedupe a research query against a mission budget before calling a provider.",{
 "operation_id":ID,"correlation_id":ID,"mission_id":ID,"query":ID,"provider":ID,"estimated_cost_sgd":{"type":"number","minimum":0}
},("operation_id","correlation_id","mission_id","query","provider","estimated_cost_sgd"))
add("offdata_research_query_complete","Finalize a reserved research query with provider receipt, result count and actual cost.",{
 "operation_id":ID,"correlation_id":ID,"query_id":ID,"status":{"type":"string","enum":["COMPLETED","FAILED","EMPTY"]},"actual_cost_sgd":{"type":"number","minimum":0},"result_count":{"type":"integer","minimum":0},"provider_receipt":{"type":"object"},"last_error":{"type":"string"}
},("operation_id","correlation_id","query_id","status","actual_cost_sgd","result_count","provider_receipt"))
