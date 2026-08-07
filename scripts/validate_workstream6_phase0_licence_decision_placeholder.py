from __future__ import annotations

import copy
from typing import Callable

import jsonschema

from build_workstream6_phase0_licence_decision_placeholder import (
    DOC,
    OUT,
    REPORT,
    ROOT,
    SRC,
    build,
    canonical,
    load,
)

SCHEMA = ROOT / "schemas/phase0-licence-decision-placeholder.schema.json"
ADR_TEMPLATE = ROOT / "templates/adr.md"

def validate_source(value: dict) -> None:
    if value["work_package_id"] != "WS6.13":
        raise ValueError("work package drift")
    if value["supplement_id"] != "WS6.13-LICENCE-PLACEHOLDER":
        raise ValueError("supplement drift")
    if value["defect_id"] != "WS6-CONSIST-009":
        raise ValueError("defect drift")
    if value["status"] != "decision_required_not_authorized":
        raise ValueError("status drift")
    if value["owner"] != "Founder":
        raise ValueError("owner drift")
    if value["decision_timing"]["implementation_task"] != "P0.1":
        raise ValueError("task drift")
    if len(value["options"]) != 4 or any(item["selection"] for item in value["options"]):
        raise ValueError("licence option unexpectedly selected")
    if value["adr"] != {
        "template": "templates/adr.md",
        "planned_path": "docs/adr/ADR-0001-licence-decision.md",
        "exists": False,
        "approved": False,
    }:
        raise ValueError("ADR state drift")
    state = value["licence_state"]
    if state["selected_licence"] is not None:
        raise ValueError("licence unexpectedly selected")
    if state["implicit_licence_grant"] or state["public_distribution_authorized"] or state["external_licence_notice_authorized"]:
        raise ValueError("licence/publication authorization widened")
    boundaries = value["boundaries"]
    if boundaries["founder_accountability_preserved"] is not True:
        raise ValueError("Founder accountability lost")
    if any(v is not False for k, v in boundaries.items() if k != "founder_accountability_preserved"):
        raise ValueError("authorization boundary widened")
    required = {
        "explicit_founder_decision",
        "selected_licence_identifier_or_proprietary_status",
        "decision_date",
        "decision_scope",
        "dependency_compatibility_review",
        "adr_record",
    }
    if set(value["evidence_required"]) != required:
        raise ValueError("closure evidence drift")

def main() -> None:
    source = load(SRC)
    validate_source(source)
    contract, doc, report = build()
    jsonschema.validate(contract, load(SCHEMA))
    if OUT.read_text(encoding="utf-8") != canonical(contract):
        raise ValueError("stale generated contract")
    if DOC.read_text(encoding="utf-8") != doc:
        raise ValueError("stale generated doc")
    if REPORT.read_text(encoding="utf-8") != report:
        raise ValueError("stale generated report")
    adr = ADR_TEMPLATE.read_text(encoding="utf-8")
    for required_phrase in (
        "No decision by template presence",
        "Decision owner: Founder",
        "does not by itself authorize implementation",
    ):
        if required_phrase not in adr:
            raise ValueError("ADR template missing fail-closed language")

    mutations: list[Callable[[dict], None]] = [
        lambda v: v.update(work_package_id="WS6.14"),
        lambda v: v.update(defect_id="WS6-CONSIST-010"),
        lambda v: v.update(status="approved"),
        lambda v: v.update(owner="Codex"),
        lambda v: v["decision_timing"].update(implementation_task="P1.1"),
        lambda v: v["options"][0].update(selection=True),
        lambda v: v["adr"].update(exists=True),
        lambda v: v["adr"].update(approved=True),
        lambda v: v["licence_state"].update(selected_licence="MIT"),
        lambda v: v["licence_state"].update(implicit_licence_grant=True),
        lambda v: v["licence_state"].update(public_distribution_authorized=True),
        lambda v: v["licence_state"].update(external_licence_notice_authorized=True),
        lambda v: v["boundaries"].update(codex_start_authorized=True),
        lambda v: v["boundaries"].update(runtime_activation_authorized=True),
        lambda v: v.update(evidence_required=[]),
    ]
    rejected = 0
    for mutate in mutations:
        candidate = copy.deepcopy(source)
        mutate(candidate)
        try:
            validate_source(candidate)
        except (KeyError, TypeError, ValueError):
            rejected += 1
    if rejected != len(mutations):
        raise ValueError("mutation rejection incomplete")
    print(
        f"WS6.13 licence placeholder passed: {rejected} mutations rejected, "
        "options=4, selected=0, implicit_grant=false, public_distribution=false, "
        "codex_start_authorized=false."
    )

if __name__ == "__main__":
    main()
