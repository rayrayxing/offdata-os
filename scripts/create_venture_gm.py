#!/usr/bin/env python3
"""Create/reconcile a dedicated Hermes Venture GM profile for one serious venture.
The dynamic profile contains role procedure only; Venture Brain remains canonical truth.
"""
from __future__ import annotations
import argparse,json,re,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def slugify(s):return re.sub(r'[^a-z0-9-]+','-',s.lower()).strip('-')[:48]
def run(cmd,check=True):print('+',' '.join(map(str,cmd)));return subprocess.run(cmd,text=True,capture_output=True,check=check)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--venture-id',required=True);ap.add_argument('--slug',required=True);ap.add_argument('--name',required=True);ap.add_argument('--base-profile',default='portfolio-director');ap.add_argument('--environment',default='TEST',choices=['TEST','SIMULATION','LIVE']);ns=ap.parse_args()
 slug=slugify(ns.slug);profile=f'venture-gm-{slug}';home=Path.home()/'.hermes'/'profiles'/profile
 if not home.exists():
  p=run(['hermes','profile','create',profile,'--description',f'General Manager for OFF/DATA venture {ns.name}','--clone'],check=False)
  if p.returncode:raise SystemExit(p.stderr or p.stdout)
 home.mkdir(parents=True,exist_ok=True)
 soul=f'''# OFF/DATA Venture GM — {ns.name}\n\nVenture ID: {ns.venture_id}\nEnvironment: {ns.environment}\n\n## Mandate\nCoordinate the venture's evidence-backed progression and specialist work. Optimize learning, commercial proof and economic value—not activity.\n\n## Hard boundaries\n- Venture Brain is canonical truth; re-read it before consequential decisions.\n- You cannot self-pass gates, admit evidence, create financial truth, grant authority or bypass owner policy.\n- Delegate through typed Kanban work and require `offdata_outcome`, artifact refs and residual risk.\n- Low-impact concerns remain visible but do not block unless deterministic policy classifies them BLOCKING.\n- External effects require controlled OFF/DATA rails and valid authorization.\n'''
 (home/'SOUL.md').write_text(soul)
 plugin=ROOT/'.hermes/plugins/off-data-venture';dst=home/'plugins'/'off-data-venture';dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():shutil.rmtree(dst)
 shutil.copytree(plugin,dst)
 # Write a machine-readable descriptor for Hermes/setup tooling. The venture fact itself remains in Venture Brain.
 (home/'OFFDATA_VENTURE_BINDING.json').write_text(json.dumps({'venture_id':ns.venture_id,'slug':slug,'profile':profile,'environment':ns.environment},indent=2))
 print(json.dumps({'profile':profile,'home':str(home),'venture_id':ns.venture_id},indent=2))
if __name__=='__main__':main()
