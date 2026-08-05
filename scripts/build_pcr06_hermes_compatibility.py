from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "configs" / "hermes-compatibility.yaml"
OUTPUT_PATH = ROOT / "contracts" / "hermes-compatibility-pack.json"
PCR05_PATH = ROOT / "contracts" / "runtime-adapter-contracts.json"
PCR04_PATH = ROOT / "handoff" / "codex-phase0-handoff.json"


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return value


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"


def _skill_files() -> list[Path]:
    return sorted(ROOT.glob("agents/*/SKILL.md"))


def _skill_files_valid(paths: list[Path]) -> bool:
    return bool(paths) and all(
        path.read_text(encoding="utf-8").strip().startswith("#")
        and len(path.read_text(encoding="utf-8").strip()) > 80
        for path in paths
    )


def build_hermes_compatibility() -> dict[str, Any]:
    source = _load_yaml(SOURCE_PATH)
    upstream = source.get("upstream")
    if not isinstance(upstream, dict):
        raise ValueError("upstream must be a mapping")
    upstream["assessment_date"] = str(upstream["assessment_date"])
    pcr05 = _load_json(PCR05_PATH)
    pcr04 = _load_json(PCR04_PATH)
    profiles = {
        item.get("adapter_id"): item
        for item in pcr05.get("adapter_profiles", [])
        if isinstance(item, dict)
    }
    hermes_profile = profiles.get("hermes-worker-harness", {})
    skill_files = _skill_files()
    checks = {
        "pcr05_adapter_present": bool(hermes_profile),
        "pcr05_adapter_activation_authorized": hermes_profile.get("activation_authorized") is False,
        "pcr05_runtime_activation_authorized": pcr05.get("readiness_snapshot", {}).get(
            "runtime_activation_authorized"
        )
        is False,
        "pcr04_codex_start_authorized": pcr04.get("readiness_snapshot", {}).get(
            "codex_start_authorized"
        )
        is False,
        "skill_files_valid": _skill_files_valid(skill_files),
    }
    readiness = {
        "pcr05_adapter_present": checks["pcr05_adapter_present"],
        "pcr05_adapter_activation_authorized": False,
        "pcr05_runtime_activation_authorized": False,
        "pcr04_codex_start_authorized": False,
        "repository_skill_count": len(skill_files),
        "skill_files_valid": checks["skill_files_valid"],
        "local_prerequisites_passed": all(checks.values()),
        "hermes_activation_authorized": False,
    }
    output = dict(source)
    output["generated_from"] = "configs/hermes-compatibility.yaml"
    output["readiness_snapshot"] = readiness
    return output


def main() -> None:
    output = build_hermes_compatibility()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(_canonical_json(output), encoding="utf-8")
    readiness = output["readiness_snapshot"]
    print(
        "Built PCR-06 Hermes compatibility pack: "
        f"{len(output['compatibility_surfaces'])} surfaces, "
        f"{len(output['tool_mapping'])} capability mappings, "
        f"{readiness['repository_skill_count']} repository skills, "
        f"local_prerequisites_passed={str(readiness['local_prerequisites_passed']).lower()}, "
        "hermes_activation_authorized=false."
    )


if __name__ == "__main__":
    main()
