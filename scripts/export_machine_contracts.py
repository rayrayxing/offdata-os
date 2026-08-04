#!/usr/bin/env python3
"""Export deterministic offdata machine contracts from Pydantic source models."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail when committed generated files differ from current model output.",
    )
    args = parser.parse_args()

    repository_root = _repository_root()
    source_path = repository_root / "packages" / "offdata-core" / "src"
    sys.path.insert(0, str(source_path))

    from offdata_core.command_catalogue import (  # noqa: PLC0415
        build_command_event_catalogue,
    )
    from offdata_core.config_contracts import build_config_schema  # noqa: PLC0415
    from offdata_core.openapi_contract import build_openapi_document  # noqa: PLC0415
    from offdata_core.registry import (  # noqa: PLC0415
        build_alias_schema,
        build_model_registry_document,
        build_schema_bundle,
        write_json,
    )

    documents = {
        repository_root / "schemas" / "offdata-contract-bundle.schema.json": (
            build_schema_bundle()
        ),
        repository_root / "schemas" / "offdata-configs.schema.json": (
            build_config_schema()
        ),
        repository_root / "schemas" / "agent-envelope.schema.json": (
            build_alias_schema(
                "AgentEnvelope", "agent-envelope.schema.json", "Offdata Agent Envelope"
            )
        ),
        repository_root / "schemas" / "context-package.schema.json": (
            build_alias_schema(
                "ContextPackage",
                "context-package.schema.json",
                "Offdata Minimum-Sufficient Context Package",
            )
        ),
        repository_root / "schemas" / "founder-decision-packet.schema.json": (
            build_alias_schema(
                "FounderDecisionPacket",
                "founder-decision-packet.schema.json",
                "Offdata Founder Decision Packet",
            )
        ),
        repository_root / "contracts" / "model-registry.json": (
            build_model_registry_document()
        ),
        repository_root / "contracts" / "command-event-catalogue.json": (
            build_command_event_catalogue()
        ),
        repository_root / "api" / "openapi.json": build_openapi_document(),
    }

    if args.check:
        import json

        failures: list[str] = []
        for path, expected in documents.items():
            if not path.is_file():
                failures.append(f"missing: {path.relative_to(repository_root)}")
                continue
            actual = json.loads(path.read_text(encoding="utf-8"))
            if actual != expected:
                failures.append(f"out of date: {path.relative_to(repository_root)}")
        if failures:
            for failure in failures:
                print(failure, file=sys.stderr)
            return 1
        print(f"{len(documents)} generated contract files are current.")
        return 0

    for path, document in documents.items():
        write_json(path, document)
        print(path.relative_to(repository_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
