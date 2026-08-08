from __future__ import annotations

import copy
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from codex_phase0_launch_core import CURRENT_STATE_PATH, ROOT, load_json
from pcfa07_backlog_reconciliation import COLUMNS, RECORD, REPORT, TASK_RE, build_records, decode, failures, run_self_test, _mutate

SCHEMA = ROOT / 'schemas/pcfa07-codex-implementation-backlog-reconciliation.schema.json'
BACKLOG = ROOT / 'docs/11-BUILD-BACKLOG.md'
DOC = ROOT / 'docs/74-PCFA-07-CODEX-IMPLEMENTATION-BACKLOG-RECONCILIATION.md'
STATUS = ROOT / 'docs/CURRENT-OPERATIONAL-STATE.md'
HANDOFF = ROOT / 'handoff/codex-phase0-current-handoff.json'
ISSUE1 = ROOT / 'handoff/codex-phase0-current-issue.md'
P4 = ROOT / 'repository/pcfa04-product-scope-implementation-addendum.json'
P5 = ROOT / 'repository/pcfa05-minimum-valuable-consulting-loop.json'
P6 = ROOT / 'repository/pcfa06-hermes-bounded-adoption-refresh.json'
COMPONENTS = ROOT / 'contracts/northstar-integration-blueprint.json'


def req(ok: bool, msg: str) -> None:
    if not ok: raise SystemExit(msg)


def source_sets() -> dict[str, set[str]]:
    p4,p5,p6=load_json(P4),load_json(P5),load_json(P6)
    return {'PCFA-04':{x['id'] for x in p4['requirements']},'PCFA-05-stages':{x['stage_id'] for x in p5['stages']},'PCFA-05-invariants':{x['id'] for x in p5['loop_invariants']},'PCFA-05-negative':{x['case_id'] for x in p5['negative_cases']},'PCFA-05-interrupts':{x['interrupt_id'] for x in p5['founder_interrupts']},'PCFA-06':{x['capability_id'] for x in p6['capability_assessments']}}


def semantic(record: dict[str, Any]) -> list[str]:
    out: list[str]=[]
    def r(ok: bool,msg: str) -> None:
        if not ok: out.append(msg)
    c,p,proj,b=record.get('obligation_counts',{}),record.get('reconciliation_policy',{}),record.get('backlog_projection',{}),record.get('boundaries',{})
    obs=decode(record); tests=[x.get('planned_test_id') for x in obs]
    r(record.get('work_package_id')=='PCFA-07' and record.get('reconciliation_id')=='CODEX-IMPLEMENTATION-BACKLOG-RECONCILIATION','identity drifted')
    r(c=={'pcfa04_requirements':29,'pcfa05_stages':19,'pcfa05_invariants':15,'pcfa05_negative_cases':13,'pcfa05_founder_interrupts':6,'pcfa06_capabilities':11,'total_obligations':93,'planned_tests':93},'counts drifted')
    r(p.get('no_new_imp_phases') is True and p.get('no_new_imp_tasks') is True and p.get('imp_p0_scope_widened') is False and p.get('phase0_obligation_count')==0 and p.get('one_planned_test_per_obligation') is True and p.get('planned_tests_are_not_executed_evidence') is True and p.get('planned_test_registry_is_pcfa07_specific') is True and p.get('blocking_gate_is_latest_bound_task_phase') is True and p.get('dependency_tasks_are_prior_bound_tasks') is True and p.get('all_statuses_remain_planned_not_implemented') is True and p.get('implementation_evidence_available') is False and p.get('pcfa08_final_acceptance_required') is True,'policy drifted')
    r(record.get('derivation_rules')=={'primary_implementation_task':'last task_bindings entry','blocking_phase_gate':'IMP phase of primary_implementation_task','dependency_tasks':'all task_bindings entries before primary','component_bindings':'ordered union of task_component_map entries for task_bindings'},'derivation drifted')
    r(len(obs)==93 and len({x.get('requirement_id') for x in obs})==93 and len(set(tests))==93 and all(x.get('status')=='planned_not_implemented' and x.get('implementation_evidence_status')=='not_available_pre_implementation' and x.get('primary_implementation_task')==x.get('task_bindings',[])[-1] and x.get('dependency_tasks')==x.get('task_bindings',[])[:-1] and x.get('blocking_phase_gate').startswith('IMP-P') and not any(str(t).startswith('P0.') for t in x.get('task_bindings',[])) and x.get('component_bindings') and x.get('evidence_type') and x.get('planned_test_id')==f"PCFA07-TST-{x.get('requirement_id')}" for x in obs),'obligation semantics drifted')
    r(proj=={'existing_imp_phase_count':13,'existing_task_count':53,'new_imp_phase_count':0,'new_task_count':0,'phase0_new_obligation_count':0,'phase0_tasks_unchanged':['P0.1','P0.2','P0.3','P0.4']},'backlog projection drifted')
    r(b.get('founder_accountability_preserved') is True and all(v is False for k,v in b.items() if k!='founder_accountability_preserved'),'boundaries drifted')
    return out


