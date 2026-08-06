from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from build_workstream6_phase_namespace import build_records

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "contracts" / "workstream6-phase-namespace.json"
SCHEMA_PATH = ROOT / "schemas" / "workstream6-phase-namespace.schema.json"
REPORT_PATH = ROOT / "reports" / "workstream6-phase-namespace-evidence.md"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"


def _semantic_failures(contract: dict[str, Any], documents: dict[str, str]) -> list[str]:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    require(contract.get("work_package_id") == "WS6.5", "work package is not WS6.5")
    require(contract.get("base_main_sha") == "fbfd052e8b76162468f7ee1ff5cd11dad4829497", "exact WS6.4 base is missing")
    require(contract.get("status") == "phase_namespace_normalized", "status is invalid")
    require(contract.get("namespace_order") == ["CF", "PCR", "WS", "IMP"], "namespace order is invalid")
    namespaces = contract.get("namespaces", [])
    require(isinstance(namespaces, list) and len(namespaces) == 4, "namespace count is invalid")
    ids: list[str] = []
    for item in namespaces:
        if isinstance(item, dict):
            ids.extend(str(value) for value in item.get("canonical_ids", []))
            require(item.get("implementation_authority") is False, f"{item.get('prefix')} grants implementation authority")
    require(len(ids) == 49, "canonical namespace id count is invalid")
    require(contract.get("namespace_id_count") == 49, "recorded namespace id count is invalid")
    require(len(ids) == len(set(ids)), "canonical namespace ids overlap")
    require(ids[:7] == [f"CF-P{i}" for i in range(1, 8)], "CF namespace is invalid")
    require([f"PCR-{i:02d}" for i in range(1, 11)] == ids[7:17], "PCR namespace is invalid")
    require(all(f"IMP-P{i}" in ids for i in range(13)), "IMP namespace is incomplete")

    aliases = contract.get("legacy_aliases", [])
    require(isinstance(aliases, list) and len(aliases) == 14, "legacy alias count is invalid")
    require(contract.get("legacy_alias_count") == 14, "recorded legacy alias count is invalid")
    alias_names = [item.get("alias") for item in aliases if isinstance(item, dict)]
    require(len(alias_names) == len(set(alias_names)), "legacy aliases are not unique")
    require(all(item.get("classification") == "legacy_display_alias" for item in aliases if isinstance(item, dict)), "legacy alias classification is invalid")
    require(all(item.get("allowed_only_when_explicitly_mapped") is True for item in aliases if isinstance(item, dict)), "legacy alias mapping rule is invalid")

    stable = contract.get("stable_compatibility_identifiers", {})
    require(stable.get("task_ids") == ["P0.1", "P0.2", "P0.3", "P0.4"], "stable task ids drifted")
    require("codex/phase-0-foundation" in stable.get("paths", []), "stable branch path is missing")
    require("phase0_implementation_authorized" in stable.get("gate_keys", []), "stable gate keys are incomplete")

    surfaces = contract.get("normalization_surfaces", [])
    alias_surfaces = set(contract.get("legacy_alias_surfaces", []))
    require(isinstance(surfaces, list) and len(surfaces) == 9, "normalization surface count is invalid")
    require(alias_surfaces == {"handoff/codex-phase0-issue-final.md"}, "legacy alias surface set is invalid")
    require(contract.get("surface_count") == 9, "surface evidence count is invalid")
    require(set(documents) == set(surfaces), "normalization document set is incomplete")
    patterns = contract.get("forbidden_unqualified_patterns", [])
    required_tokens = contract.get("required_tokens", {})
    alias_map = {str(item.get("alias")): str(item.get("canonical_id")) for item in aliases if isinstance(item, dict)}
    for relative in surfaces:
        text = documents.get(relative, "")
        require(bool(text), f"normalization surface is missing: {relative}")
        if relative not in alias_surfaces:
            for token in required_tokens.get("all_surfaces", []):
                require(token in text, f"required common token missing from {relative}: {token}")
        for token in required_tokens.get(relative, []):
            require(token in text, f"required token missing from {relative}: {token}")
        if relative in alias_surfaces:
            observed: set[str] = set()
            for pattern in patterns:
                for match in re.finditer(str(pattern), text):
                    observed.add(match.group(0))
            require(bool(observed), f"legacy alias surface has no mapped aliases: {relative}")
            for alias in observed:
                require(alias in alias_map, f"unmapped legacy phase alias in {relative}: {alias}")
                require(alias_map.get(alias, "").startswith("IMP-P"), f"legacy alias does not map to IMP namespace: {alias}")
        else:
            for pattern in patterns:
                require(re.search(str(pattern), text) is None, f"unqualified phase alias remains in {relative}: {pattern}")

    backlog = documents.get("docs/11-BUILD-BACKLOG.md", "")
    for phase in range(13):
        require(f"## IMP-P{phase} —" in backlog, f"IMP-P{phase} backlog heading is missing")
        require(f"### IMP-P{phase} gate" in backlog, f"IMP-P{phase} gate is missing")
    for task in ("P0.1", "P0.2", "P0.3", "P0.4"):
        require(task in backlog, f"IMP-P0 task missing: {task}")

    instruction = contract.get("founder_instruction", {})
    require(instruction.get("founder_approval_intent_received") is True, "Founder approval intent was not recorded")
    require(instruction.get("effective_scope") == "WS6.5_chat_first_only", "Founder instruction scope is unsafe")
    for key in ("exact_final_main_sha_bound", "final_release_bound", "hosted_controls_verified", "clean_macos_verified", "launch_permit_issued", "imp_p0_start_authorized"):
        require(instruction.get(key) is False, f"Founder instruction incorrectly satisfies {key}")

    require(contract.get("closed_defects") == ["WS6-CONSIST-002"], "closed defect set is invalid")
    require(contract.get("remaining_blocking_defects") == ["WS6-BLOCK-006"], "remaining blocker set is invalid")
    completion = contract.get("completion", {})
    for key in ("all_required_prior_components_pass", "ws65_complete", "namespace_disjoint", "current_authority_normalized", "compatibility_identifiers_preserved"):
        require(completion.get(key) is True, f"completion flag is false: {key}")
    require(completion.get("final_reconciliation_complete") is False, "final reconciliation was claimed early")
    require(completion.get("all_blocking_defects_closed") is False, "all blockers were claimed closed early")
    require(completion.get("next_permitted_work_package") == "WS6.6", "next work package is invalid")

    boundaries = contract.get("boundaries", {})
    require(boundaries.get("founder_accountability_preserved") is True, "Founder accountability was not preserved")
    for key, value in boundaries.items():
        if key != "founder_accountability_preserved":
            require(value is False, f"boundary {key} must remain false")
    return failures


