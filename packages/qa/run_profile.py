"""Minimal profile gate: validates technical media and required creative fields."""
import argparse, json, subprocess
from pathlib import Path

def main():
    p=argparse.ArgumentParser(); p.add_argument('--media',required=True); p.add_argument('--profile',choices=['EC','BR','DH'],required=True); p.add_argument('--creative',required=True); a=p.parse_args()
    c=json.loads(Path(a.creative).read_text()); required=['creative_id','mode','lang','idea','hook','cta']; missing=[x for x in required if not c.get(x)]
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,width,height','-of','json',a.media]))
    v=next((x for x in probe['streams'] if x.get('codec_type')=='video'),{})
    failures=missing[:]
    if not v: failures.append('video_stream_missing')
    if a.profile=='BR' and (v.get('width'),v.get('height')) != (1280,720): failures.append('BR_MASTER_NOT_1280x720')
    report={'schema':'adforge.qa.v03','profile':a.profile,'status':'FAIL' if failures else 'PASS','failures':failures,'media':{'width':v.get('width'),'height':v.get('height'),'duration':probe.get('format',{}).get('duration')}}
    print(json.dumps(report,ensure_ascii=False,indent=2)); raise SystemExit(1 if failures else 0)
if __name__=='__main__': main()
