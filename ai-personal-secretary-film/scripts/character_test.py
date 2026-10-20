#!/usr/bin/env python3
"""Approved single character shot; private durable state, no automatic retries."""
import argparse, os, sys
from pipeline import PROD, read, atomic, locked, reconcile, Blocked
from shot01 import submit, payload_for, key_from_local
PLAN=PROD/'tests/character-voice-v1/plan.json'
STATE=PROD/'private/character-voice-v1-state.json'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['dry-run','submit','resume']);args=ap.parse_args()
    os.umask(0o077)
    with locked():
        plan=read(PLAN);state=read(STATE) if STATE.exists() else plan
        shot=state['shots'][0];save=lambda x:atomic(STATE,x)
        payload_for(plan,shot,PLAN.parent)
        if args.command=='dry-run':
            print('One 1080p 5s character shot; estimated $0.245; $0.30 reserved, plus $0.45 prior spend and $0.05 TTS reserve. No network calls.');return
        key=key_from_local()
        if not key:raise Blocked('FAL_KEY missing')
        if args.command=='submit':print(submit(plan,state,shot,key,save=save,request_directory=PLAN.parent))
        else:
            try:print(reconcile(state,shot,key))
            finally:save(state)
if __name__=='__main__':
    try:main()
    except Blocked as e:print('BLOCKED: '+str(e));sys.exit(2)
    except Exception as e:print('ERROR: '+type(e).__name__+'; raw response omitted');sys.exit(1)
