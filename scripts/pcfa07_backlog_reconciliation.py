from __future__ import annotations
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any
import yaml
from codex_phase0_launch_core import CURRENT_STATE_PATH, ROOT, digest_file, load_json
CONFIG = ROOT / 'configs/pcfa07-codex-implementation-backlog-reconciliation.yaml'
RECORD = ROOT / 'requirements/pcfa07-codex-implementation-backlog-reconciliation.json'
REPORT = ROOT / 'reports/pcfa07-codex-implementation-backlog-reconciliation-evidence.md'
COLUMNS = ['requirement_id', 'obligation_kind', 'task_bindings', 'planned_test_id']
TASK_RE = re.compile('^### (P(?:[0-9]|1[0-2])\\.[0-9]+)\\b', re.MULTILINE)


def _yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise ValueError(f'{path} must contain a mapping')
    return value


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise ValueError(f'{path} must contain an object')
    return value


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _task_key(task: str) -> tuple[int, int]:
    p, n = task[1:].split('.', 1)
    return (int(p), int(n))


def _phase(task: str) -> str:
    return f'IMP-P{_task_key(task)[0]}'


def _uniq(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _sources(config: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], Path, Path]:
    a = config['source_authorities']
    return (_json(ROOT / a['product_scope']), _json(ROOT / a['mvcl']), _json(ROOT / a['hermes_bounded_adoption']), ROOT / a['implementation_backlog'], ROOT / a['component_contract'])


def _raw_obligations(config: dict[str, Any], p4: dict[str, Any], p5: dict[str, Any], p6: dict[str, Any]) -> list[tuple[str, str, list[str]]]:
    areas = {rid: area for area in p4['product_areas'] for rid in area['requirement_ids']}
    manual = config['manual_task_bindings']
    rows: list[tuple[str, str, list[str]]] = []
    for item in p4['requirements']:
        rid = item['id']
        kind = 'pcfa04_consulting_craft' if rid.startswith('CQ-') else 'pcfa04_requirement'
        rows.append((rid, kind, list(areas[rid]['integration_points'])))
    rows += [(x['stage_id'], 'pcfa05_stage', list(x['integration_points'])) for x in p5['stages']]
    rows += [(x['id'], 'pcfa05_invariant', list(manual['pcfa05_invariants'][x['id']])) for x in p5['loop_invariants']]
    rows += [(x['case_id'], 'pcfa05_negative_case', list(manual['pcfa05_negative_cases'][x['case_id']])) for x in p5['negative_cases']]
    rows += [(x['interrupt_id'], 'pcfa05_founder_interrupt', list(manual['pcfa05_founder_interrupts'][x['interrupt_id']])) for x in p5['founder_interrupts']]
    rows += [(x['capability_id'], 'pcfa06_capability', list(x['integration_points'])) for x in p6['capability_assessments']]
    return [(rid, kind, sorted(set(tasks), key=_task_key)) for rid, kind, tasks in rows]


