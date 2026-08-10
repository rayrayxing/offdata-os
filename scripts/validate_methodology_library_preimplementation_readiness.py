from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Any

import yaml

from codex_phase0_launch_core import ROOT, load_json

CONFIG = ROOT / "configs" / "methodology-library-preimplementation-readiness.yaml"
DOC = ROOT / "docs" / "76-METHODOLOGY-LIBRARY-PREIMPLEMENTATION-READINESS.md"
BACKLOG = ROOT / "docs" / "11-BUILD-BACKLOG.md"
PHASE6 = ROOT / "docs" / "38-PHASE-6-KNOWLEDGE-INGESTION-INTELLIGENCE-COMPLETION.md"
KNOWLEDGE_CONFIG = ROOT / "configs" / "knowledge-ingestion.yaml"
SOURCE_MANIFEST = ROOT / "knowledge" / "source-manifest.yaml"
ALIASES = ROOT / "knowledge" / "alias-map.yaml"
DEPENDENCIES = ROOT / "knowledge" / "dependency-resolution-cases.yaml"
HEADINGS = ROOT / "knowledge" / "domain-method-headings.yaml"
COLLISIONS = ROOT / "knowledge" / "method-collision-map.yaml"
EXAMPLES = ROOT / "knowledge" / "method-record-examples.yaml"
RETRIEVAL = ROOT / "knowledge" / "retrieval-evaluation.yaml"
RADAR = ROOT / "knowledge" / "radar-source-taxonomy.yaml"
BASELINE = ROOT / "knowledge" / "knowledge-ingestion-baseline.json"
TYPED_CONTRACTS = ROOT / "packages" / "offdata-core" / "src" / "offdata_core" / "knowledge.py"
APPROVAL_TEMPLATE = ROOT / "knowledge" / "canonical-source-approval.template.yaml"

EXPECTED_AUTHORITY_PATHS = {
    "implementation_backlog": "docs/11-BUILD-BACKLOG.md",
    "knowledge_schema_backlog": "docs/21-KNOWLEDGE-SCHEMA-BACKLOG.md",
    "methodology_radar": "docs/23-METHODOLOGY-RADAR-SPECIFICATION.md",
    "phase6_completion": "docs/38-PHASE-6-KNOWLEDGE-INGESTION-INTELLIGENCE-COMPLETION.md",
    "knowledge_config": "configs/knowledge-ingestion.yaml",
    "source_manifest": "knowledge/source-manifest.yaml",
    "alias_map": "knowledge/alias-map.yaml",
    "dependency_cases": "knowledge/dependency-resolution-cases.yaml",
    "method_headings": "knowledge/domain-method-headings.yaml",
    "collision_map": "knowledge/method-collision-map.yaml",
    "method_examples": "knowledge/method-record-examples.yaml",
    "retrieval_evaluation": "knowledge/retrieval-evaluation.yaml",
    "radar_taxonomy": "knowledge/radar-source-taxonomy.yaml",
    "phase6_baseline": "knowledge/knowledge-ingestion-baseline.json",
    "typed_contracts": "packages/offdata-core/src/offdata_core/knowledge.py",
    "founder_approval_template": "knowledge/canonical-source-approval.template.yaml",
}

EXPECTED_PROFILE = {
    "source_count": 23,
    "core_markdown_sources": 11,
    "domain_docx_sources": 12,
    "method_headings": 154,
    "aliases": 99,
    "dependency_cases": 21,
    "collision_families": 12,
    "method_record_examples": 12,
    "retrieval_gold_cases": 46,
    "radar_categories": 10,
}

ALLOWED_DISPOSITIONS = [
    "ingested_structured",
    "duplicate",
    "superseded",
    "quarantined",
    "excluded_with_reason",
]

REQUIRED_TYPED_MODELS = [
    "SourceDocument",
    "SourcePassage",
    "MethodRecord",
    "ProblemArchetype",
    "MethodSelection",
    "MethodologyCandidate",
]


