#!/usr/bin/env python3
"""Execute typed BuildContracts with DeepSeek Harness, Codex or Claude Code in isolated git worktrees."""
from __future__ import annotations
import argparse,json,os,shlex,shutil,subprocess,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def command_for(name):
 env={"deepseek":"OFFDATA_DEEPSEEK_HARNESS_COMMAND","codex":"OFFDATA_CODEX_COMMAND","claude":"OFFDATA_CLAUDE_COMMAND"}[name]
 if os.getenv(env):return shlex.split(os.environ[env])
 if name=="codex" and shutil.which("codex"):return ["codex","exec","--full-auto","-"]
 if name=="claude" and shutil.which("claude"):return ["claude","-p"]
 for x in ("deepseek-harness","deepseek_harness"):
  if name=="deepseek" and shutil.which(x):return [x]
 raise SystemExit(f"Builder {name} unavailable; set {env} to the tested CLI command template")
def prompt(c):
 return """OFF/DATA BUILD CONTRACT\nDo not certify your own work. Stay inside the assigned worktree.\nReturn changed files, tests, unresolved risks and exact commands run.\n\n"""+json.dumps(c,indent=2)
def run(cmd,cwd,input_text,timeout):
 t=time.time();p=subprocess.run(cmd,cwd=cwd,input=input_text,text=True,capture_output=True,timeout=timeout);return p,time.time()-t
def main():
 ap=argparse.ArgumentParser();ap.add_argument("builder",choices=["deepseek","codex","claude"]);ap.add_argument("contract");ap.add_argument("--timeout",type=int,default=3600);ns=ap.parse_args()
 c=json.loads(Path(ns.contract).read_text());repo=Path(c["repo"]).expanduser().resolve();base=c.get("base_sha","HEAD");task=c.get("work_id") or str(uuid.uuid4())
 wt=ROOT/"state"/"worktrees"/task;wt.parent.mkdir(parents=True,exist_ok=True)
 if wt.exists():raise SystemExit(f"worktree exists: {wt}")
 subprocess.run(["git","-C",str(repo),"worktree","add","--detach",str(wt),base],check=True)
 report={"builder":ns.builder,"work_id":task,"worktree":str(wt),"base_sha":base}
 try:
  p,elapsed=run(command_for(ns.builder),str(wt),prompt(c),ns.timeout);report.update({"exit_code":p.returncode,"elapsed_seconds":elapsed,"stdout":p.stdout[-50000:],"stderr":p.stderr[-10000:]})
  report["status"]="COMPLETED" if p.returncode==0 else "FAILED"
  report["git_status"]=subprocess.run(["git","-C",str(wt),"status","--short"],text=True,capture_output=True).stdout
  report["diff_stat"]=subprocess.run(["git","-C",str(wt),"diff","--stat"],text=True,capture_output=True).stdout
 finally:
  out=ROOT/"state"/"builder-results"/f"{task}-{ns.builder}.json";out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2));print(out)
if __name__=="__main__":main()
