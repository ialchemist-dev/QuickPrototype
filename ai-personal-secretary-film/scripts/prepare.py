#!/usr/bin/env python3
"""Compile the locked README into reproducible shot and reference specifications."""
import hashlib,json,re,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; PROD=ROOT/'production'
def digest(b):return hashlib.sha256(b).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
CHAR='ALEX-01, a fictional 33-year-old East Asian woman, warm medium skin, oval face, dark brown almond-shaped eyes, straight dark chin-length bob tucked behind the left ear; understated, thoughtful, approachable; no resemblance to a celebrity'
WARD='cream cotton shirt with sleeves rolled once, charcoal straight-leg trousers, plain dark shoes; matte brushed-silver 3 mm ring on RIGHT INDEX finger only; no other jewelry; muted olive jacket outdoors and carried over left shoulder when specified'
locations={
'home':'APT-01: modest brick-city apartment, tall east-facing window frame-left, sage lower cabinets, cream plaster, oak counter, brushed steel kettle, ivory ceramic mug; round oak dining table frame-right; amber practical pendant at night',
'city':'CITY-01: contemporary fictional US neighborhood, low brick buildings, mature street trees, broad pavement; generic signage with no legible words; no recognizable landmark',
'cafe':'CAFE-01: same brick corner cafe, dark green wood door, broad window, oak counter, warm ivory tiles, unbranded takeaway cups',
'park':'PARK-01: quiet tree-lined pocket park near the same cafe, simple oak-slatted bench, soft neutral midday daylight',
'office':'OFFICE-01: small design studio, oak desk, cream walls, large north window frame-left, graphite sketches, charcoal window mullions, soft defocused adult colleagues only when scripted',
'end':'Pure black; typography composited locally, not generated'}
# One deliberate action, one move; speech framed away from visible lips.
directions=[
('home','Wide establishing, 35 mm','very slow 20 cm push-in','Morning gold','Empty kitchen; untouched phone face-down at rear edge of table, no notifications. Kettle steam rises. Leave space and stillness.'),
('home','Medium close, 50 mm, shoulder and hands','gentle lateral slide','Morning gold','Alex places the kettle down, then taps the RIGHT INDEX ring once with the left forefinger. Her mouth remains above the crop. Do not pour while tapping.'),
('home','Medium rear three-quarter, 35 mm','locked camera','Morning gold','Alex spreads toast while listening; shoulders settle. Ring remains on right index. Lips hidden by rear angle.'),
('home','Insert, 50 mm','locked camera','Morning gold','A blank cream reminder card lies flat on the oak counter. Keep it still and fully visible. The words Maya\'s birthday will be composited later; generate no writing.'),
('home','Close three-quarter, 50 mm','subtle push-in','Morning gold','Alex looks toward a small framed fictional photograph of two adult friends, smiles, then deliberately returns to breakfast. Photograph stays softly defocused; human line plays over the photo insert/shoulder, lips obscured.'),
('city','Medium rear wide, 35 mm','slow follow','Clear morning daylight','Alex steps through the apartment entry into sunlight, olive jacket over left shoulder, hands otherwise free.'),
('cafe','Medium rear-side tracking, 35 mm','parallel walking track','Clear morning daylight','Alex walks past the cafe window and glances at its door. Frame rear three-quarter, with no readable lip motion. A quiet yes precedes the cut; no cup yet.'),
('cafe','Hands insert, 50 mm','locked camera','Soft window daylight','One fictional adult barista slides a generic ivory takeaway cup across the oak counter. Alex receives it with the right hand; ring visible and stable. No payment device visible.'),
('park','Medium side-back, 50 mm','slow lateral drift','Neutral midday','Alex rests on the bench and glances toward a distant plain analog park clock, then looks ahead. No new wristwatch or phone. Lips obscured.'),
('cafe','Waist-high close, 50 mm','locked camera','Neutral midday','Alex picks up a plain brown lunch bag at the counter, one smooth action; the cup is absent. Only the server\'s hand enters frame.'),
('office','Medium wide, 35 mm','slow push toward window','Cool rainy daylight','Alex stops beside the corridor window as rain begins on the glass, gaze lifting. Olive jacket draped over left forearm.'),
('office','Hands and shoulder close, 50 mm','locked camera','Cool rainy daylight','Alex pauses, taps the RIGHT INDEX ring with left forefinger once, and turns toward the office. Frame does not reveal speaking lips.'),
('office','Over-shoulder medium, 35 mm','gentle forward slide','Cool soft daylight','Alex settles at the desk; two graphite concept sketches on separate sheets, no legible writing. Two adult colleagues remain defocused in the background.'),
('office','Over-shoulder close on papers, 50 mm','locked camera','Cool soft daylight','Alex compares two simple physical graphite concept sketches and slides one slightly forward. Face remains out of shot. Left sketch compact, right sketch modular; no generated labels.'),
('office','Close thoughtful eyes then hand, 50 mm','subtle tilt from eyes to chosen sketch','Cool daylight warming slightly','Alex makes a deliberate choice, rests a finger on the right modular sketch. Human line begins as camera reaches the hands; assistant replies over papers. No sent-message cue.'),
('city','Medium wide rear, 35 mm','slow walking follow','Low dusk gold','Alex walks home looking at people and trees, empty hands relaxed. Olive jacket worn open; no phone interaction.'),
('home','Over-shoulder object insert, 50 mm','gentle push-in','Warm pendant and fading window','A small unbranded printed gift-option card shows an abstract botanical art print, not a delivered purchased item. Alex points to the option; no checkout, price, or purchase confirmation. Mouth hidden.'),
('home','Medium two-shot, 35 mm','slow pull back','Warm intimate evening','Alex sets a serving bowl down and joins one fictional adult friend at the round oak table. Both share an unforced smile. Keep ring on right index; no voice interaction gesture. End on human presence.'),
('end','Full frame','none','Black','Fade from evening to black. Center ATTENTION RETURNED. Add secondary line Technology should give your attention back. locally in editing.')]
rows=[]
for line in (ROOT/'README.md').read_text().splitlines():
 if re.match(r'\| \d\d \|',line):
  c=[x.strip() for x in line.split('|')[1:-1]];rows.append(c)
