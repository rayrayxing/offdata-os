from __future__ import annotations

import fnmatch
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "repository-governance.yaml"
BASELINE_PATH = ROOT / "repository" / "repository-governance-baseline.json"


def _canonical_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return sorted(item for item in result.stdout.decode("utf-8").split("\0") if item)


def _matches(path: str, pattern: str) -> bool:
    candidates = [pattern]
    if pattern.startswith("**/"):
        candidates.append(pattern[3:])
    return any(fnmatch.fnmatchcase(path, candidate) for candidate in candidates)


def _case_collisions(paths: list[str]) -> list[list[str]]:
    buckets: dict[str, list[str]] = {}
    for path in paths:
        buckets.setdefault(path.casefold(), []).append(path)
    return sorted(
        [sorted(values) for values in buckets.values() if len(set(values)) > 1],
        key=lambda values: values[0].casefold(),
    )


def _load_config() -> dict[str, Any]:
    raw = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("repository governance config must be a mapping")
    return raw


def build_baseline() -> dict[str, object]:
    config = _load_config()
    tracked = _tracked_files()

    required_entries = config.get("required_files")
    if not isinstance(required_entries, list):
        raise ValueError("required_files must be a list")

    required_files: list[dict[str, object]] = []
    missing_required: list[str] = []
    for entry in required_entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise ValueError("every required_files entry must contain a string path")
        relative = entry["path"]
        path = ROOT / relative
        if not path.is_file():
            missing_required.append(relative)
            continue
        record: dict[str, object] = {"path": relative}
        if bool(entry.get("digest", True)):
            record["bytes"] = path.stat().st_size
            record["sha256"] = _sha256(path)
        required_files.append(record)

    patterns = config.get("prohibited_tracked_patterns")
    exceptions = config.get("allowed_pattern_exceptions", [])
    if not isinstance(patterns, list) or not all(isinstance(item, str) for item in patterns):
        raise ValueError("prohibited_tracked_patterns must be a string list")
    if not isinstance(exceptions, list) or not all(isinstance(item, str) for item in exceptions):
        raise ValueError("allowed_pattern_exceptions must be a string list")

    prohibited = sorted(
        path
        for path in tracked
        if path not in exceptions and any(_matches(path, pattern) for pattern in patterns)
    )

    workflow_path = ROOT / ".github" / "workflows" / "contracts.yml"
    workflow_text = workflow_path.read_text(encoding="utf-8") if workflow_path.is_file() else ""
    required_tokens = config.get("workflow_required_tokens")
    if not isinstance(required_tokens, list) or not all(
        isinstance(item, str) for item in required_tokens
    ):
        raise ValueError("workflow_required_tokens must be a string list")
    workflow_checks = {token: token in workflow_text for token in required_tokens}

    return {
        "schema_version": 1,
        "phase_id": "PCR-03",
        "generated_from": "configs/repository-governance.yaml",
        "canonical_branch": config.get("canonical_branch"),
        "accountable_owner": config.get("accountable_owner"),
        "real_client_data_allowed": config.get("real_client_data_allowed"),
        "required_files": sorted(required_files, key=lambda item: str(item["path"])),
        "missing_required_files": sorted(missing_required),
        "prohibited_tracked_paths": prohibited,
        "case_collisions": _case_collisions(tracked),
        "workflow_checks": workflow_checks,
        "hosted_settings_required_before_codex": config.get(
            "hosted_settings_required_before_codex", []
        ),
    }


def main() -> None:
    baseline = build_baseline()
    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    BASELINE_PATH.write_text(_canonical_json(baseline), encoding="utf-8")
    print(
        "Built PCR-03 repository-governance baseline: "
        f"{len(baseline['required_files'])} required files, "
        f"{len(baseline['prohibited_tracked_paths'])} prohibited tracked paths, "
        f"{len(baseline['case_collisions'])} case collisions."
    )


if __name__ == "__main__":
    main()
