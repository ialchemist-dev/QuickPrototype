#!/usr/bin/env python3
"""Read-only fal usage report. Loads credentials locally; never prints them."""
import argparse, datetime, json, sys
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError
from shot01 import key_from_local, MODEL

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--start',default=(datetime.datetime.now(datetime.timezone.utc)-datetime.timedelta(days=7)).date().isoformat())
    ap.add_argument('--end')
    ap.add_argument('--model',default=MODEL)
    args=ap.parse_args()
    key=key_from_local()
    if not key:
        sys.exit('Missing FAL_KEY in environment or project .env.local')
    params={'start':args.start,'endpoint_id':args.model,'expand':'summary','limit':100,'bound_to_timeframe':'false'}
    if args.end:params['end']=args.end
    pages=[];seen=set()
    while True:
        req=Request('https://api.fal.ai/v1/models/usage?'+urlencode(params),headers={'Authorization':'Key '+key})
        try:
            with urlopen(req,timeout=30) as response:page=json.load(response)
        except HTTPError as error:
            message={401:'Authentication failed.',403:'Key lacks billing permissions. Use a BILLING preset key.'}.get(error.code,'Usage query failed.')
            sys.exit(f'HTTP {error.code}: {message}')
        pages.append(page.get('summary'))
        cursor=page.get('next_cursor')
        if not cursor:
            if page.get('has_more'):sys.exit('Incomplete pagination: provider did not return cursor')
            break
        if cursor in seen:sys.exit('Repeated cursor; incomplete report')
        seen.add(cursor);params['cursor']=cursor
    print(json.dumps({'source':'fal usage API (estimate, not finalized invoice)','model':args.model,'start':args.start,'end':args.end or 'now','summary_pages':pages},indent=2))
if __name__=='__main__':main()
