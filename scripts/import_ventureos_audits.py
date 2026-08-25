#!/usr/bin/env python3
"""Copy/hash the on-device VentureOS independent audit/certification corpus into this package."""
from pathlib import Path
import argparse,hashlib,json,re,shutil
ROOT=Path(__file__).resolve().parents[1]
PAT=re.compile(r"(CODEX|INDEPENDENT|CERTIFICATION|RELEASE[-_ ]?BLOCK|NEW[-_ ]?FINDING|AUDIT|pre-g3-runtime-trial|codex-independent-pre-g3)",re.I)
def sha(p):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('ventureos');ap.add_argument('--strict',action='store_true');ns=ap.parse_args();src=Path(ns.ventureos).expanduser().resolve();
 if not src.exists():raise SystemExit('VentureOS source missing')
 out=ROOT/'references'/'ventureos-audits';out.mkdir(parents=True,exist_ok=True);items=[]
 for p in src.rglob('*'):
  if not p.is_file() or p.stat().st_size>5_000_000:continue
  rel=str(p.relative_to(src))
  if PAT.search(rel):
   dest=out/(rel.replace('/','__'));shutil.copy2(p,dest);items.append({'source':rel,'copy':dest.name,'sha256':sha(dest),'bytes':dest.stat().st_size})
 items.sort(key=lambda x:x['source']);(out/'INDEX.json').write_text(json.dumps({'source_root':str(src),'files':items},indent=2))
 if ns.strict and len(items)<6:raise SystemExit(f'Expected at least six audit/certification artifacts, found {len(items)}')
 print(f'Imported {len(items)} audit/review artifacts to {out}')
if __name__=='__main__':main()
