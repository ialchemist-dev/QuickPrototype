#!/usr/bin/env python3
"""Approval-gated, crash-safe fal queue adapter. No automatic POST retries."""
import argparse,base64,contextlib,datetime,fcntl,hashlib,json,mimetypes,os,sys,uuid
import urllib.request,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; PROD=ROOT/'production'
MODEL='bytedance/seedance-2.5/us/reference-to-video'; RATE=1.165
class Blocked(Exception):pass
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(data):return hashlib.sha256(data).hexdigest()
def read(p):return json.loads(p.read_text())
def atomic(p,data):
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp')
 with open(tmp,'w') as f:json.dump(data,f,indent=2,ensure_ascii=False);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
@contextlib.contextmanager
def locked():
 with open(PROD/'.lock','a') as f:
  fcntl.flock(f,fcntl.LOCK_EX);yield

def creative_hash(m):
 return sha(json.dumps([{k:s[k] for k in ['id','duration','prompt_hash','reference_hashes','model','resolution']} for s in m['shots']],sort_keys=True).encode())
def reserve_total(m,pilot=False):
 return sum(a['actual_cost_usd'] if a.get('actual_cost_usd') is not None else a['reserved_usd'] for s in m['shots']+m.get('assets',[]) if not pilot or s.get('pilot') or s.get('kind') in ['reference','voice'] for a in s.get('attempts',[]))
def validate_manifest(m):
 if len(m['shots'])!=19 or sum(s['duration'] for s in m['shots'])!=m['timeline_seconds']:raise Blocked('Invalid timeline')
 for s in m['shots']:
  if abs(s['duration']-s['storyboard_duration'])>2:raise Blocked('Edit exceeds permitted shot adjustment')
  if sha((ROOT/s['prompt_path']).read_bytes())!=s['prompt_hash']:raise Blocked('Prompt changed: explicitly update manifest and renew approval')
def gates(m,s,approvals,cost):
 g=approvals.get('G0',{})
 if not g.get('approved') or not g.get('evidence'):raise Blocked('G0 budget/provider approval missing')
 if g.get('provider')!='fal' or g.get('model')!=MODEL:raise Blocked('Provider/model approval mismatch')
 if not g.get('account_access_confirmed') or not g.get('fictional_faces_permitted'):raise Blocked('US account access and fictional-face permission unverified')
 try:age=(datetime.date.today()-datetime.date.fromisoformat(g['pricing_checked_at'])).days
 except (KeyError,TypeError,ValueError):raise Blocked('Pricing verification date missing')
 if age<0 or age>7:raise Blocked('Recheck price before spending; quote older than 7 days')
 if reserve_total(m)+cost>g.get('max_total_usd',0):raise Blocked('Total spend cap exceeded')
 if (s.get('pilot') or s.get('kind') in ['reference','voice']) and reserve_total(m,True)+cost>g.get('max_pilot_usd',0):raise Blocked('Pilot spend cap exceeded')
 if s.get('kind') in ['reference','voice']:
  if s['model'] not in g.get('approved_auxiliary_models',[]):raise Blocked('Auxiliary model not approved')
  return
 if s['model']!=MODEL or s['resolution']!='1080p':raise Blocked('Unapproved video settings')
 g1=approvals.get('G1',{})
 if not g1.get('approved') or not g1.get('evidence') or g1.get('manifest_creative_hash')!=creative_hash(m):raise Blocked('G1 references/animatic approval absent or stale')
 if not s['pilot']:
  if not approvals.get('G2',{}).get('approved') or not approvals['G2'].get('evidence'):raise Blocked('G2 full render approval missing')
  if any(x['status']!='approved' for x in m['shots'] if x['pilot']):raise Blocked('All four pilots must be reviewed and approved')
def safe_local(relative):
 p=(ROOT/relative).resolve()
 if ROOT not in p.parents:raise Blocked('Asset path must be inside project')
 return p

