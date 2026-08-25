#!/usr/bin/env python3
"""Capture live Hermes/Skill/plugin/builder capability inventory and optionally persist to Venture Brain."""
from __future__ import annotations
import json,os,shutil,subprocess,datetime as dt
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(cmd,timeout=30):
 try:
  p=subprocess.run(cmd,text=True,capture_output=True,timeout=timeout);return {"ok":p.returncode==0,"code":p.returncode,"stdout":p.stdout[-12000:],"stderr":p.stderr[-4000:]}
 except Exception as e:return {"ok":False,"error":type(e).__name__,"message":str(e)}
def main():
 cmds={"hermes_version":["hermes","--version"],"profiles":["hermes","profile","list"],"plugins":["hermes","plugins","list"],"skills":["hermes","skills","list"],"cron":["hermes","cron","list"],"cron_status":["hermes","cron","status"]}
 data={"captured_at":dt.datetime.now(dt.timezone.utc).isoformat(),"commands":{},"executables":{},"env_capabilities":{}}
 for k,c in cmds.items():data["commands"][k]=run(c) if shutil.which(c[0]) else {"ok":False,"missing":c[0]}
 for exe in ("hermes","codex","claude","deepseek-harness","deepseek_harness","git","psql","pg_dump","docker"):
  data["executables"][exe]=shutil.which(exe)
 for k in ("BRAVE_SEARCH_API_KEY","EXA_API_KEY","SCRAPECREATORS_API_KEY","STRIPE_SECRET_KEY","HUBSPOT_ACCESS_TOKEN","POSTHOG_PROJECT_KEY","CLOUDFLARE_API_TOKEN","VERCEL_TOKEN"):
  data["env_capabilities"][k]=bool(os.getenv(k))
 out=ROOT/"state"/"capability-catalogue.local.json";out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(data,indent=2))
 if os.getenv("OFFDATA_DATABASE_URL"):
  try:
   import psycopg
   with psycopg.connect(os.environ["OFFDATA_DATABASE_URL"]) as conn:
    with conn.cursor() as cur:
     for exe,path in data["executables"].items():
      cur.execute("""INSERT INTO capability_catalogue(capability_key,kind,provider,version,profiles,status,details,tested_at,updated_at)
                     VALUES(%s,'EXECUTABLE',%s,NULL,'[]'::jsonb,%s,%s::jsonb,now(),now())
                     ON CONFLICT(capability_key) DO UPDATE SET status=excluded.status,details=excluded.details,tested_at=now(),updated_at=now()""",
                  ("exec:"+exe,exe,"AVAILABLE" if path else "MISSING",json.dumps({"path":path})))
  except Exception as e:data["db_warning"]=str(e);out.write_text(json.dumps(data,indent=2))
 print(out);print(json.dumps(data,indent=2))
if __name__=="__main__":main()
