from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = ROOT / "scripts" / "build_pcr03_repository_hygiene.py"
BASELINE_PATH = ROOT / "repository" / "repository-governance-baseline.json"


def _load_builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location("pcr03_builder", BUILD_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load PCR-03 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def main() -> None:
    if not BASELINE_PATH.is_file():
        raise SystemExit("PCR-03 baseline is missing")

    builder = _load_builder()
    actual = builder.build_baseline()
    expected = _load_json(BASELINE_PATH)

    if actual != expected:
        raise SystemExit(
            "PCR-03 baseline is stale or repository hygiene has changed; "
            "run scripts/build_pcr03_repository_hygiene.py and review the diff"
        )

    failures: list[str] = []
    if actual.get("missing_required_files"):
        failures.append(f"missing required files: {actual['missing_required_files']}")
    if actual.get("prohibited_tracked_paths"):
        failures.append(f"prohibited tracked paths: {actual['prohibited_tracked_paths']}")
    if actual.get("case_collisions"):
        failures.append(f"case-colliding paths: {actual['case_collisions']}")

    workflow_checks = actual.get("workflow_checks")
    if not isinstance(workflow_checks, dict):
        failures.append("workflow checks are missing")
    else:
        missing_tokens = sorted(token for token, passed in workflow_checks.items() if not passed)
        if missing_tokens:
            failures.append(f"workflow invariants missing: {missing_tokens}")

    if actual.get("real_client_data_allowed") is not False:
        failures.append("real-client-data boundary must remain false")

    if failures:
        raise SystemExit("PCR-03 validation failed:\n- " + "\n- ".join(failures))

    print(
        "PCR-03 repository and governance hygiene passed: "
        f"{len(actual['required_files'])} required files, "
        "zero prohibited tracked paths, zero case collisions, "
        f"{len(workflow_checks)} workflow invariants."
    )


if __name__ == "__main__":
    main()
