#!/usr/bin/env python3
"""Create a local, provenance-preserving creative asset manifest (no paid calls)."""
import argparse, hashlib, json
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--idea',required=True)
p.add_argument('--file',action='append',default=[])
p.add_argument('--url',action='append',default=[])
p.add_argument('--out',default='data/intake/manifest.json')
a=p.parse_args()
files=[]
for name in a.file:
    f=Path(name).expanduser().resolve()
    if not f.is_file(): p.error(f'Missing asset: {name}')
    files.append({'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'source':'user-provided','fact_level':'unverified-source','purpose':'pending-review'})
manifest={'creative_idea':a.idea,'files':files,'urls':[{'url':u,'status':'pending-review'} for u in a.url],'approved_claims':[],'forbidden_claims':[],'status':'awaiting-source-review'}
out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(f'Intake saved: {out}. Review sources and claims before generation.')
