"""Offline media gate for a completed AdForge output."""
import json, subprocess, sys
from pathlib import Path

def verify(path: str, expected_duration: float = 60, expected_ratio=(16,9)):
    p=Path(path)
    if not p.is_file(): raise FileNotFoundError(path)
    subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    out=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=width,height,codec_type','-of','json',str(p)])
    info=json.loads(out); fmt=float(info['format']['duration']); video=next(s for s in info['streams'] if s['codec_type']=='video')
    ratio=video['width']/video['height']
    if abs(fmt-expected_duration)>1.5: raise ValueError(f'duration {fmt} != {expected_duration}')
    if abs(ratio-expected_ratio[0]/expected_ratio[1])>.01: raise ValueError(f'ratio {ratio}')
    return {'status':'PASS','duration':fmt,'width':video['width'],'height':video['height']}

if __name__=='__main__': print(json.dumps(verify(sys.argv[1]),ensure_ascii=False))
