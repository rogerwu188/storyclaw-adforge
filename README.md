# StoryClaw AdForge

专业级广告营销视频生产线。输入产品创意，生成营销 brief、中文广告文案、分镜合同，并通过 Giggle API（Seedance 2.0 Pro 或 MiniMax-H3）生成镜头，使用 FFmpeg 拼接为平台成片。

## 特性

- FastAPI 项目与异步 Worker 的可移植骨架
- JSON Schema 固化项目、分镜、素材、事务与 QA 合同
- Giggle API client：text/image/omni video，持久化 task_id 与响应回执
- 1 分钟广告拆为不超过 15 秒镜头，支持 16:9/9:16/1:1
- FFmpeg 拼接、字幕/尾卡与输出规格检查
- 经验库以 JSONL 保存失败记忆和有效提示词，禁止把密钥和生产媒体提交到 GitHub
- Docker Compose：API、Worker、Redis、PostgreSQL、MinIO

## 快速开始

```bash
cp .env.example .env
# 编辑 .env，设置 GIGGLE_API_KEY
docker compose up --build
curl http://localhost:8000/healthz
python scripts/generate_storyclaw_ad.py --dry-run --idea "让我的产品解决一个明确的用户问题"
```

## 新用户向导

不要直接把产品名当作创意。先写清楚“给谁看、解决什么问题、希望观众做什么”。例如：

```text
让一台 StoryClaw 设备把闲置算力接入全球 AI 推理网络，让每一次推理请求都找到合适的节点。
```

首次运行可以省略 `--idea`，终端会进入交互式向导，解释创意、参考图和 API Key 的准备方式：

```bash
python scripts/generate_storyclaw_ad.py --reference data/reference/product.png
```

无交互终端（CI、服务器、Docker worker）必须显式传入 `--idea`；缺少时程序会返回可复制的示例命令，不会静默生成内容。

完整新用户流程：

1. `cp .env.example .env`，在本地 `.env` 中填写自己的 `GIGGLE_API_KEY`。
2. 准备产品参考图、Logo、品牌颜色和不能出现的承诺。
3. 用 `--idea` 提交用户创意；程序会保存 `data/creative_brief.json`。
4. 选择 `seedance-2.0-pro` 或 `MiniMax-H3`，生成不超过 15 秒的分镜。
5. 用后期脚本混入旁白和音乐，再运行媒体验收。

付费生成前请先使用 `--dry-run` 检查创意和参数。每个任务会在 `data/transactions/` 写入事务记录，失败或超时不能盲目重复提交。

真实生成：

```bash
python scripts/generate_storyclaw_ad.py --model seedance-2.0-pro
```

世界级成片需要显式创意输入和产品参考图：

```bash
python scripts/generate_storyclaw_ad.py --idea "用户的广告创意" --reference data/reference/product.png --run-id campaign_v1
python scripts/postprocess_worldclass.py --video outputs/campaign_v1_storyclaw_60s_zh_16x9.mp4 --voice data/audio/narration.mp3 --music data/audio/music.mp3 --out outputs/final.mp4
python packages/post/verify_media.py outputs/final.mp4
```

脚本默认只会提交 Giggle 任务，不会自动发布到任何广告平台。每次付费 POST 前会写入 `data/transactions/`；任务失败后必须先对账，不能盲目重提。

## 目录

`apps/api` 为 HTTP API，`apps/worker` 为异步任务入口，`packages/giggle` 为服务适配器，`packages/contracts` 为 Schema，`packages/post` 为 FFmpeg 后期，`knowledge` 为经验库，`examples` 为合成样例。

## 开源边界

只提交代码、Schema、文档和合成样例。`.env`、Giggle key、客户素材、签名 URL、真实 task_id、账单和成片均留在本地/私有对象存储。
