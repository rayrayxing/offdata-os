#!/usr/bin/env python3
"""Capture actual local dependency versions/SHAs after installation; never invent pins."""
from pathlib import Path
import json,os,shutil,subprocess,datetime as dt
ROOT=Path(__file__).resolve().parents[1]
def run(cmd,cwd=None):
 try:
  p=subprocess.run(cmd,cwd=cwd,text=True,capture_output=True,timeout=20);return (p.stdout or p.stderr).strip()
 except Exception as e:return f'UNAVAILABLE:{type(e).__name__}:{e}'
def git_info(path):
 p=Path(path).expanduser() if path else None
 if not p or not p.exists():return None
 return {'path':str(p.resolve()),'sha':run(['git','rev-parse','HEAD'],p),'dirty':bool(run(['git','status','--porcelain'],p)),'remote':run(['git','remote','get-url','origin'],p)}
def main():
 skill=Path.home()/'.hermes'/'skills'/'last30days';data={'captured_at':dt.datetime.now(dt.timezone.utc).isoformat(),'hermes':{'version':run(['hermes','--version']),'executable':shutil.which('hermes'),'source':git_info(os.getenv('HERMES_SOURCE_PATH'))},'last30days':git_info(os.getenv('LAST30DAYS_PATH') or (str(skill) if skill.exists() else '')),'deepseek_harness':{'executable':shutil.which('deepseek-harness') or shutil.which('deepseek_harness'),'source':git_info(os.getenv('DEEPSEEK_HARNESS_PATH'))},'codex':{'version':run(['codex','--version']) if shutil.which('codex') else None,'executable':shutil.which('codex')},'claude':{'version':run(['claude','--version']) if shutil.which('claude') else None,'executable':shutil.which('claude')},'python':run(['python3','--version']),'postgres':run(['psql','--version']) if shutil.which('psql') else None}
 out=ROOT/'state'/'dependency-lock.local.json';out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(data,indent=2));print(out)
if __name__=='__main__':main()
