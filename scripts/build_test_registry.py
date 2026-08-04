#!/usr/bin/env python3
"""Build the deterministic test registry from governed mapping sources."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Any


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_object(path: Path) -> dict[str, Any]:
    parsed = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return parsed


def collect_test_nodes(root: Path) -> set[str]:
    result: set[str] = set()
    tests_root = root / "packages" / "offdata-core" / "tests"
    for path in sorted(tests_root.glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        relative = path.relative_to(root).as_posix()
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith(
                "test_"
            ):
                result.add(f"{relative}::{node.name}")
    return result


def main() -> int:
    root = repository_root()
    implemented_source = read_object(root / "requirements/implemented-test-mappings.json")
    planned_source = read_object(root / "requirements/planned-test-mappings.json")

    collected = collect_test_nodes(root)
    mapped = set(implemented_source)
    missing = sorted(collected - mapped)
    stale = sorted(mapped - collected)
    if missing or stale:
        if missing:
            print(f"Unmapped test nodes: {missing}", file=sys.stderr)
        if stale:
            print(f"Stale test mappings: {stale}", file=sys.stderr)
        return 1

    implemented = [
        {
            "node_id": node_id,
            "kind": "fixture" if "test_fixture_" in node_id else "unit",
            "phase": "chat-first",
            "requirements": requirements,
            "evidence_status": "executable_in_chat_and_codex",
        }
        for node_id, requirements in sorted(implemented_source.items())
    ]
    planned = [
        {
            "test_id": test_id,
            "kind": record["kind"],
            "phase": record["phase"],
            "requirements": record["requirements"],
            "evidence_status": "planned_not_executed",
        }
        for test_id, record in sorted(planned_source.items())
    ]
    registry = {
        "version": "1.0.0",
        "rules": {
            "every_collected_test_requires_mapping": True,
            "mandatory_requirements_require_executed_or_planned_test": True,
            "planned_tests_do_not_count_as_executed_evidence": True,
            "requirement_ids_must_match_catalogue_pattern": True,
        },
        "implemented_tests": implemented,
        "planned_tests": planned,
    }
    destination = root / "requirements/test-registry.json"
    destination.write_text(
        json.dumps(registry, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"Wrote {destination.relative_to(root)}: "
        f"implemented={len(implemented)} planned={len(planned)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
