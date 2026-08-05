#!/usr/bin/env python3
"""Build PCR-02 semantic test identity and referential-integrity records."""

from pathlib import Path

from offdata_core.referential_integrity import (
    build_referential_integrity_report,
    build_semantic_test_registry,
    write_referential_integrity_report,
    write_semantic_test_registry,
)


ROOT = Path(__file__).resolve().parents[1]


if __name__ == "__main__":
    registry = build_semantic_test_registry(ROOT)
    report = build_referential_integrity_report(ROOT)
    test_path = write_semantic_test_registry(ROOT)
    report_path = write_referential_integrity_report(ROOT)
    print(f"Wrote {test_path.relative_to(ROOT)}")
    print(f"- semantic_tests={registry.counts.total}")
    print(f"- implemented_semantic_tests={registry.counts.implemented}")
    print(f"- planned_semantic_tests={registry.counts.planned}")
    print(f"Wrote {report_path.relative_to(ROOT)}")
    print(f"- executable_test_nodes={report.counts.executable_test_nodes}")
    print(f"- reference_edges={report.counts.edges}")
    print(f"- report_digest={report.report_digest}")
