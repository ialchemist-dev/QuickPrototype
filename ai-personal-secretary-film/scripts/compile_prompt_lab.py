#!/usr/bin/env python3
"""Offline prompt compiler, not an LLM optimizer or generation client."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LAB=ROOT/'production/prompt-lab'
def compile_pack(casting, motion):
    if motion['subject_count']!=1:raise ValueError('This experiment requires one subject')
    if motion['duration_seconds']!=5:raise ValueError('This experiment is a five-second shot')
    c=casting['common']
    if c['age']<18:raise ValueError('Casting brief must describe an adult')
    portraits=[]
    for v in casting['variants']:
        portraits.append((v['id'],v['name'],f"Photorealistic cinematic casting portrait of a {c['age']}-year-old {c['identity']} with {v['appearance']}. {v['styling'].capitalize()}. She wears {c['wardrobe']}. {c['framing'].capitalize()}. {c['lighting'].capitalize()}. Background: {c['background']}. Expression: {c['expression']}. {c['constraints'].capitalize()}."))
    video=' '.join([motion['action'],motion['camera'],motion['continuity'],'One continuous five-second take.'])
    return portraits,video

def main():
    casting=json.loads((LAB/'casting-briefs.json').read_text());motion=json.loads((LAB/'motion-brief.json').read_text())
    portraits,video=compile_pack(casting,motion)
    sections=['# Casting and motion prompt pack\n\nWritten proposals only. No reference portrait selected; no image, video or TTS generation performed.\n']
    for ident,name,prompt in portraits:
        sections.append(f'## {ident} — {name}\n\n{prompt}\n')
    sections.append('## Motion draft — use only with a selected reference\n\n'+video+'\n\n'+motion['capability_note']+'\n\nAudio/edit: '+motion['audio_note'])
    (LAB/'prompt-pack.md').write_text('\n'.join(sections)+'\n')
    print('Compiled 3 casting proposals and 1 reference-dependent motion draft. Network calls: 0. Ready to generate: no.')
if __name__=='__main__':main()
