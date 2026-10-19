#!/usr/bin/env python3
"""Create a silent five-second review edit from the two downloaded originals."""
import json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
state=json.loads((ROOT/'production/private/shot01-state.json').read_text())
paths=[str(ROOT/s['output_path']) for s in state['shots']]
output=ROOT/'production/exports/shot01-first-test.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-i',paths[0],'-i',paths[1],'-filter_complex',
 '[0:v]trim=start=0:duration=2.5,setpts=PTS-STARTPTS,crop=1920:1080,fps=24,setsar=1[a];'
 '[1:v]trim=start=1.5:duration=2.5,setpts=PTS-STARTPTS,crop=1920:1080,fps=24,setsar=1[b];'
 '[a][b]concat=n=2:v=1:a=0[v]', '-map','[v]','-c:v','libx264','-crf','18',
 '-pix_fmt','yuv420p','-movflags','+faststart',str(output)],check=True)
print(output)
