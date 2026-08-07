from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Callable

import jsonschema

from build_workstream6_renderer_preimplementation_assets import (
    CONTRACT,
    GOLDENS,
    INTERFACES,
    ROOT,
    SOURCE,
    build_records,
    canonical,
)

SCHEMA = ROOT / "schemas/workstream6-renderer-preimplementation-assets.schema.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def validate_source(source: dict[str, Any]) -> None:
    if source["work_package_id"] != "WS6.12" or source["supplement_id"] != "WS6.12-RENDERER-PREP":
        raise ValueError("supplement identity drift")
    if source["defect_ids"] != ["WS6-CODEXPREP-006"] or source["closed_defects"] != ["WS6-CODEXPREP-006"]:
        raise ValueError("supplement may close only WS6-CODEXPREP-006")
    if [item["surface"] for item in source["surfaces"]] != ["pptx", "docx", "xlsx", "pdf", "svg", "html"]:
        raise ValueError("renderer surface order drift")
    if source["interface_policy"]["physical_renderer_outputs_present"] is not False:
        raise ValueError("physical renderer output cannot be claimed")
    for key in ("physical_artifact_present", "office_or_parser_validation_executed", "visual_baseline_captured", "approved_golden"):
        if source["golden_policy"][key] is not False:
            raise ValueError(f"golden evidence cannot be claimed: {key}")
    if source["completion"]["next_permitted_work_package"] != "WS6.13":
        raise ValueError("next package drift")
    if source["boundaries"]["founder_accountability_preserved"] is not True:
        raise ValueError("Founder accountability must be preserved")
    if any(value is not False for key, value in source["boundaries"].items() if key != "founder_accountability_preserved"):
        raise ValueError("all authorization boundaries must remain false")


def expect_failure(mutator: Callable[[dict[str, Any]], None], source: dict[str, Any]) -> bool:
    value = copy.deepcopy(source)
    mutator(value)
    try:
        validate_source(value)
        return False
    except (ValueError, KeyError, TypeError):
        return True


def main() -> None:
    source = load(SOURCE)
    validate_source(source)
    interfaces, goldens, contract, report = build_records()
    expected = {
        INTERFACES: canonical(interfaces),
        GOLDENS: canonical(goldens),
        CONTRACT: canonical(contract),
    }
    for path, text in expected.items():
        if path.read_text(encoding="utf-8") != text:
            raise ValueError(f"stale generated file: {path.relative_to(ROOT)}")
    report_path = ROOT / "reports/workstream6-renderer-preimplementation-assets-evidence.md"
    if report_path.read_text(encoding="utf-8") != report:
        raise ValueError("stale supplemental report")
    jsonschema.validate(contract, load(SCHEMA))
    if interfaces["renderer_count"] != 6 or goldens["entry_count"] != 6:
        raise ValueError("renderer/golden count drift")
    for item in interfaces["interfaces"]:
        if item["implementation_status"] != "planned_not_implemented" or item["output_contract"]["automatic_repair_allowed"] is not False:
            raise ValueError("renderer implementation boundary widened")
    for item in goldens["entries"]:
        if any(item[key] is not False for key in ("physical_artifact_present", "office_or_parser_validation_executed", "visual_baseline_captured", "approved_golden")):
            raise ValueError("golden evidence falsely claimed")

    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda x: x.update(work_package_id="WS6.13"),
        lambda x: x.update(defect_ids=[]),
        lambda x: x.update(closed_defects=[]),
        lambda x: x["completion"].update(next_permitted_work_package="IMP-P0"),
        lambda x: x["boundaries"].update(codex_start_authorized=True),
        lambda x: x["boundaries"].update(external_actions_authorized=True),
        lambda x: x["interface_policy"].update(physical_renderer_outputs_present=True),
        lambda x: x["golden_policy"].update(approved_golden=True),
        lambda x: x["golden_policy"].update(physical_artifact_present=True),
        lambda x: x["golden_policy"].update(visual_baseline_captured=True),
        lambda x: x["surfaces"].pop(),
    ]
    rejected = sum(expect_failure(mutator, source) for mutator in mutations)
    if rejected != len(mutations):
        raise ValueError(f"mutation suite accepted {len(mutations)-rejected} invalid values")
    print(f"WS6.12 renderer preimplementation assets passed: {rejected} mutations rejected, interfaces=6, goldens=6, physical=0, approved=0, next=WS6.13, codex_start_authorized=false.")


if __name__ == "__main__":
    main()
