from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "configs" / "runtime-adapters.yaml"
OUTPUT_PATH = ROOT / "contracts" / "runtime-adapter-contracts.json"
AGENTS_PATH = ROOT / "configs" / "agents.yaml"
COMMANDS_PATH = ROOT / "contracts" / "command-event-catalogue.json"
SECURITY_BASELINE_PATH = ROOT / "security" / "security-regionalisation-baseline.json"
CLASSIFICATION_PATH = ROOT / "security" / "data-classification.yaml"
PROCESSOR_REGISTER_PATH = ROOT / "security" / "provider-processor-register.yaml"
CODEX_HANDOFF_PATH = ROOT / "handoff" / "codex-phase0-handoff.json"


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return value


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"


def build_runtime_contracts() -> dict[str, Any]:
    source = _load_yaml(SOURCE_PATH)
    agents = _load_yaml(AGENTS_PATH)
    catalogue = _load_json(COMMANDS_PATH)
    security = _load_json(SECURITY_BASELINE_PATH)
    classifications = _load_yaml(CLASSIFICATION_PATH)
    processors = _load_yaml(PROCESSOR_REGISTER_PATH)
    handoff = _load_json(CODEX_HANDOFF_PATH)

    agent_entries = agents.get("agents", [])
    agent_tool_classes = sorted(
        {
            tool
            for agent in agent_entries
            if isinstance(agent, dict)
            for tool in agent.get("permitted_tool_classes", [])
            if isinstance(tool, str)
        }
    )
    declared_tool_classes = {
        item.get("tool_class")
        for item in source.get("tool_classes", [])
        if isinstance(item, dict)
    }
    missing_agent_tools = sorted(set(agent_tool_classes) - declared_tool_classes)

    commands = catalogue.get("commands", [])
    idempotency_required = sum(
        1
        for command in commands
        if isinstance(command, dict) and command.get("idempotency") == "required"
    )
    class_names = [
        item.get("classification")
        for item in classifications.get("classes", [])
        if isinstance(item, dict)
    ]
    processor_entries = processors.get("processors", [])

    checks = {
        "agent_tools_declared": not missing_agent_tools,
        "agents_provider_independent": agents.get("provider_independent") is True,
        "agents_commands_only": agents.get("canonical_writes_via_commands_only") is True,
        "security_real_client_data_disabled": security.get("real_client_data_enabled") is False,
        "processor_register_empty": processor_entries == [],
        "processor_default_deny": processors.get("rules", {}).get("unregistered_processor_default") == "deny",
        "codex_start_unauthorized": handoff.get("readiness_snapshot", {}).get("codex_start_authorized") is False,
        "runtime_activation_unauthorized": source.get("boundaries", {}).get("runtime_activation_authorized") is False,
    }

    readiness = {
        "agents": {
            "count": len(agent_entries),
            "budget_profile_count": len(agents.get("budget_profiles", {})),
            "route_count": len(agents.get("routing_policy", {}).get("routes", [])),
            "permitted_tool_classes": agent_tool_classes,
            "missing_runtime_tool_classes": missing_agent_tools,
        },
        "commands": {
            "count": len(commands),
            "idempotency_required_count": idempotency_required,
        },
        "security": {
            "data_classes": class_names,
            "real_client_data_enabled": security.get("real_client_data_enabled"),
            "processor_count": len(processor_entries),
            "unregistered_processor_default": processors.get("rules", {}).get("unregistered_processor_default"),
        },
        "codex_handoff": {
            "codex_start_authorized": handoff.get("readiness_snapshot", {}).get("codex_start_authorized"),
        },
        "checks": checks,
        "local_prerequisites_passed": all(checks.values()),
        "runtime_activation_authorized": False,
    }

    output = dict(source)
    output["generated_from"] = "configs/runtime-adapters.yaml"
    output["readiness_snapshot"] = readiness
    return output


def main() -> None:
    output = build_runtime_contracts()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(_canonical_json(output), encoding="utf-8")
    readiness = output["readiness_snapshot"]
    print(
        "Built PCR-05 runtime adapter contracts: "
        f"{len(output['adapter_kinds'])} adapter kinds, "
        f"{len(output['adapter_profiles'])} profiles, "
        f"{len(output['tool_classes'])} tool classes, "
        f"{len(output['conformance_cases'])} conformance cases, "
        f"local_prerequisites_passed={str(readiness['local_prerequisites_passed']).lower()}, "
        "runtime_activation_authorized=false."
    )


if __name__ == "__main__":
    main()
