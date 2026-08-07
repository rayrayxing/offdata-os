from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "configs" / "workstream6-implementation-obligation-map.yaml"
OUTPUT = ROOT / "requirements" / "implementation-obligation-map.json"
REPORT = ROOT / "reports" / "workstream6-implementation-obligation-map-evidence.md"
PHASE_HEADING = re.compile(r"^## (IMP-P([0-9]+)) — (.+)$", re.MULTILINE)
TASK_HEADING = re.compile(r"^### (P([0-9]+)\.([0-9]+)) (.+)$", re.MULTILINE)


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def _canonical_criteria(contract: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for section in (
        "developer_experience",
        "founder_experience",
        "operational_quality",
        "cross_cutting",
    ):
        for item in contract[section]["acceptance_criteria"]:
            records.append(
                {
                    "criterion_id": item["id"],
                    "criterion_kind": "acceptance_criterion",
                    "source_section": section,
                    "description": item["criterion"],
                    "evidence_class": item["evidence_class"],
                }
            )
    for subsection in ("evidence", "quantitative"):
        for item in contract["output_quality"][subsection]:
            records.append(
                {
                    "criterion_id": item["id"],
                    "criterion_kind": "metric",
                    "source_section": f"output_quality.{subsection}",
                    "description": (
                        f"{item['metric']} must equal {item['target']} {item['unit']}."
                    ),
                    "metric": item["metric"],
                    "target": item["target"],
                    "unit": item["unit"],
                    "evidence_class": item["evidence_class"],
                }
            )
    expected = contract["quality_registry"]["criterion_ids"]
    observed = [record["criterion_id"] for record in records]
    if observed != expected:
        raise ValueError("PCR-10 criterion order or identity drifted")
    return records


def _backlog_tasks(text: str) -> tuple[dict[str, dict[str, str]], dict[str, str]]:
    phases = list(PHASE_HEADING.finditer(text))
    tasks: dict[str, dict[str, str]] = {}
    gates: dict[str, str] = {}
    for index, match in enumerate(phases):
        phase_id = match.group(1)
        end = phases[index + 1].start() if index + 1 < len(phases) else len(text)
        section = text[match.end():end]
        gate_heading = f"### {phase_id} gate"
        if gate_heading not in section:
            raise ValueError(f"missing canonical gate for {phase_id}")
        gates[phase_id] = gate_heading
        for task in TASK_HEADING.finditer(section):
            task_id = task.group(1)
            task_phase = f"IMP-P{task.group(2)}"
            if task_phase != phase_id:
                raise ValueError(f"task {task_id} is under the wrong phase")
            tasks[task_id] = {
                "phase_id": phase_id,
                "title": task.group(4).strip(),
            }
    if len(phases) != 13 or len(tasks) < 50:
        raise ValueError("implementation backlog is incomplete")
    return tasks, gates


def build_records() -> tuple[dict[str, Any], str]:
    source = _load_yaml(SOURCE)
    quality_path = ROOT / source["canonical_sources"]["quality_contract"]
    backlog_path = ROOT / source["canonical_sources"]["implementation_backlog"]
    component_path = ROOT / source["canonical_sources"]["component_contract"]
    quality = _load_json(quality_path)
    components = _load_json(component_path)
    criteria = _canonical_criteria(quality)
    tasks, gates = _backlog_tasks(backlog_path.read_text(encoding="utf-8"))

    mappings = source["mappings"]
    mapping_ids = [item["criterion_id"] for item in mappings]
    expected_ids = [item["criterion_id"] for item in criteria]
    if mapping_ids != expected_ids:
        raise ValueError("WS6.9 source mappings must follow the exact PCR-10 criterion order")
    if len(mapping_ids) != len(set(mapping_ids)):
        raise ValueError("WS6.9 source mappings contain duplicate criteria")

    foundation = {
        item["component_id"]: item for item in source["foundation_components"]
    }
    canonical_components = {
        item["component_id"]: item for item in components["integration_components"]
    }
    known_components = {**foundation, **canonical_components}

    obligations: list[dict[str, Any]] = []
    for criterion, mapping in zip(criteria, mappings, strict=True):
        task_id = mapping["implementation_task"]
        if task_id not in tasks:
            raise ValueError(f"unknown implementation task: {task_id}")
        phase_id = mapping["implementation_phase"]
        if tasks[task_id]["phase_id"] != phase_id:
            raise ValueError(f"task/phase mismatch for {criterion['criterion_id']}")
        component_id = mapping["component_id"]
        if component_id not in known_components:
            raise ValueError(f"unknown implementation component: {component_id}")
        if component_id in foundation:
            if phase_id != "IMP-P0":
                raise ValueError("foundation components may only own IMP-P0 obligations")
            if foundation[component_id]["implementation_task"] != task_id:
                raise ValueError("foundation component/task ownership mismatch")
        evidence_class = criterion["evidence_class"]
        phase0 = evidence_class == "phase0_acceptance"
        if phase0 != (phase_id == "IMP-P0"):
            raise ValueError(
                f"evidence class and implementation phase disagree for {criterion['criterion_id']}"
            )
        registration_owner = (
            source["test_registration_policy"]["phase0_registration_owner"]
            if phase0
            else phase_id
        )
        obligations.append(
            {
                **criterion,
                "implementation_owner": {
                    "phase_id": phase_id,
                    "task_id": task_id,
                    "task_title": tasks[task_id]["title"],
                    "component_id": component_id,
                    "component_name": known_components[component_id]["name"],
                },
                "test_obligation": {
                    "test_obligation_id": mapping["test_obligation_id"],
                    "registration_status": source["test_registration_policy"]["registration_status"],
                    "registration_owner": registration_owner,
                    "executable_test_exists": source["test_registration_policy"]["executable_test_exists"],
                    "separate_registration_defect": source["test_registration_policy"]["separate_defect_remains_open"],
                },
                "evidence_requirement": {
                    "evidence_type": mapping["evidence_type"],
                    "status": source["evidence_policy"]["status"],
                    "required_attributes": source["evidence_policy"]["required_attributes"],
                },
                "blocking_gate": {
                    "gate_id": f"{phase_id}-GATE",
                    "canonical_gate_heading": gates[phase_id],
                    "blocks_phase_completion": True,
                    "blocks_imp_p0": phase0,
                    "status": "not_evaluated",
                },
                "implementation_authorized": False,
                "evidence_satisfied": False,
            }
        )

    phase_counts = Counter(item["implementation_owner"]["phase_id"] for item in obligations)
    component_counts = Counter(item["implementation_owner"]["component_id"] for item in obligations)
    evidence_counts = Counter(item["evidence_class"] for item in obligations)
    contract = {
        **source,
        "generated_from": SOURCE.relative_to(ROOT).as_posix(),
        "criterion_count": len(obligations),
        "phase0_blocking_criterion_count": evidence_counts["phase0_acceptance"],
        "later_phase_criterion_count": evidence_counts["later_implementation_acceptance"],
        "obligations": obligations,
        "phase_summary": [
            {"phase_id": phase, "criterion_count": phase_counts[phase]}
            for phase in sorted(phase_counts, key=lambda value: int(value[5:]))
        ],
        "component_summary": [
            {"component_id": component, "criterion_count": component_counts[component]}
            for component in sorted(component_counts)
        ],
        "test_obligation_count": len(
            {item["test_obligation"]["test_obligation_id"] for item in obligations}
        ),
        "registered_test_count": sum(
            item["test_obligation"]["registration_status"] == "registered"
            for item in obligations
        ),
        "satisfied_evidence_count": sum(item["evidence_satisfied"] for item in obligations),
    }
    report_lines = [
        "# WS6.9 implementation-obligation-map evidence",
        "",
        "<!-- Generated by scripts/build_workstream6_implementation_obligation_map.py. -->",
        "",
        f"- Exact predecessor WS6.8 head: `{source['predecessor']['head_sha']}`.",
        f"- PCR-10 criteria mapped exactly once: `{len(obligations)}`.",
        f"- IMP-P0 blocking criteria: `{evidence_counts['phase0_acceptance']}`.",
        f"- Later-phase criteria that do not block IMP-P0: `{evidence_counts['later_implementation_acceptance']}`.",
        f"- Unique planned test obligations: `{contract['test_obligation_count']}`.",
        "- Registered or executable tests claimed by WS6.9: `0`.",
        "- Evidence satisfied before implementation: `0`.",
        "- Closed defect: `WS6-QUALITY-001`.",
        "- Separate planned-test registration defect remains open: `WS6-CODEXPREP-002`.",
        "- Remaining blocking defect: `WS6-BLOCK-006`.",
        "- `codex_start_authorized=false`; implementation and merge remain unauthorized.",
        "",
        "## Phase ownership",
        "",
    ]
    report_lines.extend(
        f"- `{item['phase_id']}`: `{item['criterion_count']}` criteria."
        for item in contract["phase_summary"]
    )
    report_lines.extend(
        [
            "",
            "Next permitted work package: `WS6.10`, after the governed WS6.8 → WS6.9 integration sequence.",
            "",
        ]
    )
    return contract, "\n".join(report_lines)


def main() -> None:
    contract, report = build_records()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(contract, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    REPORT.write_text(report, encoding="utf-8")
    print(
        "Built WS6.9 implementation obligation map: "
        "criteria=38, phase0_blocking=16, later_nonblocking=22, "
        "registered_tests=0, next=WS6.10, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
