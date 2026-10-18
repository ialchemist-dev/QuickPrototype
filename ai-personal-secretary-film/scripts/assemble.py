#!/usr/bin/env python3
"""Assemble approved footage only. Never substitutes animatic frames or scratch voices."""
import json,subprocess,shutil
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'production'
def run(a):subprocess.run(a,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
def main():
 m=json.loads((P/'manifest.json').read_text());audio=P/'audio/final_mix.wav';licensefile=P/'audio/final_audio_approval.local.json'
 if not audio.exists() or not licensefile.exists():raise SystemExit('BLOCKED: final licensed/approved audio mix missing; never use scratch audio for final output.')
 meta=json.loads(licensefile.read_text())
 if not meta.get('approved') or not meta.get('license_evidence') or not meta.get('caption_timing_verified'):raise SystemExit('BLOCKED: audio approval, rights or final caption timing not verified')
 missing=[s['id'] for s in m['shots'][:-1] if s['status']!='approved' or not s['output_path']]
 if missing:raise SystemExit('BLOCKED: footage not reviewed/approved: '+', '.join(missing))
 edit=P/'edit/conform';edit.mkdir(exist_ok=True);clips=[]
 for s in m['shots']:
  dest=edit/f'{s["id"]}.mp4'
  if s['id']=='19':
   im=Image.new('RGB',(1920,1080));d=ImageDraw.Draw(im);f=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',76);d.text((960,510),'ATTENTION RETURNED.',font=f,fill='#f2eadb',anchor='mm');plate=edit/'endcard.png';im.save(plate)
   args=['-loop','1','-framerate','24','-i',str(plate)]
  else:
   src=ROOT/s['output_path'];probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(src)]));v=next(x for x in probe['streams'] if x['codec_type']=='video')
   if float(probe['format']['duration'])<s['duration']-.05:raise SystemExit('Clip too short: '+s['id'])
   if v['width']<1920 or v['height']<1080:raise SystemExit('Native resolution below approved target: '+s['id'])
   args=['-i',str(src)]
  vf='scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=24,setsar=1,format=yuv420p'
  if s['id']=='18':vf+=f',fade=t=out:st={s["duration"]-.6}:d=0.6'
  # No mid-shot dissolves: simple cuts protect dialogue timing and one continuous visual action.
  run(['ffmpeg','-y','-v','error',*args,'-t',str(s['duration']),'-an','-vf',vf,'-c:v','libx264','-preset','medium','-crf','18',str(dest)]);clips.append(dest)
 listing=edit/'clips.ffconcat';listing.write_text('ffconcat version 1.0\n'+''.join(f"file '{x.name}'\n" for x in clips))
 out=P/'exports/final_1080p_24fps.mp4'
 run(['ffmpeg','-y','-v','error','-safe','0','-f','concat','-i',str(listing),'-i',str(audio),'-map','0:v','-map','1:a','-t',str(m['timeline_seconds']),'-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-movflags','+faststart',str(out)])
 shutil.copy2(out,P/'exports/review.mp4');shutil.copy2(P/'audio/captions_en.srt',P/'exports/captions_en.srt');shutil.copy2(P/'audio/final_script.md',P/'exports/final_script.md');shutil.copy2(P/'manifest.json',P/'exports/shot_manifest.json');shutil.copy2(P/'credits_and_licenses.md',P/'exports/credits_and_licenses.md')
 print('Assembled master and review; run technical QC and obtain G3 viewing/listening approval. NOT published.')
if __name__=='__main__':main()
