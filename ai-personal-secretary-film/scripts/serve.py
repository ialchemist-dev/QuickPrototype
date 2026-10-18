#!/usr/bin/env python3
"""Private review server; defaults to loopback. Never serves credentials or approval files."""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import unquote,urlsplit
import os,re,argparse
ROOT=Path(__file__).resolve().parents[1]/'production'
class Handler(SimpleHTTPRequestHandler):
 def do_GET(self):
  path=unquote(urlsplit(self.path).path)
  if any(x.startswith('.') for x in path.split('/')) or 'private' in path.split('/') or '.local.' in path or 'approvals' in path:
   self.send_error(403);return
  super().do_GET()
 def send_head(self):
  self.byte_limit=None
  path=self.translate_path(self.path)
  header=self.headers.get('Range','')
  if header and os.path.isfile(path):
   size=os.path.getsize(path);match=re.fullmatch(r'bytes=(\d+)-(\d*)',header)
   if match:
    start=int(match[1]);end=min(int(match[2]) if match[2] else size-1,size-1)
    if start>=size or end<start:self.send_error(416);return None
    f=open(path,'rb');f.seek(start);self.byte_limit=end-start+1
    self.send_response(206);self.send_header('Content-Type',self.guess_type(path));self.send_header('Accept-Ranges','bytes');self.send_header('Content-Range',f'bytes {start}-{end}/{size}');self.send_header('Content-Length',str(self.byte_limit));self.end_headers();return f
  return super().send_head()
 def copyfile(self,source,outputfile):
  if self.byte_limit is None:return super().copyfile(source,outputfile)
  remaining=self.byte_limit
  while remaining:
   chunk=source.read(min(remaining,1024*1024))
   if not chunk:break
   outputfile.write(chunk);remaining-=len(chunk)
 def list_directory(self,path):self.send_error(403);return None
 def log_message(self,*args):pass
os.chdir(ROOT)
parser=argparse.ArgumentParser();parser.add_argument('--bind',default='127.0.0.1');parser.add_argument('--port',type=int,default=8766);args=parser.parse_args()
print(f'Review: http://{args.bind}:{args.port}/review.html',flush=True)
ThreadingHTTPServer((args.bind,args.port),Handler).serve_forever()
