# 一句话开始

把仓库交给 Codex 或 Claude Code，然后只发送一句话：

```text
为「结合附上的 StoryClaw 产品图和白皮书，向开发者介绍全球 AI 推理交易网络」制作一条 60 秒中文 16:9 世界级广告片。请自动完成创意策略、文案、分镜、Giggle 生成、旁白、音乐、剪辑、字幕和 QA，最后返回可播放文件。
```

换产品时替换产品目标，并附上资料、图片或网址；不必先想好创意。Agent 会先读取仓库根目录的 `AGENTS.md`，再执行完整生产线。

首次部署仍需一次性完成：

```bash
cp .env.example .env
# 在 .env 填写 GIGGLE_API_KEY
mkdir -p data/reference
```

如果没有产品图片，Agent 会先生成产品资产计划并提示素材风险；如果没有有效 Giggle Key，它会完成文案/分镜预生产，但不会进行付费提交。
