# AdForge Agent Contract

当用户用一句话提出广告需求时，自动执行以下流程，不要求用户了解目录或命令：

1. 先做素材摄入：接受用户一句话创意，以及文档、图片、电商网址、品牌手册、参考广告和其它用户认为有价值的素材；写入 `data/intake/manifest.json`，为每个源记录 SHA、来源、用途和事实等级。再把用户原话保存为 `data/creative_brief.json` 的 `creative_idea`，提取产品、受众、问题、单一卖点、证明方式和 CTA。
2. 检查 `.env` 是否有 `GIGGLE_API_KEY`；没有时说明配置方法并停止付费调用。
3. 检查 `data/reference/`、用户附件、URL 和项目资料库；优先使用真实产品图、品牌手册和已批准文案。找不到时先生成待确认的资产计划，不能把虚构规格当事实。
4. 生成中文/用户原语言的营销 brief、旁白、字幕、逐镜头脚本和平台规格。超过 15 秒必须拆为多个镜头。
5. 先运行 dry-run 和 Schema/品牌/成本门；通过后才提交 Giggle。视频默认使用 `seedance-2.0-pro`，需要 H3 时必须明确记录模型。
6. 每次提交前写 durable transaction；保存 task_id、prompt SHA、参考图 SHA、provider response 和 pay/refund/net。超时或 403 时停止，禁止盲目重提。
7. 生成完成后用 FFmpeg 混音、剪辑、字幕和平台派生，再运行 `packages/post/verify_media.py`，抽帧检查产品外观、Logo、文字、黑帧、闪帧、音画和时长。
8. 把最终文件放入 `outputs/`，向用户返回文件链接、模型、镜头数、时长、QA 结果和任何待确认项；不要自动发布外部平台。

## 一句话入口

用户可以直接说：

> 为「让一台 StoryClaw 设备把闲置算力接入全球 AI 推理网络」制作一条 60 秒中文 16:9 世界级广告片。

Agent 应自动把这句话作为创意输入，并调用：

```bash
python scripts/generate_storyclaw_ad.py --idea "<用户原话>" --reference <产品图> --run-id <campaign-id>
```

不要把没有创意的“帮我做广告”当成可执行 brief；这种情况先追问产品、受众和期望行动。不要把 API Key、签名 URL、客户素材或生产媒体写进 Git 提交。
