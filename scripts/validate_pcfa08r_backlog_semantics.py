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
    p1_source = _between(value, "### P1.1 Source import", "### P1.2 Extraction pipeline")
    p1_manifest = _between(value, "### P1.3 Canonical manifest and alias resolver", "### P1.4 Method and problem schemas")
    p1_gate = _between(value, "### IMP-P1 gate", "## IMP-P2 — Engagement system of record")
    pcfa08r_overlay = _between(value, "## PCFA-08 / PCFA-08R final pre-Codex acceptance overlay", "## Deferred integrations")
    licence = current_posture.get("licence_posture", {})
    historical = current_posture.get("historical_predecessor", {})

    _need(errors, bool(p0_1), "IMP-P0.1 backlog section is missing or cannot be isolated")
    _need(errors, bool(p1_source), "IMP-P1.1 source-import section is missing or cannot be isolated")
    _need(errors, bool(p1_manifest), "IMP-P1.3 canonical-manifest section is missing or cannot be isolated")
    _need(errors, bool(p1_gate), "IMP-P1 gate section is missing or cannot be isolated")
    _need(errors, bool(pcfa08r_overlay), "PCFA-08R backlog clarification overlay is missing or cannot be isolated")
    _need(
        errors,
        "Successor authority controls current implementation semantics; retained historical package snapshots are evidence only and must not be re-promoted by backlog execution." in value,
        "backlog does not state that successor authority controls current implementation semantics",
    )
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
        "P0.1 implementation and repository documentation match the current PCFA-03 posture" in p0_1,
        "IMP-P0.1 completion does not explicitly require implementation/documentation to match current PCFA-03 authority",
    )
    _need(
        errors,
        "The historical WS6.13 licence placeholder remains historical-only" in p0_1,
        "IMP-P0.1 completion does not explicitly prevent re-promotion of the WS6.13 placeholder",
    )
    _need(
        errors,
        "Licence decision placeholder" not in p0_1 and "add_licence_decision_placeholder" not in p0_1,
        "IMP-P0.1 regressed to a predecessor licence-decision placeholder",
    )
    _need(
        errors,
        "explicit Founder-approved canonical source manifest" in p1_source
        and "unapproved discovered files do not silently expand the required corpus" in p1_source,
        "IMP-P1.1 does not explicitly bind import scope to the Founder-approved canonical source manifest",
    )
    _need(
        errors,
        "Assign every approved source a stable source identity before extraction" in p1_source,
        "IMP-P1.1 does not require stable identity for every approved source before extraction",
    )
    _need(
        errors,
        "Track one current disposition for every Founder-approved canonical source" in p1_manifest,
        "IMP-P1.3 does not explicitly track one governed disposition per approved source",
    )
    _need(
        errors,
        "Reject silent omissions" in p1_manifest and "native locator where available" in p1_manifest,
        "IMP-P1.3 does not explicitly reject silent omissions while retaining native provenance",
    )
    _need(
        errors,
        "100% of Founder-approved canonical methodology sources are accounted for" in p1_gate,
        "IMP-P1 completion no longer requires complete Founder-approved source accounting",
    )
    _need(
        errors,
        "The accounting denominator is the explicit current Founder-approved canonical source manifest" in p1_gate
        and "not a discovered-file count, extracted-chunk count or method-record count" in p1_gate,
        "IMP-P1 gate does not explicitly define the approved-source accounting denominator",
    )
    _need(
        errors,
        "Every approved source has exactly one current governed disposition; zero approved sources are silently omitted" in p1_gate,
        "IMP-P1 gate does not explicitly require complete one-disposition accounting with zero silent omissions",
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
    _need(
        errors,
        "PCFA-08R only makes the already-governed P0.1 licence-posture and IMP-P1 approved-source-accounting semantics explicit" in pcfa08r_overlay
        and "add no new IMP phase, task, PCFA-07 obligation or Phase-0 obligation" in pcfa08r_overlay
        and "do not authorize IMP-P1" in pcfa08r_overlay
        and "Codex launch scope remains exactly P0.1–P0.4" in pcfa08r_overlay,
        "PCFA-08R clarification overlay does not preserve no-widening and no-IMP-P1-authorization boundaries",
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
            "P0.1 current-authority completion removed",
            _replace_required(
                text,
                "- P0.1 implementation and repository documentation match the current PCFA-03 posture: private/internal development, no public licence grant and no repository `LICENSE` unless a later explicit Founder licence ADR changes it\n",
                "",
            ),
        ),
        (
            "historical placeholder boundary removed",
            _replace_required(
                text,
                "- The historical WS6.13 licence placeholder remains historical-only and is not treated as an unresolved launch or implementation decision\n",
                "",
            ),
        ),
        (
            "approved-source manifest removed",
            _replace_required(
                text,
                "- Begin from an explicit Founder-approved canonical source manifest; unapproved discovered files do not silently expand the required corpus\n",
                "",
            ),
        ),
        (
            "approved-source disposition tracking removed",
            _replace_required(
                text,
                "- Track one current disposition for every Founder-approved canonical source: ingested/structured, duplicate, superseded, quarantined, or explicitly excluded with a recorded reason\n",
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
            "approved-source denominator removed",
            _replace_required(
                text,
                "- The accounting denominator is the explicit current Founder-approved canonical source manifest, not a discovered-file count, extracted-chunk count or method-record count\n",
                "",
            ),
        ),
        (
            "silent omission prohibition removed",
            _replace_required(
                text,
                "- Every approved source has exactly one current governed disposition; zero approved sources are silently omitted\n",
                "",
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
        (
            "PCFA-08R no-widening overlay removed",
            _replace_required(
                text,
                "PCFA-08R only makes the already-governed P0.1 licence-posture and IMP-P1 approved-source-accounting semantics explicit in their existing tasks and gates; these clarifications add no new IMP phase, task, PCFA-07 obligation or Phase-0 obligation and do not authorize IMP-P1.",
                "PCFA-08R authorizes IMP-P1.",
            ),
        ),
        (
            "successor-authority rule removed",
            _replace_required(
                text,
                "- Successor authority controls current implementation semantics; retained historical package snapshots are evidence only and must not be re-promoted by backlog execution.\n",
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
        f"defect_classes=2, clarification_surfaces=5, mutation_cases_rejected={rejected}, "
        "p0_licence_posture=current_pcfa03, p1_completion=complete_approved_source_accounting, "
        "phase0_scope=P0.1-P0.4, imp_p1_authorized=false, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
