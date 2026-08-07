from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "configs" / "workstream6-founder-experience-specification.yaml"
CONTRACT = ROOT / "contracts" / "founder-experience-specification.json"
SPEC = ROOT / "docs" / "63-WS6-11-FOUNDER-EXPERIENCE-SPECIFICATION.md"
REPORT = ROOT / "reports" / "workstream6-founder-experience-specification-evidence.md"
QUALITY = ROOT / "contracts" / "pre-codex-readiness.json"
OBLIGATION_MAP = ROOT / "requirements" / "implementation-obligation-map.json"

CASE_CLASSES = ("happy_path", "missing_required_data", "authorization_safety", "stale_or_version_drift")


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode()).hexdigest()


def _canonical_founder_criteria(quality: dict[str, Any]) -> list[str]:
    return [item["id"] for item in quality["founder_experience"]["acceptance_criteria"]]


def build_records() -> tuple[dict[str, Any], str, str]:
    source = _load(SOURCE)
    quality = _load(QUALITY)
    obligation_map = _load(OBLIGATION_MAP)
    expected_ids = _canonical_founder_criteria(quality)
    rules = source["criterion_rules"]
    if [item["criterion_id"] for item in rules] != expected_ids:
        raise ValueError("WS6.11 criterion order must exactly match PCR-10 Founder criteria")

    obligation_by_id = {
        item["criterion_id"]: item
        for item in obligation_map["obligations"]
        if item["criterion_id"] in expected_ids
    }
    if set(obligation_by_id) != set(expected_ids):
        raise ValueError("WS6.11 obligations are incomplete")

    criteria: list[dict[str, Any]] = []
    case_ids: set[str] = set()
    for rule in rules:
        criterion_id = rule["criterion_id"]
        obligation = obligation_by_id[criterion_id]
        expected = (rule["phase_id"], rule["task_id"], rule["component_id"])
        observed = (obligation["phase_id"], obligation["task_id"], obligation["component_id"])
        if expected != observed:
            raise ValueError(f"WS6.11 ownership drift for {criterion_id}: {expected} != {observed}")
        if obligation["blocks_imp_p0"] is not False:
            raise ValueError(f"Founder criterion must not block IMP-P0: {criterion_id}")
        if tuple(rule["cases"]) != CASE_CLASSES:
            raise ValueError(f"WS6.11 acceptance classes drifted for {criterion_id}")
        cases = []
        for case_class in CASE_CLASSES:
            case_id = f"FX-{criterion_id.removeprefix('FX-')}-{case_class.upper().replace('_','-')}-001"
            if case_id in case_ids:
                raise ValueError("duplicate WS6.11 acceptance case")
            case_ids.add(case_id)
            cases.append({
                "case_id": case_id,
                "case_class": case_class,
                "registration_status": "planned_unregistered",
                "executable_test_exists": False,
            })
        criteria.append({
            "criterion_id": criterion_id,
            "phase_id": rule["phase_id"],
            "task_id": rule["task_id"],
            "component_id": rule["component_id"],
            "surface_id": rule["surface_id"],
            "required_fields": list(rule["required_fields"]),
            "invariants": list(rule["invariants"]),
            "source_digest": _digest(rule),
            "acceptance_cases": cases,
            "implementation_status": "specified_not_implemented",
            "evidence_satisfied": False,
        })

    contract = {
        "schema_version": source["schema_version"],
        "work_package_id": source["work_package_id"],
        "title": source["title"],
        "predecessor": source["predecessor"],
        "generated_from": SOURCE.relative_to(ROOT).as_posix(),
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "canonical_sources": source["canonical_sources"],
        "document_path_resolution": source["document_path_resolution"],
        "surface_count": len(source["surfaces"]),
        "state_count": len(source["states"]),
        "criterion_count": len(criteria),
        "acceptance_case_count": len(case_ids),
        "surfaces": [{"id": item["id"], "route": item["route"]} for item in source["surfaces"]],
        "states": [{"id": item["id"], "terminal": item["terminal"]} for item in source["states"]],
        "criteria": criteria,
        "decision_packet_digest": _digest(source["decision_packet"]),
        "authorization_digest": _digest(source["authorization"]),
        "external_send_digest": _digest(source["external_send"]),
        "evidence_drillthrough_digest": _digest(source["evidence_drillthrough"]),
        "accessibility_digest": _digest(source["accessibility"]),
        "inbox_digest": _digest(source["inbox"]),
        "test_registration": source["test_registration"],
        "evidence": source["evidence"],
        "closed_defects": source["closed_defects"],
        "remaining_blocking_defects": source["remaining_blocking_defects"],
        "remaining_preparation_defects": source["remaining_preparation_defects"],
        "completion": source["completion"],
        "boundaries": source["boundaries"],
    }

    spec = _render_spec(source, criteria)
    report = "\n".join([
        "# WS6.11 Founder experience specification evidence",
        "",
        "<!-- Generated by scripts/build_workstream6_founder_experience_specification.py. -->",
        "",
        f"- Exact WS6.10 predecessor: `{source['predecessor']['head_sha']}`.",
        f"- PCR-10 Founder criteria specified: `{len(criteria)}/8`.",
        f"- Founder surfaces: `{len(source['surfaces'])}`.",
        f"- Explicit workflow states: `{len(source['states'])}`.",
        f"- Planned acceptance cases: `{len(case_ids)}`; registered/executable: `0`.",
        "- Recommendation, authorization and execution remain separate.",
        "- Stale/version/action drift invalidates authorization.",
        "- External sending remains disabled without exact scoped Founder authorization.",
        "- Closed defect: `WS6-QUALITY-003`.",
        "- `WS6-CODEXPREP-002` and `WS6-BLOCK-006` remain open.",
        "- `codex_start_authorized=false`; no implementation evidence is claimed.",
        "",
        "Next permitted work package: `WS6.12`, after the governed predecessor integration sequence.",
        "",
    ])
    return contract, spec, report


