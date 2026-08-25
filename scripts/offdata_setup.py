#!/usr/bin/env python3
"""Operator helper Hermes can invoke during OFF/DATA setup. It reconciles, it does not guess credentials/policy."""
from pathlib import Path
import argparse,os,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def run(cmd,env=None,check=True):print('+',' '.join(map(str,cmd)));return subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,check=check)
def plugin():
 dst=Path.home()/'.hermes'/'plugins'/'off-data-venture';dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():shutil.rmtree(dst)
 shutil.copytree(ROOT/'.hermes/plugins/off-data-venture',dst)
 run(['hermes','plugins','enable','off-data-venture'],check=False)
def deps():run([sys.executable,'-m','pip','install','-r',str(ROOT/'.hermes/plugins/off-data-venture/requirements.txt')])
def migrate():
 if not os.getenv('OFFDATA_DATABASE_URL'):raise SystemExit('OFFDATA_DATABASE_URL required')
 for p in sorted((ROOT/'database/migrations').glob('*.sql')):run(['psql',os.environ['OFFDATA_DATABASE_URL'],'-v','ON_ERROR_STOP=1','-f',str(p)])
def audit():
 v=os.getenv('VENTUREOS_PATH');
 if not v:raise SystemExit('VENTUREOS_PATH required for audit/gate import')
 run([sys.executable,'scripts/import_ventureos_audits.py',v,'--strict'])
def main():
 ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['preflight','deps','plugin','migrate','profiles','skills','capabilities','cron','audit','lock','test','validate','checksums','all']);ns=ap.parse_args()
 phases=['preflight','deps','plugin','migrate','profiles','skills','capabilities','cron','audit','lock','test','validate','checksums'] if ns.phase=='all' else [ns.phase]
 for x in phases:
  if x=='preflight':run([sys.executable,'scripts/preflight.py'])
  elif x=='deps':deps()
  elif x=='plugin':plugin()
  elif x=='migrate':migrate()
  elif x=='profiles':run([sys.executable,'scripts/reconcile_profiles.py'])
  elif x=='skills':run([sys.executable,'scripts/materialize_skills.py'])
  elif x=='capabilities':run([sys.executable,'scripts/inventory_capabilities.py'])
  elif x=='cron':run([sys.executable,'scripts/reconcile_cron.py'])
  elif x=='audit':audit()
  elif x=='lock':run([sys.executable,'scripts/capture_dependency_lock.py'])
  elif x=='test':run([sys.executable,'tests/run_all.py'])
  elif x=='validate':run([sys.executable,'scripts/validate_package.py'])
  elif x=='checksums':run([sys.executable,'scripts/generate_checksums.py'])
if __name__=='__main__':main()
