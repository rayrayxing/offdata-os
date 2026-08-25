#!/usr/bin/env python3
"""Idempotently create/edit OFF/DATA Hermes cron routines from config/cron_jobs.final.json."""
from __future__ import annotations
import json,os,subprocess,shlex
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];CFG=json.loads((ROOT/"config"/"cron_jobs.final.json").read_text())
def run(cmd):print("+"," ".join(shlex.quote(str(x)) for x in cmd));return subprocess.run(cmd,text=True,capture_output=True)
def main():
 listing=run(["hermes","cron","list"]);text=(listing.stdout+listing.stderr).lower();provider=os.getenv("OFFDATA_CRON_PROVIDER");model=os.getenv("OFFDATA_CRON_MODEL")
 for j in CFG["jobs"]:
  exists=j["name"].lower() in text
  if j.get("no_agent"):
   script=str((ROOT/j["script"]).resolve());cmd=["hermes","cron","edit" if exists else "create"]
   if exists:cmd += [j["name"],"--schedule",j["schedule"],"--no-agent","--script",script,"--deliver",j["deliver"]]
   else:cmd += [j["schedule"],"--no-agent","--script",script,"--deliver",j["deliver"],"--name",j["name"]]
  else:
   if exists:cmd=["hermes","cron","edit",j["name"],"--schedule",j["schedule"],"--prompt",j["prompt"],"--workdir",str(ROOT),"--deliver",j["deliver"]]
   else:cmd=["hermes","cron","create",j["schedule"],j["prompt"],"--workdir",str(ROOT),"--deliver",j["deliver"],"--name",j["name"]]
   for s in j.get("skills",[]):cmd += ["--skill",s]
   if j.get("continuity"):cmd += ["--continuity"]
   if provider:cmd += ["--provider",provider]
   if model:cmd += ["--model",model]
  p=run(cmd)
  if p.returncode:print(p.stderr or p.stdout)
 print("Verify with: hermes cron list && hermes cron status")
if __name__=="__main__":main()