assert len(rows)==19
shots=[];cursor=0
for i,c in enumerate(rows):
 sid=c[0];d=int(c[2][:-1]);edit=d+({'05':2,'07':1,'14':2}.get(sid,0));loc,size,move,light,action=directions[i]
 lines=[{'speaker':s,'text':t} for s,t in re.findall(r'(HUMAN|AI)(?:, very softly)?: “([^”]+)”',c[4])]
 refs=[] if sid=='19' else (['R02'] if sid in ['01','04'] else ['R01',{'home':'R02','city':'R03','cafe':'R03','park':'R03','office':'R04'}[loc]])
 if sid=='18':refs=['R01','R05']
 prompt=(f'Cinematic live-action realism, 16:9, one continuous shot, {edit} seconds.\nCharacter: {CHAR}.\nWardrobe: {WARD}.\nLocation: {locations[loc]}.\nAction: {action}\nCamera: {size}; {move}; natural lens rendering, restrained depth of field, no internal cuts.\nLighting: {light}; realistic skin texture, muted sage and oak palette, no glossy advertising look.\nContinuity: use approved reference identity and location only. Preserve facial proportions, bob haircut, ring hand and wardrobe.\nExclude: phone interaction, holograms, HUD, floating interfaces, generated captions, brand logos, distorted anatomy, extra fingers, duplicated props, sudden wardrobe changes. Include only the people and objects explicitly described above.\nAudio: no speech or music; final dialogue and sound are assembled in post.\n') if sid!='19' else 'LOCAL COMPOSITE ONLY. Four-second black end card. ATTENTION RETURNED. No paid video generation.\n'
 path=PROD/'prompts'/f'{sid}.txt';path.write_text(prompt)
 shots.append({'id':sid,'storyboard_duration':d,'duration':edit,'start':cursor,'end':cursor+edit,'visual':c[3],'canonical_audio':c[4],'dialogue':lines,'location':loc,'camera':size+'; '+move,'lighting':light,'action':action,'pilot':sid in ['02','07','14','18'],'required_references':refs,'prompt_path':str(path.relative_to(ROOT)),'prompt_hash':digest(prompt.encode()),'provider':'local' if sid=='19' else 'fal','model':'local-title-v1' if sid=='19' else 'bytedance/seedance-2.5/us/reference-to-video','model_version':'provider alias; immutable version not exposed','resolution':'1080p','reference_hashes':{},'attempt_count':0,'generation_job_id':None,'status':'planned','output_path':None,'estimated_cost_usd':round(edit*1.165,4) if sid!='19' else 0,'actual_cost_usd':None,'qc_notes':[],'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'updated_at':None,'idempotency_key':digest((sid+digest(prompt.encode())).encode()),'attempts':[]});cursor+=edit
manifest=PROD/'manifest.json'
if manifest.exists():raise SystemExit('Refusing to overwrite existing execution manifest; reconcile creative changes explicitly.')
dump(manifest,{'schema_version':1,'title':'ATTENTION RETURNED','source_readme_sha256':digest((ROOT/'README.md').read_bytes()),'timeline_seconds':cursor,'fps':24,'size':[1920,1080],'paid_calls_made':0,'shots':shots,'assets':[],'actual_spend_usd':0,'provider_access_verified':False})
dump(PROD/'storyboard.json',shots)
refs=[('R01','Character master',f'{CHAR}. {WARD}. Neutral soft daylight, cream seamless background. Reference sheet with front, three-quarter and profile views of exactly the same adult woman, plus one right-index ring detail. Natural 50 mm lens. No text or logos. Derive separate crops from the approved sheet, do not invent new faces.'),('R02','Apartment geography',locations['home']+'. Wide 35 mm empty establishing still, morning sunlight from frame-left. Add a separate evening lighting variant after approval. No text, no logos.'),('R03','Cafe and street',locations['cafe']+'. '+locations['city']+'. Wide eye-level exterior establishing still with visible counter through window. Soft daytime light. No identifiable people, no text or logos.'),('R04','Office geography',locations['office']+'. Empty medium wide frame, camera behind desk toward rain-streaked window. Two simple graphite sketches on desk. No screens or legible text.'),('R05','Evening relational master',f'{CHAR}. {WARD}, no jacket. '+locations['home']+'. Evening dinner with one fictional adult friend, 34, medium-brown skin, short curls, navy knit top. Warm pendant light, muted amber, round oak table, serving bowl. Natural 35 mm lens, restrained intimacy. Use approved character and apartment reference images. No text, no logos.')]
refdata=[]
for rid,title,prompt in refs:
 (PROD/'references'/f'{rid}.txt').write_text(prompt+'\n');refdata.append({'id':rid,'title':title,'prompt':prompt,'status':'planned','approved':False,'path':None,'sha256':None})
dump(PROD/'references/plan.json',refdata)
dump(PROD/'approvals.example.json',{'G0':{'approved':False,'evidence':'user message / date','provider':'fal','model':'bytedance/seedance-2.5/us/reference-to-video','max_total_usd':550,'max_pilot_usd':110,'account_access_confirmed':False,'fictional_faces_permitted':False,'pricing_checked_at':None},'G1':{'approved':False,'evidence':'specific reference hashes and animatic review','manifest_creative_hash':None},'G2':{'approved':False,'evidence':'four pilot review and remainder authorization'},'G3':{'approved':False,'evidence':'final audiovisual review; publishing separately authorized'}})
(PROD/'audio/final_script.md').write_text('# Canonical dialogue — ATTENTION RETURNED\n\n'+ '\n\n'.join(f'## Shot {s["id"]} — {s["start"]}–{s["end"]} s\n\n'+s['canonical_audio'] for s in shots)+'\n')
print(f'Prepared {len(shots)} shots; {cursor}s edit; {sum(s["duration"] for s in shots if s["pilot"])}s pilot; {sum(len(l["text"]) for s in shots for l in s["dialogue"])} dialogue characters.')
