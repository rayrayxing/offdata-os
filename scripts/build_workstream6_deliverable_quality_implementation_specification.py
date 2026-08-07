from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "configs" / "workstream6-deliverable-quality-implementation-specification.yaml"
CONTRACT = ROOT / "contracts" / "deliverable-quality-implementation-specification.json"
SPEC = ROOT / "docs" / "64-WS6-12-DELIVERABLE-QUALITY-IMPLEMENTATION-SPECIFICATION.md"
REPORT = ROOT / "reports" / "workstream6-deliverable-quality-implementation-specification-evidence.md"
QUALITY = ROOT / "contracts" / "pre-codex-readiness.json"
OBLIGATIONS = ROOT / "requirements" / "implementation-obligation-map.json"
BACKLOG = ROOT / "docs" / "11-BUILD-BACKLOG.md"
DELIVERY = ROOT / "packages" / "offdata-core" / "src" / "offdata_core" / "delivery.py"
SEMANTIC = ROOT / "packages" / "offdata-core" / "src" / "offdata_core" / "deliverable_semantic.py"
FIXTURE = ROOT / "packages" / "offdata-core" / "src" / "offdata_core" / "ai_audit_deliverable.py"

SURFACES = ("pptx", "docx", "xlsx", "pdf", "svg", "html")
DIMENSIONS = ("package_integrity", "editability_structure", "accessibility", "semantic_reconciliation", "visual_regression")
OQ_IDS = ("OQ-CITE", "OQ-CLAIM", "OQ-LABEL", "OQ-CONTRA", "OQ-NUM", "OQ-HARD", "OQ-RECALC", "OQ-XFMT")
OFFICE = frozenset({"pptx", "docx", "xlsx"})
TASK_RE = re.compile(r"^### (P(?:[0-9]|1[0-2])\.[0-9]+) ", re.MULTILINE)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def digest(value: object) -> str:
    if isinstance(value, str):
        payload = value
    else:
        payload = canonical(value)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def slug(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", value.upper()).strip("-")


def validate_sources(source: dict[str, Any]) -> None:
    if source["work_package_id"] != "WS6.12":
        raise ValueError("wrong work package")
    predecessor = source["predecessor"]
    if predecessor != {
        "work_package_id": "WS6.11",
        "pull_request": 52,
        "branch": "governance/ws611-founder-experience-specification",
        "head_sha": "9f138fd3f35fb9826c6da0ab696e83775312508e",
        "integrated_to_main": False,
    }:
        raise ValueError("WS6.12 predecessor drift")
    if source["required_surfaces"] != list(SURFACES):
        raise ValueError("surface order changed")
    if source["mandatory_dimensions"] != list(DIMENSIONS):
        raise ValueError("mandatory dimensions changed")

    quality = load(QUALITY)["output_quality"]
    groups = {key: list(quality["artifact_surfaces"][key]) for key in ("pptx", "docx", "xlsx", "pdf_svg_html")}
    if source["canonical_pcr10_artifact_surface_requirements"] != groups:
        raise ValueError("PCR-10 renderer requirements drifted")
    expected_pairs = [(g, r) for g, reqs in groups.items() for r in reqs]
    observed_pairs = [(x["group"], x["requirement"]) for x in source["pcr10_requirement_applicability"]]
    if observed_pairs != expected_pairs or len(observed_pairs) != len(set(observed_pairs)):
        raise ValueError("PCR-10 requirements must map once in canonical order")
    for item in source["pcr10_requirement_applicability"]:
        if item["dimension"] not in DIMENSIONS or not item["surfaces"] or not set(item["surfaces"]).issubset(SURFACES):
            raise ValueError("invalid PCR-10 applicability")
    if next(x for x in source["pcr10_requirement_applicability"] if x["requirement"] == "responsive_html")["surfaces"] != ["html"]:
        raise ValueError("responsive_html applicability changed")
    if next(x for x in source["pcr10_requirement_applicability"] if x["requirement"] == "print_safe_views")["surfaces"] != ["pdf", "html"]:
        raise ValueError("print_safe_views applicability changed")

    canonical_oq = [x["id"] for x in quality["evidence"]] + [x["id"] for x in quality["quantitative"]]
    if canonical_oq != list(OQ_IDS):
        raise ValueError("PCR-10 output-quality order changed")
    rules = source["criterion_rules"]
    if [x["criterion_id"] for x in rules] != list(OQ_IDS):
        raise ValueError("WS6.12 must bind all OQ criteria in canonical order")
    obligations = {x["criterion_id"]: x for x in load(OBLIGATIONS)["obligations"] if x["criterion_id"] in OQ_IDS}
    if set(obligations) != set(OQ_IDS):
        raise ValueError("WS6.9 output-quality obligations missing")
    for rule in rules:
        observed = obligations[rule["criterion_id"]]
        for field in ("phase_id", "task_id", "component_id", "evidence_type"):
            if observed[field] != rule[field]:
                raise ValueError(f"{rule['criterion_id']} {field} differs from WS6.9")

    tasks = set(TASK_RE.findall(BACKLOG.read_text(encoding="utf-8")))
    needed = {"P5.3", "P5.4", "P6.4", "P7.1", "P7.2", "P7.3", "P7.4", "P7.5"}
    if not needed.issubset(tasks):
        raise ValueError("required implementation backlog tasks missing")
    renderers = source["renderers"]
    if [x["surface"] for x in renderers] != list(SURFACES):
        raise ValueError("all six renderer contracts are required")
    for item in renderers:
        expected_integrity = "no_repair_warning" if item["surface"] in OFFICE else "no_parser_recovery"
        if item["integrity_mode"] != expected_integrity:
            raise ValueError(f"{item['surface']} integrity mode changed")
        if item["implementation_task"] not in tasks or item["quality_task"] != "P7.5":
            raise ValueError("renderer implementation ownership changed")
    if next(x for x in renderers if x["surface"] == "xlsx").get("model_quality_task") != "P6.4":
        raise ValueError("XLSX must retain P6.4 model QA")

    repair = source["repair_policy"]
    if repair["automatic_repair_allowed"] is not False or repair["repaired_or_recovered_output_blocks_release"] is not True:
        raise ValueError("repair policy widened")
    visual = source["visual_regression_policy"]
    if visual["material_region_changed_pixel_ratio_max"] != 0.0 or visual["global_changed_pixel_ratio_max"] > 0.005:
        raise ValueError("visual-regression tolerance widened")
    if visual["baseline_change_requires_review"] is not True:
        raise ValueError("visual baseline changes require review")
    reconciliation = source["reconciliation_policy"]
    if reconciliation["semantic_model_is_source_of_truth"] is not True or reconciliation["renderer_may_change_material_semantics"] is not False:
        raise ValueError("semantic authority widened")
    if reconciliation["required_cross_format_checks"] != ["headline", "assumption", "number", "recommendation", "roadmap", "source", "version", "rendered_inspection"]:
        raise ValueError("cross-format check set changed")
    for key, expected in {
        "material_number_agreement_percent": 100,
        "material_citation_resolution_percent": 100,
        "unsupported_material_claims": 0,
        "unexplained_hardcoded_material_numbers": 0,
        "independent_recalculation_pass_percent": 100,
        "fact_assumption_synthesis_recommendation_label_percent": 100,
        "contradicting_evidence_retained_percent": 100,
    }.items():
        if reconciliation[key] != expected:
            raise ValueError(f"quality target changed: {key}")

    tree = ast.parse(DELIVERY.read_text(encoding="utf-8"))
    enum_values: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "DeliverableSurface":
            for child in node.body:
                if isinstance(child, ast.Assign) and isinstance(child.value, ast.Constant) and isinstance(child.value.value, str):
                    enum_values.add(child.value.value)
    if not set(SURFACES).issubset(enum_values):
        raise ValueError("delivery contract no longer defines all six surfaces")
    semantic_text = SEMANTIC.read_text(encoding="utf-8")
    for surface in SURFACES:
        if f"DeliverableSurface.{surface.upper()}" not in semantic_text:
            raise ValueError("semantic required-surface set drifted")
    if "editable_required" not in semantic_text or "CrossFormatReconciliation" not in semantic_text:
        raise ValueError("semantic editability/reconciliation contract missing")
    fixture_text = FIXTURE.read_text(encoding="utf-8")
    if "ReconciliationCheck.RENDERED_INSPECTION" not in fixture_text or "renderer and Office inspection remain a later execution gate" not in fixture_text:
        raise ValueError("Phase 4 rendered-inspection handoff missing")

    if source["closed_defects"] != ["WS6-QUALITY-004"] or source["remaining_quality_defects"] != ["WS6-QUALITY-005"] or source["remaining_blocking_defects"] != ["WS6-BLOCK-006"]:
        raise ValueError("defect boundary changed")
    if source["test_registration"]["registered_case_count"] != 0 or source["test_registration"]["executable_test_count"] != 0:
        raise ValueError("renderer tests cannot be represented as registered/executable")
    if any(source["implementation_evidence"][k] != 0 for k in ("satisfied_renderer_count", "satisfied_cross_format_criterion_count")):
        raise ValueError("implementation evidence cannot exist pre-implementation")
    boundaries = source["boundaries"]
    if boundaries["founder_accountability_preserved"] is not True or any(v is not False for k, v in boundaries.items() if k != "founder_accountability_preserved"):
        raise ValueError("authorization boundary widened")


def requirement_list(source: dict[str, Any], surface: str, dimension: str) -> list[str]:
    return [x["requirement"] for x in source["pcr10_requirement_applicability"] if surface in x["surfaces"] and x["dimension"] == dimension]


def build_records() -> tuple[dict[str, Any], str, str]:
    source_text = SOURCE.read_text(encoding="utf-8")
    source = json.loads(source_text)
    validate_sources(source)

    renderers = []
    for renderer in source["renderers"]:
        cases = [{
            "case_id": f"DQ-{renderer['surface'].upper()}-{slug(dimension)}-001",
            "dimension": dimension,
            "pcr10_requirements": requirement_list(source, renderer["surface"], dimension),
            "evidence_type": f"{renderer['surface']}_{dimension}_report",
            "registration_status": "planned_unregistered",
            "executable_test_exists": False,
            "implementation_evidence_satisfied": False,
        } for dimension in DIMENSIONS]
        renderers.append({
            "surface": renderer["surface"],
            "implementation_task": renderer["implementation_task"],
            "component_id": renderer["component_id"],
            "quality_task": renderer["quality_task"],
            **({"model_quality_task": renderer["model_quality_task"]} if "model_quality_task" in renderer else {}),
            "integrity_mode": renderer["integrity_mode"],
            "editability_mode": renderer["editability_mode"],
            "source_digest": digest(renderer),
            "acceptance_cases": cases,
        })

    xfmt = [{
        "criterion_id": rule["criterion_id"],
        "phase_id": rule["phase_id"],
        "task_id": rule["task_id"],
        "component_id": rule["component_id"],
        "evidence_type": rule["evidence_type"],
        "source_digest": digest(rule),
        "case_id": f"DQ-XFMT-{rule['criterion_id']}-001",
        "registration_status": "planned_unregistered",
        "executable_test_exists": False,
        "implementation_evidence_satisfied": False,
    } for rule in source["criterion_rules"]]

    contract = {
        "schema_version": 1,
        "work_package_id": "WS6.12",
        "title": source["title"],
        "predecessor": source["predecessor"],
        "defect_ids": source["defect_ids"],
        "canonical_sources": source["canonical_sources"],
        "document_path_resolution": source["document_path_resolution"],
        "generated_from": str(SOURCE.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
        "renderer_count": 6,
        "mandatory_dimension_count": 5,
        "canonical_pcr10_requirement_count": len(source["pcr10_requirement_applicability"]),
        "surface_requirement_binding_count": sum(len(x["surfaces"]) for x in source["pcr10_requirement_applicability"]),
        "renderer_acceptance_case_count": 30,
        "cross_format_acceptance_case_count": 8,
        "acceptance_case_count": 38,
        "required_surfaces": source["required_surfaces"],
        "mandatory_dimensions": source["mandatory_dimensions"],
        "policy_digests": {
            "repair": digest(source["repair_policy"]),
            "visual_regression": digest(source["visual_regression_policy"]),
            "accessibility": digest(source["accessibility_policy"]),
            "reconciliation": digest(source["reconciliation_policy"]),
        },
        "renderers": renderers,
        "cross_format_quality_cases": xfmt,
        "test_registration": {**source["test_registration"], "planned_case_count": 38},
        "implementation_evidence": source["implementation_evidence"],
        "closed_defects": source["closed_defects"],
        "remaining_blocking_defects": source["remaining_blocking_defects"],
        "remaining_quality_defects": source["remaining_quality_defects"],
        "completion": source["completion"],
        "boundaries": source["boundaries"],
        "rollback": source["rollback"],
    }

    lines = [
        "# WS6.12 — Deliverable quality implementation specification", "",
        "> [!CAUTION]",
        "> **SPECIFIED, NOT IMPLEMENTED OR AUTHORISED.** This defines future renderer acceptance gates only.",
        "> It does not render or issue a client artefact, activate runtime, authorize Codex, or satisfy implementation evidence.", "",
        "## Purpose", "",
        "WS6.12 extends the existing Phase 4 semantic model with implementation-ready renderer gates for PPTX, DOCX, XLSX, PDF, SVG and HTML.",
        "The semantic model remains the source of truth; renderers may not change material semantics.", "",
        "- Renderer surfaces: `6`.",
        "- Mandatory dimensions per renderer: `5`.",
        "- PCR-10 renderer requirements: `26`.",
        "- Explicit surface bindings: `37`.",
        "- Renderer acceptance cases: `30`.",
        "- Cross-format OQ cases: `8`.",
        "- Total planned cases: `38`.",
        "- Registered/executable renderer tests: `0`.",
        "- Satisfied implementation evidence: `0`.",
        "- `codex_start_authorized=false`.", "",
        "## Canonical path", "",
        "The defect register suggested `docs/55-DELIVERABLE-QUALITY-IMPLEMENTATION-SPEC.md`, but `docs/55-WS6-3-CURRENT-STATUS-DOCUMENT-REPAIR.md` is immutable retained WS6.3 evidence.",
        "This file is the canonical WS6.12 specification.", "",
        "## Release-wide hard gates", "",
        "- Automatic repair is forbidden; repaired or parser-recovered output blocks release.",
        "- PPTX, DOCX and XLSX must open in an independent office consumer without repair/recovery warnings.",
        "- PDF, SVG and HTML must parse/render without recovery or fatal resource/console errors.",
        "- Material-region visual diffs have zero tolerance; global normalized raster difference is at most `0.005` with anti-alias channel delta at most `12`.",
        "- Visual masks cannot cover text, material numbers, citations, decision labels or semantic visual labels.",
        "- Clipped material text, off-canvas material objects, protected overlaps, missing fonts and missing assets each have zero tolerance.",
        "- Material number agreement, citation resolution, semantic labels, contradiction retention and independent recalculation are 100%; unsupported material claims and unexplained hardcoded material numbers are zero.",
        "- Baseline changes require review.", "",
        "## PCR-10 requirement expansion", "",
        "| Group | Requirement | Surfaces | Dimension |", "|---|---|---|---|",
    ]
    for item in source["pcr10_requirement_applicability"]:
        lines.append(f"| `{item['group']}` | `{item['requirement']}` | `{', '.join(item['surfaces'])}` | `{item['dimension']}` |")
    lines += ["", "## Renderer contracts", ""]
    source_renderers = {x["surface"]: x for x in source["renderers"]}
    for renderer in renderers:
        detail = source_renderers[renderer["surface"]]
        lines += [
            f"### `{renderer['surface'].upper()}`", "",
            f"- Implementation: `{renderer['implementation_task']}` / `{renderer['component_id']}`.",
            f"- Visual QA: `{renderer['quality_task']}`.",
            f"- Integrity: `{renderer['integrity_mode']}`.",
            f"- Editability/structure: `{renderer['editability_mode']}`.",
            f"- Independent consumer: `{detail['independent_consumer']}`.", "",
            "**Native structures**", *[f"- `{x}`" for x in detail["required_native_structures"]], "",
            "**Accessibility**", *[f"- `{x}`" for x in detail["accessibility_assertions"]], "",
            "**Semantic reconciliation**", *[f"- `{x}`" for x in detail["reconciliation_assertions"]], "",
            "**Visual regression**", *[f"- `{x}`" for x in detail["visual_assertions"]], "",
            "| Planned case | Dimension | PCR-10 requirements | Evidence |", "|---|---|---|---|",
        ]
        for case in renderer["acceptance_cases"]:
            covered = ", ".join(case["pcr10_requirements"]) or "WS6.12 cross-cutting requirement"
            lines.append(f"| `{case['case_id']}` | `{case['dimension']}` | {covered} | `{case['evidence_type']}` |")
        lines.append("")
    lines += ["## Cross-format output-quality obligations", "", "| Criterion | Owner | Evidence | Planned case |", "|---|---|---|---|"]
    for case in xfmt:
        lines.append(f"| `{case['criterion_id']}` | `{case['phase_id']}` / `{case['task_id']}` / `{case['component_id']}` | `{case['evidence_type']}` | `{case['case_id']}` |")
    lines += [
        "", "## Evidence contract", "",
        "Each future gate must retain the exact implementation commit, semantic-model digest, renderer/profile version, produced-artifact digest, independent consumer/parser result, accessibility report, reconciliation report and visual-regression report.",
        "On failure, retain the original unmodified artifact and diagnostics; a repaired copy cannot replace the failing artifact as evidence.", "",
        "## Completion boundary", "",
        "WS6.12 closes only `WS6-QUALITY-004`. `WS6-QUALITY-005`, `WS6-CODEXPREP-002` and `WS6-BLOCK-006` remain open.",
        "No renderer, visual-QA implementation or external deliverable release is claimed.", "",
        "The next permitted chat-first work package is `WS6.13` after the governed predecessor sequence and exact hosted acceptance requirements are satisfied.", "",
        "## Rollback", "", source["rollback"]["before_merge"], "", source["rollback"]["after_merge"], "",
    ]
    spec = "\n".join(lines)
    report = "\n".join([
        "# WS6.12 deliverable quality implementation specification evidence", "",
        "<!-- Generated by scripts/build_workstream6_deliverable_quality_implementation_specification.py. -->", "",
        f"- Exact WS6.11 predecessor: `{source['predecessor']['head_sha']}`",
        "- Renderer surfaces: `6`",
        "- Mandatory dimensions per renderer: `5`",
        "- Canonical PCR-10 renderer requirements: `26`",
        "- Explicit surface bindings: `37`",
        "- Renderer acceptance cases: `30`",
        "- Cross-format output-quality cases: `8`",
        "- Total planned cases: `38`",
        "- Registered/executable tests: `0`",
        "- Satisfied renderer/cross-format implementation evidence: `0`",
        "- Closed defect: `WS6-QUALITY-004`",
        "- Remaining quality defect: `WS6-QUALITY-005`",
        "- Remaining blocking defect: `WS6-BLOCK-006`",
        "- Automatic repair and semantic drift remain fail-closed.",
        "- `codex_start_authorized=false`; implementation, runtime, external release and production remain unauthorized.", "",
        "Next permitted work package: `WS6.13`.", "",
    ])
    return contract, spec, report


def main() -> None:
    contract, spec, report = build_records()
    CONTRACT.write_text(canonical(contract), encoding="utf-8")
    SPEC.write_text(spec, encoding="utf-8")
    REPORT.write_text(report, encoding="utf-8")
    print("Built WS6.12 deliverable quality implementation specification: renderers=6, requirements=26, bindings=37, cases=38, implemented=0, next=WS6.13, codex_start_authorized=false.")


if __name__ == "__main__":
    main()
