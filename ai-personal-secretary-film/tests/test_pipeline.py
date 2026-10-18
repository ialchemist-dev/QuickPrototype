import copy,sys,unittest,datetime,tempfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import pipeline as p
class GuardTests(unittest.TestCase):
 def setUp(self):
  self.m=p.read(p.PROD/'manifest.json');self.s=self.m['shots'][1]
  self.ap={'G0':{'approved':True,'evidence':'test fixture only','provider':'fal','model':p.MODEL,'max_total_usd':600,'max_pilot_usd':110,'account_access_confirmed':True,'fictional_faces_permitted':True,'pricing_checked_at':datetime.date.today().isoformat()},'G1':{'approved':True,'evidence':'test fixture only','manifest_creative_hash':p.creative_hash(self.m)}}
 def test_canonical_timeline(self):
  p.validate_manifest(self.m);self.assertEqual(self.m['timeline_seconds'],143);self.assertEqual([s['id'] for s in self.m['shots'] if s['pilot']],['02','07','14','18'])
 def test_no_approval_no_network(self):
  calls=[]
  with self.assertRaises(p.Blocked):p.submit(self.m,self.s,{}, {},'fake',transport=lambda *a:calls.append(a),save=lambda m:None)
  self.assertEqual(calls,[])
 def test_missing_access(self):
  self.ap['G0']['account_access_confirmed']=False
  with self.assertRaises(p.Blocked):p.gates(self.m,self.s,self.ap,8)
 def test_cap(self):
  self.ap['G0']['max_total_usd']=1
  with self.assertRaises(p.Blocked):p.gates(self.m,self.s,self.ap,8)
 def test_stale_approval(self):
  self.m['shots'][0]['duration']+=1
  with self.assertRaises(p.Blocked):p.gates(self.m,self.s,self.ap,8)
 def test_nonpilot_requires_g2(self):
  with self.assertRaises(p.Blocked):p.gates(self.m,self.m['shots'][0],self.ap,8)
 def test_missing_references(self):
  with self.assertRaises(p.Blocked):p.request_for(self.s,{})
 def test_save_before_post_and_ambiguous_timeout(self):
  events=[]
  def save(m):events.append(('save',copy.deepcopy(m)))
  def network(*args):events.append(('post',None));raise TimeoutError()
  with patch.object(p,'request_for',return_value={'prompt':'fixture'}):
   with self.assertRaises(p.Blocked):p.submit(self.m,self.s,self.ap,{},'fake',transport=network,save=save)
  self.assertEqual(events[0][0],'save');self.assertEqual(events[0][1]['shots'][1]['attempts'][0]['status'],'submitting')
  self.assertEqual(self.s['attempts'][0]['status'],'uncertain');self.assertGreater(p.reserve_total(self.m),0)
  with self.assertRaises(p.Blocked):p.submit(self.m,self.s,self.ap,{},'fake',transport=network,save=save)
  self.assertEqual(sum(e[0]=='post' for e in events),1)
 def test_completed_submission_persists_job(self):
  def network(*args):return {'request_id':'fixture-id','status_url':'https://queue.fal.run/status','response_url':'https://queue.fal.run/result'}
  with patch.object(p,'request_for',return_value={'prompt':'fixture'}):p.submit(self.m,self.s,self.ap,{},'fake',transport=network,save=lambda m:None)
  self.assertEqual(self.s['generation_job_id'],'fixture-id');self.assertIsNone(self.s['actual_cost_usd'])
 def test_unknown_cost_is_reserved(self):
  self.s['attempts']=[{'reserved_usd':10,'actual_cost_usd':None}];self.assertEqual(p.reserve_total(self.m),10)
  self.s['attempts'][0]['actual_cost_usd']=8;self.assertEqual(p.reserve_total(self.m),8)
 def test_title_never_paid(self):
  with self.assertRaises(p.Blocked):p.submit(self.m,self.m['shots'][-1],self.ap,{},'fake',save=lambda m:None)
 def test_no_credential_on_untrusted_url(self):
  with self.assertRaises(p.Blocked):p.http('GET','https://example.com','fake')
if __name__=='__main__':unittest.main()
