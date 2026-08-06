from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from build_workstream6_configuration_contradictions import build_records

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "workstream6-configuration-contradictions.json"
SCHEMA = ROOT / "schemas" / "workstream6-configuration-contradictions.schema.json"
REPORT = ROOT / "reports" / "workstream6-configuration-contradictions-evidence.md"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"


def _failures(value: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    require(value.get("work_package_id") == "WS6.7", "work package")
    require(value.get("base_main_sha") == "16e45598da7214d2cf9086405b7439b254eae472", "base")
    require(value.get("status") == "configuration_contradictions_reconciled", "status")
    require(value.get("defect", {}).get("id") == "WS6-CONSIST-004", "defect")
    require(value.get("required_committed_value") == "0", "required environment value")
    require(value.get("observed_environment_value") == "0", "observed environment value")
    require(all(item == "" for item in value.get("observed_provider_key_defaults", {}).values()), "provider key defaults")
    expected = value.get("required_contract_values", {})
    observed = value.get("observed_contract_values", {})
    require(expected == observed, "contract values")
    require(observed.get("paid_provider_spend_hard_cap") == 0, "hard cap")
    require(observed.get("purchases_authorized") is False, "purchases")
    require(observed.get("paid_services_authorized") is False, "paid services")
    require(value.get("closed_defects") == ["WS6-CONSIST-004"], "closed defects")
    require(value.get("remaining_blocking_defects") == ["WS6-BLOCK-006"], "blockers")
    completion = value.get("completion", {})
    for key in ("all_required_prior_components_pass", "ws67_complete", "committed_defaults_zero_spend", "configuration_and_contract_consistent"):
        require(completion.get(key) is True, key)
    require(completion.get("final_reconciliation_complete") is False, "final reconciliation")
    require(completion.get("all_blocking_defects_closed") is False, "all blockers")
    require(completion.get("next_permitted_work_package") == "WS6.8", "next")
    boundaries = value.get("boundaries", {})
    require(boundaries.get("founder_accountability_preserved") is True, "accountability")
    for key, item in boundaries.items():
        if key != "founder_accountability_preserved":
            require(item is False, key)
    return failures


def main() -> None:
    contract = _load(CONTRACT)
    schema = _load(SCHEMA)
    errors = list(Draft202012Validator(schema).iter_errors(contract))
    if errors:
        raise SystemExit("WS6.7 schema validation failed: " + "; ".join(error.message for error in errors))
    expected, report = build_records()
    if _canonical(contract) != _canonical(expected):
        raise SystemExit("WS6.7 contract is not deterministic")
    if REPORT.read_text(encoding="utf-8") != report:
        raise SystemExit("WS6.7 report is not deterministic")
    failures = _failures(contract)
    if failures:
        raise SystemExit("WS6.7 semantic validation failed: " + "; ".join(failures))

    mutations = [("observed_environment_value", "25"), ("required_committed_value", "25"), ("closed_defects", []), ("remaining_blocking_defects", [])]
    rejected = 0
    for key, replacement in mutations:
        mutated = copy.deepcopy(contract)
        mutated[key] = replacement
        if _failures(mutated):
            rejected += 1
        else:
            raise SystemExit(f"WS6.7 mutation not rejected: {key}")
    for key in contract["observed_provider_key_defaults"]:
        mutated = copy.deepcopy(contract)
        mutated["observed_provider_key_defaults"][key] = "configured"
        if _failures(mutated):
            rejected += 1
        else:
            raise SystemExit(f"WS6.7 provider mutation not rejected: {key}")
    for key, replacement in (("paid_provider_spend_hard_cap", 1), ("purchases_authorized", True), ("paid_services_authorized", True)):
        mutated = copy.deepcopy(contract)
        mutated["observed_contract_values"][key] = replacement
        if _failures(mutated):
            rejected += 1
        else:
            raise SystemExit(f"WS6.7 contract mutation not rejected: {key}")
    for key in ("ws67_complete", "committed_defaults_zero_spend", "configuration_and_contract_consistent"):
        mutated = copy.deepcopy(contract)
        mutated["completion"][key] = False
        if _failures(mutated):
            rejected += 1
        else:
            raise SystemExit(f"WS6.7 completion mutation not rejected: {key}")
    for key in ("codex_start_authorized", "phase0_implementation_authorized", "phase0_merge_authorized", "runtime_activation_authorized", "production_deployment_authorized", "phase1_authorized"):
        mutated = copy.deepcopy(contract)
        mutated["boundaries"][key] = True
        if _failures(mutated):
            rejected += 1
        else:
            raise SystemExit(f"WS6.7 boundary mutation not rejected: {key}")

    print(f"WS6.7 configuration contradictions passed: {rejected} mutations rejected, closed=WS6-CONSIST-004, remaining=WS6-BLOCK-006, next=WS6.8, codex_start_authorized=false.")


if __name__ == "__main__":
    main()
