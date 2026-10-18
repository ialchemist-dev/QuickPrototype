#!/usr/bin/env python3
"""Register reference and voice plans locally. This script never makes API calls."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pipeline as p

def main():
 with p.locked():
  m=p.read(p.PROD/'manifest.json');assets=m['assets'];existing={x['id'] for x in assets}
  def add(id,kind,model,inputs,cost,refs=None):
   if id in existing:return
   promptfile=p.PROD/('references' if kind=='reference' else 'audio')/(id+'.txt')
   text=inputs.get('prompt',inputs.get('text',''));promptfile.write_text(text+'\n')
   assets.append({'id':id,'kind':kind,'provider':'fal','model':model,'model_version':'provider alias','input':inputs,'input_reference_ids':refs or [],'required_references':refs or [],'reference_hashes':{},'prompt_path':str(promptfile.relative_to(p.ROOT)),'prompt_hash':p.sha(promptfile.read_bytes()),'status':'planned','attempt_count':0,'attempts':[],'generation_job_id':None,'output_path':None,'estimated_cost_usd':cost,'actual_cost_usd':None,'qc_notes':[],'created_at':p.now(),'updated_at':None,'idempotency_key':p.sha((id+text).encode())})
  for r in p.read(p.PROD/'references/plan.json'):
   inp={'prompt':r['prompt'],'image_size':{'width':2560,'height':1440},'num_images':1,'max_images':1,'enable_safety_checker':True}
   add(r['id'],'reference','fal-ai/bytedance/seedream/v4.5/'+('edit' if r['id']=='R05' else 'text-to-image'),inp,.04,['R01','R02'] if r['id']=='R05' else [])
  for s in m['shots']:
   for i,line in enumerate(s['dialogue']):
    # Proposed stock casting, to be auditioned after G0. No impersonation or cloning.
    inp={'text':line['text'],'voice':'Rachel' if line['speaker']=='AI' else 'Aria','stability':.65,'similarity_boost':.75,'style':.1,'speed':1,'timestamps':True,'language_code':'en'}
    add(f'V{s["id"]}-{i+1}','voice','fal-ai/elevenlabs/tts/multilingual-v2',inp,round(len(line['text'])*.1/1000,6))
  p.atomic(p.PROD/'manifest.json',m);print(f'{len(assets)} planned auxiliary jobs, zero submissions')
if __name__=='__main__':main()
