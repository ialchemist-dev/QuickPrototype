#!/usr/bin/env python3
"""One resumable A1 reference-guided test under the existing shared budget."""
import argparse,base64,os,sys,uuid
from pipeline import ROOT,PROD,read,atomic,sha,now,locked,http,reconcile,Blocked
from shot01 import key_from_local
PLAN=PROD/'tests/a1-breakfast-v1/plan.json'
STATE=PROD/'private/a1-breakfast-v1-state.json'
MODEL='fal-ai/bytedance/seedance/v1/pro/fast/image-to-video'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['dry-run','submit','resume']);args=ap.parse_args()
    os.umask(0o077)
    with locked():
        p=read(PLAN);state=read(STATE) if STATE.exists() else {'shots':[{'id':'S1-A1-breakfast-v1','status':'planned','attempts':[],'qc_notes':[]}]}
        shot=state['shots'][0];save=lambda:atomic(STATE,state)
        if args.command=='resume':
            k=key_from_local()
            if not k:raise Blocked('Missing FAL_KEY')
            try:print(reconcile(state,shot,k))
            finally:save()
            return
        data=(ROOT/p['reference_path']).read_bytes()
        if sha(data)!=p['reference_sha256'] or p['model']!=MODEL:raise Blocked('Reference or model mismatch')
        if shot['attempts']:raise Blocked('Existing attempt: resume; never blindly regenerate')
        prior=read(PROD/'private/character-voice-v1-state.json')
        reserve=.45+.05+sum(a.get('actual_cost_usd') if a.get('actual_cost_usd') is not None else a['reserved_usd'] for s in prior['shots'] for a in s['attempts'])+.30
        if reserve>2:raise Blocked('Combined budget exceeded')
        if args.command=='dry-run':print('Validated reference and model; total committed/reserved including next call: $'+str(round(reserve,2))+'. No network calls.');return
        k=key_from_local()
        if not k:raise Blocked('Missing FAL_KEY')
        payload=dict(p['input']);payload['image_url']='data:image/png;base64,'+base64.b64encode(data).decode()
        a={'idempotency_key':str(uuid.uuid4()),'created_at':now(),'status':'submitting','job_id':None,'reserved_usd':.30,'actual_cost_usd':None,'reference_sha256':sha(data)}
        shot['attempts'].append(a);shot['status']='submitted';save()
        try:
            r=http('POST','https://queue.fal.run/'+MODEL,k,payload)
            a.update(job_id=r['request_id'],status_url=r['status_url'],response_url=r['response_url'],status='submitted')
        except Exception:
            a['status']='uncertain';save();raise Blocked('Submission uncertain; reservation retained, no automatic retry')
        save();print('Submitted A1 reference-guided shot')
if __name__=='__main__':
    try:main()
    except Blocked as e:print('BLOCKED: '+str(e));sys.exit(2)
    except Exception as e:print('ERROR: '+type(e).__name__+'; raw response omitted');sys.exit(1)
