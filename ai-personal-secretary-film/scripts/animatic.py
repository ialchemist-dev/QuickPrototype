#!/usr/bin/env python3
"""Free local schematic animatic, scratch voices, original synthesized temp score."""
import json,subprocess,textwrap,wave,hashlib,re
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'production';SR=24000
FONT='/System/Library/Fonts/Supplemental/Arial.ttf';BOLD='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
def font(n,b=False):return ImageFont.truetype(BOLD if b else FONT,n)
def run(args):subprocess.run(args,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)]))
def text(d,xy,t,size=26,fill='#e7dbc8',width=75):
 d.multiline_text(xy,'\n'.join(textwrap.wrap(t,width)),font=font(size),fill=fill,spacing=8)
def person(d,x,y,s=1,friend=False,back=False):
 skin='#ad795f' if not friend else '#885f4a';shirt='#e2d9c4' if not friend else '#334b59';hair='#2a2626'
 d.ellipse((x-34*s,y-95*s,x+34*s,y-20*s),fill=hair)
 d.ellipse((x-26*s,y-83*s,x+26*s,y-22*s),fill=skin)
 if back:d.ellipse((x-32*s,y-95*s,x+32*s,y-30*s),fill=hair)
 else:
  d.arc((x-34*s,y-95*s,x+34*s,y-20*s),180,350,fill=hair,width=max(2,int(10*s)))
  d.line((x-15*s,y-58*s,x-8*s,y-58*s),fill=hair,width=2);d.line((x+8*s,y-58*s,x+15*s,y-58*s),fill=hair,width=2)
 d.polygon([(x-30*s,y-20*s),(x+30*s,y-20*s),(x+56*s,y+110*s),(x-56*s,y+110*s)],fill=shirt)
 d.line((x-30*s,y,x-70*s,y+78*s),fill=shirt,width=max(2,int(20*s)));d.line((x+30*s,y,x+66*s,y+77*s),fill=shirt,width=max(2,int(20*s)))
 d.ellipse((x+56*s,y+68*s,x+75*s,y+88*s),fill=skin);d.line((x+59*s,y+73*s,x+72*s,y+73*s),fill='#b8b9ad',width=max(2,int(3*s)))
 d.line((x-22*s,y+108*s,x-28*s,y+230*s),fill='#303333',width=max(2,int(30*s)));d.line((x+22*s,y+108*s,x+28*s,y+230*s),fill='#303333',width=max(2,int(30*s)))
