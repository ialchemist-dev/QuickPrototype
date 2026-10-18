#!/usr/bin/env python3
"""Technical QC is not a substitute for audiovisual review."""
import argparse,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'production'
def check(path):
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]));v=next(s for s in info['streams'] if s['codec_type']=='video');a=next((s for s in info['streams'] if s['codec_type']=='audio'),None)
 logs=subprocess.run(['ffmpeg','-hide_banner','-i',str(path),'-af','volumedetect','-vf','blackdetect=d=0.2:pix_th=0.1','-f','null','-'],capture_output=True,text=True,check=True).stderr
 peak=re.search(r'max_volume: ([\-\d.]+) dB',logs);blacks=[{'start':float(x),'end':float(y),'duration':float(z)} for x,y,z in re.findall(r'black_start:([\d.]+) black_end:([\d.]+) black_duration:([\d.]+)',logs)]
 expected=json.loads((P/'manifest.json').read_text())['timeline_seconds'];caps=(P/'audio/captions_en.srt').read_text();spoken=[l['text'] for s in json.loads((P/'storyboard.json').read_text()) for l in s['dialogue']]
 # Compare full normalized caption bodies, ignoring only wrap and cue metadata.
 bodies=[]
 for block in caps.strip().split('\n\n'):
  rows=block.splitlines();bodies.append(' '.join(rows[2:]))
 tests={'1080p':(v['width'],v['height'])==(1920,1080),'24fps':v['r_frame_rate']=='24/1','H264':v['codec_name']=='h264','AAC':bool(a and a['codec_name']=='aac'),'duration_matches':abs(float(info['format']['duration'])-expected)<.1,'within_120_150':120<=float(info['format']['duration'])<=150,'no_sample_clipping':bool(peak and float(peak[1])<0),'black_only_intentional_end':all(x['start']>=expected-4-.25 for x in blacks),'captions_match_canonical':bodies==spoken}
 return {'file':str(path.relative_to(ROOT)),'checks':tests,'sample_peak_dbfs':float(peak[1]) if peak else None,'black_intervals':blacks,'human_visual_audio_review':'NOT PERFORMED; owner review required','note':'Sample peak only, not intersample true peak. No claim of final loudness compliance or semantic video QC.'}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('file');a=ap.parse_args();r=check(Path(a.file).resolve());(P/'qc/technical-report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));raise SystemExit(0 if all(r['checks'].values()) else 1)
