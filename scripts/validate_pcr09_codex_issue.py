from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import yaml
from jsonschema import Draft202012Validator

from build_pcr09_codex_issue import build_codex_issue

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "configs" / "codex-phase0-issue.yaml"
CONTRACT = ROOT / "contracts" / "codex-phase0-issue.json"
SCHEMA = ROOT / "schemas" / "codex-phase0-issue.schema.json"
MARKDOWN = ROOT / "handoff" / "codex-phase0-issue.md"
DOC = ROOT / "docs" / "48-PCR-09-FIRST-CODEX-ISSUE-REWRITE.md"
Mutation = Callable[[dict[str, Any]], None]

EXPECTED_TASKS = ["P0.1", "P0.2", "P0.3", "P0.4"]
EXPECTED_ACTIVATION = {
    "pcr03_merged_to_main", "pcr04_merged_to_main", "pcr05_merged_to_main",
    "pcr06_merged_to_main", "pcr07_merged_to_main", "pcr08_merged_to_main",
    "pcr09_merged_to_main", "github_hosted_controls_in_issue_19_verified",
    "explicit_founder_phase_0_approval_received", "clean_macos_environment_available",
}
DENIED = {
    "issue_rewrite_is_codex_start", "codex_start_authorized", "phase1_authorized",
    "runtime_activation_authorized", "hermes_activation_authorized",
    "northstar_implementation_authorized", "initial_operating_controls_activation_authorized",
    "real_client_data_enabled", "external_actions_authorized", "paid_services_authorized",
    "production_deployment_authorized", "autonomous_merge_authorized",
}


