#!/usr/bin/env python3
"""Generate a 60s Chinese 16:9 StoryClaw ad as five Giggle shots and stitch with FFmpeg."""
from __future__ import annotations
import argparse, base64, hashlib, json, os, subprocess, sys, time, uuid
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; TX=DATA/'transactions'; OUT=ROOT/'outputs'
BASE=os.getenv('GIGGLE_API_BASE','https://giggle.pro').rstrip('/'); KEY=os.getenv('GIGGLE_API_KEY')
MODEL=os.getenv('VIDEO_MODEL','seedance-2.0-pro')
RUN_ID='storyclaw_v1'
REFERENCE=None
PRODUCT='真实 StoryClaw ClawBot：黑色小型计算节点，顶部白色 StoryClaw 标识，前面有 USB、音频和电源接口。保持外形、标识和接口一致。'
SHOTS=[
('01_hook',PRODUCT+' 深色数据中心桌面，设备从静止到启动，冷白光沿边缘亮起，抽象 AI 请求光点汇聚到设备；商业广告微距推进，前三秒表达“实体节点成为全球推理入口”，无字幕无额外Logo，16:9。'),
('02_problem',PRODUCT+' 安静工作台与远方城市的抽象请求光点，镜头从拥堵的混乱光线移动到设备，表达推理需求等待和算力分散，不出现可读屏幕文字、价格或收益承诺，电影级低调照明，16:9。'),
('03_solution',PRODUCT+' 镜头环绕设备，蓝绿色数据光线连接到多个远方城市节点，形成稳定的全球 AI 推理交换网络；表达物理节点、请求匹配和可追踪连接，不添加未经证实的规格，品牌级科技广告，16:9。'),
('04_proof',PRODUCT+' 近景，前面板接口清晰可见；一条 AI 推理请求光束进入，另一条光束离开连接远方节点，设备稳定运行，连续镜头表达节点在线、请求匹配、回执可追踪，不显示具体数字或伪文字，16:9。'),
('05_cta',PRODUCT+' 产品英雄镜头，深色渐变背景，蓝绿色轮廓光，镜头缓慢环绕后定格，左侧留出后期中文文案安全区，高级全球基础设施广告质感，不生成字幕、价格或额外Logo，16:9。'),
]
def headers(): return {'x-auth': KEY, 'Content-Type':'application/json'}
def sha(s): return hashlib.sha256(s.encode()).hexdigest()
def request(path,payload):
    r=requests.post(BASE+path,headers=headers(),json=payload,timeout=90); r.raise_for_status(); return r.json()
def query(task_id):
    r=requests.get(BASE+'/api/v1/generation/task/query',headers=headers(),params={'task_id':task_id},timeout=60); r.raise_for_status(); return r.json()
def result_url(p):
    for k in ('video_url','url','output_url','result_url','download_url','signed_url'):
        if isinstance(p.get(k),str) and p[k].startswith('http'): return p[k]
    for k in ('videos','results','data','asset_info'):
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
    tx=TX/f'{RUN_ID}_{shot_id}.json'; TX.mkdir(parents=True,exist_ok=True)
    if tx.exists():
        old=json.loads(tx.read_text());
        if old.get('task_id') and old.get('state') not in ('FAILED_RECONCILED','BLOCKED'): return old
    record={'transaction_id':uuid.uuid4().hex,'shot_id':shot_id,'prompt_sha256':sha(prompt),'state':'PREPARED','model':MODEL}
    if dry: tx.write_text(json.dumps(record,ensure_ascii=False,indent=2)); return record
    if not KEY: raise RuntimeError('GIGGLE_API_KEY is not set')
    payload={'prompt':prompt,'model':MODEL,'duration':12,'aspect_ratio':'16:9','resolution':'720p','generate_count':1}
    endpoint='/api/v1/generation/text-to-video'
    if REFERENCE and Path(REFERENCE).is_file():
        payload['start_frame']={'base64':base64.b64encode(Path(REFERENCE).read_bytes()).decode()}
        endpoint='/api/v1/generation/image-to-video'
    response=request(endpoint,payload); record['provider_response']=response
    nested=response.get('data') if isinstance(response.get('data'),dict) else {}
    record['task_id']=response.get('task_id') or response.get('id') or nested.get('task_id') or nested.get('id')
    if not record['task_id']: record['state']='BLOCKED'; tx.write_text(json.dumps(record,ensure_ascii=False,indent=2)); raise RuntimeError(f'No task_id: {response}')
    record['state']='SUBMITTED_TASK_ID_BOUND'; tx.write_text(json.dumps(record,ensure_ascii=False,indent=2)); return record
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--idea',required=True,help='用户创意；必须先提供并固化后才会生成镜头'); ap.add_argument('--reference'); ap.add_argument('--run-id',default='storyclaw_v1'); ap.add_argument('--dry-run',action='store_true'); ap.add_argument('--model',choices=['seedance-2.0-pro','MiniMax-H3']); args=ap.parse_args()
    global MODEL, RUN_ID, REFERENCE
    if args.model: MODEL=args.model
    RUN_ID=args.run_id; REFERENCE=args.reference
    results=[]
    creative = f"用户创意：{args.idea}。严格围绕这个创意，不添加未经证实的产品功能，不生成字幕或Logo。"
    (DATA/'creative_brief.json').write_text(json.dumps({'creative_idea':args.idea,'product':'StoryClaw设备','language':'中文','aspect_ratio':'16:9','duration_seconds':60,'status':'CREATIVE_LOCKED'},ensure_ascii=False,indent=2))
    for sid,prompt in SHOTS:
        prompt = creative + prompt
        print(f'{sid}: submit model={MODEL}',flush=True); rec=submit(sid,prompt,args.dry_run); results.append(rec)
        if args.dry_run: continue
        while True:
            q=query(rec['task_id']); qdata=q.get('data') if isinstance(q.get('data'),dict) else q; status=str(qdata.get('status','')).lower(); print(f'{sid}: {status}',flush=True)
            u=result_url(q)
            if u:
                video=OUT/f'{RUN_ID}_{sid}.mp4'; OUT.mkdir(exist_ok=True); video.write_bytes(requests.get(u,timeout=180).content); rec['output']=str(video); rec['state']='SUCCEEDED'; TX.joinpath(f'{RUN_ID}_{sid}.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)); break
            if status in ('failed','error','cancelled','canceled'): rec['state']='FAILED_RECONCILED'; TX.joinpath(f'{sid}.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)); raise RuntimeError(f'{sid} failed: {q}')
            time.sleep(10)
    if not args.dry_run:
        concat=OUT/f'{RUN_ID}_concat.txt'; concat.write_text('\n'.join(f"file '{(OUT/(RUN_ID+'_'+sid+'.mp4')).resolve()}'" for sid,_ in SHOTS))
        target=OUT/f'{RUN_ID}_storyclaw_60s_zh_16x9.mp4'; subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(concat),'-c','copy',str(target)],check=True); print(target)
    else: print('DRY_RUN_OK: five 12s shots, total 60s, 16:9')
if __name__=='__main__': main()
