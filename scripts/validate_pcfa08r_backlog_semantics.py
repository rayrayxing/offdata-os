from __future__ import annotations

import copy

from codex_phase0_launch_core import ROOT, load_json
from pcfa08_final_acceptance import BACKLOG, backlog_semantic_failures

POSTURE = ROOT / "repository" / "repository-visibility-and-licence-posture.json"


def _need(errors: list[str], ok: bool, message: str) -> None:
    if not ok:
        errors.append(message)


def _between(text: str, start: str, end: str) -> str:
    if start not in text or end not in text:
        return ""
    return text.split(start, 1)[1].split(end, 1)[0]


def semantic_failures(text: str | None = None, posture: dict[str, object] | None = None) -> list[str]:
    value = BACKLOG.read_text(encoding="utf-8") if text is None else text
    current_posture = load_json(POSTURE) if posture is None else posture
    errors = list(backlog_semantic_failures(value))

    p0_1 = _between(value, "### P0.1 Repository baseline", "### P0.2 Local development environment")
    p1_gate = _between(value, "### IMP-P1 gate", "## IMP-P2 — Engagement system of record")
    licence = current_posture.get("licence_posture", {})
    historical = current_posture.get("historical_predecessor", {})

    _need(errors, bool(p0_1), "IMP-P0.1 backlog section is missing or cannot be isolated")
    _need(errors, bool(p1_gate), "IMP-P1 gate section is missing or cannot be isolated")
    _need(
        errors,
        isinstance(licence, dict)
        and licence.get("mode") == "no_public_licence_grant_proprietary_internal"
        and licence.get("licence_file_required_for_private_internal_development") is False
        and licence.get("public_distribution_authorized") is False,
        "PCFA-03 current licence authority no longer matches the backlog's resolved private/internal posture",
    )
    _need(
        errors,
        isinstance(historical, dict)
        and historical.get("classification") == "retained_historical_package_snapshot"
        and historical.get("package") == "WS6.13",
        "PCFA-03 no longer classifies the WS6.13 licence placeholder as historical-only evidence",
    )
    _need(
        errors,
        "Resolved PCFA-03 repository/licence posture: private/internal development, no public licence grant" in p0_1,
        "IMP-P0.1 does not carry the current PCFA-03 repository/licence posture in the task that implements it",
    )
    _need(
        errors,
        "no repository `LICENSE` unless a later explicit Founder licence ADR changes that posture" in p0_1,
        "IMP-P0.1 does not preserve the current no-LICENSE-unless-Founder-ADR rule",
    )
    _need(
        errors,
        "Licence decision placeholder" not in p0_1 and "add_licence_decision_placeholder" not in p0_1,
        "IMP-P0.1 regressed to a predecessor licence-decision placeholder",
    )
    _need(
        errors,
        "100% of Founder-approved canonical methodology sources are accounted for" in p1_gate,
        "IMP-P1 completion no longer requires complete Founder-approved source accounting",
    )
    _need(
        errors,
        "Method-count coverage is reported as a secondary diagnostic only" in p1_gate,
        "IMP-P1 method count is no longer explicitly subordinate to approved-source accounting",
    )
    _need(
        errors,
        "Initial 150-plus method records are structured and searchable" not in p1_gate,
        "IMP-P1 regressed to the historical count-only 150-plus completion gate",
    )

    return list(dict.fromkeys(errors))


def _replace_required(text: str, old: str, new: str) -> str:
    if old not in text:
        raise SystemExit(f"PCFA-08R self-test fixture missing expected text: {old}")
    return text.replace(old, new, 1)


def run_self_test() -> int:
    text = BACKLOG.read_text(encoding="utf-8")
    posture = load_json(POSTURE)
    if failures := semantic_failures(text, posture):
        raise SystemExit("PCFA-08R backlog semantic validation failed before self-test: " + "; ".join(failures))

    cases = [
        (
            "stale licence placeholder",
            _replace_required(
                text,
                "Resolved PCFA-03 repository/licence posture: private/internal development, no public licence grant, and no repository `LICENSE` unless a later explicit Founder licence ADR changes that posture",
                "Licence decision placeholder",
            ),
        ),
        (
            "licence posture removed from P0.1",
            _replace_required(
                text,
                "- Resolved PCFA-03 repository/licence posture: private/internal development, no public licence grant, and no repository `LICENSE` unless a later explicit Founder licence ADR changes that posture\n",
                "",
            ),
        ),
        (
            "count-only P1 completion gate",
            _replace_required(
                text,
                "100% of Founder-approved canonical methodology sources are accounted for as ingested/structured, duplicate, superseded, quarantined, or explicitly excluded with a recorded reason",
                "Initial 150-plus method records are structured and searchable",
            ),
        ),
        (
            "method count made controlling",
            _replace_required(
                text,
                "- Method-count coverage is reported as a secondary diagnostic only; it is not a substitute for complete approved-source accounting\n",
                "",
            ),
        ),
    ]

    rejected = 0
    for label, mutated in cases:
        if not semantic_failures(mutated, posture):
            raise SystemExit(f"PCFA-08R backlog semantic mutation not rejected: {label}")
        rejected += 1

    posture_mode = copy.deepcopy(posture)
    posture_mode["licence_posture"]["mode"] = "undecided"
    if not semantic_failures(text, posture_mode):
        raise SystemExit("PCFA-08R backlog semantic mutation not rejected: current licence authority drift")
    rejected += 1

    predecessor = copy.deepcopy(posture)
    predecessor["historical_predecessor"]["classification"] = "current_authority"
    if not semantic_failures(text, predecessor):
        raise SystemExit("PCFA-08R backlog semantic mutation not rejected: historical placeholder re-promoted")
    rejected += 1

    return rejected


def main() -> None:
    failures = semantic_failures()
    if failures:
        raise SystemExit("PCFA-08R backlog semantic validation failed: " + "; ".join(failures))
    rejected = run_self_test()
    print(
        "PCFA-08R backlog successor-authority semantics validation passed: "
        f"defect_classes=2, mutation_cases_rejected={rejected}, "
        "p0_licence_posture=current_pcfa03, p1_completion=complete_approved_source_accounting, "
        "codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