def main() -> None:
    record,state,schema=load_json(RECORD),load_json(CURRENT_STATE_PATH),load_json(SCHEMA)
    Draft202012Validator.check_schema(schema); validator=Draft202012Validator(schema,format_checker=FormatChecker()); errors=list(validator.iter_errors(record))
    req(not errors,'PCFA-07 schema validation failed: '+'; '.join(e.message for e in errors))
    expected,report=build_records(); req(record==expected,'PCFA-07 generated JSON does not match governed sources'); req(REPORT.read_text(encoding='utf-8')==report,'PCFA-07 evidence report drifted')
    req(not semantic(record),'PCFA-07 semantic validation failed: '+'; '.join(semantic(record))); req(not failures(state,record),'PCFA-07 launch binding failed: '+'; '.join(failures(state,record)))
    obs=decode(record); sets=source_sets(); actual={'PCFA-04':{x['requirement_id'] for x in obs if x['source_work_package']=='PCFA-04'},'PCFA-05-stages':{x['requirement_id'] for x in obs if x['obligation_kind']=='pcfa05_stage'},'PCFA-05-invariants':{x['requirement_id'] for x in obs if x['obligation_kind']=='pcfa05_invariant'},'PCFA-05-negative':{x['requirement_id'] for x in obs if x['obligation_kind']=='pcfa05_negative_case'},'PCFA-05-interrupts':{x['requirement_id'] for x in obs if x['obligation_kind']=='pcfa05_founder_interrupt'},'PCFA-06':{x['requirement_id'] for x in obs if x['source_work_package']=='PCFA-06'}}
    req(actual==sets,'PCFA-07 source identity coverage drifted')
    for pred,name in ((load_json(P4),'PCFA-04'),(load_json(P5),'PCFA-05'),(load_json(P6),'PCFA-06')):
        contract=pred.get('pcfa07_reconciliation_contract',{}); req(isinstance(contract,dict) and contract and all(v is True for v in contract.values()),f'{name} PCFA-07 reconciliation contract drifted')
    backlog=BACKLOG.read_text(encoding='utf-8'); task_ids=set(TASK_RE.findall(backlog)); req(len(task_ids)==53,'existing IMP task namespace drifted'); req(not any(t.startswith('P0.') for x in obs for t in x['task_bindings']),'PCFA-07 widened IMP-P0')
    component_ids={x['component_id'] for x in load_json(COMPONENTS)['integration_components']}; req({c for x in obs for c in x['component_bindings']}<=component_ids,'unknown component binding')
    handoff=load_json(HANDOFF); req(handoff['authority'].get('codex_implementation_backlog_reconciliation')=='requirements/pcfa07-codex-implementation-backlog-reconciliation.json' and handoff['readiness'].get('pcfa07_implementation_backlog_reconciled') is True,'current handoff omits PCFA-07')
    req('requirements/pcfa07-codex-implementation-backlog-reconciliation.json' in handoff['read_order'] and 'python scripts/validate_pcfa07_backlog_reconciliation.py' in handoff['execution']['required_commands'],'current handoff read/preflight omits PCFA-07')
    for path,tokens in ((BACKLOG,('PCFA-07 reconciled corrective obligation overlay','93 `planned_not_implemented` obligations','No PCFA-07 obligation is assigned to IMP-P0')),(DOC,('Total reconciled obligations: **93**','Planned PCFA-07 implementation-test identities: **93**','No Phase 0 widening','PCFA-08','codex_start_authorized=false')),(STATUS,('PCFA-07 Codex implementation backlog reconciliation','93','PCFA07-TST-*','PCFA-08')),(ISSUE1,('PCFA-07 Codex implementation backlog reconciliation','93','planned_not_executed','P0.1–P0.4'))):
        text=path.read_text(encoding='utf-8'); [req(token in text,f'{path.relative_to(ROOT)} missing {token}') for token in tokens]
    cases=[('count',('obligation_counts','total_obligations'),92),('phase',('reconciliation_policy','no_new_imp_phases'),False),('p0 policy',('reconciliation_policy','imp_p0_scope_widened'),True),('identity',('obligations','0','requirement_id'),'PS-OTHER-001'),('implemented',('obligations','0','status'),'implemented'),('p0 task',('obligations','0','task_bindings'),['P0.1']),('primary',('obligations','0','primary_implementation_task'),'P1.1'),('deps',('obligations','0','dependency_tasks'),[]),('components',('obligations','0','component_bindings'),[]),('gate',('derivation_rules','blocking_phase_gate'),'arbitrary'),('test',('obligations','0','planned_test_id'),'PCFA07-TST-OTHER'),('evidence',('obligations','0','implementation_evidence_status'),'available'),('duplicate',('obligations','1','planned_test_id'),'PCFA07-TST-PS-MANDATE-001'),('task count',('backlog_projection','new_task_count'),1),('p0 obligation',('backlog_projection','phase0_new_obligation_count'),1),('pcfa08',('reconciliation_policy','pcfa08_final_acceptance_required'),False),('runtime',('boundaries','runtime_activation_authorized'),True),('codex',('boundaries','codex_start_authorized'),True)]
    rejected=0
    for label,path,repl in cases:
        v=copy.deepcopy(record); _mutate(v,path,repl)
        if list(validator.iter_errors(v)) or semantic(v) or failures(state,v): rejected+=1
        else: raise SystemExit(f'PCFA-07 mutation not rejected: {label}')
    launch=run_self_test(state); assignments=len({t for x in obs for t in x['task_bindings']})
    print(f"PCFA-07 Codex implementation backlog reconciliation validation passed: obligations=93, planned_tests=93, task_assignments={assignments}, semantic_mutations_rejected={rejected}, launch_mutations_rejected={launch}, new_imp_phases=0, new_tasks=0, phase0_new_obligations=0, planned_not_implemented=true, pcfa08_required=true, codex_start_authorized=false.")

if __name__=='__main__': main()
