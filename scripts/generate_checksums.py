#!/usr/bin/env python3
from pathlib import Path
import hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'CHECKSUMS.sha256'
def include(p):
 r=p.relative_to(ROOT);s=str(r)
 return p.is_file() and s!='CHECKSUMS.sha256' and not s.startswith('state/') and '.env' not in p.name and 'private' not in p.name.lower() and '__pycache__' not in s
def sha(p):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
files=sorted((p for p in ROOT.rglob('*') if include(p)),key=lambda p:str(p.relative_to(ROOT)))
OUT.write_text(''.join(f"{sha(p)}  {p.relative_to(ROOT)}\n" for p in files));print(f'{OUT} files={len(files)}')
