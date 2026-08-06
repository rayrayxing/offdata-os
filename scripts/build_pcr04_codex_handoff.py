from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "configs" / "codex-handoff.yaml"
OUTPUT_PATH = ROOT / "handoff" / "codex-phase0-handoff.json"
CANONICAL_RELEASE_PATH = ROOT / "releases" / "canonical-chat-first-phase1-7-release.json"
REFERENTIAL_BASELINE_PATH = ROOT / "requirements" / "referential-integrity-baseline.json"
REPOSITORY_BASELINE_PATH = ROOT / "repository" / "repository-governance-baseline.json"


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
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _repository_gate(repository: dict[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    for field in (
        "missing_required_files",
        "prohibited_tracked_paths",
        "case_collisions",
    ):
        value = repository.get(field)
        if value:
            failures.append(field)

    workflow_checks = repository.get("workflow_checks")
    if not isinstance(workflow_checks, dict) or not workflow_checks:
        failures.append("workflow_checks")
    elif any(value is not True for value in workflow_checks.values()):
        failures.append("workflow_checks")

    if repository.get("real_client_data_allowed") is not False:
        failures.append("real_client_data_allowed")

    return not failures, sorted(set(failures))


def build_handoff() -> dict[str, Any]:
    source = _load_yaml(SOURCE_PATH)
    canonical = _load_json(CANONICAL_RELEASE_PATH)
    referential = _load_json(REFERENTIAL_BASELINE_PATH)
    repository = _load_json(REPOSITORY_BASELINE_PATH)

    repository_passed, repository_failures = _repository_gate(repository)
    canonical_boundaries = canonical.get("boundaries", {})
    canonical_passed = (
        canonical.get("phases") == [1, 2, 3, 4, 5, 6, 7]
        and canonical.get("final_validation", {}).get("conclusion") == "success"
        and canonical_boundaries.get("real_client_data_enabled") is False
        and canonical_boundaries.get("external_actions_authorised") is False
        and canonical_boundaries.get("founder_accountability_preserved") is True
    )
    referential_passed = (
        referential.get("status") == "pass"
        and referential.get("issues") == []
        and referential.get("counts", {}).get("requirements") == 123
        and referential.get("counts", {}).get("edges") == 604
    )

    readiness = {
        "canonical_release": {
            "passed": canonical_passed,
            "release_id": canonical.get("release_id"),
            "phases": canonical.get("phases"),
            "final_validation_conclusion": canonical.get("final_validation", {}).get(
                "conclusion"
            ),
            "boundaries": canonical_boundaries,
        },
        "referential_integrity": {
            "passed": referential_passed,
            "status": referential.get("status"),
            "issue_count": len(referential.get("issues", [])),
            "counts": referential.get("counts", {}),
            "report_digest": referential.get("report_digest"),
        },
        "repository_governance": {
            "passed": repository_passed,
            "failures": repository_failures,
            "required_file_count": len(repository.get("required_files", [])),
            "workflow_invariant_count": len(repository.get("workflow_checks", {})),
            "hosted_settings_required_before_codex": repository.get(
                "hosted_settings_required_before_codex", []
            ),
        },
    }
    readiness["local_prerequisites_passed"] = all(
        item.get("passed") is True
        for key, item in readiness.items()
        if key in {"canonical_release", "referential_integrity", "repository_governance"}
    )
    readiness["codex_start_authorized"] = False
    readiness["activation_blockers"] = source.get("activation_conditions", [])

    output = dict(source)
    output["generated_from"] = "configs/codex-handoff.yaml"
    output["readiness_snapshot"] = readiness
    return output


def main() -> None:
    handoff = build_handoff()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(_canonical_json(handoff), encoding="utf-8")
    readiness = handoff["readiness_snapshot"]
    print(
        "Built PCR-04 Codex handoff: "
        f"{len(handoff['task_graph'])} Phase 0 tasks, "
        f"{len(handoff['read_order'])} read-order files, "
        f"local_prerequisites_passed={str(readiness['local_prerequisites_passed']).lower()}, "
        "codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