def load(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8")) if path.suffix in {".yaml", ".yml"} else json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate(value: dict[str, Any], markdown: str) -> None:
    require(value["phase_id"] == "PCR-09", "phase")
    require(value["status"] == "canonical_issue_prepared", "status")
    target = value["target_issue"]
    require(target["number"] == 1, "target issue")
    require(target["rewritten_title"].startswith("Codex Phase 0"), "title")
    require(target["canonical_body_path"] == "handoff/codex-phase0-issue.md", "body path")
    supersession = value["supersession"]
    require(supersession["issue_numbers"] == [2], "superseded issue")
    require(supersession["treatment"] == "close_as_duplicate_after_target_rewrite", "supersession treatment")
    require(supersession["preserve_history"] is True, "history")
    authority = value["authority"]
    require(authority["controlling_instruction"] == "AGENTS.md", "authority")
    require(authority["machine_handoff"] == "handoff/codex-phase0-handoff.json", "handoff")
    require(authority["issue_is_execution_summary_not_authority"] is True, "issue authority")
    require(authority["founder_explicit_approval_required_to_start"] is True, "Founder approval")
    require(all(value["rewrite_rules"].values()), "rewrite rules")
    require(all(value["boundaries"][key] is False for key in DENIED), "denied boundary")
    require(value["boundaries"]["founder_accountability_preserved"] is True, "accountability")

    snapshot = value["handoff_snapshot"]
    tasks = snapshot["task_graph"]
    require([item["id"] for item in tasks] == EXPECTED_TASKS, "task identity")
    require(tasks[0]["dependencies"] == [], "P0.1 dependency")
    require(tasks[1]["dependencies"] == ["P0.1"], "P0.2 dependency")
    require(tasks[2]["dependencies"] == ["P0.1", "P0.2"], "P0.3 dependency")
    require(tasks[3]["dependencies"] == ["P0.1"], "P0.4 dependency")
    require(snapshot["target"]["phase_number"] == 0, "phase number")
    require(snapshot["target"]["maximum_authorised_phase"] == 0, "maximum phase")
    require(snapshot["target"]["next_phase_is_prohibited"] is True, "next phase")
    require(snapshot["execution"]["branch_name"] == "codex/phase-0-foundation", "branch")
    require(snapshot["execution"]["pull_request_mode"] == "draft", "draft PR")
    require(snapshot["execution"]["merge_requires_founder_approval"] is True, "merge approval")
    require(set(snapshot["activation_conditions"]) == EXPECTED_ACTIVATION, "activation")
    require("python scripts/build_pcr09_codex_issue.py" in snapshot["execution"]["required_commands"], "PCR-09 build command")
    require("python scripts/validate_pcr09_codex_issue.py" in snapshot["execution"]["required_commands"], "PCR-09 validation command")
    require("progress_beyond_phase_0" in snapshot["prohibited_actions"], "phase prohibition")
    require("phase_boundary_would_be_crossed" in snapshot["stop_conditions"], "phase stop")

    generated = value["generated_issue"]
    require(generated["title"] == target["rewritten_title"], "generated title")
    require(generated["body_sha256"] == hashlib.sha256(markdown.encode("utf-8")).hexdigest(), "body digest")
    require(generated["body_character_count"] == len(markdown) <= 65536, "body length")
    require(generated["github_issue_sync_verified"] is False, "sync evidence")
    required_tokens = [
        "NOT AUTHORISED TO START", "AGENTS.md", "handoff/codex-phase0-handoff.json",
        "pcr09_merged_to_main", "codex/phase-0-foundation", "DRAFT pull request",
        "Do not begin Phase 1", "Issue #2 is superseded", "Historical issue comments",
        "python scripts/validate_pcr09_codex_issue.py", "## Rollback",
    ]
    for token in required_tokens:
        require(token in markdown, f"markdown token {token}")
    require("51 unit-test" not in markdown and "247 tests" not in markdown, "dynamic test count")

    readiness = value["readiness_snapshot"]
    expected = {
        "task_count": 4,
        "read_order_count": 26,
        "prerequisite_record_count": 9,
        "required_command_count": 36,
        "prohibited_action_count": 11,
        "stop_condition_count": 8,
        "activation_condition_count": 10,
        "completion_report_field_count": 11,
        "superseded_issue_count": 1,
    }
    require(all(readiness[key] == expected_value for key, expected_value in expected.items()), "readiness counts")
    require(all(readiness["checks"].values()), "readiness checks")
    require(readiness["local_prerequisites_passed"] is True, "local prerequisites")
    require(readiness["github_issue_sync_verified"] is False, "remote evidence honesty")
    require(readiness["codex_start_authorized"] is False, "Codex start")
    require(readiness["phase1_authorized"] is False, "Phase 1")


def mutations() -> list[tuple[str, Mutation]]:
    cases: list[tuple[str, Mutation]] = []

    def add(name: str, mutate: Mutation) -> None:
        cases.append((name, mutate))

    def path(path_items: tuple[str, ...], replacement: Any) -> Mutation:
        def mutate(value: dict[str, Any]) -> None:
            cursor: dict[str, Any] = value
            for key in path_items[:-1]:
                cursor = cursor[key]
            cursor[path_items[-1]] = replacement
        return mutate

    for name, path_items, replacement in [
        ("phase", ("phase_id",), "PCR-10"),
        ("status", ("status",), "issue_active"),
        ("target", ("target_issue", "number"), 2),
        ("title", ("target_issue", "rewritten_title"), "Phase 1 build"),
        ("authority", ("authority", "issue_is_execution_summary_not_authority"), False),
        ("Founder approval", ("authority", "founder_explicit_approval_required_to_start"), False),
        ("Codex start", ("boundaries", "codex_start_authorized"), True),
        ("Phase 1", ("boundaries", "phase1_authorized"), True),
        ("runtime", ("boundaries", "runtime_activation_authorized"), True),
        ("real data", ("boundaries", "real_client_data_enabled"), True),
        ("external", ("boundaries", "external_actions_authorized"), True),
        ("paid", ("boundaries", "paid_services_authorized"), True),
        ("production", ("boundaries", "production_deployment_authorized"), True),
        ("merge", ("boundaries", "autonomous_merge_authorized"), True),
        ("remote evidence", ("readiness_snapshot", "github_issue_sync_verified"), True),
        ("close target", ("target_issue", "preserve_open_state"), False),
        ("body size", ("generated_issue", "body_character_count"), 1),
    ]:
        add(name, path(path_items, replacement))

    def remove_superseded(v: dict[str, Any]) -> None:
        v["supersession"]["issue_numbers"] = []

    def remove_task(v: dict[str, Any]) -> None:
        v["handoff_snapshot"]["task_graph"].pop()

    def break_dependency(v: dict[str, Any]) -> None:
        v["handoff_snapshot"]["task_graph"][2]["dependencies"] = []

    def remove_activation(v: dict[str, Any]) -> None:
        v["handoff_snapshot"]["activation_conditions"].remove("pcr09_merged_to_main")

    def remove_build(v: dict[str, Any]) -> None:
        v["handoff_snapshot"]["execution"]["required_commands"].remove("python scripts/build_pcr09_codex_issue.py")

    def remove_validate(v: dict[str, Any]) -> None:
        v["handoff_snapshot"]["execution"]["required_commands"].remove("python scripts/validate_pcr09_codex_issue.py")

    def enable_rule(v: dict[str, Any]) -> None:
        v["rewrite_rules"]["no_implicit_activation"] = False

    def bad_hash(v: dict[str, Any]) -> None:
        v["generated_issue"]["body_sha256"] = "0" * 64

    def phase_scope(v: dict[str, Any]) -> None:
        v["handoff_snapshot"]["target"]["maximum_authorised_phase"] = 1

    def ready_pr(v: dict[str, Any]) -> None:
        v["handoff_snapshot"]["execution"]["pull_request_mode"] = "ready"

    def no_merge_approval(v: dict[str, Any]) -> None:
        v["handoff_snapshot"]["execution"]["merge_requires_founder_approval"] = False

    def remove_prohibition(v: dict[str, Any]) -> None:
        v["handoff_snapshot"]["prohibited_actions"].remove("progress_beyond_phase_0")

    def remove_stop(v: dict[str, Any]) -> None:
        v["handoff_snapshot"]["stop_conditions"].remove("phase_boundary_would_be_crossed")

    cases.extend([
        ("remove superseded issue", remove_superseded),
        ("remove task", remove_task),
        ("break dependency", break_dependency),
        ("remove PCR-09 activation", remove_activation),
        ("remove PCR-09 build", remove_build),
        ("remove PCR-09 validation", remove_validate),
        ("disable rewrite rule", enable_rule),
        ("stale body hash", bad_hash),
        ("expand phase scope", phase_scope),
        ("non-draft PR", ready_pr),
        ("remove merge approval", no_merge_approval),
        ("remove phase prohibition", remove_prohibition),
        ("remove phase stop", remove_stop),
    ])
    return cases


def main() -> None:
    source, contract, schema = load(SOURCE), load(CONTRACT), load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(contract))
    require(not errors, "; ".join(error.message for error in errors))
    expected_contract, expected_markdown = build_codex_issue()
    require(canonical(expected_contract) == CONTRACT.read_text(encoding="utf-8"), "stale contract")
    require(expected_markdown == MARKDOWN.read_text(encoding="utf-8"), "stale markdown")
    require(source["contract_id"] == contract["contract_id"], "contract id")
    markdown = MARKDOWN.read_text(encoding="utf-8")
    validate(contract, markdown)
    documentation = DOC.read_text(encoding="utf-8")
    for token in ["PCR-09", "issue #1", "issue #2", "single canonical", "NOT AUTHORISED TO START", "codex_start_authorized=false", "thirty-one mutation"]:
        require(token in documentation, token)
    rejected = 0
    cases = mutations()
    for name, mutate in cases:
        candidate = copy.deepcopy(contract)
        mutate(candidate)
        try:
            if list(validator.iter_errors(candidate)):
                rejected += 1
                continue
            validate(candidate, markdown)
        except (AssertionError, KeyError, TypeError, ValueError):
            rejected += 1
            continue
        raise AssertionError(f"Mutation was not rejected: {name}")
    readiness = contract["readiness_snapshot"]
    print(
        "PCR-09 first Codex issue rewrite passed: "
        f"issue #1, {readiness['task_count']} Phase 0 tasks, "
        f"{readiness['read_order_count']} read-order files, "
        f"{readiness['activation_condition_count']} activation conditions, "
        f"{len(cases)} mutation cases rejected, "
        "github_issue_sync_verified=false, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