def _yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def _need(errors: list[str], ok: bool, message: str) -> None:
    if not ok:
        errors.append(message)


def _sha256(value: object) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[0-9a-f]{64}", value))


def load_snapshot() -> dict[str, Any]:
    return {
        "config": _yaml(CONFIG),
        "source_manifest": _yaml(SOURCE_MANIFEST),
        "knowledge_config": _yaml(KNOWLEDGE_CONFIG),
        "aliases": _yaml(ALIASES),
        "dependencies": _yaml(DEPENDENCIES),
        "headings": _yaml(HEADINGS),
        "collisions": _yaml(COLLISIONS),
        "examples": _yaml(EXAMPLES),
        "retrieval": _yaml(RETRIEVAL),
        "radar": _yaml(RADAR),
        "baseline": load_json(BASELINE),
        "approval": _yaml(APPROVAL_TEMPLATE),
        "backlog": BACKLOG.read_text(encoding="utf-8"),
        "phase6": PHASE6.read_text(encoding="utf-8"),
        "typed_contracts": TYPED_CONTRACTS.read_text(encoding="utf-8"),
        "doc": DOC.read_text(encoding="utf-8"),
    }


def failures(snapshot: dict[str, Any] | None = None) -> list[str]:
    state = load_snapshot() if snapshot is None else snapshot
    errors: list[str] = []

    cfg = state["config"]
    manifest = state["source_manifest"]
    knowledge_cfg = state["knowledge_config"]
    aliases = state["aliases"]
    dependencies = state["dependencies"]
    headings = state["headings"]
    collisions = state["collisions"]
    examples = state["examples"]
    retrieval = state["retrieval"]
    radar = state["radar"]
    baseline = state["baseline"]
    approval = state["approval"]
    backlog = state["backlog"]
    phase6 = state["phase6"]
    typed = state["typed_contracts"]
    doc = state["doc"]

    _need(
        errors,
        cfg.get("status") == "governed_chat_first_complete"
        and cfg.get("scope") == "methodology_library_preimplementation_contracts_only"
        and cfg.get("work_package") == "METHODOLOGY-LIBRARY-PREIMPLEMENTATION-READINESS",
        "methodology-library preimplementation identity/status drifted",
    )
    authorities = cfg.get("source_authorities", {})
    _need(errors, authorities == EXPECTED_AUTHORITY_PATHS, "methodology-library source-authority set drifted")
    if isinstance(authorities, dict):
        for rel in authorities.values():
            _need(errors, isinstance(rel, str) and (ROOT / rel).is_file(), f"methodology authority missing: {rel}")

    expected = cfg.get("expected_profile", {})
    _need(errors, expected == EXPECTED_PROFILE, "methodology-library expected profile counts drifted")

    core = manifest.get("canonical_core_sources", [])
    domain = manifest.get("domain_methodology_sources", [])
    sources = core + domain if isinstance(core, list) and isinstance(domain, list) else []
    source_ids = [item.get("source_id") for item in sources if isinstance(item, dict)]
    _need(errors, len(sources) == 23 and len(set(source_ids)) == 23, "profiled source identity coverage is not exactly 23 unique sources")
    _need(errors, len(core) == 11 and all(item.get("source_format") == "markdown" for item in core), "core Markdown source profile drifted")
    _need(errors, len(domain) == 12 and all(item.get("source_format") == "docx" for item in domain), "domain DOCX source profile drifted")
    _need(
        errors,
        all(
            _sha256(item.get("checksum_sha256"))
            and item.get("import_status") == "profiled_original_not_committed"
            and item.get("external_redistribution_allowed") is False
            for item in sources
            if isinstance(item, dict)
        ),
        "source profiles no longer preserve checksum/import/redistribution boundary",
    )
    manifest_rules = manifest.get("rules", {})
    physical_gate = manifest.get("physical_import_gate", {})
    _need(
        errors,
        manifest.get("status") == "profiled_awaiting_original_file_import"
        and isinstance(manifest_rules, dict)
        and manifest_rules.get("original_source_files_committed") is False
        and manifest_rules.get("client_content_allowed") is False,
        "source manifest no longer preserves profiled-not-imported/global-library boundary",
    )
    _need(
        errors,
        isinstance(physical_gate, dict)
        and physical_gate.get("status") == "deferred_to_codex"
        and physical_gate.get("planned_test_id") == "IT-INGEST-001"
        and "no source binary added without Founder authority" in physical_gate.get("requirements", []),
        "physical import gate no longer remains explicit, deferred and Founder-controlled",
    )

    alias_rules = aliases.get("rules", {})
    _need(errors, len(aliases.get("aliases", [])) == 99, "alias coverage is not exactly 99")
    _need(
        errors,
        isinstance(alias_rules, dict)
        and alias_rules.get("aliases_are_navigation_only") is True
        and alias_rules.get("ambiguous_aliases_enter_quarantine") is True
        and alias_rules.get("unresolved_aliases_enter_quarantine") is True,
        "alias navigation/quarantine semantics drifted",
    )

    dependency_rules = dependencies.get("rules", {})
    _need(errors, len(dependencies.get("cases", [])) == 21, "dependency-resolution case coverage is not exactly 21")
    _need(
        errors,
        isinstance(dependency_rules, dict)
        and dependency_rules.get("unresolved_dependencies_are_not_invented") is True
        and dependency_rules.get("ambiguous_dependencies_are_quarantined") is True,
        "dependency gap/quarantine semantics drifted",
    )

    heading_records = headings.get("records", [])
    _need(
        errors,
        headings.get("record_count") == 154
        and len(heading_records) == 154
        and all(item.get("canonicalisation_state") == "indexed_not_promoted" for item in heading_records),
        "154 profiled headings no longer remain indexed_not_promoted",
    )

    collision_families = collisions.get("collision_families", [])
    _need(errors, len(collision_families) == 12, "collision-family coverage is not exactly 12")
    _need(
        errors,
        all(item.get("automatic_merge_allowed") is False for item in collision_families),
        "a methodology collision family now permits automatic merge",
    )

    example_rules = examples.get("rules", {})
    example_records = examples.get("examples", [])
    _need(errors, len(example_records) == 12, "representative method-record coverage is not exactly 12")
    _need(
        errors,
        isinstance(example_rules, dict)
        and example_rules.get("one_example_per_domain") is True
        and example_rules.get("not_canonical_until_review") is True
        and example_rules.get("protected_expression_not_reproduced") is True,
        "representative method-record review/protected-expression boundary drifted",
    )
    _need(
        errors,
        all(item.get("promotion_state") != "approved" for item in example_records),
        "a representative method example was silently promoted to approved",
    )

    retrieval_rules = retrieval.get("rules", {})
    _need(errors, retrieval.get("case_count") == 46 and len(retrieval.get("cases", [])) == 46, "retrieval gold-set coverage is not exactly 46")
    _need(
        errors,
        isinstance(retrieval_rules, dict)
        and retrieval_rules.get("exact_source_identity_required") is True
        and retrieval_rules.get("exact_heading_anchor_required") is True
        and retrieval_rules.get("prohibited_source_return_fails") is True
        and retrieval_rules.get("search_snippet_is_not_evidence") is True,
        "retrieval exact-source/anchor/prohibited-substitution semantics drifted",
    )

    radar_policy = radar.get("promotion_policy", {})
    _need(errors, len(radar.get("source_categories", [])) == 10, "Methodology Radar taxonomy is not exactly 10 categories")
    _need(
        errors,
        isinstance(radar_policy, dict)
        and radar_policy.get("automatic_promotion") is False
        and "Founder approval" in radar_policy.get("required", []),
        "Methodology Radar no longer blocks automatic promotion or Founder bypass",
    )

    method_admission = knowledge_cfg.get("method_admission", {})
    extraction = knowledge_cfg.get("extraction", {})
    rights = knowledge_cfg.get("rights", {})
    retrieval_cfg = knowledge_cfg.get("retrieval", {})
    _need(
        errors,
        isinstance(method_admission, dict)
        and method_admission.get("indexed_state") == "indexed_not_promoted"
        and method_admission.get("automatic_merge") is False
        and method_admission.get("automatic_promotion") is False
        and "Founder_approval" in method_admission.get("promotion_requires", []),
        "knowledge-ingestion method admission/promotion boundary drifted",
    )
    _need(
        errors,
        isinstance(extraction, dict)
        and extraction.get("instruction_like_content") == "mark_untrusted_and_never_execute"
        and extraction.get("empty_or_malformed_sources") == "quarantine",
        "knowledge extraction untrusted-content/quarantine boundary drifted",
    )
    _need(
        errors,
        isinstance(rights, dict)
        and rights.get("external_redistribution") == "blocked_until_explicit_rights_confirmation"
        and rights.get("distinctive_templates_or_diagrams") == "do_not_copy",
        "knowledge rights/protected-expression boundary drifted",
    )
    _need(
        errors,
        isinstance(retrieval_cfg, dict)
        and retrieval_cfg.get("search_snippets_not_evidence") is True
        and retrieval_cfg.get("full_source_provenance_retained") is True,
        "knowledge retrieval evidence/provenance boundary drifted",
    )

    contract = cfg.get("preimplementation_contract", {})
    corpus = contract.get("corpus_control", {}) if isinstance(contract, dict) else {}
    accounting = contract.get("source_accounting", {}) if isinstance(contract, dict) else {}
    identity = contract.get("identity_and_provenance", {}) if isinstance(contract, dict) else {}
    quarantine = contract.get("extraction_and_quarantine", {}) if isinstance(contract, dict) else {}
    admission = contract.get("method_admission", {}) if isinstance(contract, dict) else {}
    retrieval_acceptance = contract.get("retrieval_acceptance", {}) if isinstance(contract, dict) else {}
    release = contract.get("release_and_rollback", {}) if isinstance(contract, dict) else {}

    _need(
        errors,
        corpus.get("denominator") == "explicit_current_founder_approved_canonical_source_manifest"
        and corpus.get("current_23_source_profile_is_candidate_inventory_not_approval_evidence") is True
        and corpus.get("explicit_founder_approval_record_required_before_physical_import") is True
        and corpus.get("unapproved_discovery_expands_required_corpus") is False
        and corpus.get("source_identity_assigned_before_extraction") is True
        and corpus.get("no_source_binary_added_without_founder_authority") is True,
        "preimplementation corpus-control contract drifted",
    )
    _need(
        errors,
        accounting.get("allowed_current_dispositions") == ALLOWED_DISPOSITIONS
        and accounting.get("exactly_one_current_disposition_per_approved_source") is True
        and accounting.get("zero_silent_omissions") is True
        and accounting.get("exclusion_requires_recorded_reason") is True
        and accounting.get("disposition_history_preserved") is True,
        "approved-source disposition/accounting contract drifted",
    )
    _need(
        errors,
        identity.get("checksum_algorithm") == "sha256"
        and identity.get("original_bytes_immutable") is True
        and identity.get("aliases_do_not_replace_canonical_identity") is True
        and identity.get("source_passages_require_native_locator_where_available") is True
        and identity.get("generated_records_link_to_source_ids") is True
        and identity.get("transformation_history_required") is True
        and identity.get("supersession_preserves_prior_version") is True
        and identity.get("source_changes_create_new_review_work_not_silent_replacement") is True,
        "identity/provenance/versioning contract drifted",
    )
    _need(
        errors,
        all(
            quarantine.get(key) is True
            for key in [
                "markdown_and_docx_supported",
                "deterministic_chunking_required",
                "instruction_like_source_content_is_untrusted",
                "malformed_sources_quarantine",
                "ambiguous_aliases_quarantine",
                "unresolved_dependencies_remain_visible",
                "duplicate_identity_quarantine",
                "incomplete_method_records_quarantine",
            ]
        ),
        "extraction/quarantine contract drifted",
    )
    _need(
        errors,
        admission.get("indexed_headings_are_not_canonical_methods") is True
        and admission.get("automatic_merge") is False
        and admission.get("automatic_promotion") is False
        and all(
            admission.get(key) is True
            for key in [
                "complete_method_record_required",
                "provenance_review_required",
                "copyright_review_required",
                "evaluation_tests_required",
                "independent_review_required",
                "founder_approval_required_for_promotion",
                "collision_review_required_before_merge_or_supersession",
                "protected_expression_must_not_be_reproduced",
            ]
        ),
        "method admission/review/promotion contract drifted",
    )
    _need(
        errors,
        retrieval_acceptance.get("gold_case_count") == 46
        and all(
            retrieval_acceptance.get(key) is True
            for key in [
                "exact_source_identity_required",
                "exact_heading_anchor_required",
                "prohibited_source_return_fails",
                "ambiguity_must_not_auto_resolve",
                "access_and_rights_filters_mandatory",
                "search_snippet_is_not_evidence",
                "full_source_provenance_retained",
            ]
        ),
        "retrieval acceptance contract drifted",
    )
    _need(
        errors,
        all(
            release.get(key) is True
            for key in [
                "immutable_method_versions_required",
                "release_manifest_required",
                "prior_release_retained",
                "regression_failure_blocks_release",
                "rollback_restores_prior_canonical_release",
                "promotion_and_supersession_require_audit_history",
            ]
        ),
        "methodology release/supersession/rollback contract drifted",
    )

    mapping = cfg.get("implementation_mapping", {})
    _need(errors, list(mapping) == ["P1.1", "P1.2", "P1.3", "P1.4", "P1.5"], "methodology implementation mapping is not exactly P1.1-P1.5")
    _need(
        errors,
        all(
            isinstance(mapping.get(task), dict)
            and bool(mapping[task].get("purpose"))
            and bool(mapping[task].get("implementation_evidence_required"))
            for task in ["P1.1", "P1.2", "P1.3", "P1.4", "P1.5"]
        ),
        "P1 methodology implementation evidence mapping is incomplete",
    )

    chat_exit = cfg.get("chat_first_exit", {})
    _need(
        errors,
        all(
            chat_exit.get(key) is True
            for key in [
                "typed_contracts_defined",
                "profiled_candidate_inventory_defined",
                "alias_and_dependency_behavior_defined",
                "collision_behavior_defined",
                "representative_method_records_defined",
                "retrieval_gold_cases_defined",
                "rights_and_promotion_boundaries_defined",
                "implementation_task_mapping_defined",
            ]
        )
        and all(
            chat_exit.get(key) is False
            for key in [
                "physical_import_complete",
                "searchable_runtime_complete",
                "canonical_method_promotion_complete",
                "implementation_evidence_claimed",
                "imp_p1_authorized",
                "codex_start_authorized",
            ]
        ),
        "chat-first completion or implementation/authorization boundary drifted",
    )

    approval_boundaries = approval.get("boundaries", {})
    approval_semantics = approval.get("required_semantics", {})
    _need(
        errors,
        approval.get("status") == "template_not_approval"
        and approval.get("approval_type") == "methodology_library_canonical_source_manifest"
        and approval.get("source_manifest_path") == "knowledge/source-manifest.yaml"
        and approval.get("approved_source_ids") == []
        and approval.get("excluded_source_ids") == [],
        "Founder corpus approval template was converted into synthetic approval evidence",
    )
    _need(
        errors,
        isinstance(approval_semantics, dict)
        and all(value is True for value in approval_semantics.values()),
        "Founder corpus approval required semantics drifted",
    )
    _need(
        errors,
        isinstance(approval_boundaries, dict)
        and approval_boundaries.get("this_file_is_only_a_template") is True
        and all(
            approval_boundaries.get(key) is False
            for key in [
                "founder_approval_recorded",
                "physical_import_authorized",
                "imp_p1_authorized",
                "codex_start_authorized",
                "external_redistribution_authorized",
            ]
        ),
        "Founder corpus approval template authorization boundary drifted",
    )

    for model in REQUIRED_TYPED_MODELS:
        _need(errors, f"class {model}(BaseModel):" in typed, f"typed methodology contract missing: {model}")
    _need(
        errors,
        "source_ids: tuple[str, ...]" in typed
        and "Source passage requires a page, section, paragraph or line location." in typed
        and "Founder approval" in typed,
        "typed methodology provenance/location/promotion semantics drifted",
    )

    _need(
        errors,
        "100% of Founder-approved canonical methodology sources are accounted for" in backlog
        and "The accounting denominator is the explicit current Founder-approved canonical source manifest" in backlog
        and "Every approved source has exactly one current governed disposition; zero approved sources are silently omitted" in backlog
        and "Method-count coverage is reported as a secondary diagnostic only" in backlog
        and "Initial 150-plus method records are structured and searchable" not in backlog,
        "IMP-P1 backlog completion semantics no longer match methodology readiness",
    )
    _need(
        errors,
        all(f"### P1.{number} " in backlog for number in range(1, 6)),
        "IMP-P1 task namespace P1.1-P1.5 drifted",
    )

    _need(
        errors,
        "Phase 6 does **not** claim that the source files have been physically imported" in phase6
        and "promotion of the 154 source-local headings into canonical methods" in phase6
        and "These are integration or governance gates and must not be represented as complete." in phase6,
        "Phase 6 deferred implementation boundary was weakened",
    )

    required_doc_phrases = [
        "**Chat-first methodology-library design readiness: complete.**",
        "explicit current Founder-approved canonical source manifest",
        "The existing 23-source profile is the prepared candidate inventory.",
        "Every Founder-approved source must have exactly one current governed disposition",
        "The 154 profiled domain headings are source-local retrieval and reconstruction signals. They are **not** 154 canonical methods.",
        "The existing 46 source-grounded retrieval cases are the minimum governed gold set for implementation.",
        "This readiness package adds no IMP phase, no backlog task, no PCFA-07 obligation and no Phase-0 obligation.",
        "`imp_p1_authorized=false`.",
        "`codex_start_authorized=false`.",
    ]
    _need(errors, all(phrase in doc for phrase in required_doc_phrases), "methodology preimplementation human specification is incomplete or permissive")

    baseline_counts = baseline.get("counts", {})
    if isinstance(baseline_counts, dict) and baseline_counts:
        for key, expected_value in {
            "source_profiles": 23,
            "method_headings": 154,
            "aliases": 99,
            "dependency_cases": 21,
            "collision_families": 12,
            "method_record_examples": 12,
            "retrieval_cases": 46,
            "radar_categories": 10,
        }.items():
            if key in baseline_counts:
                _need(errors, baseline_counts.get(key) == expected_value, f"Phase 6 baseline count drifted: {key}")

    return list(dict.fromkeys(errors))


