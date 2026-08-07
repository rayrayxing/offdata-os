from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "configs/workstream6-renderer-preimplementation-assets.yaml"
QUALITY = ROOT / "contracts/deliverable-quality-implementation-specification.json"
INTERFACES = ROOT / "contracts/renderer-interface-contracts.json"
GOLDENS = ROOT / "fixtures/golden-output-manifest.json"
CONTRACT = ROOT / "contracts/workstream6-renderer-preimplementation-assets.json"
REPORT = ROOT / "reports/workstream6-renderer-preimplementation-assets-evidence.md"
DIMS = ("package_integrity", "editability_structure", "accessibility", "semantic_reconciliation", "visual_regression")


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"


def sha(value: object) -> str:
    text = value if isinstance(value, str) else canonical(value)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_records() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str]:
    source = load(SOURCE)
    quality = load(QUALITY)
    surfaces = [item["surface"] for item in source["surfaces"]]
    if surfaces != quality["required_surfaces"] or quality["renderer_count"] != 6:
        raise ValueError("WS6.12 renderer surface set drift")
    if quality["acceptance_case_count"] != 38 or quality["renderer_acceptance_case_count"] != 30:
        raise ValueError("WS6.12 acceptance case baseline drift")
    renderer_by_surface = {item["surface"]: item for item in quality["renderers"]}

    interfaces = []
    goldens = []
    for surface_item in source["surfaces"]:
        surface = surface_item["surface"]
        renderer = renderer_by_surface[surface]
        cases = renderer["acceptance_cases"]
        if [case["dimension"] for case in cases] != list(DIMS):
            raise ValueError(f"{surface} dimension set drift")
        interface_id = f"RENDERER-{surface.upper()}"
        interfaces.append({
            "interface_id": interface_id,
            "surface": surface,
            "implementation_task": renderer["implementation_task"],
            "component_id": renderer["component_id"],
            "quality_task": renderer["quality_task"],
            **({"model_quality_task": renderer["model_quality_task"]} if "model_quality_task" in renderer else {}),
            "implementation_status": source["interface_policy"]["status"],
            "input_contract": {
                "semantic_model_required": True,
                "surface_plan_required": True,
                "material_semantic_mutation_allowed": False,
            },
            "output_contract": {
                "integrity_mode": renderer["integrity_mode"],
                "editability_mode": renderer["editability_mode"],
                "automatic_repair_allowed": False,
            },
            "quality_dimensions": list(DIMS),
            "acceptance_case_ids": [case["case_id"] for case in cases],
        })
        goldens.append({
            "golden_id": f"GOLDEN-{surface.upper()}-DAI-001",
            "surface": surface,
            "renderer_interface_id": interface_id,
            "semantic_fixture_id": source["semantic_fixture_id"],
            "semantic_model_id": source["semantic_model_id"],
            "planned_filename": surface_item["planned_filename"],
            "implementation_status": "planned_not_implemented",
            "physical_artifact_present": False,
            "office_or_parser_validation_executed": False,
            "visual_baseline_captured": False,
            "approved_golden": False,
            "required_quality_dimensions": list(DIMS),
            "acceptance_case_ids": [case["case_id"] for case in cases],
        })

    interface_contract = {
        "schema_version": 1,
        "work_package_id": "WS6.12",
        "supplement_id": source["supplement_id"],
        "generated_from": str(SOURCE.relative_to(ROOT)),
        "semantic_source_of_truth": source["canonical_sources"]["semantic_model"],
        "status": source["interface_policy"]["status"],
        "renderer_count": len(interfaces),
        "physical_renderer_outputs_present": False,
        "interfaces": interfaces,
        "boundaries": source["boundaries"],
    }
    golden_manifest = {
        "schema_version": 1,
        "work_package_id": "WS6.12",
        "supplement_id": source["supplement_id"],
        "generated_from": str(SOURCE.relative_to(ROOT)),
        "fixture_id": source["semantic_fixture_id"],
        "semantic_model_id": source["semantic_model_id"],
        "status": source["golden_policy"]["status"],
        "entry_count": len(goldens),
        "baseline_policy": {key: source["golden_policy"][key] for key in (
            "approval_requires_physical_render",
            "approval_requires_independent_consumer_or_parser",
            "approval_requires_visual_regression",
            "baseline_change_requires_review",
        )},
        "entries": goldens,
        "boundaries": source["boundaries"],
    }
    contract = {
        "schema_version": 1,
        "work_package_id": "WS6.12",
        "supplement_id": source["supplement_id"],
        "title": source["title"],
        "generated_from": str(SOURCE.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "parent_package_head_sha": source["parent_package_head_sha"],
        "defect_ids": source["defect_ids"],
        "renderer_count": len(interfaces),
        "golden_entry_count": len(goldens),
        "renderer_interface_digest": sha(interface_contract),
        "golden_output_manifest_digest": sha(golden_manifest),
        "closed_defects": source["closed_defects"],
        "remaining_preparation_defects": source["remaining_preparation_defects"],
        "completion": source["completion"],
        "boundaries": source["boundaries"],
        "rollback": source["rollback"],
    }
    report = "\n".join([
        "# WS6.12 renderer preimplementation asset evidence", "",
        "<!-- Generated by scripts/build_workstream6_renderer_preimplementation_assets.py. -->", "",
        f"- Parent WS6.12 head: `{source['parent_package_head_sha']}`",
        "- Closed defect: `WS6-CODEXPREP-006`",
        f"- Renderer interfaces: `{len(interfaces)}`",
        f"- Planned synthetic golden entries: `{len(goldens)}`",
        "- Physical renderer outputs: `0`",
        "- Approved golden baselines: `0`",
        "- Office/parser executions: `0`",
        "- Visual-regression executions: `0`",
        "- `codex_start_authorized=false`.", "",
        "Next permitted work package: `WS6.13`.", "",
    ])
    return interface_contract, golden_manifest, contract, report


def main() -> None:
    interfaces, goldens, contract, report = build_records()
    INTERFACES.write_text(canonical(interfaces), encoding="utf-8")
    GOLDENS.parent.mkdir(parents=True, exist_ok=True)
    GOLDENS.write_text(canonical(goldens), encoding="utf-8")
    CONTRACT.write_text(canonical(contract), encoding="utf-8")
    REPORT.write_text(report, encoding="utf-8")
    print("Built WS6.12 renderer preimplementation assets: interfaces=6, goldens=6, physical=0, approved=0, next=WS6.13, codex_start_authorized=false.")


if __name__ == "__main__":
    main()
