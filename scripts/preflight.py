#!/usr/bin/env python3
"""Non-destructive bootstrap preflight. Never reads secret values."""
from pathlib import Path
import json, os, platform, shutil, subprocess, sys
root=Path(__file__).resolve().parents[1]

def version(cmd):
    try:
        p=subprocess.run(cmd, text=True, capture_output=True, timeout=10)
        return (p.stdout or p.stderr).strip().splitlines()[0] if p.returncode==0 else f'ERROR({p.returncode})'
    except Exception as e: return f'UNAVAILABLE:{type(e).__name__}'

report={
 'python':sys.version.split()[0], 'platform':platform.platform(),
 'hermes':version(['hermes','--version']) if shutil.which('hermes') else 'MISSING',
 'git':version(['git','--version']) if shutil.which('git') else 'MISSING',
 'docker':version(['docker','--version']) if shutil.which('docker') else 'MISSING',
 'psql':version(['psql','--version']) if shutil.which('psql') else 'MISSING',
 'ventureos_path_exists': bool(os.getenv('VENTUREOS_PATH') and Path(os.getenv('VENTUREOS_PATH','')).exists()),
 'database_url_configured': bool(os.getenv('OFFDATA_DATABASE_URL')),
 'telegram_configured': bool(os.getenv('TELEGRAM_BOT_TOKEN')),
 'primary_model_configured': bool(os.getenv('OFFDATA_PRIMARY_BASE_URL')),
 'fallback_model_configured': bool(os.getenv('OFFDATA_FALLBACK_BASE_URL')),
}
print(json.dumps(report,indent=2))
if report['hermes']=='MISSING': sys.exit(3)
