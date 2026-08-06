from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SECRET_NAME_RE = re.compile(r"(token|secret|password|credential|api[_-]?key)", re.IGNORECASE)


def _command_version(command: str, args: list[str]) -> dict[str, Any]:
    path = shutil.which(command)
    if path is None:
        return {"available": False, "path": None, "version": None}
    result = subprocess.run(
        [path, *args],
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )
    output = (result.stdout or result.stderr).strip().splitlines()
    return {
        "available": result.returncode == 0,
        "path": path,
        "version": output[0][:240] if output else None,
    }


def _git_state() -> dict[str, Any]:
    if not (ROOT / ".git").exists():
        return {"repository": False, "clean": False, "head": None, "branch": None}
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )
    branch = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )
    return {
        "repository": status.returncode == 0,
        "clean": status.returncode == 0 and not status.stdout.strip(),
        "head": head.stdout.strip() if head.returncode == 0 else None,
        "branch": branch.stdout.strip() if branch.returncode == 0 else None,
    }


def _resource_state() -> dict[str, Any]:
    usage = shutil.disk_usage(ROOT)
    return {
        "disk_free_bytes": usage.free,
        "disk_free_gib": round(usage.free / (1024 ** 3), 2),
        "disk_minimum_gib": 20,
        "disk_requirement_met": usage.free >= 20 * 1024 ** 3,
    }


def _environment_name_check() -> dict[str, Any]:
    suspicious = sorted(
        name for name in os.environ
        if SECRET_NAME_RE.search(name)
        and name not in {"GITHUB_TOKEN", "GH_TOKEN"}
    )
    return {
        "secret_named_environment_variables_detected": len(suspicious),
        "values_captured": False,
        "names_reported": [],
        "note": "Values and variable names are intentionally not emitted.",
    }


def build_report() -> dict[str, Any]:
    system = platform.system()
    machine = platform.machine()
    commands = {
        "git": _command_version("git", ["--version"]),
        "python": _command_version(sys.executable, ["--version"]),
        "node": _command_version("node", ["--version"]),
        "pnpm": _command_version("pnpm", ["--version"]),
        "docker": _command_version("docker", ["--version"]),
        "orb": _command_version("orb", ["version"]),
        "gh": _command_version("gh", ["--version"]),
    }
    git_state = _git_state()
    resources = _resource_state()
    checks = {
        "os_is_macos": system == "Darwin",
        "architecture_supported": machine in {"arm64", "x86_64"},
        "git_available": commands["git"]["available"],
        "python_available": commands["python"]["available"],
        "repository_is_git_clone": git_state["repository"],
        "repository_is_clean": git_state["clean"],
        "disk_requirement_met": resources["disk_requirement_met"],
        "container_runtime_available": (
            commands["docker"]["available"] or commands["orb"]["available"]
        ),
    }
    return {
        "schema_version": "1.0.0",
        "report_type": "offdata_pre_codex_macos_doctor",
        "non_destructive": True,
        "generated_values_include_secrets": False,
        "platform": {
            "system": system,
            "release": platform.release(),
            "version": platform.version(),
            "architecture": machine,
            "python_runtime": platform.python_version(),
        },
        "commands": commands,
        "git": git_state,
        "resources": resources,
        "environment": _environment_name_check(),
        "checks": checks,
        "machine_checks_passed": all(checks.values()),
        "manual_attestations": {
            "clean_machine_available": False,
            "no_real_client_files_present": False,
            "no_repository_credentials_present": False,
            "no_paid_service_or_trial_required": False,
            "founder_environment_attestation_received": False,
        },
        "clean_macos_environment_verified": False,
        "codex_start_authorized": False,
    }


def _self_test() -> None:
    report = build_report()
    assert report["non_destructive"] is True
    assert report["generated_values_include_secrets"] is False
    assert report["environment"]["values_captured"] is False
    assert report["environment"]["names_reported"] == []
    assert report["clean_macos_environment_verified"] is False
    assert report["codex_start_authorized"] is False
    assert all(value is False for value in report["manual_attestations"].values())
    sentinel_name = "OFFDATA_TEST_SECRET_TOKEN"
    sentinel_value = "offdata-self-test-secret-value-should-not-appear"
    previous = os.environ.get(sentinel_name)
    os.environ[sentinel_name] = sentinel_value
    try:
        encoded = json.dumps(build_report(), sort_keys=True)
        assert sentinel_value not in encoded
        assert sentinel_name not in encoded
    finally:
        if previous is None:
            os.environ.pop(sentinel_name, None)
        else:
            os.environ[sentinel_name] = previous
    print("Pre-Codex macOS doctor self-test passed: non-destructive, redacted, authorization denied.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Non-destructive pre-Codex macOS readiness doctor."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.self_test:
        _self_test()
        return

    report = build_report()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote redacted doctor report: {args.output}")
    else:
        print(rendered, end="")
    if not report["machine_checks_passed"]:
        raise SystemExit(2)
    raise SystemExit(
        "Machine checks passed, but manual Founder environment attestations remain required."
    )


if __name__ == "__main__":
    main()
