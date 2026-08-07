from __future__ import annotations

import copy
import json
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from build_workstream6_implementation_obligation_map import build_records

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "requirements" / "implementation-obligation-map.json"
SCHEMA = ROOT / "schemas" / "implementation-obligation-map.schema.json"
REPORT = ROOT / "reports" / "workstream6-implementation-obligation-map-evidence.md"
QUALITY = ROOT / "contracts" / "pre-codex-readiness.json"


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def _canonical_ids() -> list[str]:
    value = _json(QUALITY)["quality_registry"]["criterion_ids"]
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError("PCR-10 quality registry is invalid")
    return value


def _failures(value: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    require(value.get("work_package_id") == "WS6.9", "work package")
    predecessor = value.get("predecessor", {})
    require(predecessor.get("work_package_id") == "WS6.8", "predecessor package")
    require(
        predecessor.get("head_sha")
        == "46abab02ad08a3a1cca519391e0114555f11230c",
        "predecessor head",
    )
    require(predecessor.get("integrated_to_main") is False, "integration honesty")

    obligations = value.get("obligations", [])
    require(isinstance(obligations, list) and len(obligations) == 38, "obligation count")
    if not isinstance(obligations, list):
        obligations = []
    ids = [
        item.get("criterion_id")
        for item in obligations
        if isinstance(item, dict)
    ]
    require(ids == _canonical_ids(), "criterion identity and order")
    require(len(ids) == len(set(ids)), "criterion uniqueness")

    evidence = Counter(
        item.get("evidence_class")
        for item in obligations
        if isinstance(item, dict)
    )
    phases: Counter[str] = Counter()
    test_ids: list[str] = []
    for item in obligations:
        if not isinstance(item, dict):
            failures.append("obligation object")
            continue
        criterion_id = item.get("criterion_id")
        phase_id = item.get("phase_id")
        task_id = item.get("task_id")
        phase0 = item.get("evidence_class") == "phase0_acceptance"
        phases[str(phase_id)] += 1
        require(
            isinstance(task_id, str)
            and isinstance(phase_id, str)
            and phase_id == f"IMP-{task_id.split('.')[0]}",
            f"task/phase: {criterion_id}",
        )
        require(
            item.get("gate_id") == f"{phase_id}-GATE",
            f"gate/phase: {criterion_id}",
        )
        require((phase_id == "IMP-P0") is phase0, f"phase split: {criterion_id}")
        require(item.get("blocks_imp_p0") is phase0, f"P0 blocker: {criterion_id}")
        test_ids.append(str(item.get("test_obligation_id")))
        owner = item.get("test_registration_owner")
        require(
            owner == ("WS6.13" if phase0 else phase_id),
            f"test owner: {criterion_id}",
        )
        require(bool(item.get("component_id")), f"component: {criterion_id}")
        require(bool(item.get("evidence_type")), f"evidence type: {criterion_id}")

    require(evidence["phase0_acceptance"] == 16, "phase0 count")
    require(evidence["later_implementation_acceptance"] == 22, "later count")
    require(len(test_ids) == len(set(test_ids)) == 38, "test identity")
    require(value.get("criterion_count") == 38, "criterion summary")
    require(value.get("phase0_blocking_criterion_count") == 16, "phase0 summary")
    require(value.get("later_phase_criterion_count") == 22, "later summary")
    require(
        value.get("phase_summary")
        == [
            {"phase_id": phase, "criterion_count": phases[phase]}
            for phase in sorted(phases, key=lambda item: int(item[5:]))
        ],
        "phase summary",
    )

    test_policy = value.get("test_policy", {})
    require(
        test_policy
        == {
            "registration_status": "planned_unregistered",
            "executable_test_count": 0,
            "separate_registration_defect": "WS6-CODEXPREP-002",
        },
        "test policy",
    )
    evidence_policy = value.get("evidence_policy", {})
    require(
        evidence_policy.get("status") == "not_available_pre_implementation",
        "evidence status",
    )
    require(evidence_policy.get("satisfied_evidence_count") == 0, "evidence count")
    require(
        isinstance(evidence_policy.get("required_attributes"), list)
        and len(evidence_policy["required_attributes"]) == 8
        and len(set(evidence_policy["required_attributes"])) == 8,
        "evidence attributes",
    )
    require(
        value.get("gate_policy")
        == {
            "all_obligations_block_assigned_phase_completion": True,
            "only_phase0_acceptance_blocks_imp_p0": True,
        },
        "gate policy",
    )

    require(value.get("closed_defects") == ["WS6-QUALITY-001"], "closed defects")
    require(
        value.get("remaining_blocking_defects") == ["WS6-BLOCK-006"],
        "remaining blocker",
    )
    require(
        value.get("remaining_preparation_defects") == ["WS6-CODEXPREP-002"],
        "remaining preparation defect",
    )
    completion = value.get("completion", {})
    for key in (
        "all_required_prior_components_pass",
        "stacked_on_exact_ws68_head",
        "ws69_repository_package_complete",
        "criterion_mapping_complete",
        "phase0_blocking_split_verified",
    ):
        require(completion.get(key) is True, key)
    for key in (
        "ws68_integrated_to_main",
        "test_registration_complete",
        "final_reconciliation_complete",
        "all_blocking_defects_closed",
    ):
        require(completion.get(key) is False, key)
    require(completion.get("next_permitted_work_package") == "WS6.10", "next")

    boundaries = value.get("boundaries", {})
    require(
        boundaries.get("founder_accountability_preserved") is True,
        "accountability",
    )
    for key, current in boundaries.items():
        if key != "founder_accountability_preserved":
            require(current is False, key)
    return failures


def _set(value: dict[str, Any], path: tuple[Any, ...], replacement: Any) -> None:
    node: Any = value
    for part in path[:-1]:
        node = node[part]
    node[path[-1]] = replacement


def main() -> None:
    contract = _json(OUTPUT)
    errors = list(Draft202012Validator(_json(SCHEMA)).iter_errors(contract))
    if errors:
        raise SystemExit(
            "WS6.9 schema validation failed: "
            + "; ".join(error.message for error in errors)
        )
    expected, report = build_records()
    expected_bytes = (
        json.dumps(
            expected,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        + "\n"
    )
    if contract != expected or OUTPUT.read_text(encoding="utf-8") != expected_bytes:
        raise SystemExit("WS6.9 map is not deterministic")
    if REPORT.read_text(encoding="utf-8") != report:
        raise SystemExit("WS6.9 report is not deterministic")
    failures = _failures(contract)
    if failures:
        raise SystemExit(
            "WS6.9 semantic validation failed: " + "; ".join(failures)
        )

    rejected = 0
    for index, item in enumerate(contract["obligations"]):
        mutated = copy.deepcopy(contract)
        mutated["obligations"][index]["blocks_imp_p0"] = not item["blocks_imp_p0"]
        if _failures(mutated):
            rejected += 1
        else:
            raise SystemExit(
                f"WS6.9 blocking mutation not rejected: {item['criterion_id']}"
            )

    cases: list[tuple[tuple[Any, ...], Any]] = [
        (("work_package_id",), "WS6.8"),
        (("predecessor", "head_sha"), "0" * 40),
        (("predecessor", "integrated_to_main"), True),
        (("criterion_count",), 37),
        (("phase0_blocking_criterion_count",), 15),
        (("later_phase_criterion_count",), 23),
        (("test_policy", "executable_test_count"), 1),
        (("test_policy", "registration_status"), "registered"),
        (("evidence_policy", "satisfied_evidence_count"), 1),
        (("gate_policy", "only_phase0_acceptance_blocks_imp_p0"), False),
        (("closed_defects",), []),
        (("remaining_blocking_defects",), []),
        (("remaining_preparation_defects",), []),
        (("completion", "all_required_prior_components_pass"), False),
        (("completion", "stacked_on_exact_ws68_head"), False),
        (("completion", "ws68_integrated_to_main"), True),
        (("completion", "test_registration_complete"), True),
        (("completion", "next_permitted_work_package"), "WS6.11"),
        (("boundaries", "codex_start_authorized"), True),
        (("boundaries", "phase0_implementation_authorized"), True),
    ]
    for path, replacement in cases:
        mutated = copy.deepcopy(contract)
        _set(mutated, path, replacement)
        if _failures(mutated):
            rejected += 1
        else:
            raise SystemExit(f"WS6.9 mutation not rejected: {path}")

    structural: list[tuple[str, dict[str, Any]]] = []
    missing = copy.deepcopy(contract)
    missing["obligations"] = missing["obligations"][:-1]
    structural.append(("missing criterion", missing))
    duplicate = copy.deepcopy(contract)
    duplicate["obligations"][1]["criterion_id"] = duplicate["obligations"][0][
        "criterion_id"
    ]
    structural.append(("duplicate criterion", duplicate))
    duplicate_test = copy.deepcopy(contract)
    duplicate_test["obligations"][1]["test_obligation_id"] = duplicate_test[
        "obligations"
    ][0]["test_obligation_id"]
    structural.append(("duplicate test", duplicate_test))
    wrong_phase = copy.deepcopy(contract)
    wrong_phase["obligations"][0]["phase_id"] = "IMP-P1"
    structural.append(("phase0 criterion moved later", wrong_phase))
    wrong_task = copy.deepcopy(contract)
    wrong_task["obligations"][8]["task_id"] = "P3.3"
    structural.append(("task mismatch", wrong_task))
    wrong_owner = copy.deepcopy(contract)
    wrong_owner["obligations"][0]["test_registration_owner"] = "IMP-P0"
    structural.append(("registration owner", wrong_owner))
    wrong_gate = copy.deepcopy(contract)
    wrong_gate["obligations"][0]["gate_id"] = "IMP-P1-GATE"
    structural.append(("gate mismatch", wrong_gate))
    missing_component = copy.deepcopy(contract)
    missing_component["obligations"][0]["component_id"] = ""
    structural.append(("missing component", missing_component))
    for label, mutated in structural:
        if _failures(mutated):
            rejected += 1
        else:
            raise SystemExit(
                f"WS6.9 structural mutation not rejected: {label}"
            )

    print(
        "WS6.9 implementation obligation map passed: "
        f"{rejected} mutations rejected, criteria=38, phase0_blocking=16, "
        "later_nonblocking=22, registered_tests=0, satisfied_evidence=0, "
        "next=WS6.10, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
