#!/usr/bin/env python3
"""One initial attempt per approved insert. Never automatically retry a POST."""
import argparse, json, os, sys, uuid
from urllib.error import HTTPError
from pipeline import ROOT, PROD, atomic, read, sha, now, locked, http, reconcile, Blocked
PLAN = PROD/'tests/shot01/plan.json'
STATE = PROD/'private/shot01-state.json'
MODEL = 'fal-ai/bytedance/seedance/v1/pro/fast/text-to-video'

def payload_for(plan, shot, directory=None):
    if plan['model'] != MODEL or plan['approval']['max_generation_usd'] != 2:
        raise Blocked('Approval mismatch')
    path = (directory or PLAN.parent)/shot['request_file']
    if sha(path.read_bytes()) != shot['request_sha256']:
        raise Blocked('Request changed')
    payload = read(path)
    if payload['resolution'] != '1080p' or payload['duration'] != '5' or payload['aspect_ratio'] != '16:9':
        raise Blocked('Unapproved settings')
    return payload

def submit(plan, state, shot, key, transport=http, save=None, request_directory=None):
    payload = payload_for(plan, shot, request_directory)
    if shot.get('attempts'):
        raise Blocked('Existing attempt; resume or reconcile, never blindly retry')
    reserved = state.get('prior_spend_usd', 0) + state.get('other_reserved_usd', 0) + sum(a['reserved_usd'] for s in state['shots'] for a in s['attempts'])
    if reserved + 0.30 > 2:
        raise Blocked('Budget exceeded')
    if not key:
        raise Blocked('Missing FAL_KEY')
    attempt = {'idempotency_key':str(uuid.uuid4()), 'created_at':now(), 'status':'submitting',
               'job_id':None, 'reserved_usd':0.30, 'actual_cost_usd':None}
    shot['attempts'].append(attempt)
    shot['status'] = 'submitted'
    save(state)
    try:
        reply = transport('POST', 'https://queue.fal.run/'+MODEL, key, payload)
        if not reply.get('request_id'):
            raise ValueError('No request ID')
        attempt.update(job_id=reply['request_id'], status_url=reply['status_url'],
                       response_url=reply['response_url'], status='submitted')
    except HTTPError as error:
        attempt['http_status'] = error.code
        attempt['status'] = 'rejected' if error.code in (401,402,403,422) else 'uncertain'
        shot['status'] = attempt['status']
        save(state)
        raise Blocked('Provider HTTP '+str(error.code)+'; no automatic retry; reservation retained')
    except Exception:
        attempt['status'] = 'uncertain'
        save(state)
        raise Blocked('Submission uncertain; reservation retained; inspect dashboard')
    save(state)
    return 'Submitted '+shot['id']

def key_from_local():
    if os.environ.get('FAL_KEY'):
        return os.environ['FAL_KEY']
    p = ROOT/'.env.local'
    if not p.exists():
        return ''
    return next((line.split('=',1)[1].strip() for line in p.read_text().splitlines()
                 if line.startswith('FAL_KEY=')), '')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('command',choices=['dry-run','submit','resume'])
    ap.add_argument('--shot',choices=['A','B'],required=True)
    args = ap.parse_args()
    os.umask(0o077)
    with locked():
        plan = read(PLAN)
        state = read(STATE) if STATE.exists() else {'shots':[
            dict(s, status='planned', qc_notes=[]) for s in plan['shots']]}
        shot = next(s for s in state['shots'] if s['id']=='S1-01'+args.shot)
        save = lambda value: atomic(STATE,value)
        payload_for(plan,shot)
        if args.command == 'dry-run':
            print(json.dumps({'shot':shot['id'],'model':MODEL,'estimated_usd':0.245,
                              'reserved_usd':0.30,'network_calls':0,'status':shot['status']}))
            return
        key = key_from_local()
        if not key:
            raise Blocked('Missing FAL_KEY')
        if args.command == 'submit':
            print(submit(plan,state,shot,key,save=save))
        else:
            try:
                print(reconcile(state,shot,key))
            finally:
                save(state)

if __name__ == '__main__':
    try:
        main()
    except Blocked as error:
        print('BLOCKED: '+str(error),file=sys.stderr)
        sys.exit(2)
    except Exception as error:
        print('ERROR: '+type(error).__name__+'; raw response omitted',file=sys.stderr)
        sys.exit(1)
