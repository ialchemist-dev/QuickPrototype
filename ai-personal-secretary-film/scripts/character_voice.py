#!/usr/bin/env python3
"""One approved OpenAI speech test; no automatic retry after uncertain submission."""
import argparse, json, os, sys
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from pipeline import ROOT, PROD, read, atomic, locked, sha, now, Blocked
REQUEST=PROD/'tests/character-voice-v1/tts-request.json'
STATE=PROD/'private/character-voice-tts.json'
OUT=PROD/'audio/character-voice-v1.wav'
def key():
    if os.environ.get('OPENAI_API_KEY'):return os.environ['OPENAI_API_KEY']
    p=ROOT/'.env.local'
    return next((x.split('=',1)[1].strip() for x in p.read_text().splitlines() if x.startswith('OPENAI_API_KEY=')),'') if p.exists() else ''
def main():
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['dry-run','generate']);args=ap.parse_args()
    payload=read(REQUEST)
    if payload['model']!='gpt-4o-mini-tts' or payload['voice']!='coral' or len(payload['input'])>100 or payload['response_format']!='wav':raise Blocked('Request outside approved short voice test')
    if args.command=='dry-run':
        print('OpenAI gpt-4o-mini-tts / coral / WAV; single short line; USD 0.05 reserved; no network calls.');return
    os.umask(0o077)
    with locked():
        if STATE.exists():raise Blocked('Existing attempt; inspect state before any retry')
        secret=key()
        if not secret:raise Blocked('OPENAI_API_KEY missing; no request sent')
        plan=read(PROD/'tests/character-voice-v1/plan.json')
        if plan['approval']['max_tts_usd']!=.05 or plan['approval']['max_generation_usd']!=2:raise Blocked('Approval mismatch')
        video_state=PROD/'private/character-voice-v1-state.json'
        state=read(video_state) if video_state.exists() else plan
        total=state['prior_spend_usd']+.05+sum(a['reserved_usd'] for s in state['shots'] for a in s['attempts'])
        if total>2:raise Blocked('Combined cap exceeded')
        journal={'status':'submitting','created_at':now(),'request_sha256':sha(REQUEST.read_bytes()),'reserved_usd':.05,'actual_cost_usd':None}
        atomic(STATE,journal)
        req=Request('https://api.openai.com/v1/audio/speech',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+secret,'Content-Type':'application/json'},method='POST')
        try:
            with urlopen(req,timeout=60) as response:
                journal['provider_request_id']=response.headers.get('x-request-id')
                data=response.read()
            if data[:4]!=b'RIFF':raise ValueError('Unexpected audio format')
            temp=OUT.with_suffix('.part');temp.write_bytes(data);os.replace(temp,OUT)
            journal.update(status='rendered',output_path=str(OUT.relative_to(ROOT)),output_sha256=sha(data))
        except HTTPError as error:
            journal.update(status='rejected',http_status=error.code);atomic(STATE,journal)
            raise Blocked('OpenAI HTTP '+str(error.code)+'; no automatic retry')
        except Exception:
            journal['status']='uncertain';atomic(STATE,journal)
            raise Blocked('Outcome uncertain; no automatic retry')
        atomic(STATE,journal)
        print('Voice downloaded:',OUT)
if __name__=='__main__':
    try:main()
    except Blocked as e:print('BLOCKED: '+str(e));sys.exit(2)
    except Exception as e:print('ERROR: '+type(e).__name__+'; raw response omitted');sys.exit(1)