def run_self_test() -> int:
    baseline = load_snapshot()
    if errors := failures(baseline):
        raise SystemExit("Methodology readiness validation failed before self-test: " + "; ".join(errors))

    mutations: list[tuple[str, dict[str, Any]]] = []

    def mutated(label: str) -> dict[str, Any]:
        value = copy.deepcopy(baseline)
        mutations.append((label, value))
        return value

    value = mutated("source count drift")
    value["config"]["expected_profile"]["source_count"] = 22

    value = mutated("synthetic corpus approval")
    value["approval"]["boundaries"]["founder_approval_recorded"] = True

    value = mutated("unapproved discovery widens corpus")
    value["config"]["preimplementation_contract"]["corpus_control"]["unapproved_discovery_expands_required_corpus"] = True

    value = mutated("silent omission allowed")
    value["config"]["preimplementation_contract"]["source_accounting"]["zero_silent_omissions"] = False

    value = mutated("source disposition cardinality weakened")
    value["config"]["preimplementation_contract"]["source_accounting"]["exactly_one_current_disposition_per_approved_source"] = False

    value = mutated("provenance history removed")
    value["config"]["preimplementation_contract"]["identity_and_provenance"]["transformation_history_required"] = False

    value = mutated("automatic methodology promotion")
    value["knowledge_config"]["method_admission"]["automatic_promotion"] = True

    value = mutated("indexed heading promoted")
    value["headings"]["records"][0]["canonicalisation_state"] = "approved"

    value = mutated("automatic collision merge")
    value["collisions"]["collision_families"][0]["automatic_merge_allowed"] = True

    value = mutated("representative example made canonical")
    value["examples"]["examples"][0]["promotion_state"] = "approved"

    value = mutated("retrieval prohibited substitution allowed")
    value["retrieval"]["rules"]["prohibited_source_return_fails"] = False

    value = mutated("radar automatic promotion")
    value["radar"]["promotion_policy"]["automatic_promotion"] = True

    value = mutated("external redistribution relaxed")
    value["knowledge_config"]["rights"]["external_redistribution"] = "allowed"

    value = mutated("typed MethodRecord removed")
    value["typed_contracts"] = value["typed_contracts"].replace("class MethodRecord(BaseModel):", "class RemovedMethodRecord(BaseModel):", 1)

    value = mutated("historical count-only P1 gate restored")
    value["backlog"] = value["backlog"].replace(
        "100% of Founder-approved canonical methodology sources are accounted for",
        "Initial 150-plus method records are structured and searchable",
        1,
    )

    value = mutated("Phase 6 physical import falsely complete")
    value["phase6"] = value["phase6"].replace(
        "Phase 6 does **not** claim that the source files have been physically imported",
        "Phase 6 claims that the source files have been physically imported",
        1,
    )

    value = mutated("IMP-P1 authorization widened")
    value["config"]["chat_first_exit"]["imp_p1_authorized"] = True

    value = mutated("Codex launch authorization widened")
    value["config"]["chat_first_exit"]["codex_start_authorized"] = True

    value = mutated("approval template authorizes import")
    value["approval"]["boundaries"]["physical_import_authorized"] = True

    value = mutated("preimplementation document removes no-widening")
    value["doc"] = value["doc"].replace(
        "This readiness package adds no IMP phase, no backlog task, no PCFA-07 obligation and no Phase-0 obligation.",
        "This readiness package adds IMP-P1 scope.",
        1,
    )

    rejected = 0
    for label, candidate in mutations:
        if not failures(candidate):
            raise SystemExit(f"Methodology readiness mutation not rejected: {label}")
        rejected += 1
    return rejected


def main() -> None:
    errors = failures()
    if errors:
        raise SystemExit("Methodology library preimplementation readiness validation failed: " + "; ".join(errors))
    rejected = run_self_test()
    print(
        "Methodology library preimplementation readiness validation passed: "
        f"sources=23, core=11, domain=12, method_headings=154, aliases=99, "
        f"dependency_cases=21, collision_families=12, method_examples=12, retrieval_cases=46, "
        f"radar_categories=10, mutation_cases_rejected={rejected}, "
        "design_readiness=complete, founder_corpus_approval=pending_explicit_record, "
        "physical_import=false, imp_p1_authorized=false, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
