from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "scripts/build_pcr05_runtime_adapters.py"
CONTRACT = ROOT / "contracts/runtime-adapter-contracts.json"
SCHEMA = ROOT / "schemas/runtime-adapter-contracts.schema.json"
AGENTS = ROOT / "configs/agents.yaml"
DOCS = [
    ROOT / "docs/44-PCR-05-RUNTIME-ADAPTER-CONTRACTS.md",
    ROOT / "README.md",
    ROOT / "docs/14-CODEX-KICKOFF.md",
    ROOT / "docs/19-PHASE-0-VALIDATION-ADDENDUM.md",
]
KINDS = {"agent_runtime", "workflow_runtime", "worker_harness", "tool_runtime"}
ACTIVATION = {
    "pcr03_merged_to_main",
    "pcr04_merged_to_main",
    "pcr05_merged_to_main",
    "github_hosted_controls_in_issue_19_verified",
    "explicit_founder_phase_0_approval_received",
    "clean_macos_environment_available",
}
EVENTS = {
    "runtime.invocation.accepted", "runtime.invocation.started",
    "runtime.invocation.completed", "runtime.invocation.failed",
    "runtime.invocation.blocked", "runtime.invocation.cancelled",
    "runtime.invocation.timed_out", "runtime.budget.exceeded",
    "runtime.policy.denied", "runtime.kill_switch.triggered",
}
CASES = {f"RA-CONF-{i:03d}" for i in range(1, 15)}
SAMPLES = {
    "AgentRuntimeRequest", "AgentRuntimeResponse", "WorkflowRuntimeRequest",
    "WorkflowRuntimeResponse", "WorkerPackage", "WorkerResult",
    "ToolInvocation", "ToolResult",
}
TOKENS = {
    "contracts/runtime-adapter-contracts.json",
    "scripts/validate_pcr05_runtime_adapters.py",
    "runtime_activation_authorized=false",
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def load_builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location("pcr05_builder", BUILD)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load PCR-05 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample_errors(schema: dict[str, Any], name: str, message: object) -> list[str]:
    if name not in schema.get("$defs", {}):
        return [f"unknown sample definition: {name}"]
    local = {"$schema": schema["$schema"], "$ref": f"#/$defs/{name}", "$defs": schema["$defs"]}
    return [error.message for error in Draft202012Validator(local).iter_errors(message)]


def semantic_failures(contract: dict[str, Any], *, samples: bool = True) -> list[str]:
    fail: list[str] = []
    if "stacked_base_branch" in contract:
        fail.append("transient stacked metadata is prohibited")

    authority = contract.get("authority", {})
    expected = {
        "controlling_instruction": "AGENTS.md", "control_plane_owner": "offdata",
        "provider_independent": True, "canonical_write_mode": "commands_only",
        "runtime_memory_is_canonical": False,
        "founder_accountability_preserved": True,
    }
    if not isinstance(authority, dict):
        fail.append("authority is missing")
    else:
        fail += [f"authority.{key} changed" for key, value in expected.items() if authority.get(key) != value]

    protocol = contract.get("protocol", {})
    for key in ("correlation_required", "idempotency_required_for_mutating_or_external_operations", "contract_version_required"):
        if not isinstance(protocol, dict) or protocol.get(key) is not True:
            fail.append(f"protocol.{key} must remain true")

    schema = load_json(SCHEMA)
    definitions = set(schema.get("$defs", {}))
    kinds = contract.get("adapter_kinds", [])
    kind_ids = [item.get("adapter_kind") for item in kinds if isinstance(item, dict)]
    if set(kind_ids) != KINDS or len(kind_ids) != len(KINDS):
        fail.append("four adapter kinds are required exactly once")
    for item in kinds if isinstance(kinds, list) else []:
        if not isinstance(item, dict):
            fail.append("adapter kind must be an object")
            continue
        name = item.get("adapter_kind")
        if item.get("canonical_write_mode") != "commands_only":
            fail.append(f"{name} permits direct writes")
        if item.get("external_action_mode") != "deny_by_default":
            fail.append(f"{name} external actions are not denied")
        if item.get("kill_switch_required") is not True or item.get("health_check_required") is not True:
            fail.append(f"{name} lacks health or kill-switch controls")
        for key in ("request_definition", "response_definition"):
            if item.get(key) not in definitions:
                fail.append(f"{name} has unknown {key}")

    profiles = contract.get("adapter_profiles", [])
    profile_ids = [item.get("adapter_id") for item in profiles if isinstance(item, dict)]
    if len(profile_ids) != len(set(profile_ids)):
        fail.append("adapter profile IDs must be unique")
    if {item.get("adapter_kind") for item in profiles if isinstance(item, dict)} != KINDS:
        fail.append("every adapter kind needs a profile")
    for item in profiles if isinstance(profiles, list) else []:
        if not isinstance(item, dict):
            fail.append("adapter profile must be an object")
            continue
        name = item.get("adapter_id")
        if item.get("activation_authorized") is not False:
            fail.append(f"{name} is activated")
        if item.get("status") not in {"contract_test_only", "planned", "planned_phase0", "deferred"}:
            fail.append(f"{name} has invalid status")
        if item.get("status") == "deferred" and (item.get("credential_mode") != "none" or item.get("network_mode") != "deny_until_review"):
            fail.append(f"{name} weakens deferred controls")
        if item.get("paid_service_required") is not False:
            fail.append(f"{name} requires payment")

    agents = load_yaml(AGENTS)
    used = {
        tool for agent in agents.get("agents", []) if isinstance(agent, dict)
        for tool in agent.get("permitted_tool_classes", []) if isinstance(tool, str)
    }
    tools = contract.get("tool_classes", [])
    tool_map = {item.get("tool_class"): item for item in tools if isinstance(item, dict)}
    if len(tool_map) != len([item for item in tools if isinstance(item, dict)]):
        fail.append("tool class IDs must be unique")
    if missing := sorted(used - set(tool_map)):
        fail.append(f"agent tools are undeclared: {missing}")
    for name, item in tool_map.items():
        if item.get("canonical_write_permitted") is not False:
            fail.append(f"{name} permits direct writes")
        if item.get("external_side_effect") is True and (
            item.get("available") is not False
            or item.get("founder_approval_required") is not True
            or item.get("idempotency_required") is not True
        ):
            fail.append(f"{name} weakens side-effect controls")

    budget = contract.get("budget_enforcement", {})
    if not isinstance(budget, dict) or budget.get("source") != "configs/agents.yaml" or budget.get("adapter_may_raise_limits") is not False or budget.get("actual_usage_required") is not True:
        fail.append("budget enforcement changed")
    security = contract.get("data_and_security", {})
    security_expected = {
        "pre_codex_permitted_classes": ["public", "internal"],
        "real_client_data_enabled": False, "unregistered_processor_default": "deny",
        "provider_training_allowed": False, "credential_values_permitted": False,
        "cross_tenant_execution_permitted": False,
    }
    if not isinstance(security, dict):
        fail.append("security boundary is missing")
    else:
        fail += [f"security.{key} changed" for key, value in security_expected.items() if security.get(key) != value]
    observability = contract.get("observability", {})
    if not isinstance(observability, dict) or not EVENTS.issubset(set(observability.get("required_events", []))) or observability.get("raw_secret_logging_permitted") is not False:
        fail.append("runtime observability controls are incomplete")

    cases = contract.get("conformance_cases", [])
    case_ids = [item.get("case_id") for item in cases if isinstance(item, dict)]
    if set(case_ids) != CASES or len(case_ids) != len(CASES):
        fail.append("fourteen conformance identities are required")
    if not any(item.get("expected_outcome") == "reject" for item in cases if isinstance(item, dict)):
        fail.append("negative conformance cases are required")

    boundaries = contract.get("boundaries", {})
    false_fields = (
        "runtime_activation_authorized", "real_client_data_enabled",
        "external_actions_authorized", "paid_services_authorized",
        "production_deployment_authorized", "credential_collection_authorized",
        "autonomous_merge_authorized",
    )
    if not isinstance(boundaries, dict):
        fail.append("boundaries are missing")
    else:
        fail += [f"{key} must remain false" for key in false_fields if boundaries.get(key) is not False]
        if boundaries.get("founder_accountability_preserved") is not True:
            fail.append("Founder accountability changed")
    if set(contract.get("activation_conditions", [])) != ACTIVATION:
        fail.append("activation conditions changed")

    readiness = contract.get("readiness_snapshot", {})
    checks = readiness.get("checks", {}) if isinstance(readiness, dict) else {}
    if not checks or any(value is not True for value in checks.values()):
        fail.append("runtime prerequisite checks must all pass")
    if not isinstance(readiness, dict) or readiness.get("local_prerequisites_passed") is not True or readiness.get("runtime_activation_authorized") is not False:
        fail.append("runtime readiness changed")
    if readiness.get("codex_handoff", {}).get("codex_start_authorized") is not False:
        fail.append("Codex start became authorized")
    if readiness.get("security", {}).get("real_client_data_enabled") is not False:
        fail.append("readiness enables client data")

    if samples:
        messages = contract.get("sample_messages", [])
        ids = [item.get("sample_id") for item in messages if isinstance(item, dict)]
        defs = {item.get("definition") for item in messages if isinstance(item, dict)}
        if len(ids) != len(set(ids)) or defs != SAMPLES:
            fail.append("eight unique typed samples are required")
        for item in messages if isinstance(messages, list) else []:
            if not isinstance(item, dict):
                fail.append("sample must be an object")
                continue
            fail += [f"{item.get('sample_id')}: {error}" for error in sample_errors(schema, str(item.get("definition")), item.get("message"))]
    return fail


def mutated(contract: dict[str, Any], change: Callable[[dict[str, Any]], None]) -> dict[str, Any]:
    value = copy.deepcopy(contract)
    change(value)
    return value


def run_mutations(contract: dict[str, Any]) -> int:
    def side(value: dict[str, Any]) -> dict[str, Any]:
        return next(
            item
            for item in value["tool_classes"]
            if item["external_side_effect"]
        )

    def tool_sample(value: dict[str, Any]) -> dict[str, Any]:
        return next(
            item
            for item in value["sample_messages"]
            if item["definition"] == "ToolInvocation"
        )["message"]
    changes: list[Callable[[dict[str, Any]], None]] = [
        lambda v: v["adapter_kinds"][0].__setitem__("canonical_write_mode", "direct"),
        lambda v: v["authority"].__setitem__("runtime_memory_is_canonical", True),
        lambda v: v["adapter_profiles"][4].__setitem__("activation_authorized", True),
        lambda v: v["adapter_profiles"][4].__setitem__("credential_mode", "inline"),
        lambda v: v.__setitem__("adapter_kinds", v["adapter_kinds"][:-1]),
        lambda v: side(v).__setitem__("available", True),
        lambda v: side(v).__setitem__("founder_approval_required", False),
        lambda v: v.__setitem__("tool_classes", [x for x in v["tool_classes"] if x["tool_class"] != "search_knowledge"]),
        lambda v: v["boundaries"].__setitem__("runtime_activation_authorized", True),
        lambda v: v["data_and_security"].__setitem__("real_client_data_enabled", True),
        lambda v: v["budget_enforcement"].__setitem__("adapter_may_raise_limits", True),
        lambda v: v["protocol"].__setitem__("idempotency_required_for_mutating_or_external_operations", False),
        lambda v: v["observability"]["required_events"].remove("runtime.policy.denied"),
        lambda v: v["activation_conditions"].remove("pcr05_merged_to_main"),
        lambda v: v.__setitem__("stacked_base_branch", "temporary"),
        lambda v: v["readiness_snapshot"]["checks"].__setitem__("agent_tools_declared", False),
        lambda v: (tool_sample(v).__setitem__("external_side_effect", True), tool_sample(v).__setitem__("approval_id", None), tool_sample(v).__setitem__("idempotency_key", None)),
    ]
    for index, change in enumerate(changes, 1):
        if not semantic_failures(mutated(contract, change)):
            raise SystemExit(f"PCR-05 mutation case {index} was not rejected")
    return len(changes)


def main() -> None:
    contract, schema = load_json(CONTRACT), load_json(SCHEMA)
    errors = sorted(Draft202012Validator(schema).iter_errors(contract), key=lambda error: list(error.absolute_path))
    if errors:
        raise SystemExit("PCR-05 schema validation failed:\n- " + "\n- ".join(error.message for error in errors))
    if contract != load_builder().build_runtime_contracts():
        raise SystemExit("PCR-05 contract is stale; run scripts/build_pcr05_runtime_adapters.py")
    failures = semantic_failures(contract)
    for path in DOCS:
        text = path.read_text(encoding="utf-8")
        failures += [f"{path.relative_to(ROOT)} is missing token: {token}" for token in TOKENS if token not in text]
    if failures:
        raise SystemExit("PCR-05 validation failed:\n- " + "\n- ".join(failures))
    count = run_mutations(contract)
    ready = contract["readiness_snapshot"]
    print(
        "PCR-05 runtime adapter contracts passed: "
        f"{len(contract['adapter_kinds'])} adapter kinds, {len(contract['adapter_profiles'])} profiles, "
        f"{len(contract['tool_classes'])} tool classes, {len(contract['sample_messages'])} typed samples, "
        f"{len(contract['conformance_cases'])} conformance cases, {count} mutation cases rejected, "
        f"local_prerequisites_passed={str(ready['local_prerequisites_passed']).lower()}, "
        "runtime_activation_authorized=false."
    )


if __name__ == "__main__":
    main()
