#!/usr/bin/env python3
"""Generate a 60s Chinese 16:9 StoryClaw ad as five Giggle shots and stitch with FFmpeg."""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, time, uuid
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; TX=DATA/'transactions'; OUT=ROOT/'outputs'
BASE=os.getenv('GIGGLE_API_BASE','https://giggle.pro').rstrip('/'); KEY=os.getenv('GIGGLE_API_KEY')
MODEL=os.getenv('VIDEO_MODEL','seedance-2.0-pro')
SHOTS=[
('01_hook','深蓝色科技工作台上，一台StoryClaw智能设备从暗处亮起，蓝金色光线勾勒机身轮廓，镜头快速推进，桌面上的复杂信息流被它整理成清晰的可视化路径。前三秒必须形成“混乱变清晰”的强烈对比，无字幕无Logo，商业产品摄影，16:9。'),
('02_problem','年轻创业者面对多个屏幕、零散便签和不断弹出的提醒，表情焦虑，镜头环绕展示混乱；StoryClaw设备在画面右侧保持清晰可见并发出柔和指示灯，真实办公空间，电影级光影，16:9，无屏幕乱码。'),
('03_solution','StoryClaw设备成为画面中心，柔和光束连接电脑、手机和纸质笔记，信息被组织成一条清晰的行动路径；镜头从中景平滑推至产品近景，强调可靠、安静、高效，品牌级科技广告摄影，16:9，无文字水印。'),
('04_proof','创业者按下StoryClaw设备，桌面从凌乱变得井然有序，日程、灵感和任务以抽象光点归位；人物露出轻松自信的笑容，镜头跟随手部动作再回到产品，温暖自然光，真实可用产品展示，16:9，无字幕。'),
('05_cta','干净的深色渐变背景中，StoryClaw设备置于画面中央偏右，蓝金轮廓光，高级商业产品英雄镜头，镜头缓慢环绕后定格，左侧留出后期文字安全区，画面只保留产品和光影，不生成任何文字或Logo，16:9。'),
]
def headers(): return {'Authorization':f'Bearer {KEY}','Content-Type':'application/json'}
def sha(s): return hashlib.sha256(s.encode()).hexdigest()
def request(path,payload):
    r=requests.post(BASE+path,headers=headers(),json=payload,timeout=90); r.raise_for_status(); return r.json()
def query(task_id):
    r=requests.get(BASE+'/api/v1/generation/task/query',headers=headers(),params={'task_id':task_id},timeout=60); r.raise_for_status(); return r.json()
def result_url(p):
    for k in ('video_url','url','output_url','result_url'):
        if isinstance(p.get(k),str) and p[k].startswith('http'): return p[k]
    for k in ('videos','results','data'):
        v=p.get(k)
        if isinstance(v,list):
            for x in v:
                if isinstance(x,str) and x.startswith('http'): return x
                if isinstance(x,dict):
                    u=result_url(x)
                    if u:return u
        if isinstance(v,dict):
            u=result_url(v)
            if u:return u
    return None
def submit(shot_id,prompt,dry):
    tx=TX/f'{shot_id}.json'; TX.mkdir(parents=True,exist_ok=True)
    if tx.exists():
        old=json.loads(tx.read_text());
        if old.get('task_id') and old.get('state') not in ('FAILED_RECONCILED','BLOCKED'): return old
    record={'transaction_id':uuid.uuid4().hex,'shot_id':shot_id,'prompt_sha256':sha(prompt),'state':'PREPARED','model':MODEL}
    if dry: tx.write_text(json.dumps(record,ensure_ascii=False,indent=2)); return record
    if not KEY: raise RuntimeError('GIGGLE_API_KEY is not set')
    payload={'prompt':prompt,'model':MODEL,'duration':12,'aspect_ratio':'16:9','resolution':'720p','generate_count':1}
    response=request('/api/v1/generation/text-to-video',payload); record['provider_response']=response; record['task_id']=response.get('task_id') or response.get('id')
    if not record['task_id']: record['state']='BLOCKED'; tx.write_text(json.dumps(record,ensure_ascii=False,indent=2)); raise RuntimeError(f'No task_id: {response}')
    record['state']='SUBMITTED_TASK_ID_BOUND'; tx.write_text(json.dumps(record,ensure_ascii=False,indent=2)); return record
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--dry-run',action='store_true'); ap.add_argument('--model',choices=['seedance-2.0-pro','MiniMax-H3']); args=ap.parse_args()
    global MODEL
    if args.model: MODEL=args.model
    results=[]
    for sid,prompt in SHOTS:
        print(f'{sid}: submit model={MODEL}',flush=True); rec=submit(sid,prompt,args.dry_run); results.append(rec)
        if args.dry_run: continue
        while True:
            q=query(rec['task_id']); status=str(q.get('status','')).lower(); print(f'{sid}: {status}',flush=True)
            u=result_url(q)
            if u:
                video=OUT/f'{sid}.mp4'; OUT.mkdir(exist_ok=True); video.write_bytes(requests.get(u,timeout=180).content); rec['output']=str(video); rec['state']='SUCCEEDED'; TX.joinpath(f'{sid}.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)); break
            if status in ('failed','error','cancelled','canceled'): rec['state']='FAILED_RECONCILED'; TX.joinpath(f'{sid}.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)); raise RuntimeError(f'{sid} failed: {q}')
            time.sleep(10)
    if not args.dry_run:
        concat=OUT/'concat.txt'; concat.write_text('\n'.join(f"file '{(OUT/sid+'.mp4').resolve()}'" for sid,_ in SHOTS))
        target=OUT/'storyclaw_60s_zh_16x9.mp4'; subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(concat),'-c','copy',str(target)],check=True); print(target)
    else: print('DRY_RUN_OK: five 12s shots, total 60s, 16:9')
if __name__=='__main__': main()