def request_for(s,reference_map):
 if s.get('kind') in ['reference','voice']:
  payload=dict(s['input'])
  if s.get('input_reference_ids'):
   images=[]
   for rid in s['input_reference_ids']:
    ref=reference_map.get(rid,{})
    if not ref.get('approved') or not ref.get('path'):raise Blocked('Auxiliary reference not approved: '+rid)
    path=safe_local(ref['path']);data=path.read_bytes()
    if sha(data)!=ref.get('sha256'):raise Blocked('Auxiliary reference hash changed')
    images.append('data:'+mimetypes.guess_type(path.name)[0]+';base64,'+base64.b64encode(data).decode())
   payload['image_urls']=images
  return payload
 prompt=(ROOT/s['prompt_path']).read_text();images=[];bindings=[]
 for i,rid in enumerate(s['required_references'],1):
  ref=reference_map.get(rid,{})
  if not ref.get('approved') or not ref.get('path'):raise Blocked('Reference '+rid+' is not approved')
  p=safe_local(ref['path']);data=p.read_bytes();h=sha(data)
  if h!=ref.get('sha256') or h!=s['reference_hashes'].get(rid):raise Blocked('Reference hash mismatch: '+rid)
  if len(data)>30_000_000:raise Blocked('Reference exceeds model limit')
  mime=mimetypes.guess_type(p.name)[0]
  if mime not in ['image/jpeg','image/png','image/webp']:raise Blocked('Unsupported reference image format')
  images.append('data:'+mime+';base64,'+base64.b64encode(data).decode());bindings.append(f'@Image{i} is {rid}; preserve its approved identity or location.')
 return {'prompt':' '.join(bindings)+'\n'+prompt,'task':'reference','image_urls':images,'duration':str(s['duration']),'resolution':s['resolution'],'aspect_ratio':'16:9','generate_audio':False,'codec':'H264','seed':41000+int(s['id'])}

def http(method,url,key,payload=None):
 u=urllib.parse.urlparse(url)
 if u.scheme!='https' or u.hostname!='queue.fal.run':raise Blocked('Untrusted API URL')
 req=urllib.request.Request(url,data=json.dumps(payload).encode() if payload is not None else None,headers={'Authorization':'Key '+key,'Content-Type':'application/json'},method=method)
 # No retries: a POST timeout may already have incurred a charge.
 with urllib.request.urlopen(req,timeout=90) as r:return json.load(r)

def submit(m,s,approvals,refs,key,transport=http,save=None):
 validate_manifest(m)
 if s['id']=='19':raise Blocked('End card is local; never submit to video provider')
 if s['status']!='planned' or (s.get('attempts') and not s.get('retry_prepared')):raise Blocked('Existing attempt: reconcile or explicitly prepare a retry; never resubmit blindly')
 cost=s['estimated_cost_usd'];gates(m,s,approvals,cost)
 if not key:raise Blocked('FAL_KEY missing')
 payload=request_for(s,refs)
 a={'idempotency_key':str(uuid.uuid4()),'created_at':now(),'status':'submitting','job_id':None,'reserved_usd':cost,'actual_cost_usd':None,'request_hash':sha(json.dumps(payload,sort_keys=True).encode())}
 s['retry_prepared']=False;s['attempts'].append(a);s['attempt_count']=len(s['attempts']);s['status']='submitted';s['updated_at']=now()
 save(m) # Write intent and cost reservation BEFORE any network I/O.
 try:
  reply=transport('POST','https://queue.fal.run/'+s['model'],key,payload)
  if not reply.get('request_id'):raise ValueError('Missing job id')
  a.update({'job_id':reply['request_id'],'status':'submitted','status_url':reply['status_url'],'response_url':reply['response_url']});s['generation_job_id']=reply['request_id'];m['paid_calls_made']+=1
 except Exception:
  a['status']='uncertain';s['qc_notes'].append('Submission outcome uncertain. Reservation retained. Reconcile provider dashboard; do not regenerate.');save(m);raise Blocked('Submission outcome uncertain; credentials and provider response omitted from logs')
 save(m);return a['job_id']