def _set(value: dict[str, Any], path: tuple[str, ...], replacement: Any) -> None:
    node: Any = value
    for part in path[:-1]:
        node = node[part]
    node[path[-1]] = replacement


def main() -> None:
    contract = _load(CONTRACT_PATH)
    schema = _load(SCHEMA_PATH)
    errors = list(Draft202012Validator(schema).iter_errors(contract))
    if errors:
        raise SystemExit("WS6.5 schema validation failed:\n- " + "\n- ".join(error.message for error in errors))
    expected, report = build_records()
    if _canonical(contract) != _canonical(expected):
        raise SystemExit("WS6.5 contract is not deterministic")
    if REPORT_PATH.read_text(encoding="utf-8") != report:
        raise SystemExit("WS6.5 evidence report is not deterministic")
    documents = {relative: (ROOT / relative).read_text(encoding="utf-8") for relative in contract["normalization_surfaces"]}
    failures = _semantic_failures(contract, documents)
    if failures:
        raise SystemExit("WS6.5 semantic validation failed:\n- " + "\n- ".join(failures))

    cases = [
        (("work_package_id",), "WS6.4"), (("base_main_sha",), "0" * 40),
        (("namespace_order",), ["IMP", "CF", "PCR", "WS"]), (("namespace_id_count",), 48),
        (("legacy_alias_count",), 13), (("founder_instruction", "effective_scope"), "IMP-P0"),
        (("founder_instruction", "exact_final_main_sha_bound"), True), (("founder_instruction", "launch_permit_issued"), True),
        (("founder_instruction", "imp_p0_start_authorized"), True), (("closed_defects",), []),
        (("remaining_blocking_defects",), []), (("completion", "ws65_complete"), False),
        (("completion", "namespace_disjoint"), False), (("completion", "final_reconciliation_complete"), True),
        (("completion", "all_blocking_defects_closed"), True), (("completion", "next_permitted_work_package"), "WS6.7"),
        (("boundaries", "phase0_implementation_authorized"), True), (("boundaries", "founder_accountability_preserved"), False),
    ]
    rejected = 0
    for path, replacement in cases:
        mutated = copy.deepcopy(contract)
        _set(mutated, path, replacement)
        if _semantic_failures(mutated, documents):
            rejected += 1
        else:
            raise SystemExit(f"WS6.5 contract mutation was not rejected: {'.'.join(path)}")

    for pattern in contract["forbidden_unqualified_patterns"]:
        mutated_docs = dict(documents)
        mutated_docs["README.md"] += f"\n{pattern.replace(chr(92)+'b', '')}\n"
        if _semantic_failures(contract, mutated_docs):
            rejected += 1
        else:
            raise SystemExit(f"WS6.5 alias mutation was not rejected: {pattern}")

    mutated_docs = dict(documents)
    mutated_docs["docs/11-BUILD-BACKLOG.md"] = mutated_docs["docs/11-BUILD-BACKLOG.md"].replace("## IMP-P12 —", "## REMOVED —", 1)
    if _semantic_failures(contract, mutated_docs):
        rejected += 1
    else:
        raise SystemExit("WS6.5 backlog namespace mutation was not rejected")

    print(
        "WS6.5 phase namespace normalization passed: "
        f"canonical_ids={contract['namespace_id_count']}, surfaces={contract['surface_count']}, "
        f"aliases={contract['legacy_alias_count']}, {rejected} mutations rejected, "
        "next=WS6.6, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
