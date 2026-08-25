#!/usr/bin/env python3
from pathlib import Path
import json,subprocess,sys
R=Path(__file__).resolve().parents[1]
required=['START_HERE.md','AGENTS.md','OFFDATA_MANIFEST.json','manifests/profiles.final.json','manifests/skills.final.json','.hermes/plugins/off-data-venture/plugin.yaml','.hermes/plugins/off-data-venture/external_tools.py','.hermes/plugins/off-data-venture/dashboard/manifest.json','database/migrations/001_offdata_v02_final.sql','database/migrations/003_external_effects_and_guard_policies.sql','config/cron_jobs.final.json','adapters/builder_runner.py','ops/macos/backup.sh','scripts/validate_package.py','tests/run_all.py','certification/CODEX_CERTIFICATION.md']
missing=[x for x in required if not (R/x).exists()]
if missing:print('FAIL missing:',*missing,sep='\n- ');sys.exit(2)
m=json.loads((R/'manifests/profiles.final.json').read_text());s=json.loads((R/'manifests/skills.final.json').read_text());assert len(m['profiles'])>=46;assert len(s['skills'])>=40
for cmd in ([sys.executable,'scripts/validate_package.py'],[sys.executable,'tests/run_all.py']):
 p=subprocess.run(cmd,cwd=R);assert p.returncode==0,cmd
print(f"PASS package files={sum(1 for p in R.rglob('*') if p.is_file())} profiles={len(m['profiles'])} skills={len(s['skills'])}")
