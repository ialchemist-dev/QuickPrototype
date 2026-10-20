#!/usr/bin/env python3
"""Original deterministic synthesized Foley for the five-second opening test.
No external recordings, paid services, or third-party music.
"""
import json, subprocess, wave
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
SR=48000; DURATION=5; rng=np.random.default_rng(1019)
track=np.zeros((SR*DURATION,2),dtype=np.float64)
def add(signal,start,level=1,pan=0):
    pos=round(start*SR); n=min(len(signal),len(track)-pos)
    track[pos:pos+n,0]+=signal[:n]*level*np.sqrt((1-pan)/2)
    track[pos:pos+n,1]+=signal[:n]*level*np.sqrt((1+pan)/2)
def noise(duration,width):
    n=round(duration*SR)
    x=rng.normal(0,1,n)
    return np.convolve(x,np.ones(width)/width,mode='same')
def rustle(start,duration,level,pan):
    t=np.arange(round(duration*SR))/SR
    env=np.sin(np.pi*t/duration)**2*(.65+.35*np.sin(2*np.pi*7*t)**2)
    add(noise(duration,10)*env,start,level,pan)
def foot(start,level,pan):
    t=np.arange(round(.32*SR))/SR
    attack=1-np.exp(-t/.004)
    x=attack*(.7*np.sin(2*np.pi*91*t)*np.exp(-t/0.045)+.2*np.sin(2*np.pi*157*t)*np.exp(-t/.028))
    x+=noise(.32,70)*np.exp(-t/.035)*2
    add(x,start,level,pan)
def ceramic(start,level,pan):
    t=np.arange(round(.48*SR))/SR
    x=sum(a*np.sin(2*np.pi*f*t)*np.exp(-t/tau) for f,a,tau in [(1780,.55,.075),(2851,.25,.045),(4217,.12,.026)])
    x*=1-np.exp(-t/.0006)
    add(x,start,level,pan)
# Very soft diffuse indoor air; separate channels avoid a mono noise bed.
for channel in range(2):track[:,channel]+=noise(DURATION,130)*.016
rustle(.02,.65,.07,-.2)
foot(.20,.13,-.18);foot(.48,.10,.15)
rustle(.65,.45,.025,0)
# Kitchen cut at 2.5s. Soft plate/utensil contact and brief sliding texture.
rustle(2.55,.65,.022,.1)
ceramic(3.02,.045,.15)
rustle(3.05,.48,.045,.1)
ceramic(3.61,.023,-.1)
rustle(3.65,.45,.025,-.15)
# Gentle fades; preserve quiet Foley rather than maximizing loudness.
fade=round(.05*SR)
track[:fade]*=np.linspace(0,1,fade)[:,None]
track[-fade:]*=np.linspace(1,0,fade)[:,None]
peak=float(np.max(np.abs(track)))
folder=ROOT/'production/audio';folder.mkdir(exist_ok=True)
wav=folder/'shot01-foley.wav'
with wave.open(str(wav),'wb') as f:
    f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR)
    f.writeframes((np.clip(track,-1,1)*32767).astype('<i2').tobytes())
video=ROOT/'production/exports/shot01-first-test-1080p.mp4'
output=ROOT/'production/exports/shot01-with-sound-1080p.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-i',str(wav),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-t','5','-movflags','+faststart',str(output)],check=True)
report={'audio':'Original procedural Foley; no external recordings or music','seed':1019,'duration_seconds':5,'sample_rate':SR,'channels':2,'source_peak_dbfs':round(20*np.log10(peak),2),'added_api_cost_usd':0,'full_listening_review':'Not performed','cues':[{'seconds':.20,'event':'soft bare foot contact'},{'seconds':.48,'event':'second bare foot contact'},{'seconds':2.5,'event':'kitchen cut'},{'seconds':3.02,'event':'utensil and ceramic contact'},{'seconds':3.61,'event':'light second utensil contact'}]}
(ROOT/'production/tests/shot01/audio-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2));print(output)
if __name__=='__main__':pass
