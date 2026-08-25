#!/usr/bin/env python3
from pathlib import Path
import json, sys
root=Path(__file__).resolve().parents[1]
required=['START_HERE.md','AGENTS.md','README.md','INCORPORATION_STATUS.md','OFFDATA_MANIFEST.json','spec/SYSTEM_ARCHITECTURE.md','policies/KNOWN_GATE_INVARIANTS.yaml','policies/capital-risk.defaults.yaml','skills/off-data-bootstrap/SKILL.md','plugin/off-data-venture/plugin.yaml','plugin/off-data-venture/tools.py','plugin/off-data-venture/schema.sql','adapters/deepseek-harness-lane.md','scripts/model_gateway_qualification.py','certification/CODEX_CERTIFICATION.md','references/VENTUREOS_AUDIT_SUMMARY.md']
missing=[x for x in required if not (root/x).exists()]
if missing: print('FAIL missing:',*missing,sep='\n- '); sys.exit(2)
m=json.loads((root/'OFFDATA_MANIFEST.json').read_text())
assert len(m['profiles'])>=46, 'profile roster incomplete'
assert set(m['environments'])=={'TEST','SIMULATION','LIVE'}
for inv in ['strict G3 complete seven-tuple for every contributing evidence item','zero duplicate financial effect']:
    assert inv in m['hard_invariants'], inv
print(f'PASS package files={sum(1 for p in root.rglob("*") if p.is_file())} profiles={len(m["profiles"])}')
