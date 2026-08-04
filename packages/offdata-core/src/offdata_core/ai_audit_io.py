"""Input parsing, validation and checksums for the Northstar AI-audit oracle."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml

from .ai_audit_models import CLIENT_VISIBLE_FILES, SourceChecksum


def _read_yaml(path: Path) -> dict[str, Any]:
    parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError(f"Expected YAML object: {path}")
    return parsed


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"Expected non-empty CSV: {path}")
    if any(value is None for row in rows for value in row.values()):
        raise ValueError(f"Malformed CSV row: {path}")
    return rows


def _float(row: Mapping[str, str], key: str) -> float:
    try:
        return float(row[key])
    except (KeyError, ValueError) as exc:
        raise ValueError(f"Invalid numeric field {key}: {row}") from exc


def _int(row: Mapping[str, str], key: str) -> int:
    value = _float(row, key)
    if not value.is_integer():
        raise ValueError(f"Expected integer field {key}: {row}")
    return int(value)


def _round(value: float, digits: int = 2) -> float:
    return round(value + 0.0, digits)


def _weighted(rows: Sequence[Mapping[str, str]], value_key: str, weight_key: str) -> float:
    denominator = sum(_float(row, weight_key) for row in rows)
    if denominator <= 0:
        raise ValueError(f"Cannot calculate weighted value with non-positive {weight_key}.")
    numerator = sum(_float(row, value_key) * _float(row, weight_key) for row in rows)
    return numerator / denominator


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _checksums(fixture_dir: Path) -> tuple[tuple[SourceChecksum, ...], str]:
    checksums: list[SourceChecksum] = []
    digest = hashlib.sha256()
    for name in CLIENT_VISIBLE_FILES:
        path = fixture_dir / name
        if not path.is_file():
            raise ValueError(f"Missing client-visible fixture input: {name}")
        sha = _sha256(path)
        checksums.append(
            SourceChecksum(path=name, sha256=sha, classification="client_visible_synthetic")
        )
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return tuple(checksums), digest.hexdigest()
