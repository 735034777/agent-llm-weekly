<p align="center"><img src="assets/banner.svg" alt="Agent & LLM Weekly · 每周读懂值得跟踪的技术变化" width="900"></p>

# Agent & LLM 前沿周报

面向研究者与开发者的中文技术周报。优先跟踪高 star、仍活跃的 Agent／LLM 项目，再精选相关研究与评测。每条说明**更新了什么、为什么值得看、证据有什么限制**，附原始出处和有查询日期的 star 数。

[阅读最新一期](#最新一期) · [高 star 项目池](PROJECTS.md) · [全部期刊](ARCHIVE.md) · [信息源](SOURCES.md) · [编辑准则](docs/EDITORIAL.md) · [RSS](https://raw.githubusercontent.com/735034777/agent-llm-weekly/main/feed.xml)

## 最新一期

<!-- LATEST:START -->
### [第 001 期｜高 star Agent：从插件架构到工作流追踪](content/001.md)

覆盖 2026-11-02 — 2026-11-08 · 发布 2026-11-12 · 8 条本周更新

修订后的创刊号以 4 个高 star 项目的实质更新开篇，再看记忆、训练与评测。共 8 条本周更新和 2 个长期参考，覆盖 2026-11-02—11-08。项目 star 是 11 月 12 日查询快照，不是覆盖周末的历史数值。

<!-- LATEST:END -->

## 每期有什么

| 栏目 | 内容 |
| --- | --- |
| 本周值得先看 | 从本期入选内容中挑出最值得花时间的一项 |
| 高 star 项目更新 | 优先选择 5 万 star 以上项目，说明其用途与本周实质变化 |
| 模型与研究 | 精选训练、推理、强化学习与 Agent 学习方法 |
| Agent 工程 | 工具、上下文、记忆、长任务与执行系统 |
| 评测与观察 | 测了什么、在什么条件下成立、还不能说明什么 |
| 长期参考 | 与本周主题相关的旧文，明确标记，不冒充新闻 |
| 本周动手 | 一个可小规模验证的实践建议 |

栏目按实际内容出现，不为凑数填充。目标每期精选 6—10 条，以 4—6 个高 star 项目为主体，研究论文通常 1—2 篇。项目通常不低于 3 万 star，优先 5 万以上；有足够候选时至少 70% 的项目条目来自 5 万以上仓库。高 star 但当周只有琐碎改动的项目可以不入选。

## 更新与订阅

- 计划每周一 **09:00（Asia/Shanghai）** 更新，覆盖上一周一至周日。
- 首期于 2026-11-12 创刊发布，回顾 2026-11-02—11-08；下一期覆盖 11-09—11-15。
- 可在 GitHub 的 **Watch → Custom → Releases** 中订阅每期发布，或将上面的 RSS 链接加入阅读器。
- 内容收集、核实和编写由本机 Codex 定时任务执行；GitHub Actions 负责校验。定时执行依赖本机 Codex 可运行、网络可用及 GitHub 登录有效，不能视为独立云服务。延迟执行时按周补齐，不把多周内容混成一周。

## 如何判断一条消息

优先使用原始论文、实验室文章、官方仓库和评测说明。社区推荐用于发现线索。论文结果明确归属于作者报告；“已核查原文”不代表独立复现。预印本、未验证的开源完整性和实际使用限制会在条目中说明。

每期区分事件日期、覆盖区间和周报发布日期。旧文进入“长期参考”；无法访问的来源记入核查范围，不写成“没有更新”。日期按原始来源展示，周报排期使用北京时间。

## 维护

Python 3.11+，只用标准库，不需要额外 API key。

```bash
python3 scripts/build.py --next-period
python3 scripts/build.py --write
python3 scripts/build.py --check
python3 -m unittest discover -s tests -v
```

新增一期的正文输入是 `data/issues/NNN.json`，项目池及 star 快照维护在 `data/sources.json`。构建器生成 `content/NNN.md`、首页最新一期、归档、信息源目录、高 star 项目池与 RSS。研究和发布步骤见 [周报维护流程](docs/WORKFLOW.md)。

发现错误或推荐项目，欢迎通过 [Issue](https://github.com/735034777/agent-llm-weekly/issues/new/choose) 提交原始链接和说明。已发布内容的实质更正在该期更正记录中留痕。

## 关于

形式参考 [HelloGitHub 第 127 期](https://hellogithub.com/periodical/volume/127) 的分类精选、简短介绍和往期归档，未复制其项目文案或图片。本项目与 HelloGitHub 无关联。

摘要与点评由 AI 辅助编写，保留可追溯来源；仓库维护者为 [735034777](https://github.com/735034777)。第三方论文、代码和图片的权利及许可证归原作者。
