from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from build_workstream6_current_status import build_records

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "contracts" / "workstream6-current-status.json"
SCHEMA_PATH = ROOT / "schemas" / "workstream6-current-status.schema.json"
REPORT_PATH = ROOT / "reports" / "workstream6-current-status-evidence.md"
CANONICAL_STATUS_FILES = {
    "README.md",
    "docs/00-START-HERE.md",
    "docs/14-CODEX-KICKOFF.md",
    "docs/19-PHASE-0-VALIDATION-ADDENDUM.md",
    "docs/20-DEVELOPMENT-STATUS.md",
}


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _canonical(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ) + "\n"


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def _document_failures(
    contract: dict[str, Any], documents: dict[str, str]
) -> list[str]:
    failures: list[str] = []
    status = contract["canonical_status_phrase"]
    forbidden = contract["forbidden_patterns"]
    common = contract["required_common_tokens"]
    per_file = contract["required_file_tokens"]
    for relative in contract["current_authority_files"]:
        text = documents.get(relative, "")
        if not text:
            failures.append(f"missing document text: {relative}")
            continue
        if relative in CANONICAL_STATUS_FILES and status not in text:
            failures.append(f"canonical status phrase missing: {relative}")
        for token in common:
            if token not in text:
                failures.append(
                    f"required current token missing from {relative}: {token}"
                )
        for token in per_file[relative]:
            if token not in text:
                failures.append(
                    f"required file token missing from {relative}: {token}"
                )
        for pattern in forbidden:
            if pattern in text:
                failures.append(f"stale-state pattern in {relative}: {pattern}")
    return failures


def _contract_failures(contract: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    require(contract.get("work_package_id") == "WS6.3", "work package is not WS6.3")
    require(
        contract.get("base_main_sha")
        == "1b518253abb187bbc31b1c809ee4f7ca5506f7e8",
        "exact WS6.2 base is missing",
    )
    require(
        contract.get("status") == "current_status_documents_reconciled",
        "WS6.3 status is invalid",
    )
    require(
        contract.get("document_count") == 6,
        "current authority surface count is invalid",
    )
    require(
        contract.get("forbidden_pattern_count", 0) >= 13,
        "stale-state scanner pattern floor is too low",
    )
    require(
        set(contract.get("document_fingerprints", {}))
        == set(contract.get("current_authority_files", [])),
        "fingerprint set is incomplete",
    )
    repairs = contract.get("repairs", {})
    for key in (
        "one_canonical_status_phrase",
        "obsolete_pr_sequence_removed",
        "obsolete_status_check_removed",
        "pre_permit_branch_creation_removed",
        "current_issue19_body_prepared",
        "historical_completion_evidence_preserved",
    ):
        require(repairs.get(key) is True, f"repair {key} is incomplete")
    require(
        contract.get("closed_defects")
        == ["WS6-BLOCK-003", "WS6-CONSIST-008"],
        "closed defect set is invalid",
    )
    require(
        contract.get("remaining_blocking_defects") == ["WS6-BLOCK-006"],
        "remaining blocker set is invalid",
    )
    completion = contract.get("completion", {})
    require(
        completion.get("all_required_prior_components_pass") is True,
        "prior components are incomplete",
    )
    require(completion.get("ws63_complete") is True, "WS6.3 is incomplete")
    require(
        completion.get("final_reconciliation_complete") is False,
        "final reconciliation was claimed early",
    )
    require(
        completion.get("all_blocking_defects_closed") is False,
        "all blockers were claimed closed early",
    )
    require(
        completion.get("next_permitted_work_package") == "WS6.4",
        "next work package is invalid",
    )
    boundaries = contract.get("boundaries", {})
    require(
        boundaries.get("founder_accountability_preserved") is True,
        "Founder accountability was not preserved",
    )
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
        raise SystemExit(
            "WS6.3 schema validation failed:\n- "
            + "\n- ".join(error.message for error in errors)
        )
    expected, report = build_records()
    if _canonical(contract) != _canonical(expected):
        raise SystemExit("WS6.3 contract is not deterministic")
    if REPORT_PATH.read_text(encoding="utf-8") != report:
        raise SystemExit("WS6.3 evidence report is not deterministic")
    semantic = _contract_failures(contract)
    if semantic:
        raise SystemExit(
            "WS6.3 contract validation failed:\n- " + "\n- ".join(semantic)
        )
    documents = {
        relative: (ROOT / relative).read_text(encoding="utf-8")
        for relative in contract["current_authority_files"]
    }
    document_failures = _document_failures(contract, documents)
    if document_failures:
        raise SystemExit(
            "WS6.3 stale-state scan failed:\n- "
            + "\n- ".join(document_failures)
        )
    for item in contract["document_evidence"]:
        if _git_blob_sha(ROOT / item["path"]) != item["git_blob_sha"]:
            raise SystemExit(f"WS6.3 fingerprint drift: {item['path']}")

    contract_cases = [
        (("work_package_id",), "WS6.2"),
        (("base_main_sha",), "0" * 40),
        (("status",), "pending"),
        (("document_count",), 5),
        (("forbidden_pattern_count",), 1),
        (("repairs", "one_canonical_status_phrase"), False),
        (("repairs", "obsolete_pr_sequence_removed"), False),
        (("repairs", "obsolete_status_check_removed"), False),
        (("repairs", "pre_permit_branch_creation_removed"), False),
        (("repairs", "current_issue19_body_prepared"), False),
        (("closed_defects",), ["WS6-BLOCK-003"]),
        (("remaining_blocking_defects",), []),
        (("completion", "all_required_prior_components_pass"), False),
        (("completion", "ws63_complete"), False),
        (("completion", "final_reconciliation_complete"), True),
        (("completion", "all_blocking_defects_closed"), True),
        (("completion", "next_permitted_work_package"), "WS6.5"),
        (("boundaries", "phase0_implementation_authorized"), True),
        (("boundaries", "founder_accountability_preserved"), False),
    ]
    rejected = 0
    for path, replacement in contract_cases:
        mutated = copy.deepcopy(contract)
        _set(mutated, path, replacement)
        if _contract_failures(mutated):
            rejected += 1
        else:
            raise SystemExit(
                f"WS6.3 contract mutation was not rejected: {'.'.join(path)}"
            )

    for pattern in contract["forbidden_patterns"]:
        mutated_docs = dict(documents)
        mutated_docs["README.md"] += f"\n{pattern}\n"
        if _document_failures(contract, mutated_docs):
            rejected += 1
        else:
            raise SystemExit(
                f"WS6.3 stale-state mutation was not rejected: {pattern}"
            )
    for token in contract["required_common_tokens"]:
        mutated_docs = dict(documents)
        mutated_docs["README.md"] = mutated_docs["README.md"].replace(
            token, "REMOVED"
        )
        if _document_failures(contract, mutated_docs):
            rejected += 1
        else:
            raise SystemExit(
                f"WS6.3 required-token mutation was not rejected: {token}"
            )
    mutated_docs = dict(documents)
    mutated_docs["docs/20-DEVELOPMENT-STATUS.md"] = mutated_docs[
        "docs/20-DEVELOPMENT-STATUS.md"
    ].replace(contract["canonical_status_phrase"], "Repository is ready for Codex.", 1)
    if _document_failures(contract, mutated_docs):
        rejected += 1
    else:
        raise SystemExit("WS6.3 canonical-status mutation was not rejected")

    print(
        f"WS6.3 current-status reconciliation passed: documents=6, "
        f"{rejected} mutations rejected, closed_defects=2, "
        "remaining_blockers=1, next=WS6.4, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
