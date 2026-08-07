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
PHASE = re.compile(r"^## (IMP-P([0-9]+)) — ", re.MULTILINE)
TASK = re.compile(r"^### (P([0-9]+)\.[0-9]+) (.+)$", re.MULTILINE)


def _yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def _criteria(value: dict[str, Any]) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for section in (
        "developer_experience",
        "founder_experience",
        "operational_quality",
        "cross_cutting",
    ):
        records.extend(
            {
                "criterion_id": item["id"],
                "evidence_class": item["evidence_class"],
            }
            for item in value[section]["acceptance_criteria"]
        )
    for section in ("evidence", "quantitative"):
        records.extend(
            {
                "criterion_id": item["id"],
                "evidence_class": item["evidence_class"],
            }
            for item in value["output_quality"][section]
        )
    if [item["criterion_id"] for item in records] != value["quality_registry"]["criterion_ids"]:
        raise ValueError("PCR-10 criterion identity or order drifted")
    return records


def _tasks(text: str) -> tuple[dict[str, str], set[str]]:
    phase_matches = list(PHASE.finditer(text))
    tasks: dict[str, str] = {}
    gates: set[str] = set()
    for index, match in enumerate(phase_matches):
        phase_id = match.group(1)
        end = phase_matches[index + 1].start() if index + 1 < len(phase_matches) else len(text)
        section = text[match.end():end]
        if f"### {phase_id} gate" not in section:
            raise ValueError(f"missing gate for {phase_id}")
        gates.add(phase_id)
        for task in TASK.finditer(section):
            task_id = task.group(1)
            task_phase = f"IMP-P{task.group(2)}"
            if task_phase != phase_id:
                raise ValueError(f"task {task_id} is under the wrong phase")
            tasks[task_id] = phase_id
    if len(phase_matches) != 13 or len(tasks) < 50:
        raise ValueError("implementation backlog is incomplete")
    return tasks, gates


def build_records() -> tuple[dict[str, Any], str]:
    source = _yaml(SOURCE)
    quality = _json(ROOT / source["canonical_sources"]["quality_contract"])
    components = _json(ROOT / source["canonical_sources"]["component_contract"])
    tasks, gates = _tasks(
        (ROOT / source["canonical_sources"]["implementation_backlog"]).read_text(
            encoding="utf-8"
        )
    )
    criteria = _criteria(quality)
    mappings = source["mappings"]
    expected_ids = [item["criterion_id"] for item in criteria]
    if [item["criterion_id"] for item in mappings] != expected_ids:
        raise ValueError("WS6.9 mappings must match the PCR-10 registry exactly")
    component_ids = {
        item["component_id"] for item in source["foundation_components"]
    } | {
        item["component_id"] for item in components["integration_components"]
    }
    foundation = {
        item["component_id"]: item["implementation_task"]
        for item in source["foundation_components"]
    }
    obligations: list[dict[str, Any]] = []
    for criterion, mapping in zip(criteria, mappings, strict=True):
        phase_id = mapping["implementation_phase"]
        task_id = mapping["implementation_task"]
        component_id = mapping["component_id"]
        if tasks.get(task_id) != phase_id or phase_id not in gates:
            raise ValueError(f"invalid task or phase for {criterion['criterion_id']}")
        if component_id not in component_ids:
            raise ValueError(f"unknown component for {criterion['criterion_id']}")
        if component_id in foundation and (
            phase_id != "IMP-P0" or foundation[component_id] != task_id
        ):
            raise ValueError("foundation component ownership drifted")
        phase0 = criterion["evidence_class"] == "phase0_acceptance"
        if phase0 != (phase_id == "IMP-P0"):
            raise ValueError(f"evidence class split drifted for {criterion['criterion_id']}")
        obligations.append(
            {
                "criterion_id": criterion["criterion_id"],
                "evidence_class": criterion["evidence_class"],
                "phase_id": phase_id,
                "task_id": task_id,
                "component_id": component_id,
                "test_obligation_id": mapping["test_obligation_id"],
                "test_registration_owner": (
                    source["test_registration_policy"]["phase0_registration_owner"]
                    if phase0
                    else phase_id
                ),
                "evidence_type": mapping["evidence_type"],
                "gate_id": f"{phase_id}-GATE",
                "blocks_imp_p0": phase0,
            }
        )
    phases = Counter(item["phase_id"] for item in obligations)
    evidence = Counter(item["evidence_class"] for item in obligations)
    contract = {
        "schema_version": source["schema_version"],
        "work_package_id": source["work_package_id"],
        "title": source["title"],
        "predecessor": source["predecessor"],
        "canonical_sources": source["canonical_sources"],
        "generated_from": SOURCE.relative_to(ROOT).as_posix(),
        "defect_ids": source["defect_ids"],
        "obligations": obligations,
        "criterion_count": len(obligations),
        "phase0_blocking_criterion_count": evidence["phase0_acceptance"],
        "later_phase_criterion_count": evidence["later_implementation_acceptance"],
        "phase_summary": [
            {"phase_id": phase, "criterion_count": phases[phase]}
            for phase in sorted(phases, key=lambda value: int(value[5:]))
        ],
        "test_policy": {
            "registration_status": "planned_unregistered",
            "executable_test_count": 0,
            "separate_registration_defect": "WS6-CODEXPREP-002",
        },
        "evidence_policy": {
            "status": "not_available_pre_implementation",
            "satisfied_evidence_count": 0,
            "required_attributes": source["evidence_policy"]["required_attributes"],
        },
        "gate_policy": {
            "all_obligations_block_assigned_phase_completion": True,
            "only_phase0_acceptance_blocks_imp_p0": True,
        },
        "completion": source["completion"],
        "closed_defects": source["closed_defects"],
        "remaining_blocking_defects": source["remaining_blocking_defects"],
        "remaining_preparation_defects": source["remaining_preparation_defects"],
        "boundaries": source["boundaries"],
    }
    lines = [
        "# WS6.9 implementation-obligation-map evidence",
        "",
        "<!-- Generated by scripts/build_workstream6_implementation_obligation_map.py. -->",
        "",
        f"- Exact predecessor WS6.8 head: `{source['predecessor']['head_sha']}`.",
        "- PCR-10 criteria mapped exactly once: `38`.",
        "- IMP-P0 blocking criteria: `16`.",
        "- Later-phase criteria that do not block IMP-P0: `22`.",
        "- Planned test obligations: `38`; registered or executable tests claimed: `0`.",
        "- Evidence satisfied before implementation: `0`.",
        "- Closed defect: `WS6-QUALITY-001`.",
        "- Separate planned-test registration defect remains open: `WS6-CODEXPREP-002`.",
        "- Remaining blocking defect: `WS6-BLOCK-006`.",
        "- `codex_start_authorized=false`; implementation and merge remain unauthorized.",
        "",
        "## Phase ownership",
        "",
        *[
            f"- `{item['phase_id']}`: `{item['criterion_count']}` criteria."
            for item in contract["phase_summary"]
        ],
        "",
        "Next permitted work package: `WS6.10`, after the governed WS6.8 → WS6.9 integration sequence.",
        "",
    ]
    return contract, "\n".join(lines)


def main() -> None:
    contract, report = build_records()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(contract, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        + "\n",
        encoding="utf-8",
    )
    REPORT.write_text(report, encoding="utf-8")
    print(
        "Built WS6.9 implementation obligation map: criteria=38, "
        "phase0_blocking=16, later_nonblocking=22, registered_tests=0, "
        "next=WS6.10, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