def scene(s):
 im=Image.new('RGB',(1920,1080),'#151b1b');d=ImageDraw.Draw(im);loc=s['location'];night=s['id'] in ['17','18'];rain=loc=='office';warm='#897257' if night else '#b8ac91';bg='#687e83' if rain else warm
 d.rectangle((60,125,1860,800),fill=bg)
 if loc in ['home','office']:
  d.rectangle((135,170,530,530),fill='#586c70' if night else '#a6c2c3' if rain else '#f0ddac');d.line((330,170,330,530),fill='#4d5650',width=12);d.line((135,350,530,350),fill='#4d5650',width=12)
  d.polygon([(535,530),(1100,800),(65,800)],fill='#a39270' if not rain else '#77888a')
  d.rectangle((180,580,1000,630),fill='#765a42');d.rectangle((180,630,1000,790),fill='#667564')
  if rain:
   for x in range(150,530,32):d.line((x,185,x-12,510),fill='#ccdbda',width=2)
  if s['id']=='01':d.rounded_rectangle((1100,650,1250,702),radius=12,fill='#22292c')
  if s['id']=='04':
   d.polygon([(650,380),(1250,400),(1220,650),(620,620)],fill='#e9dfc8');text(d,(690,470),"Maya's birthday",52,fill='#484740')
  elif s['id'] in ['13','14','15']:
   person(d,650,430,1.4,back=True);d.rectangle((800,590,1600,780),fill='#806d54')
   for x in [950,1260]:
    d.polygon([(x,610),(x+190,610),(x+210,750),(x-20,750)],fill='#e5dfd1');d.rectangle((x+20,640,x+150,700),outline='#66685f',width=3);d.line((x+30,650,x+125,690),fill='#66685f',width=3)
  elif s['id']=='17':
   person(d,670,460,1.2,back=True);d.rectangle((1050,500,1400,730),fill='#ece0cb');d.line((1220,680,1215,540),fill='#6a795f',width=5)
   for y in [570,600,630]:d.ellipse((1170,y,1220,y+22),fill='#7c8969')
  elif s['id']=='18':
   person(d,720,440,1.1);person(d,1300,440,1.1,friend=True);d.ellipse((630,590,1420,810),fill='#78553d');d.ellipse((940,630,1100,690),fill='#c5b691');d.polygon([(1000,145),(1100,145),(1160,230),(940,230)],fill='#e2b776')
  elif s['id']!='01':
   person(d,1000,430,1.45,back=s['id'] in ['03','05'])
   if s['id'] in ['02','03']:d.rectangle((1100,540,1170,605),fill='#e3d8c1')
 else:
  d.rectangle((60,620,1860,800),fill='#696c60')
  for x in [120,580,1420]:
   d.rectangle((x,160,x+320,620),fill='#756b5b');d.rectangle((x+45,240,x+275,440),fill='#354b48');d.rectangle((x+100,455,x+210,620),fill='#38544b')
  if loc=='park':
   d.rectangle((600,550,1300,585),fill='#6b533e')
   for x in [280,1550]:d.rectangle((x,330,x+30,650),fill='#665341');d.ellipse((x-160,160,x+180,440),fill='#5e765e')
  person(d,1000,410,1.3,back=True)
  if s['id'] in ['08','10']:
   d.rectangle((500,640,1480,800),fill='#785b42');d.rectangle((1190,550,1270,640),fill='#e3d8c1' if s['id']=='08' else '#b59b72')
 d.rectangle((60,125,1860,800),outline='#d7c9ad',width=2)
 text(d,(64,35),f'ATTENTION RETURNED   /   SHOT {s["id"]}   /   {s["start"]:03d}–{s["end"]:03d}s',28)
 text(d,(1110,40),'SCHEMATIC ANIMATIC · NOT GENERATED FOOTAGE',21,fill='#d7b778',width=70)
 text(d,(65,835),s['visual'],32,width=100);text(d,(65,935),s['camera']+' / '+s['lighting'],23,fill='#aeb8af',width=120)
 if s['id']=='19':
  im=Image.new('RGB',(1920,1080),'black');d=ImageDraw.Draw(im);d.text((960,500),'ATTENTION RETURNED.',font=font(78),fill='#f2eadb',anchor='mm');d.text((960,600),'Technology should give your attention back.',font=font(30),fill='#adad9f',anchor='mm')
 return im

def srt_time(t):
 ms=round(t*1000);return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