def build_records() -> tuple[dict[str, Any], str]:
    c = _yaml(CONFIG)
    if c.get('work_package_id') != 'PCFA-07' or c.get('reconciliation_id') != 'CODEX-IMPLEMENTATION-BACKLOG-RECONCILIATION':
        raise ValueError('PCFA-07 identity drifted')
    p4, p5, p6, backlog, components = _sources(c)
    tasks = sorted(set(TASK_RE.findall(backlog.read_text(encoding='utf-8'))), key=_task_key)
    component_ids = {x['component_id'] for x in _json(components)['integration_components']}
    task_map = c['task_component_map']
    raw = _raw_obligations(c, p4, p5, p6)
    seen: set[str] = set()
    test_ids: set[str] = set()
    logical: list[dict[str, Any]] = []
    for rid, kind, bound in raw:
        if rid in seen or not bound or any((t not in tasks or t.startswith('P0.') for t in bound)):
            raise ValueError(f'invalid obligation binding: {rid}')
        seen.add(rid)
        comps = _uniq([comp for task in bound for comp in task_map[task]])
        if not comps or not set(comps) <= component_ids:
            raise ValueError(f'invalid component binding: {rid}')
        test_id = f'PCFA07-TST-{rid}'
        if test_id in test_ids:
            raise ValueError(f'duplicate planned test: {test_id}')
        test_ids.add(test_id)
        logical.append({'requirement_id': rid, 'obligation_kind': kind, 'task_bindings': bound, 'source_work_package': 'PCFA-04' if kind.startswith('pcfa04_') else 'PCFA-05' if kind.startswith('pcfa05_') else 'PCFA-06', 'primary_implementation_task': bound[-1], 'blocking_phase_gate': _phase(bound[-1]), 'dependency_tasks': bound[:-1], 'component_bindings': comps, 'planned_test_id': test_id, 'evidence_type': c['evidence_type_by_obligation_kind'][kind], 'status': 'planned_not_implemented', 'implementation_evidence_status': 'not_available_pre_implementation'})
    counts = {'pcfa04_requirements': 29, 'pcfa05_stages': 19, 'pcfa05_invariants': 15, 'pcfa05_negative_cases': 13, 'pcfa05_founder_interrupts': 6, 'pcfa06_capabilities': 11, 'total_obligations': 93, 'planned_tests': 93}
    actual = {k: sum((x['source_work_package'] == 'PCFA-04' for x in logical)) if k == 'pcfa04_requirements' else sum((x['obligation_kind'] == {'pcfa05_stages': 'pcfa05_stage', 'pcfa05_invariants': 'pcfa05_invariant', 'pcfa05_negative_cases': 'pcfa05_negative_case', 'pcfa05_founder_interrupts': 'pcfa05_founder_interrupt', 'pcfa06_capabilities': 'pcfa06_capability'}.get(k) for x in logical)) for k in counts if k not in {'total_obligations', 'planned_tests'}}
    actual |= {'total_obligations': len(logical), 'planned_tests': len(test_ids)}
    if actual != counts or counts != c['expected_counts']:
        raise ValueError(f'PCFA-07 count drift: {actual}')
    kind_meta = {kind: {'source_work_package': next((x['source_work_package'] for x in logical if x['obligation_kind'] == kind)), 'evidence_type': c['evidence_type_by_obligation_kind'][kind]} for kind in sorted({x['obligation_kind'] for x in logical})}
    record = {k: v for k, v in c.items() if k not in {'task_component_map', 'manual_task_bindings', 'test_kind_by_obligation_kind', 'evidence_type_by_obligation_kind'}}
    record['generated_from'] = str(CONFIG.relative_to(ROOT))
    record['source_digests'] = {'product_scope_sha256': _digest(ROOT / c['source_authorities']['product_scope']), 'mvcl_sha256': _digest(ROOT / c['source_authorities']['mvcl']), 'hermes_bounded_adoption_sha256': _digest(ROOT / c['source_authorities']['hermes_bounded_adoption']), 'implementation_backlog_sha256': _digest(backlog), 'component_contract_sha256': _digest(components)}
    record['obligation_counts'] = counts
    record['obligation_columns'] = COLUMNS
    record['obligation_defaults'] = {'status': 'planned_not_implemented', 'implementation_evidence_status': 'not_available_pre_implementation'}
    record['kind_metadata'] = kind_meta
    record['derivation_rules'] = {'primary_implementation_task': 'last task_bindings entry', 'blocking_phase_gate': 'IMP phase of primary_implementation_task', 'dependency_tasks': 'all task_bindings entries before primary', 'component_bindings': 'ordered union of task_component_map entries for task_bindings'}
    record['task_component_map'] = task_map
    record['obligations'] = [[x[col] for col in COLUMNS] for x in logical]
    record['backlog_projection'] = {'existing_imp_phase_count': 13, 'existing_task_count': len(tasks), 'new_imp_phase_count': 0, 'new_task_count': 0, 'phase0_new_obligation_count': 0, 'phase0_tasks_unchanged': ['P0.1', 'P0.2', 'P0.3', 'P0.4']}
    by_phase: dict[str, int] = {}
    for x in logical:
        by_phase[x['blocking_phase_gate']] = by_phase.get(x['blocking_phase_gate'], 0) + 1
    report = '\n'.join(['# PCFA-07 Codex implementation backlog reconciliation evidence', '', '<!-- Generated by scripts/build_pcfa07_backlog_reconciliation.py. -->', '', '- Work package: `PCFA-07`', '- Reconciliation: `CODEX-IMPLEMENTATION-BACKLOG-RECONCILIATION`', '- Total reconciled obligations: `93`', '- PCFA-04 requirements: `29`', '- PCFA-05 stages: `19`', '- PCFA-05 invariants: `15`', '- PCFA-05 negative cases: `13`', '- PCFA-05 Founder interrupts: `6`', '- PCFA-06 capabilities: `11`', '- Planned test identities: `93`', '- New IMP phases: `0`', '- New IMP tasks: `0`', '- New IMP-P0 obligations: `0`', '- Every obligation has an exact existing task binding, component binding, blocking phase gate, dependency list, planned test ID and evidence type.', '- Every obligation remains `planned_not_implemented`; planned tests are not execution evidence.', '- PCFA-08 final cross-authority acceptance remains required.', '- `codex_start_authorized=false`; IMP-P1+, runtime activation, merge and external actions remain denied.', '', '## Primary acceptance assignments by phase', ''] + [f'- {phase}: `{by_phase[phase]}` obligations' for phase in sorted(by_phase, key=lambda x: int(x.removeprefix('IMP-P')))] + [''])
    return (record, report)


