#!/usr/bin/env python3
from pathlib import Path
import json, sys
p=Path('state/imported-gate-policy.json')
if not p.exists(): print('BLOCKED_SOURCE_REQUIRED: state/imported-gate-policy.json absent'); sys.exit(3)
data=json.loads(p.read_text())
gates=data.get('gates',{})
missing=[f'G{i}' for i in range(11) if f'G{i}' not in gates]
if missing: print('FAIL missing gates',missing); sys.exit(2)
g3=gates['G3']; req=set(g3.get('required_direct_tuple',[])); expected={'accountIdentity','actorIdentity','counterpartyRole','interactionType','occurredAt','channel','receiptRef'}
if req!=expected or g3.get('allow_url_domain_fallback',True): print('FAIL G3 invariant mismatch'); sys.exit(2)
print('PASS imported G0-G10 includes strict G3 floor; still requires independent source ratification')
