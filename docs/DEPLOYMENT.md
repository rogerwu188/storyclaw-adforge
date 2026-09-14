# 异地部署与生产检查

## 本地/服务器

1. 安装 Docker 24+ 和 Compose v2，克隆仓库。
2. `cp .env.example .env`，只在服务器本地填入有效的 `GIGGLE_API_KEY`。
3. `docker compose up --build -d`。
4. 运行 `curl http://localhost:8000/healthz`；返回 `{"status":"ok"}` 后再做低成本 dry-run/单镜测试。
5. 将 `data/` 与 `outputs/` 放在受限磁盘或私有对象存储，定期备份 `data/transactions/`。

## 生产前检查

- `python scripts/generate_storyclaw_ad.py --dry-run`
- `python -m compileall -q apps packages scripts`
- 所有 Schema 可由 `json.loads` 读取
- Giggle Key 用一次 `GET/POST` 低成本验证，403 时停止，不重试
- 每次请求必须先写 PREPARED 事务；收到 task_id 后写 SUBMITTED_TASK_ID_BOUND
- Provider 失败必须对账、记录响应 SHA、标记 BLOCKED；禁止盲目重新付费
- 成片用 ffprobe 检查时长、画幅、编码和可解码性，再人工观看

## 数据边界

`.env`、客户图片/视频、签名 URL、真实 task_id、账单和成片不得提交公开仓库。GitHub 仓库只保存代码、Schema、合成样例、经验卡和本部署文档。