def decode(value: dict[str, Any]) -> list[dict[str, Any]]:
    if value.get('obligation_columns') != COLUMNS or not isinstance(value.get('obligations'), list):
        return []
    defaults, meta, task_map = (value.get('obligation_defaults', {}), value.get('kind_metadata', {}), value.get('task_component_map', {}))
    result = []
    try:
        for row in value['obligations']:
            core = dict(zip(COLUMNS, row, strict=True))
            tasks = core['task_bindings']
            kind = core['obligation_kind']
            comps = _uniq([c for t in tasks for c in task_map[t]])
            result.append(core | {'source_work_package': meta[kind]['source_work_package'], 'primary_implementation_task': tasks[-1], 'blocking_phase_gate': _phase(tasks[-1]), 'dependency_tasks': tasks[:-1], 'component_bindings': comps, 'evidence_type': meta[kind]['evidence_type'], 'status': defaults['status'], 'implementation_evidence_status': defaults['implementation_evidence_status']})
    except (KeyError, TypeError, ValueError):
        return []
    return result


def failures(state: dict[str, Any], record: dict[str, Any] | None=None) -> list[str]:
    if not RECORD.is_file():
        return ['PCFA-07 Codex implementation backlog reconciliation is missing']
    value = record or load_json(RECORD)
    out: list[str] = []

    def req(ok: bool, msg: str) -> None:
        if not ok:
            out.append(msg)
    try:
        expected, _ = build_records()
    except (KeyError, TypeError, ValueError) as e:
        return [f'PCFA-07 deterministic source reconstruction failed: {e}']
    req(value == expected, 'PCFA-07 reconciliation does not match governed source authorities and backlog')
    auth, ready, target = (state.get('current_authority', {}), state.get('repository_readiness', {}), state.get('launch_target', {}))
    req(auth.get('codex_implementation_backlog_reconciliation') == 'requirements/pcfa07-codex-implementation-backlog-reconciliation.json', 'PCFA-07 current authority missing')
    req(auth.get('codex_implementation_backlog_reconciliation_sha256') == digest_file(RECORD), 'PCFA-07 digest binding drifted')
    req(ready.get('pcfa07_implementation_backlog_reconciled') is True, 'PCFA-07 readiness missing')
    req(target.get('permitted_tasks') == ['P0.1', 'P0.2', 'P0.3', 'P0.4'] and target.get('permitted_phase') == 'Codex Phase 0 only', 'PCFA-07 widened Phase 0')
    p, c, proj, b = (value.get('reconciliation_policy', {}), value.get('obligation_counts', {}), value.get('backlog_projection', {}), value.get('boundaries', {}))
    req(c == {'pcfa04_requirements': 29, 'pcfa05_stages': 19, 'pcfa05_invariants': 15, 'pcfa05_negative_cases': 13, 'pcfa05_founder_interrupts': 6, 'pcfa06_capabilities': 11, 'total_obligations': 93, 'planned_tests': 93}, 'PCFA-07 counts drifted')
    req(p.get('no_new_imp_phases') is True and p.get('no_new_imp_tasks') is True and (p.get('imp_p0_scope_widened') is False) and (p.get('phase0_obligation_count') == 0) and (p.get('one_planned_test_per_obligation') is True) and (p.get('planned_tests_are_not_executed_evidence') is True) and (p.get('all_statuses_remain_planned_not_implemented') is True) and (p.get('implementation_evidence_available') is False) and (p.get('pcfa08_final_acceptance_required') is True), 'PCFA-07 policy drifted')
    obs = decode(value)
    tests = [x.get('planned_test_id') for x in obs]
    req(len(obs) == 93 and len(set(tests)) == 93 and all((x.get('status') == 'planned_not_implemented' and x.get('implementation_evidence_status') == 'not_available_pre_implementation' and x.get('task_bindings') and (not any((str(t).startswith('P0.') for t in x.get('task_bindings', [])))) and x.get('component_bindings') and x.get('evidence_type') for x in obs)), 'PCFA-07 obligation semantics drifted')
    req(proj == {'existing_imp_phase_count': 13, 'existing_task_count': 53, 'new_imp_phase_count': 0, 'new_task_count': 0, 'phase0_new_obligation_count': 0, 'phase0_tasks_unchanged': ['P0.1', 'P0.2', 'P0.3', 'P0.4']}, 'PCFA-07 backlog projection drifted')
    req(b.get('founder_accountability_preserved') is True and all((v is False for k, v in b.items() if k != 'founder_accountability_preserved')), 'PCFA-07 boundaries drifted')
    req(len(digest_file(CURRENT_STATE_PATH)) == 64, 'current operational-state digest unavailable')
    return out


