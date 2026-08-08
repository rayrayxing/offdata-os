from __future__ import annotations
import json
from pcfa07_backlog_reconciliation import RECORD, REPORT, build_records

OBLIGATION_COLUMNS = ['requirement_id','obligation_kind','task_bindings','planned_test_id']
OUTPUT_PATH = RECORD
REPORT_PATH = REPORT
TASK_RE = __import__('pcfa07_backlog_reconciliation').TASK_RE

def main() -> None:
    record, report = build_records()
    OUTPUT_PATH.write_text(json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    REPORT_PATH.write_text(report, encoding='utf-8')
    c=record['obligation_counts']
    print(f"Built PCFA-07 Codex implementation backlog reconciliation: obligations={c['total_obligations']}, planned_tests={c['planned_tests']}, new_imp_phases=0, new_tasks=0, phase0_new_obligations=0, planned_not_implemented=true, codex_start_authorized=false.")

if __name__ == '__main__': main()
