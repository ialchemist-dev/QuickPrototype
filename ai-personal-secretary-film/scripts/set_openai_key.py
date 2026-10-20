#!/usr/bin/env python3
"""Securely add an OpenAI key while preserving other local configuration."""
import getpass, os
from pathlib import Path

def main():
    root=Path(__file__).resolve().parents[1]
    path=root/'.env.local'
    key=getpass.getpass('Paste your OpenAI API key (hidden), then press Enter: ').strip()
    if not key or any(c.isspace() for c in key):
        raise SystemExit('Empty or invalid input; nothing saved.')
    lines=path.read_text().splitlines() if path.exists() else []
    lines=[line for line in lines if not line.startswith('OPENAI_API_KEY=')]
    lines.append('OPENAI_API_KEY='+key)
    os.umask(0o077)
    temp=root/'.env.local.tmp'
    with open(temp,'w') as f:
        f.write('\n'.join(lines)+'\n');f.flush();os.fsync(f.fileno())
    os.chmod(temp,0o600);os.replace(temp,path)
    print('OpenAI key saved. Existing fal configuration preserved.')
if __name__=='__main__':main()
