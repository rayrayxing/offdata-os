"""Model-facing Hermes tool schemas for OFF/DATA VENTURE."""

def _schema(name, description, properties, required=()):
    return {
        "name": name,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": list(required),
            "additionalProperties": False,
        },
    }

S = {}
def add(name, description, properties, required=()):
    S[name] = _schema(name, description, properties, required)

ID = {"type":"string","minLength":1}
ENV = {"type":"string","enum":["TEST","SIMULATION","LIVE"]}
OBJ = {"type":"object"}
ARR = {"type":"array","items":{}}
NUM = {"type":"number"}

add("offdata_status","Read OFF/DATA Venture Brain readiness and policy status.",{},())
add("offdata_venture_create","Create an idempotent venture/opportunity container in canonical Venture Brain.",{
    "operation_id":ID,"correlation_id":ID,"portfolio_id":ID,"slug":ID,"name":ID,"environment":ENV,"stage":{"type":"string"},"payload":OBJ
},("operation_id","correlation_id","portfolio_id","slug","name","environment"))
add("offdata_venture_get","Read canonical venture state. Profile memory is not authoritative.",{"venture_id":ID},("venture_id",))
add("offdata_research_mission_create","Create a versioned research mission with budget, freshness and contrary-source requirements.",{
    "operation_id":ID,"correlation_id":ID,"venture_id":ID,"objective":ID,"questions":{"type":"array","items":{"type":"string"}},"freshness_days":{"type":"integer","minimum":0},"max_cost_sgd":NUM,"min_source_diversity":{"type":"integer","minimum":1},"require_contrary":{"type":"boolean"}
},("operation_id","correlation_id","venture_id","objective","questions"))
add("offdata_research_record","Record a real research artifact/receipt against a research mission.",{
    "operation_id":ID,"correlation_id":ID,"venture_id":ID,"mission_id":ID,"source_url":{"type":"string"},"source_type":ID,"provider":ID,"occurred_at":{"type":"string"},"retrieved_at":ID,"raw_ref":{"type":"string"},"content_hash":ID,"role":{"type":"string","enum":["SUPPORTING","CONTRARY","NEUTRAL"]},"claims":{"type":"array","items":{"type":"string"}},"receipt":OBJ,"environment":ENV
},("operation_id","correlation_id","venture_id","mission_id","source_type","provider","retrieved_at","content_hash","role","environment"))
add("offdata_claim_record","Record OBSERVED/INFERRED/HYPOTHESIS claim with evidence references.",{
    "operation_id":ID,"correlation_id":ID,"venture_id":ID,"statement":ID,"claim_class":{"type":"string","enum":["OBSERVED","INFERRED","HYPOTHESIS"]},"supporting_refs":{"type":"array","items":{"type":"string"}},"contrary_refs":{"type":"array","items":{"type":"string"}},"confidence":{"type":"number","minimum":0,"maximum":1},"disclosure_policy":OBJ
},("operation_id","correlation_id","venture_id","statement","claim_class"))
add("offdata_evidence_record","Record evidence. Direct-buyer evidence must never infer missing attribution.",{
    "operation_id":ID,"correlation_id":ID,"venture_id":ID,"purpose":{"type":"string","enum":["MARKET_RESEARCH","BEHAVIORAL_VALIDATION","DIRECT_BUYER","FINANCIAL","OPERATING"]},"account_identity":{"type":"string"},"actor_identity":{"type":"string"},"counterparty_role":{"type":"string"},"interaction_type":{"type":"string"},"occurred_at":{"type":"string"},"channel":{"type":"string"},"receipt_ref":{"type":"string"},"source_ref":{"type":"string"},"content_hash":ID,"environment":ENV,"is_provisional":{"type":"boolean"},"payload":OBJ
},("operation_id","correlation_id","venture_id","purpose","content_hash","environment"))
add("offdata_evidence_validate","Deterministically validate evidence admissibility for its intended purpose.",{"evidence_id":ID},("evidence_id",))
add("offdata_concern_record","Record and classify a concern without treating every uncertainty as blocking.",{
    "operation_id":ID,"correlation_id":ID,"venture_id":ID,"description":ID,"severity":{"type":"string","enum":["BLOCKING","MATERIAL_EXPERIMENT","DESIGN_CONSTRAINT","MONITOR"]},"confidence":{"type":"number","minimum":0,"maximum":1},"source_refs":{"type":"array","items":{"type":"string"}},"mitigation":{"type":"string"}
},("operation_id","correlation_id","venture_id","description","severity"))
add("offdata_experiment_create","Create a typed, budgeted ExperimentContract around a principal uncertainty.",{
    "operation_id":ID,"correlation_id":ID,"venture_id":ID,"concept_revision":{"type":"integer","minimum":1},"principal_uncertainty":ID,"hypothesis":ID,"experiment_type":ID,"target":ID,"method":ID,"success_signal":ID,"failure_signal":ID,"stopping_rule":ID,"budget_sgd":{"type":"number","minimum":0},"deadline":{"type":"string"},"evidence_requirement":OBJ,"analysis_method":OBJ
},("operation_id","correlation_id","venture_id","principal_uncertainty","hypothesis","experiment_type","target","method","success_signal","failure_signal","stopping_rule","budget_sgd"))
add("offdata_prototype_record","Record an immutable prototype revision bound to its experiment.",{
    "operation_id":ID,"correlation_id":ID,"venture_id":ID,"experiment_id":ID,"artifact_ref":ID,"artifact_hash":ID,"is_simulation":{"type":"boolean"},"critical_workflow":ID,"isolation_verified":{"type":"boolean"},"limitations":{"type":"array","items":{"type":"string"}}
},("operation_id","correlation_id","venture_id","experiment_id","artifact_ref","artifact_hash","is_simulation","critical_workflow","isolation_verified"))
add("offdata_validation_record","Record a validation package or real interaction outcome with provenance.",{
    "operation_id":ID,"correlation_id":ID,"venture_id":ID,"kind":{"type":"string","enum":["PACKAGE","OBSERVATION"]},"payload":OBJ
},("operation_id","correlation_id","venture_id","kind","payload"))
add("offdata_gate_evaluate","Deterministically evaluate a compiled, activated G0-G10 gate policy and create an immutable snapshot.",{
    "operation_id":ID,"correlation_id":ID,"venture_id":ID,"gate":{"type":"string","pattern":"^G(?:10|[0-9])$"},"policy_version":ID
},("operation_id","correlation_id","venture_id","gate","policy_version"))
add("offdata_action_request","Create a pending scoped action authorization, normally requiring owner approval for consequential actions.",{
    "operation_id":ID,"correlation_id":ID,"venture_id":ID,"action_class":ID,"tool_scope":{"type":"array","items":{"type":"string"}},"target_scope":OBJ,"environment":ENV,"amount_sgd":{"type":"number","minimum":0},"reason":ID,"expires_at":{"type":"string"}
},("operation_id","correlation_id","venture_id","action_class","tool_scope","target_scope","environment","amount_sgd","reason"))
add("offdata_action_resolve","Owner/control-profile resolution of a pending action authorization.",{
    "operation_id":ID,"correlation_id":ID,"authorization_id":ID,"decision":{"type":"string","enum":["APPROVED","DENIED","REVOKED"]},"resolver_identity":ID,"note":{"type":"string"}
},("operation_id","correlation_id","authorization_id","decision","resolver_identity"))
add("offdata_capital_request","Request bounded venture capital for a declared purpose.",{
    "operation_id":ID,"correlation_id":ID,"venture_id":ID,"purpose":ID,"amount_sgd":{"type":"number","exclusiveMinimum":0},"expected_value":OBJ,"gate_snapshot_id":{"type":"string"},"expires_at":{"type":"string"}
},("operation_id","correlation_id","venture_id","purpose","amount_sgd"))
add("offdata_capital_authorize","Authorize or deny a capital request under owner policy.",{
    "operation_id":ID,"correlation_id":ID,"request_id":ID,"decision":{"type":"string","enum":["APPROVED","DENIED"]},"authorized_amount_sgd":{"type":"number","minimum":0},"resolver_identity":ID
},("operation_id","correlation_id","request_id","decision","resolver_identity"))
add("offdata_financial_post","Post a balanced double-entry journal entry. Debits must equal credits.",{
    "operation_id":ID,"correlation_id":ID,"venture_id":ID,"entry_date":ID,"currency":{"type":"string","default":"SGD"},"description":ID,"lines":{"type":"array","minItems":2,"items":{"type":"object","properties":{"account":ID,"debit":{"type":"number","minimum":0},"credit":{"type":"number","minimum":0},"memo":{"type":"string"}},"required":["account","debit","credit"],"additionalProperties":False}},"source_receipt_ref":{"type":"string"},"environment":ENV
},("operation_id","correlation_id","venture_id","entry_date","currency","description","lines","environment"))
add("offdata_financial_snapshot_close","Close a financial period into an immutable snapshot.",{
    "operation_id":ID,"correlation_id":ID,"venture_id":ID,"period_start":ID,"period_end":ID
},("operation_id","correlation_id","venture_id","period_start","period_end"))
add("offdata_contact_upsert","Create/update canonical prospect/customer relationship state and opt-out controls.",{
    "operation_id":ID,"correlation_id":ID,"venture_id":ID,"account_identity":{"type":"string"},"person_identity":{"type":"string"},"email":{"type":"string"},"opt_out":{"type":"boolean"},"metadata":OBJ
},("operation_id","correlation_id","venture_id"))
add("offdata_interaction_record","Record a real external interaction/receipt; may later support an EvidenceArtifact.",{
    "operation_id":ID,"correlation_id":ID,"venture_id":ID,"contact_id":{"type":"string"},"interaction_type":ID,"channel":ID,"occurred_at":ID,"receipt_ref":{"type":"string"},"summary":{"type":"string"},"raw_ref":{"type":"string"},"environment":ENV
},("operation_id","correlation_id","venture_id","interaction_type","channel","occurred_at","environment"))
add("offdata_capability_upsert","Record a tested Hermes/tool/Skill/model/integration capability in the shared capability catalogue.",{
    "operation_id":ID,"correlation_id":ID,"capability_key":ID,"kind":ID,"provider":ID,"version":{"type":"string"},"profiles":{"type":"array","items":{"type":"string"}},"status":{"type":"string","enum":["AVAILABLE","DEGRADED","MISSING","UNTESTED"]},"details":OBJ
},("operation_id","correlation_id","capability_key","kind","provider","status"))
add("offdata_capability_list","Read the current shared Capability Catalogue.",{"status":{"type":"string"}},())
add("offdata_learning_record","Record FACT/PRIOR/PROCEDURE/POLICY_PROPOSAL learning candidate; protected policy cannot auto-activate.",{
    "operation_id":ID,"correlation_id":ID,"venture_id":{"type":"string"},"learning_type":{"type":"string","enum":["FACT","PRIOR","PROCEDURE","POLICY_PROPOSAL"]},"content":OBJ,"evidence_refs":{"type":"array","items":{"type":"string"}}
},("operation_id","correlation_id","learning_type","content"))
add("offdata_aar_record","Store a factual AAR payload before Telegram delivery.",{
    "operation_id":ID,"correlation_id":ID,"venture_id":{"type":"string"},"aar_type":ID,"payload":OBJ
},("operation_id","correlation_id","aar_type","payload"))

globals().update({k.upper(): v for k,v in S.items()})