def wavwrite(path,data):
 with wave.open(str(path),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(SR);f.writeframes((np.clip(data,-.98,.98)*32767).astype('<i2').tobytes())
def main():
 shots=json.loads((P/'storyboard.json').read_text());duration=shots[-1]['end'];boards=P/'edit/boards';boards.mkdir(exist_ok=True)
 for s in shots:scene(s).save(boards/f'{s["id"]}.png')
 # A free illustrated contact sheet for composition approval, not a face reference.
 sheet=Image.new('RGB',(1600,5*230),'#151b1b')
 for i,s in enumerate(shots):
  thumb=Image.open(boards/f'{s["id"]}.png').resize((400,225));sheet.paste(thumb,(i%4*400,i//4*230))
 sheet.save(P/'references/storyboard-contact-sheet.jpg',quality=90)
 mix=np.zeros(int(duration*SR),dtype=np.float32);timing=[];captions=[];n=0;report=[]
 for s in shots:
  utterances=[]
  for j,line in enumerate(s['dialogue']):
   voice='Samantha' if line['speaker']=='AI' else 'Karen';rate=170
   key=hashlib.sha256((voice+str(rate)+line['text']).encode()).hexdigest()[:12];base=P/'audio'/f'{s["id"]}-{j}-{key}';aiff=base.with_suffix('.aiff');wav=base.with_suffix('.wav')
   if not wav.exists():
    run(['say','-v',voice,'-r',str(rate),'-o',str(aiff),line['text']]);run(['ffmpeg','-y','-v','error','-i',str(aiff),'-ar',str(SR),'-ac','1','-c:a','pcm_s16le',str(wav)])
   with wave.open(str(wav)) as f:data=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(np.float32)/32768
   # Trim only leading/trailing near-silence; preserve breaths inside each line.
   active=np.where(np.abs(data)>.008)[0]
   if len(active):data=data[max(0,active[0]-int(.08*SR)):min(len(data),active[-1]+int(.15*SR))]
   utterances.append((line,data))
  total=sum(len(data)/SR for _,data in utterances)+max(0,len(utterances)-1)*.22
  available=s['duration']-.5
  if total>available:report.append({'shot':s['id'],'dialogue_seconds':round(total,2),'available_seconds':available,'status':'OVERFLOW: revise timing before final voice generation'})
  # Do not silently speed speech or truncate. A failing timing check stops the render.
  if total>available:continue
  offset=s['start']+.25
  for line,data in utterances:
   start=round(offset*SR);mix[start:start+len(data)]+=data*.8;end=offset+len(data)/SR;n+=1
   captions.append(f'{n}\n{srt_time(offset)} --> {srt_time(end)}\n'+ '\n'.join(textwrap.wrap(line['text'],46))+'\n')
   timing.append({'shot':s['id'],'speaker':line['speaker'],'text':line['text'],'start':round(offset,3),'end':round(end,3),'voice_type':'LOCAL SCRATCH ONLY'});offset=end+.22
 (P/'audio/timing-check.json').write_text(json.dumps(report,indent=2)+'\n')
 if report:raise SystemExit('Dialogue timing overflows; inspect production/audio/timing-check.json')
 # Original slow additive score: simple open fifths, not a reference to an existing song.
 t=np.arange(len(mix))/SR;music=np.zeros_like(mix)
 for start in np.arange(0,duration,8):
  idx=(t>=start)&(t<min(start+8,duration));u=t[idx]-start;env=np.minimum(1,u/1.5)*np.minimum(1,(8-u)/3)
  freq=[130.8128,146.8324,164.8138,130.8128][int(start/8)%4]
  music[idx]=.018*env*(np.sin(2*np.pi*freq*u)+.35*np.sin(2*np.pi*freq*1.5*u))
 # Reduce music during lines. Original synthesized soft room texture, not recorded ambience.
 for cue in timing:music[int(cue['start']*SR):int(cue['end']*SR)]*=.35
 rng=np.random.default_rng(42);air=rng.normal(0,.0009,len(mix));mix+=music+air.astype(np.float32);mix*=np.minimum(1,t/1.2)*np.minimum(1,(duration-t)/2)
 wavwrite(P/'audio/animatic_mix.wav',mix);wavwrite(P/'audio/original_temp_score.wav',music)
 (P/'audio/dialogue-timing.json').write_text(json.dumps(timing,indent=2,ensure_ascii=False)+'\n');(P/'audio/captions_en.srt').write_text('\n'.join(captions));(P/'audio/captions_en.vtt').write_text('WEBVTT\n\n'+re.sub(r'(\d\d:\d\d:\d\d),(\d{3})',r'\1.\2','\n'.join(captions)))
 concat=P/'edit/animatic.ffconcat';concat.write_text('ffconcat version 1.0\n'+''.join(f"file 'boards/{s['id']}.png'\nduration {s['duration']}\n" for s in shots)+"file 'boards/19.png'\n")
 out=P/'exports/animatic_1080p_24fps.mp4'
 cache=P/'exports/animatic-cache.txt';fingerprint=hashlib.sha256(Path(__file__).read_bytes()+(P/'storyboard.json').read_bytes()).hexdigest()
 if not out.exists() or not cache.exists() or cache.read_text()!=fingerprint:run(['ffmpeg','-y','-v','error','-safe','0','-f','concat','-i',str(concat),'-i',str(P/'audio/animatic_mix.wav'),'-vf','fps=24,format=yuv420p','-t',str(duration),'-c:v','libx264','-preset','veryfast','-crf','23','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(out)])
 cache.write_text(fingerprint)
 report={'artifact':str(out.relative_to(ROOT)),'duration':duration,'probe':probe(out),'dialogue_cues':len(timing),'peak_before_encoding_dbfs':round(float(20*np.log10(max(abs(mix)))),2),'media_type':'schematic animatic, not generated footage','human_review':'pending','paid_cost_usd':0}
 report['probe']['format']['filename']=str(out.relative_to(ROOT))
 (P/'qc/animatic-report.json').write_text(json.dumps(report,indent=2)+'\n');print(f'Rendered {out.name}: {duration}s, {len(timing)} lines, no paid services.')
if __name__=='__main__':main()