def _render_spec(source: dict[str, Any], criteria: list[dict[str, Any]]) -> str:
    lines = [
        "# WS6.11 — Founder experience specification",
        "",
        "> [!CAUTION]",
        "> **SPECIFIED, NOT IMPLEMENTED OR AUTHORISED.** This package defines future Founder",
        "> review and decision-state contracts. It does not activate a runtime, create an",
        "> authorization, enable external sending, or authorize Codex.",
        "",
        "## Purpose",
        "",
        "Every material Founder decision must be findable, explainable, evidence-linked,",
        "versioned and explicitly authorized before any governed action executes.",
        "",
        f"- PCR-10 Founder criteria: `{len(criteria)}/8`.",
        f"- Governed surfaces: `{len(source['surfaces'])}`.",
        f"- Explicit decision/workflow states: `{len(source['states'])}`.",
        "- Planned acceptance cases: `32`; registered/executable tests: `0`.",
        "- `codex_start_authorized=false`.",
        "",
        "The defect register suggested `docs/54-FOUNDER-EXPERIENCE-SPEC.md`, but numeric",
        "prefix `54` is immutable WS6.2 evidence. This document is the canonical WS6.11",
        "specification.",
        "",
        "## Core invariants",
        "",
        "- Recommendation is not authorization.",
        "- Founder authorization is exact, versioned, scoped and append-only.",
        "- Execution cannot begin before authorization where approval is required.",
        "- Any record, preview or action-digest drift invalidates prior authorization.",
        "- `stale` work requires re-review; it never continues under old authority.",
        "- External sending is disabled by default and cannot be autonomous.",
        "- Evidence drill-through is read-only with respect to authorization.",
        "- Accessibility alternatives preserve identical authorization semantics.",
        "",
        "## Founder surfaces",
        "",
        "| Surface | Route | Purpose |",
        "|---|---|---|",
    ]
    for item in source["surfaces"]:
        lines.append(f"| `{item['id']}` | `{item['route']}` | {item['purpose']} |")
    lines += [
        "",
        "## Decision packet",
        "",
        "A material decision packet must expose the exact recommendation, consequences,",
        "deadline, reversibility, evidence, action preview, state and version before a",
        "Founder action is possible.",
        "",
        "Required fields:",
        "",
    ]
    lines += [f"- `{field}`" for field in source["decision_packet"]["required_fields"]]
    lines += [
        "",
        "Unknown reversibility or any missing material field blocks authorization.",
        "",
        "## Authorization contract",
        "",
    ]
    for key, value in source["authorization"].items():
        lines.append(f"- `{key}`: `{json.dumps(value, ensure_ascii=False)}`")
    lines += [
        "",
        "## Explicit states",
        "",
        "| State | Terminal | Meaning |",
        "|---|:---:|---|",
    ]
    for item in source["states"]:
        lines.append(f"| `{item['id']}` | `{str(item['terminal']).lower()}` | {item['meaning']} |")
    lines += [
        "",
        "At minimum, `waiting`, `blocked`, `retrying`, `failed`, `stale` and `complete`",
        "must remain visually and semantically distinct.",
        "",
        "## Evidence drill-through",
        "",
        "Material claims and numbers must resolve to versioned evidence references and/or",
        "named model outputs while preserving the originating decision context. Unsupported",
        "material items remain visibly unsupported. Drill-through cannot mutate decision state.",
        "",
        "## Accessibility",
        "",
        f"- Target: `{source['accessibility']['standard']}`.",
        f"- Minimum normal-text contrast: `{source['accessibility']['text_contrast_min']}:1`.",
        f"- Minimum large-text contrast: `{source['accessibility']['large_text_contrast_min']}:1`.",
        "- All Founder tasks are keyboard-completable with visible focus and readable errors.",
        "- State changes are announced without unexpected focus loss.",
        "- No authorization shortcut may exist for an alternate input mode.",
        "",
        "## Controlled external send",
        "",
        "Client/prospect sending remains disabled unless the current version has exact scoped",
        "Founder authorization and a final recipient/channel/content preview. Recipient,",
        "content or action drift invalidates authorization. Autonomous sending remains prohibited.",
        "",
        "## Criterion contracts",
        "",
        "| Criterion | Phase/task | Component | Surface | Planned cases |",
        "|---|---|---|---|---:|",
    ]
    rule_by_id = {item["criterion_id"]: item for item in source["criterion_rules"]}
    for item in criteria:
        lines.append(
            f"| `{item['criterion_id']}` | `{item['phase_id']}` / `{item['task_id']}` | "
            f"`{item['component_id']}` | `{item['surface_id']}` | `4` |"
        )
    for item in criteria:
        rule = rule_by_id[item["criterion_id"]]
        lines += [
            "",
            f"### `{item['criterion_id']}`",
            "",
            f"- Owner: `{item['phase_id']}` / `{item['task_id']}` / `{item['component_id']}`.",
            f"- Surface: `{item['surface_id']}`.",
            "- Required fields: " + ", ".join(f"`{field}`" for field in rule["required_fields"]) + ".",
            "- Invariants: " + ", ".join(f"`{inv}`" for inv in rule["invariants"]) + ".",
            "",
            "| Case | Scenario |",
            "|---|---|",
        ]
        for case_class in CASE_CLASSES:
            lines.append(f"| `{case_class}` | {rule['cases'][case_class]} |")
    lines += [
        "",
        "## Completion boundary",
        "",
        "WS6.11 closes only `WS6-QUALITY-003`. It does not implement the Founder cockpit,",
        "register executable tests, satisfy implementation evidence, authorize external",
        "sending, or alter any Codex/IMP-P0 boundary. `WS6-CODEXPREP-002` and",
        "`WS6-BLOCK-006` remain open.",
        "",
        "The next permitted package is WS6.12 after the governed WS6.8 → WS6.9 → WS6.10",
        "→ WS6.11 integration sequence.",
        "",
        "## Rollback",
        "",
        "Before merge, close the WS6.11 pull request and delete only its branch. After merge,",
        "revert this specification package as one unit. No Founder runtime exists to roll back.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    contract, spec, report = build_records()
    CONTRACT.write_text(json.dumps(contract, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
    SPEC.write_text(spec, encoding="utf-8")
    REPORT.write_text(report, encoding="utf-8")
    print("Built WS6.11 Founder experience specification: criteria=8, states=13, cases=32, implemented=0, next=WS6.12, codex_start_authorized=false.")


if __name__ == "__main__":
    main()
