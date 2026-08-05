#!/usr/bin/env python3
"""Build the deterministic Phase 7 security and regionalisation baseline."""

from __future__ import annotations

from pathlib import Path

from offdata_core.security_regionalisation import build_security_baseline, write_security_baseline


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    destination = write_security_baseline(root)
    baseline = build_security_baseline(root)
    print(f"Wrote {destination.relative_to(root)}")
    print(f"- data_classes={baseline.data_class_count}")
    print(f"- regional_cells={baseline.regional_cell_count}")
    print(f"- retention_policies={baseline.retention_policy_count}")
    print(f"- processor_records={baseline.processor_record_count}")
    print(f"- processor_fixtures={baseline.processor_fixture_count}")
    print(f"- threats={baseline.threat_count}")
    print(f"- controls={baseline.control_count}")
    print(f"- security_tests={baseline.test_case_count}")
    print(f"- incident_playbooks={baseline.incident_playbook_count}")
    print(f"- mandatory_real_client_controls={baseline.mandatory_real_client_control_count}")
    print(f"- real_client_data_enabled={str(baseline.real_client_data_enabled).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
