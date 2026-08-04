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
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
                result.add(f"{relative}::{node.name}")
    return result


def merge_implemented_mappings(root: Path) -> dict[str, list[str]]:
    merged: dict[str, list[str]] = {}
    paths = sorted((root / "requirements").glob("implemented-test-mappings*.json"))
    if not paths:
        raise ValueError("No implemented test mapping sources found.")
    for path in paths:
        source = read_object(path)
        for node_id, requirements in source.items():
            if node_id in merged:
                raise ValueError(f"Duplicate implemented test mapping: {node_id}")
            if not isinstance(requirements, list) or not all(isinstance(item, str) for item in requirements):
                raise ValueError(f"Invalid implemented test mapping: {node_id}")
            merged[node_id] = requirements
    return merged


def completed_planned_test_ids(root: Path) -> set[str]:
    completed: set[str] = set()
    for path in sorted((root / "requirements").glob("completed-planned-tests*.json")):
        values = read_object(path).get("completed_test_ids")
        if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
            raise ValueError(f"Invalid completed planned-test register: {path}")
        overlap = completed & set(values)
        if overlap:
            raise ValueError(f"Duplicate completed planned-test IDs: {sorted(overlap)}")
        completed.update(values)
    return completed


def main() -> int:
    root = repository_root()
    implemented_source = merge_implemented_mappings(root)
    planned_source = read_object(root / "requirements/planned-test-mappings.json")
    completed_planned = completed_planned_test_ids(root)
    unknown_completed = sorted(completed_planned - set(planned_source))
    if unknown_completed:
        print(f"Completed planned tests not found in source: {unknown_completed}", file=sys.stderr)
        return 1
    planned_source = {test_id: record for test_id, record in planned_source.items() if test_id not in completed_planned}
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
    implemented = [{"node_id": node_id, "kind": "fixture" if "test_fixture_" in node_id else "unit", "phase": "chat-first", "requirements": requirements, "evidence_status": "executable_in_chat_and_codex"} for node_id, requirements in sorted(implemented_source.items())]
    planned = [{"test_id": test_id, "kind": record["kind"], "phase": record["phase"], "requirements": record["requirements"], "evidence_status": "planned_not_executed"} for test_id, record in sorted(planned_source.items())]
    registry = {"version": "2.0.0", "rules": {"every_collected_test_requires_mapping": True, "mandatory_requirements_require_executed_or_planned_test": True, "planned_tests_do_not_count_as_executed_evidence": True, "requirement_ids_must_match_catalogue_pattern": True, "completed_planned_tests_are_removed": True}, "implemented_tests": implemented, "planned_tests": planned}
    destination = root / "requirements/test-registry.json"
    destination.write_text(json.dumps(registry, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {destination.relative_to(root)}: implemented={len(implemented)} planned={len(planned)} completed_planned={len(completed_planned)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