def _mutate(value: dict[str, Any], path: tuple[str, ...], replacement: Any) -> None:
    if path[0] == 'obligations':
        row = value['obligations'][int(path[1])]
        field = path[2]
        if field in COLUMNS:
            row[COLUMNS.index(field)] = replacement
            return
        if field in {'status', 'implementation_evidence_status'}:
            value['obligation_defaults'][field] = replacement
            return
        if field == 'evidence_type':
            value['kind_metadata'][row[COLUMNS.index('obligation_kind')]][field] = replacement
            return
        if field == 'component_bindings':
            value['task_component_map'][row[COLUMNS.index('task_bindings')][0]] = replacement
            return
        if field == 'dependency_tasks':
            row[COLUMNS.index('task_bindings')] = list(replacement) + row[COLUMNS.index('task_bindings')][-1:]
            return
        if field == 'primary_implementation_task':
            row[COLUMNS.index('task_bindings')][-1] = replacement
            return
    node: Any = value
    for part in path[:-1]:
        node = node[int(part)] if part.isdigit() else node[part]
    final = path[-1]
    if final.isdigit():
        node[int(final)] = replacement
    else:
        node[final] = replacement


def run_self_test(state: dict[str, Any]) -> int:
    record = load_json(RECORD)
    if failures(state, record):
        raise SystemExit('PCFA-07 backlog reconciliation rejected: ' + '; '.join(failures(state, record)))
    cases = [('authority', ('current_authority', 'codex_implementation_backlog_reconciliation'), 'requirements/implementation-obligation-map.json'), ('digest', ('current_authority', 'codex_implementation_backlog_reconciliation_sha256'), 'd' * 64), ('readiness', ('repository_readiness', 'pcfa07_implementation_backlog_reconciled'), False), ('p0 scope', ('launch_target', 'permitted_tasks'), ['P0.1', 'P1.1'])]
    rejected = 0
    for label, path, repl in cases:
        v = copy.deepcopy(state)
        _mutate(v, path, repl)
        if not failures(v, record):
            raise SystemExit(f'PCFA-07 launch-state mutation not rejected: {label}')
        rejected += 1
    first_test = decode(record)[0]['planned_test_id']
    cases2 = [('implemented', ('obligations', '0', 'status'), 'implemented'), ('evidence', ('obligations', '0', 'implementation_evidence_status'), 'available'), ('p0 task', ('obligations', '0', 'task_bindings'), ['P0.1']), ('primary', ('obligations', '0', 'primary_implementation_task'), 'P1.1'), ('gate', ('derivation_rules', 'blocking_phase_gate'), 'arbitrary'), ('deps', ('obligations', '0', 'dependency_tasks'), []), ('components', ('obligations', '0', 'component_bindings'), []), ('duplicate test', ('obligations', '1', 'planned_test_id'), first_test), ('evidence type', ('obligations', '0', 'evidence_type'), ''), ('new phase', ('backlog_projection', 'new_imp_phase_count'), 1), ('new task', ('backlog_projection', 'new_task_count'), 1), ('p0 obligation', ('backlog_projection', 'phase0_new_obligation_count'), 1), ('pcfa08', ('reconciliation_policy', 'pcfa08_final_acceptance_required'), False), ('authorized', ('boundaries', 'codex_start_authorized'), True)]
    for label, path, repl in cases2:
        v = copy.deepcopy(record)
        _mutate(v, path, repl)
        if not failures(state, v):
            raise SystemExit(f'PCFA-07 launch-record mutation not rejected: {label}')
        rejected += 1
    return rejected


backlog_reconciliation_failures = failures
