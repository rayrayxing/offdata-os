#!/usr/bin/env python3
"""Qualify OpenAI-compatible primary/fallback endpoints without exposing keys.

Env per prefix PRIMARY/FALLBACK:
 OFFDATA_<PREFIX>_BASE_URL, OFFDATA_<PREFIX>_API_KEY, OFFDATA_<PREFIX>_MODEL.
The harness checks model listing and repeated structured chat responses. It does
not automate OAuth refresh or proxy process restarts; those are explicit manual
qualification items recorded in the report.
"""
from __future__ import annotations
import json, os, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

def env(prefix,key): return os.getenv(f'OFFDATA_{prefix}_{key}')

def request_json(url, key, method='GET', body=None, timeout=60):
    data=json.dumps(body).encode() if body is not None else None
    req=urllib.request.Request(url,data=data,method=method,headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'})
    t=time.monotonic()
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r:
            raw=r.read(); return {'ok':True,'status':r.status,'latency_ms':round((time.monotonic()-t)*1000),'json':json.loads(raw or b'{}')}
    except urllib.error.HTTPError as e:
        return {'ok':False,'status':e.code,'latency_ms':round((time.monotonic()-t)*1000),'error':e.read().decode(errors='replace')[:500]}
    except Exception as e:
        return {'ok':False,'status':None,'latency_ms':round((time.monotonic()-t)*1000),'error':f'{type(e).__name__}:{e}'}

def qualify(prefix, sequential=20, concurrent=5):
    base=(env(prefix,'BASE_URL') or '').rstrip('/'); key=env(prefix,'API_KEY'); model=env(prefix,'MODEL')
    if not all([base,key,model]): return {'qualified':False,'reason':'MISSING_CONFIGURATION'}
    models=request_json(base+'/models',key)
    payload={'model':model,'messages':[{'role':'user','content':'Return exactly JSON: {"ok":true,"value":7}'}],'temperature':0}
    runs=[request_json(base+'/chat/completions',key,'POST',payload) for _ in range(sequential)]
    with ThreadPoolExecutor(max_workers=concurrent) as ex:
        conc=list(ex.map(lambda _:request_json(base+'/chat/completions',key,'POST',payload), range(concurrent)))
    allruns=runs+conc; successes=sum(1 for r in allruns if r['ok'])
    rate=successes/len(allruns) if allruns else 0
    return {'qualified':bool(models['ok'] and rate>=0.95),'models_check':models['ok'],'success_rate':rate,
            'status_counts':{str(s):sum(1 for r in allruns if r.get('status')==s) for s in sorted({r.get('status') for r in allruns},key=str)},
            'latency_ms':{'max':max(r['latency_ms'] for r in allruns),'avg':round(sum(r['latency_ms'] for r in allruns)/len(allruns))},
            'manual_required':['proxy_restart_recovery','oauth_token_refresh','quota_window_observation','terms_of_service_review']}

def main():
    result={'generated_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'primary':qualify('PRIMARY'),'fallback':qualify('FALLBACK')}
    result['controlled_autonomy_model_ready']=bool(result['primary'].get('qualified') and result['fallback'].get('qualified'))
    out=os.getenv('OFFDATA_MODEL_QUAL_REPORT','state/model-qualification.json')
    Path=__import__('pathlib').Path; Path(out).parent.mkdir(parents=True,exist_ok=True); Path(out).write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2)); raise SystemExit(0 if result['controlled_autonomy_model_ready'] else 4)
if __name__=='__main__': main()
