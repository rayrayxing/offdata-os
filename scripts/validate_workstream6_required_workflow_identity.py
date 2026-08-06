from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from build_workstream6_required_workflow_identity import build_records

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "contracts" / "workstream6-required-workflow-identity.json"
SCHEMA_PATH = ROOT / "schemas" / "workstream6-required-workflow-identity.schema.json"
REPORT_PATH = ROOT / "reports" / "workstream6-required-workflow-identity-evidence.md"
CHECK = "Validate final pre-Codex canonical handoff and complete release"


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


def _scan_workflows() -> list[dict[str, Any]]:
    workflow_root = ROOT / ".github/workflows"
    paths = sorted([*workflow_root.glob("*.yml"), *workflow_root.glob("*.yaml")])
    result: list[dict[str, Any]] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        workflow_name = ""
        current_job = ""
        jobs: dict[str, str] = {}
        triggers: list[str] = []
        in_jobs = False
        for line in text.splitlines():
            if line.startswith("name: ") and not workflow_name:
                workflow_name = line.split(":", 1)[1].strip()
            trigger_match = re.match(
                r"^  (push|pull_request|workflow_dispatch|workflow_call):",
                line,
            )
            if trigger_match:
                triggers.append(trigger_match.group(1))
            if line == "jobs:":
                in_jobs = True
                continue
            if not in_jobs:
                continue
            job_match = re.match(r"^  ([A-Za-z0-9_-]+):\s*$", line)
            if job_match:
                current_job = job_match.group(1)
                jobs[current_job] = ""
                continue
            name_match = re.match(r"^    name:\s*(.+)$", line)
            if name_match and current_job:
                jobs[current_job] = name_match.group(1).strip()
        result.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "workflow_name": workflow_name,
                "triggers": triggers,
                "jobs": jobs,
                "text": text,
            }
        )
    return result


