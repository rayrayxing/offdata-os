#!/usr/bin/env python3
"""Static executable release validation; safe to run before credentials/database exist."""
from pathlib import Path
import ast,json,re,sys
ROOT=Path(__file__).resolve().parents[1];fail=[]
def req(p):
 if not (ROOT/p).exists():fail.append('missing '+p)
for p in ['.hermes/plugins/off-data-venture/plugin.yaml','.hermes/plugins/off-data-venture/__init__.py','.hermes/plugins/off-data-venture/external_tools.py','.hermes/plugins/off-data-venture/dashboard/manifest.json','.hermes/plugins/off-data-venture/dashboard/dist/index.js','database/migrations/003_external_effects_and_guard_policies.sql','manifests/profiles.final.json','manifests/skills.final.json','config/cron_jobs.final.json','ops/macos/backup.sh','tests/run_all.py']:req(p)
for p in ROOT.rglob('*.py'):
 try:ast.parse(p.read_text(),filename=str(p))
 except SyntaxError as e:fail.append(f'python syntax {p}:{e}')
for p in list(ROOT.rglob('*.json')):
 if str(p.relative_to(ROOT)).startswith('state/'):continue
 try:json.loads(p.read_text())
 except Exception as e:fail.append(f'json {p}:{e}')
try:
 prof=json.loads((ROOT/'manifests/profiles.final.json').read_text());skills=json.loads((ROOT/'manifests/skills.final.json').read_text());wf=json.loads((ROOT/'.hermes/plugins/off-data-venture/data/workflow.json').read_text())
 names={x['name'] for x in prof['profiles']};missing_profiles=sorted({n.get('profile') for n in wf['nodes'].values() if n.get('profile')} - names)
 if missing_profiles:fail.append('workflow profiles missing '+str(missing_profiles))
 custom=set(skills['skills']);wanted={s for p in prof['profiles'] for s in p.get('skills',[]) if s in custom};
 if len(wanted)<20:fail.append('too few materialized custom skills referenced')
except Exception as e:fail.append('cross-manifest validation '+str(e))
plugin=(ROOT/'.hermes/plugins/off-data-venture/plugin.yaml').read_text();
for x in ['offdata_email_send','offdata_stripe_checkout_create','offdata_research_query_reserve','pre_tool_call','post_tool_call']:
 if x not in plugin and x not in (ROOT/'.hermes/plugins/off-data-venture/__init__.py').read_text():fail.append('plugin contract missing '+x)
sql='\n'.join(p.read_text() for p in sorted((ROOT/'database/migrations').glob('*.sql')))
for x in ['external_effects','action_authorizations','gate_snapshots','journal_lines','research_queries','customer_commitments','delivery_obligations']:
 if x not in sql:fail.append('SQL entity missing '+x)
if fail:
 print('FAIL');print('\n'.join('- '+x for x in fail));sys.exit(2)
print('PASS static package validation')