def reconcile(m,s,key):
 a=s['attempts'][-1]
 if not a.get('job_id'):raise Blocked('No known job ID; recover from provider dashboard before retrying')
 if s['status'] in ['rendered','approved']:return 'Already downloaded; no request made'
 r=http('GET',a['status_url'],key)
 a['last_checked_at']=now();a['remote_status']=r.get('status')
 if r.get('error') or r.get('status') in ['FAILED','CANCELED','CANCELLED']:
  a['status']='failed';s['status']='failed';s['qc_notes'].append('Remote failure. Check private provider dashboard. Reservation retained pending billing reconciliation.');return 'Failed'
 if r.get('status')!='COMPLETED':return r.get('status','Unknown')
 out=http('GET',a['response_url'],key)
 kind=s.get('kind','video');asset=out.get('video') if kind=='video' else out.get('audio') if kind=='voice' else (out.get('images') or [None])[0]
 if not asset or not asset.get('url'):raise Blocked('No output URL; leave job reserved and reconcile')
 url=asset['url'];u=urllib.parse.urlparse(url)
 if u.scheme!='https' or not (u.hostname.endswith('.fal.media') or u.hostname=='storage.googleapis.com'):raise Blocked('Output host requires explicit inspection before download')
 folder={'video':'shots','voice':'audio','reference':'references'}[kind];ext={'video':'mp4','voice':'mp3','reference':'png'}[kind]
 target=PROD/folder/f'{s["id"]}-{a["idempotency_key"][:8]}.{ext}';tmp=target.with_suffix('.part')
 # Download without Authorization. No credentials sent to output storage.
 with urllib.request.urlopen(url,timeout=120) as r,open(tmp,'wb') as f:
  while True:
   chunk=r.read(1024*1024)
   if not chunk:break
   f.write(chunk)
 os.replace(tmp,target);s['output_path']=str(target.relative_to(ROOT));s['output_sha256']=sha(target.read_bytes());s['status']='rendered';a['status']='rendered';s['updated_at']=now()
 s['qc_notes'].append('Downloaded, not visually approved. Cost still reserved until invoice reconciliation.')
 return 'Rendered; human QC required'

def main():
 ap=argparse.ArgumentParser();ap.add_argument('command',choices=['validate','cost','dry-run','submit','resume','creative-hash','record-cost','prepare-retry']);ap.add_argument('--reason');ap.add_argument('--shot');ap.add_argument('--usd',type=float);ap.add_argument('--invoice');args=ap.parse_args()
 with locked():
  m=read(PROD/'manifest.json');save=lambda x:atomic(PROD/'manifest.json',x)
  if args.command=='validate':validate_manifest(m);print('19 shots; hashes and timing valid');return
  if args.command=='creative-hash':print(creative_hash(m));return
  if args.command=='cost':print(json.dumps({'committed_or_reserved_usd':reserve_total(m),'actual_confirmed_usd':m['actual_spend_usd']},indent=2));return
  s=next((s for s in m['shots']+m.get('assets',[]) if s['id']==args.shot),None)
  if not s:raise Blocked('Specify a known --shot ID')
  if args.command=='dry-run':
   print(json.dumps({'id':s['id'],'model':s['model'],'duration':s.get('duration'),'cost_reservation_usd':s['estimated_cost_usd'],'references_required':s.get('required_references',[]),'prompt_hash':s.get('prompt_hash'),'network_calls':0},indent=2));return
  if args.command=='prepare-retry':
   if s['status'] not in ['rendered','failed'] or not args.reason or not s['attempts'] or any(a.get('actual_cost_usd') is None or a.get('status') in ['uncertain','submitting','submitted'] for a in s['attempts']):raise Blocked('Retry requires a known completed attempt, reconciled billing and --reason; never retry an uncertain job')
   s['attempts'][-1]['previous_output_path']=s.get('output_path');s['qc_notes'].append('Explicit retry: '+args.reason);s['status']='planned';s['retry_prepared']=True;s['output_path']=None;s['generation_job_id']=None;save(m);print('Retry prepared; submit will recheck approvals and budget');return
  if args.command=='record-cost':
   if args.usd is None or args.usd<0 or not args.invoice or not s['attempts']:raise Blocked('Supply nonnegative --usd, --invoice reference, and an existing attempt')
   s['attempts'][-1]['actual_cost_usd']=args.usd;s['attempts'][-1]['billing_evidence']=args.invoice;s['actual_cost_usd']=sum(a.get('actual_cost_usd') or 0 for a in s['attempts']);m['actual_spend_usd']=sum(a.get('actual_cost_usd') or 0 for x in m['shots']+m.get('assets',[]) for a in x.get('attempts',[]));save(m);print('Recorded confirmed billing amount');return
  key=os.environ.get('FAL_KEY')
  if args.command=='resume':
   if not key:raise Blocked('FAL_KEY missing')
   try:print(reconcile(m,s,key))
   finally:save(m)
  else:
   approvals=read(PROD/'approvals.local.json') if (PROD/'approvals.local.json').exists() else {}
   refpath=PROD/'references/approved.local.json';refs=read(refpath) if refpath.exists() else {}
   print('Submitted job '+submit(m,s,approvals,refs,key,save=save))
if __name__=='__main__':
 try:main()
 except Blocked as e:print('BLOCKED: '+str(e),file=sys.stderr);sys.exit(2)
 except Exception as e:print('ERROR: '+type(e).__name__+'; no raw provider payload logged. Inspect local state before retrying.',file=sys.stderr);sys.exit(1)