def _failures(
    contract: dict[str, Any],
    documents: dict[str, str],
    workflows: list[dict[str, Any]],
) -> list[str]:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    require(contract.get("work_package_id") == "WS6.6", "work package is not WS6.6")
    require(
        contract.get("base_main_sha") == "08f043b8dd1102bebd0186d3fc52041261f51920",
        "exact WS6.5 base is missing",
    )
    require(
        contract.get("status") == "required_workflow_identity_reserved_fail_closed",
        "status is invalid",
    )

    identity = contract.get("canonical_identity", {})
    require(
        identity.get("workflow_file") == ".github/workflows/workstream6-final-pre-codex.yml",
        "canonical workflow path is invalid",
    )
    require(
        identity.get("workflow_name") == "Final pre-Codex canonical handoff and release",
        "canonical workflow name is invalid",
    )
    require(identity.get("job_key") == "validate-final-pre-codex", "canonical job key is invalid")
    require(identity.get("job_name") == CHECK, "canonical job name is invalid")
    require(identity.get("identity_is_case_sensitive") is True, "case-sensitive rule is missing")
    require(
        identity.get("identity_is_whitespace_sensitive") is True,
        "whitespace-sensitive rule is missing",
    )

    occurrences: list[tuple[str, str]] = []
    for workflow in workflows:
        for key, name in workflow["jobs"].items():
            if name == CHECK:
                occurrences.append((workflow["path"], key))
    require(
        occurrences == [(identity.get("workflow_file"), identity.get("job_key"))],
        f"canonical identity occurrence set is invalid: {occurrences}",
    )

    canonical = next(
        (workflow for workflow in workflows if workflow["path"] == identity.get("workflow_file")),
        None,
    )
    require(canonical is not None, "canonical workflow is missing")
    if canonical:
        require(
            canonical["workflow_name"] == identity.get("workflow_name"),
            "observed workflow name is invalid",
        )
        require(canonical["triggers"] == ["workflow_dispatch"], "canonical workflow must be manual-only")
        require("exit 1" in canonical["text"], "canonical workflow does not fail closed")
        require("WS6.15" in canonical["text"], "WS6.15 activation marker is missing")
        require("WS6.16" in canonical["text"], "WS6.16 release marker is missing")

    activation = contract.get("activation", {})
    require(activation.get("state") == "reserved_fail_closed", "reservation state is invalid")
    require(
        activation.get("allowed_triggers") == ["workflow_dispatch"],
        "allowed trigger set is invalid",
    )
    require(
        activation.get("automatic_triggers_enabled") is False,
        "automatic triggers were enabled early",
    )
    require(
        activation.get("manual_dispatch_must_fail") is True,
        "manual dispatch fail-closed rule is missing",
    )
    require(activation.get("activation_work_package") == "WS6.15", "activation package is invalid")
    require(
        activation.get("permanent_release_work_package") == "WS6.16",
        "release package is invalid",
    )
    require(
        activation.get("hosted_branch_protection_configured") is False,
        "hosted enforcement was claimed early",
    )
    require(activation.get("final_release_verified") is False, "final release was claimed early")

    superseded = contract.get("superseded_required_checks", [])
    require(
        isinstance(superseded, list) and len(superseded) == 2,
        "superseded identity set is invalid",
    )
    for item in superseded:
        require(item.get("current") is False, "predecessor identity remains current")
        require(
            item.get("classification") == "retained_predecessor_identity",
            "predecessor classification is invalid",
        )
        require(item.get("job_name") != CHECK, "predecessor identity aliases canonical check")

    package = contract.get("package_check_rule", {})
    require(
        package.get("may_satisfy_final_branch_protection") is False,
        "package check may satisfy final protection",
    )
    require(
        package.get("example")
        == "Validate WS6.6 required workflow identity and complete prior components",
        "package check example is invalid",
    )

    require(contract.get("authority_surface_count") == 6, "authority surface count is invalid")
    require(
        set(documents) == set(contract.get("authority_surfaces", [])),
        "authority document set is incomplete",
    )
    tokens = contract.get("required_surface_tokens", {})
    predecessor_names = [item.get("job_name") for item in superseded]
    for relative, text in documents.items():
        for token in tokens.get("all", []):
            require(token in text, f"common token missing from {relative}: {token}")
        for token in tokens.get(relative, []):
            require(token in text, f"required token missing from {relative}: {token}")
        for old in predecessor_names:
            require(
                old not in text,
                f"superseded required check remains in current authority: {relative}",
            )

    require(contract.get("closed_defects") == ["WS6-CONSIST-003"], "closed defect set is invalid")
    require(
        contract.get("remaining_blocking_defects") == ["WS6-BLOCK-006"],
        "remaining blocker set is invalid",
    )
    completion = contract.get("completion", {})
    for key in (
        "all_required_prior_components_pass",
        "ws66_complete",
        "canonical_identity_unique",
        "predecessor_identities_superseded",
        "reservation_fail_closed",
    ):
        require(completion.get(key) is True, f"completion flag is false: {key}")
    require(completion.get("final_workflow_active") is False, "final workflow was activated early")
    require(
        completion.get("final_reconciliation_complete") is False,
        "final reconciliation was claimed early",
    )
    require(
        completion.get("all_blocking_defects_closed") is False,
        "all blockers were claimed closed early",
    )
    require(
        completion.get("next_permitted_work_package") == "WS6.7",
        "next work package is invalid",
    )

    boundaries = contract.get("boundaries", {})
    require(
        boundaries.get("founder_accountability_preserved") is True,
        "Founder accountability is missing",
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
            "WS6.6 schema validation failed:\n- "
            + "\n- ".join(error.message for error in errors)
        )

    expected, report = build_records()
    if _canonical(contract) != _canonical(expected):
        raise SystemExit("WS6.6 contract is not deterministic")
    if REPORT_PATH.read_text(encoding="utf-8") != report:
        raise SystemExit("WS6.6 evidence report is not deterministic")

    documents = {
        relative: (ROOT / relative).read_text(encoding="utf-8")
        for relative in contract["authority_surfaces"]
    }
    workflows = _scan_workflows()
    failures = _failures(contract, documents, workflows)
    if failures:
        raise SystemExit("WS6.6 semantic validation failed:\n- " + "\n- ".join(failures))

    cases: list[tuple[tuple[str, ...], Any]] = [
        (("work_package_id",), "WS6.5"),
        (("base_main_sha",), "0" * 40),
        (("status",), "active"),
        (("canonical_identity", "job_name"), CHECK + " "),
        (("canonical_identity", "workflow_file"), ".github/workflows/other.yml"),
        (("activation", "state"), "active"),
        (("activation", "allowed_triggers"), ["push"]),
        (("activation", "automatic_triggers_enabled"), True),
        (("activation", "manual_dispatch_must_fail"), False),
        (("activation", "hosted_branch_protection_configured"), True),
        (("activation", "final_release_verified"), True),
        (("package_check_rule", "may_satisfy_final_branch_protection"), True),
        (("closed_defects",), []),
        (("remaining_blocking_defects",), []),
        (("completion", "ws66_complete"), False),
        (("completion", "canonical_identity_unique"), False),
        (("completion", "reservation_fail_closed"), False),
        (("completion", "final_workflow_active"), True),
        (("completion", "final_reconciliation_complete"), True),
        (("completion", "all_blocking_defects_closed"), True),
        (("completion", "next_permitted_work_package"), "WS6.8"),
        (("boundaries", "codex_start_authorized"), True),
        (("boundaries", "phase0_implementation_authorized"), True),
        (("boundaries", "founder_accountability_preserved"), False),
    ]
    rejected = 0
    for path, replacement in cases:
        mutated = copy.deepcopy(contract)
        _set(mutated, path, replacement)
        if _failures(mutated, documents, workflows):
            rejected += 1
        else:
            raise SystemExit(
                f"WS6.6 contract mutation was not rejected: {'.'.join(path)}"
            )

    duplicate = copy.deepcopy(workflows)
    duplicate.append(
        {
            "path": ".github/workflows/duplicate.yml",
            "workflow_name": "duplicate",
            "triggers": ["pull_request"],
            "jobs": {"duplicate": CHECK},
            "text": CHECK,
        }
    )
    if _failures(contract, documents, duplicate):
        rejected += 1
    else:
        raise SystemExit("WS6.6 duplicate check mutation was not rejected")

    automatic = copy.deepcopy(workflows)
    for item in automatic:
        if item["path"] == contract["canonical_identity"]["workflow_file"]:
            item["triggers"] = ["push", "workflow_dispatch"]
    if _failures(contract, documents, automatic):
        rejected += 1
    else:
        raise SystemExit("WS6.6 automatic-trigger mutation was not rejected")

    for relative in documents:
        mutated_documents = dict(documents)
        mutated_documents[relative] = mutated_documents[relative].replace(CHECK, "REMOVED")
        if _failures(contract, mutated_documents, workflows):
            rejected += 1
        else:
            raise SystemExit(
                f"WS6.6 authority identity mutation was not rejected: {relative}"
            )

    print(
        "WS6.6 required workflow identity passed: "
        f"workflows_scanned={len(workflows)}, authority_surfaces=6, "
        f"{rejected} mutations rejected, next=WS6.7, "
        "codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
