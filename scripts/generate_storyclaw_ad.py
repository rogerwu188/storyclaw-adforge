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
('01_hook',PRODUCT+' 黑屏中一粒温暖的金色“想法光点”从一张空白画布里诞生，像一颗刚被想出的星星，突然穿过屏幕冲入现实城市；前三秒必须让观众想知道它要去哪里。镜头从微观光点一镜加速到宏观城市，诗意、克制、电影级，设备只在最后一瞬以真实外形闪现，不生成文字。'),
('02_problem',PRODUCT+' 那粒金色想法光点穿过深夜创作者的桌面、设计草图和实验室玻璃，周围是彼此断开的灰色光线和等待中的请求；不要拍焦虑的人脸，不要做普通“多个屏幕”广告，用一条光点的孤独旅程表达好想法找不到承载路径，16:9，无可读伪文字。'),
('03_solution',PRODUCT+' 想法光点抵达真实 StoryClaw ClawBot，设备顶部白色标识和前面板接口保持一致；接触瞬间，光点没有爆炸而是安静地分裂成几条蓝绿色路径，穿过一张由城市灯光组成的全球网络。视觉隐喻“一个节点让想法找到路径”，优雅、惊喜、无虚构规格。'),
('04_proof',PRODUCT+' 连续镜头：金色想法光点沿蓝绿色路径经过多个抽象节点，最后回到一张完成的创意画布；真实 ClawBot 保持清晰，前面板接口不变，网络连接有方向、有回执般的柔和脉冲，证明“请求被承载和连接”，不出现收益、速度或虚构数字。'),
('05_cta',PRODUCT+' 真实产品英雄镜头不是孤立摆拍：一条金色光线从设备延伸到画面外的城市天际线，设备保持准确比例、Logo方向和接口；留出干净左侧空间给后期 CTA。高级品牌电影，情绪收束，字幕后期添加“每个想法，都有一条回家的路。”和“StoryClaw｜连接每一个想实现的想法”，画面不生成任何文字。'),
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
    ap=argparse.ArgumentParser(description='AdForge onboarding + Giggle 广告生成器'); ap.add_argument('--idea',help='用户创意；必须先提供并固化后才会生成镜头'); ap.add_argument('--reference',help='产品参考图 PNG/JPG'); ap.add_argument('--run-id',default='storyclaw_v1'); ap.add_argument('--dry-run',action='store_true'); ap.add_argument('--model',choices=['seedance-2.0-pro','MiniMax-H3']); args=ap.parse_args()
    global MODEL, RUN_ID, REFERENCE
    if args.model: MODEL=args.model
    RUN_ID=args.run_id; REFERENCE=args.reference
    if not args.idea:
        if not sys.stdin.isatty():
            ap.error('--idea 必填。示例：--idea "让产品连接全球 AI 推理需求"')
        print('\nAdForge 首次使用向导')
        print('1) 先输入你的广告创意；不要只输入产品名。')
        print('2) 准备产品参考图，保持产品外观一致。')
        print('3) 生成前会写入创意 brief，并按镜头逐个提交 Giggle。')
        args.idea=input('\n请输入广告创意：').strip()
        if not args.idea: ap.error('创意不能为空')
    if not REFERENCE and sys.stdin.isatty():
        value=input('产品参考图路径（可回车跳过，跳过则使用纯文本生成）：').strip()
        REFERENCE=value or None
    if not KEY and not args.dry_run:
        print('未检测到 GIGGLE_API_KEY。请复制 .env.example 为 .env 并填写 Key，再重新运行。')
        raise SystemExit(2)
    results=[]
    creative = f"用户创意：{args.idea}。严格围绕这个创意，不添加未经证实的产品功能，不生成字幕或Logo。"
    creative_id=f"storyclaw-BR-every-idea-home-v01-zh-r1"
    (DATA/'creative_brief.json').write_text(json.dumps({'creative_id':creative_id,'creative_idea':args.idea,'product':'StoryClaw ClawBot','mode':'BR','lang':'zh','hook':'一粒想法光点在前三秒离开空白画布，寻找承载它的路径','proof':['实体 ClawBot 节点承载网络连接','请求沿节点路径获得回执式脉冲'],'cta':'每个想法，都有一条回家的路。StoryClaw｜连接每一个想实现的想法','aspect_ratio':'16:9','duration_seconds':'script_derived','status':'CREATIVE_LOCKED'},ensure_ascii=False,indent=2))
    if REFERENCE and Path(REFERENCE).is_file():
        import hashlib as _hashlib
        ref_sha=_hashlib.sha256(Path(REFERENCE).read_bytes()).hexdigest()
        (DATA/'product_kit.json').write_text(json.dumps({'product_id':'storyclaw-clawbot','canonical_images':[{'path':REFERENCE,'view':'45deg','sha256':ref_sha}], 'identity_contract':{'logo':'white StoryClaw mark, never mirrored','ports':'USB-C, USB-A, audio and power layout from canonical image','power_button':'red illuminated square power button','body_ratio':'black compact rectangular mini-PC'},'verified_selling_points':['physical node supports exchange network records and accountable node identity'],'unverified_claims':['fixed income','speed SLA','real-time online count']},ensure_ascii=False,indent=2))
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
