#!/usr/bin/env python3
"""Mix a rendered five-shot master with voiceover and music, then run the media gate."""
import argparse, subprocess
from pathlib import Path

def main():
    p=argparse.ArgumentParser(); p.add_argument('--video',required=True); p.add_argument('--voice',required=True); p.add_argument('--music',required=True); p.add_argument('--out',required=True); a=p.parse_args()
    filt='[0:a]volume=0.12[a0];[1:a]apad=pad_dur=60,volume=1.0[a1];[2:a]volume=0.16[a2];[a0][a1][a2]amix=inputs=3:duration=first:dropout_transition=3[a]'
    subprocess.run(['ffmpeg','-y','-i',a.video,'-i',a.voice,'-i',a.music,'-filter_complex',filt,'-map','0:v','-map','[a]','-t','60','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',a.out],check=True)

if __name__=='__main__': main()
