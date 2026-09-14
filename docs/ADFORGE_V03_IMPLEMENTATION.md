# AdForge v0.3 实现状态

附件方案已落成“一核三模式”合同：`EC` 电商出海、`BR` 品牌广告、`DH` 数字人口播。三模式共用创意血缘、BrandKit/ProductKit、Giggle 适配器、事务账本、本地化、后期和检测器；通过 profile 配置不同硬门。

当前 StoryClaw 重制使用 `BR`。原因是它要求 16:9 母版、canonical 产品图、品牌连续性、人工审片和 9:16/1:1 派生。DH 的口型 provider 尚未接入，项目将它标记为能力缺口，不把画外旁白冒充数字人交付。

## v0.3 相对旧版的硬改变

- ProductKit canonical 图是 BR 产品特写的强制输入，禁止纯文本重新想象产品。
- Creative 先锁定 Hook、Proof、CTA，再由脚本反推时长；不再先做 60 秒空镜。
- creative_id 包含 project、mode、scene、variant、lang、revision，任务和输出可追溯。
- Logo、端口、电源键、比例、颜色和环境逻辑进入 BR 硬门。
- TTS 前固定品牌读音，旁白逐字稿、ASR 和字幕必须一致。
- v0.2 样片作为 BR 负样本回归，允许验证检测器能抓到镜像 Logo、端口漂移、伪丝印、尾部无信息和 CTA 缺失。

## 仍需真实接入的能力

EC 商品页抓取、DH 授权账本与 lip-sync provider 仍是下一阶段，当前只提供合同和 profile，不声称已经完成生产能力。
