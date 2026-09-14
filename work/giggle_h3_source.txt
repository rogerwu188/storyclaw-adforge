---
name: giggle-minimax-h3-gen
description: >
  Use when the user wants to generate AI video, optimize video prompts, or work with MiniMax-H3.
  Covers text-to-video, image-to-video, omni multi-modal via giggle.pro API with built-in prompt engineering.
  Triggers: generate video, AI video, minimax-h3, giggle, 视频提示词, image to video, text to video, omni, 多模态, 短剧, 广告视频, 首帧图, 角色参考.
license: MIT
metadata:
  {
    "openclaw": {
      "emoji": "🎬",
      "requires": {
        "bins": ["python3"],
        "env": ["GIGGLE_API_KEY"],
        "pip": ["requests"]
      },
      "primaryEnv": "GIGGLE_API_KEY",
      "installSpec": {
        "bins": ["python3"],
        "env": ["GIGGLE_API_KEY"],
        "pip": ["requests"]
      }
    }
  }
---

# Giggle · MiniMax-H3 视频生成与提示词（合并版）

**Source**: [giggle-official/skills](https://github.com/giggle-official/skills) · **API:** [giggle.pro](https://giggle.pro/) · **Script:** `scripts/generation_api.py`

本技能 = **Giggle API 成片**（`scripts/generation_api.py`）+ **MiniMax-H3 提示词工程资料库**（`references/`、`prompts/`）。

- **主流程**：优化提示词 → API Key → 用 `text` / `image` / `omni` 提交并轮询结果。
- **深度写法**：创意钩子、分镜模板、长视频流水线、词表与范例见资源索引。

## 仓库内资源索引

| 路径 | 用途 |
|------|------|
| [references/prompt-engineering.md](references/prompt-engineering.md) | **提示词工程规范**：10 大能力、4 种结构模板、交互流程、质量自检 |
| [references/creative-strategy.md](references/creative-strategy.md) | 写什么、≤15s 与长片创意策略 |
| [references/production-pipeline.md](references/production-pipeline.md) | 长视频前期流水线（角色→分镜→生成→拼接） |
| [references/long-video-strategy.md](references/long-video-strategy.md) | 分段、延长、衔接、锁定语句、输出模板 |
| [references/examples.md](references/examples.md) | 场景与多模态示例（10 大能力分类） |
| [references/vocabulary.md](references/vocabulary.md) | 运镜、画质、大气效果词库 |
| [references/image-generation.md](references/image-generation.md) | 角色参考图 / 首帧图前置生图规范 |
| [prompts/](prompts/) | 主题扩展包、OpenClaw 全案短文 |

---

## ⚠️ 平台与 API 约束（以 Giggle 为准）

资料库为通用 MiniMax-H3 提示词最佳实践；**视频与多模态成片仅通过 giggle.pro 提交**。实际调用本仓库脚本时遵守下表：

| 项目 | Giggle（本脚本） |
|------|------------------|
| 语言 | 与**用户输入语言一致**（见下节 Language Rule）；资料里中文模板可套用结构 |
| 时长 | **3–15** 秒整数，`--duration` |
| 画幅 / 清晰度 | `--aspect-ratio`、`--resolution` |
| omni 图片 | 最多 **9** 张，`url:` 或 `base64:` |
| 参考音 / 视频 | 仅 `url:`，`--audios`、`--videos` |
| 提示词里的 `@图片N` / `@视频N` | **仅编号习惯**；必须通过 CLI 传入**对应真实 URL**，且**全部**引用都要传 |

若资料写「混合素材 ≤12 个」与 Giggle 限制冲突，**取更严一侧**（尤其图片 ≤9）。

### `@引用` → Giggle CLI（omni）

| 提示词习惯 | 映射到 |
|------------|--------|
| `@图片1` … `@图片N` | `--images "url:..."`（按编号顺序，可多参数或多次 `--images`，脚本会合并） |
| `@视频1` … | `--videos "url:..."` |
| `@音频1` … | `--audios "url:..."` |

---

## ⚠️ Language Rule — MUST FOLLOW

**Match the user's input language exactly. Never translate. Never output a second language version.**

- User writes in Chinese → optimize in Chinese → pass Chinese prompt to API
- User writes in English → optimize in English → pass English prompt to API
- Output **ONE** version of the optimized prompt. No bilingual display. No "API submission version".

（资料库中大量中文范例：仅借鉴**结构与章法**，输出语言仍以上述规则为准。）

---

## Step 1: 提示词优化（必须完成后才能进入 Step 2）

用户输入往往描述不准确。**必须先走完以下完整优化流程，生成高质量 prompt，用户确认后再提交 API。**

完整规范见 [references/prompt-engineering.md](references/prompt-engineering.md)，以下为 SKILL.md 内联的执行摘要。

---

### MiniMax-H3 核心能力速查

| # | 能力 | 提示词核心模式 |
|---|------|---------------|
| 1 | **一致性控制** | `[角色]@图片N + [动作/剧情] + [场景]@图片N` |
| 2 | **运镜/动作复刻** | `参考@视频1的[运镜/动作/节奏] + [主体]@图片N` |
| 3 | **创意/特效复刻** | `参考@视频1的[特效/转场] + 将[元素]替换为@图片N` |
| 4 | **剧情补全** | `[分镜脚本] + [演绎方式] + [音效/台词]` |
| 5 | **视频延长** | `将@视频1延长Xs + [新增内容]` |
| 6 | **声音控制** | `[画面] + 音色参考@视频1 + "台词"` |
| 7 | **一镜到底** | `一镜到底 + @图片1@图片2... + 全程不切镜头` |
| 8 | **视频编辑** | `将@视频1中的[A]换成@图片1 + [修改说明]` |
| 9 | **音乐卡点** | `@图片1...@图片N + 参考@视频1的画面节奏/卡点` |
| 10 | **情绪演绎** | `[角色] + [情绪变化描述] + [运镜配合]` |

各能力详细示例见 [references/examples.md](references/examples.md)。

---

### Phase 0：判断内容类型（最关键的一步）

| 场景 | 路径 | 核心任务 |
|------|------|---------|
| ≤15秒 | 路径A | 帮用户找到一个**有传播力的单一视觉 hook**；参考 [creative-strategy.md](references/creative-strategy.md) 爆款模式库 |
| >15秒 | 路径B | 走完整前期流水线：角色设计 → 角色卡图提示词 → 分镜脚本 → 首帧图提示词 → 逐镜头视频提示词；参考 [production-pipeline.md](references/production-pipeline.md) |

### Phase 1：获取用户创意

用户描述想要生成的内容。

### Phase 2：确认关键参数（已明确可跳过）

1. **时长**：短片 3–8s / 中 9–12s / 长 13–15s / 超长 >15s
2. **比例**：横 16:9 / 竖 9:16 / 方 1:1
3. **素材**：纯文本 / 有图片 / 有图+视频 / 全模态
4. **补充偏好**（可选）：情绪氛围、镜头风格、用途场景

### Phase 3：生成优化提示词（≤15秒输出 2–3 个版本，>15秒按流水线输出）

**提示词结构速查：**

| 场景 | 推荐结构 |
|------|---------|
| ≤12秒 | `[风格总纲]，[主体]，[动作]，[环境/光影]，[运镜]，[音效]` |
| 13–15秒 | 时间戳分镜法（0-3s / 4-8s / 9-12s / 13-15s 逐段描述） |
| 短剧对白 | 画面 + 台词（角色/情绪标注）+ 音效分离 |
| 史诗大制作 | 品质锚定 + 大气连贯声明 + 逐段 + 光影三层 + 收束句 |

**运镜三级速查：**
- **基础动作**：Pan / Dolly / Zoom / Crane / Orbit / Tracking
- **修饰词**：Smooth / Slow / Fast / Cinematic / Dreamy / Handheld / Aerial
- **组合技**：一次最多 2–3 个，用 `+` 连接；"雾粒粘镜"等镜头质感词可大幅提升沉浸感

**图片风格匹配（生成角色参考图 / 首帧图时）：**

| 题材 | 推荐生图风格 |
|------|------------|
| 仙侠 / 修真 | 3D国漫渲染、中国仙侠概念设计 |
| 古风 / 历史 | 中国风工笔画、水墨画 |
| 赛博朋克 / 科幻 | 未来科幻写实CG、概念设计 |
| 现实 / 人物 | 电影摄影写实、人像摄影 |
| 美食 / 产品 | 美食广告摄影、商业摄影 |
| 动漫（日） | 赛璐璐风格 |
| 动漫（国） | 3D国漫渲染 |

角色参考图格式：`9:16竖版构图。[风格锚定]角色设定图，[构图视角]，角色居中。[面部7要素]。[发型]。[服装逐件+新旧状态]。[道具]。[体态气质]。[光影]。禁止：任何文字、字幕、LOGO、水印`

首帧图格式：`[画幅比]。[风格锚定]，[构图+角色位置]。[角色状态+关键辨识特征]。[环境细节]。[光影层次]。[色调氛围]。禁止：任何文字、字幕、LOGO、水印`

**@引用编号分配规则：**
1. **公共素材**（角色参考图等跨版本共用）从 `@图片1` 开始依次编号
2. **版本独立素材**（各版本首帧图、尾帧图）在公共素材编号之后递增
3. 每个素材标注用途，写清楚是"参考"（借鉴风格/动作）还是"编辑"（在原素材上修改）

**多模态组合技巧：**
- 有首帧图 + 想参考视频动作 → `@图片1为首帧，参考@视频1的打斗动作`
- 融合多个视频 → `在@视频1和@视频2之间加一个场景，内容为xxx`
- 没有音频素材 → 直接参考视频里的声音，无需单独上传音频
- 连续动作 → `角色从跳跃直接过渡到翻滚，保持动作连贯流畅`
- 多素材时务必检查各 @对象有没有标清楚，别把图、视频、角色搞混

**≤15秒输出格式（完整模式）：**

```
## 视频提示词

**主题**：[一句话概括]
**时长**：[X秒]  |  **比例**：[16:9 / 9:16 / 1:1]

### 公共参考素材（如有）
- @图片1：[用途说明 + 图片生成提示词]

---

### 版本一：[版本标题]
#### 提示词
[完整提示词]
#### 参考素材
- 首帧 @图片N：[描述 + 图片生成提示词]

---

### 版本二：[版本标题]
[同上结构]

---

### 提示词解析
[各版本设计意图差异]
```

>15秒输出格式见 [references/long-video-strategy.md](references/long-video-strategy.md)（含全局锁定语句、统一负面提示词、分段模板）。

**深度资源索引：**

| 需求 | 参考文件 |
|------|---------|
| 爆款概念、前 2 秒钩子 | [creative-strategy.md](references/creative-strategy.md) |
| 长片分段、衔接、流水线 | [production-pipeline.md](references/production-pipeline.md)、[long-video-strategy.md](references/long-video-strategy.md) |
| 运镜词汇、画质锚定词 | [vocabulary.md](references/vocabulary.md) |
| 多模态场景样板 | [examples.md](references/examples.md) |
| 角色参考图 / 首帧图规范 | [image-generation.md](references/image-generation.md) |
| 主题扩展包、短剧全案 | [prompts/](prompts/) |

### Phase 4：用户确认

用户选定版本（可要求调整：风格/色调/运镜/台词/时长），确认最终版本后进入 Step 2。

---

### Giggle 覆盖规则（优先于 prompt-engineering.md）

1. **语言**：严格遵守 Language Rule。用户中文 → 中文 prompt；用户英文 → 英文 prompt。"Output ONE version" 指禁止双语对照输出，不限制版本数量。
2. **平台**：references 中的通用提示词方法，以本文件 MiniMax-H3 的 Giggle 约束（时长 3–15s、图片 ≤9 张、@引用命名等）为准。
3. **多模态引用**：若用户提供了多张图片/视频/音频，优化提示词时须逐条说明各参考用途，Step 3 提交时必须全部传入 CLI，不能只取第一条。

---

### Step 1 交付物

- 用户已选定的**一条**优化 prompt（与用户语言一致，已通过质量自检）
- Omni：提示词中每条参考均有对应 URL，编号映射（`@图片N` 等）已完成
- 超长视频：已按 [long-video-strategy.md](references/long-video-strategy.md) 确定分段数量和衔接点

---

## Step 2: API Key Setup (One-Time)

```bash
python3 scripts/generation_api.py --check-key
```

**已配置**则进入 Step 3；**未配置**则向用户索要 Key 后执行：

```bash
python3 scripts/generation_api.py --setup --api-key <key>
```

---

## Step 3: Generate Video

**Text-to-Video:**
```bash
python3 scripts/generation_api.py \
  --mode text --prompt "<optimized_prompt>" \
  --model MiniMax-H3 --duration 4 --aspect-ratio 16:9 --resolution 480p
```

**Image-to-Video:**
```bash
python3 scripts/generation_api.py \
  --mode image --prompt "<optimized_prompt>" \
  --start-frame "url:<URL>" --model MiniMax-H3 --duration 4
```

**Omni:**

- **多参考资源：** 从对话中 **收集用户给出的全部** 参考图 / 参考视频 / 参考音频 URL（含 `url:` 前缀），再一次性调用 CLI。同一选项后可跟 **多个** 空格分隔的参数（如 `--images "url:a" "url:b"`）；也可 **多次** 写同一选项（如两行 `--images`），脚本会合并为完整列表。禁止只取第一个链接就提交。
- **数量：** 图片总计最多 9 张（接口校验）；音视频按对话实际条数全部传入。

```bash
# 示例：多图 + 多音频 + 多参考视频（按实际数量增删参数）
python3 scripts/generation_api.py \
  --mode omni --prompt "<optimized_prompt>" \
  --images "url:<img1>" "url:<img2>" \
  --audios "url:<audio1>" "url:<audio2>" \
  --videos "url:<ref_video1>" "url:<ref_video2>" \
  --model MiniMax-H3 --duration 4
```

若某类参考未提供，可省略对应选项（但至少保留 `--images`、`--audios`、`--videos` 之一）。

**提交后：** 脚本默认每约 10 秒轮询一次（最长约 10 分钟）；任务完成后**主动**将结果（含链接）推送给用户，无需等用户追问。

---

## Parameters

| Parameter | Default | Options |
|-----------|---------|---------|
| `--mode` | required | `text` / `image` / `omni` |
| `--prompt` | required | Max 10,000 chars — use user's input language |
| `--model` | `MiniMax-H3` | `MiniMax-H3` |
| `--duration` | `4` | `3` / `4` / `5` / `6` / `7` / `8` / `9` / `10` / `11` / `12` / `13` / `14` / `15` seconds |
| `--aspect-ratio` | `16:9` | `1:1` / `9:16` / `16:9` / `4:3` / `3:4` |
| `--resolution` | `480p` | `480p` / `768p` |
| `--generating-count` | `1` | 1–4 |
| `--images` | — | **omni**：`url:` 或 `base64:`，可重复多个；最多 9 张 |
| `--audios` | — | **omni**：仅 `url:`，可重复多个 |
| `--videos` | — | **omni**：参考视频，仅 `url:`，可重复多个 |

---

## 质量自检（提交前）

### 提示词质量（Phase 3 生成后检查）

- [ ] @引用编号与素材清单一一对应，公共素材优先编号
- [ ] 总文件数 ≤ 12（图片+视频+音频合计）；omni 图片 ≤ 9
- [ ] 未包含写实真人面部素材
- [ ] 13–15秒视频已使用时间戳分镜，覆盖完整时长无遗漏
- [ ] 台词已用引号包裹并标注角色和情绪
- [ ] 音效描述与画面描述分开写
- [ ] 超长视频每段均含风格锁定、角色锁定、场景锁定语句
- [ ] 超长视频延长段开头已安排桥接镜头或尾帧延续微动
- [ ] 统一负面提示词已覆盖风格漂移、角色变脸、偏色、光线突变、水印
- [ ] 角色参考图画幅比为 9:16 竖版；首帧图画幅比与视频一致

### API 提交（Step 3 执行前检查）

- [ ] 提示词语言与用户输入语言一致；无双语对照
- [ ] `duration ∈ [3,15]`（整数）
- [ ] omni：每条音频 / 视频以 `url:` 开头，base64 仅限图片
- [ ] 用户提供的参考 URL **全部**出现在 CLI 中，无遗漏
- [ ] 超长叙事已按 [long-video-strategy.md](references/long-video-strategy.md) 拆段，未假定单次超出 15s

---

## 常见错误排查

| 错误 / 现象 | 原因 | 解决方法 |
|------------|------|---------|
| `401 Unauthorized` | API Key 无效或已过期 | 重新执行 `--setup --api-key <新key>` |
| `422 images 超限` | omni 模式图片总数超过 9 张 | 减少 `--images` 数量至 ≤9 |
| `duration 不合法` | 传入了非 3–15 的整数（如 2、16、5.5） | 确认 `--duration` 为 3–15 整数 |
| 音频 / 视频参数报错 | `--audios` / `--videos` 传入了 `base64:` 前缀 | 音视频仅接受 `url:` 前缀，图片才可用 base64 |
| 轮询超时（>10 分钟） | 平台队列繁忙或网络异常 | 等待后重新提交；检查网络连通性 |
| Key 文件找不到 | 首次使用未配置 | 先执行 Step 2 配置流程 |
| 生成结果与提示词差异大 | 提示词过长或信息过载 | 精简提示词至核心要素；参考 references/examples.md |
