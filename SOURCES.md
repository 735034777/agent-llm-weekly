# 信息源目录

[首页](README.md) · [项目索引](PROJECTS.md) · [编辑准则](docs/EDITORIAL.md)

优先级 1 为常规选题入口，2 为补充线索。每期按实际访问记录核查范围；列入目录不代表每周全部读完。聚合、社区和人物账号提供线索，入刊事实须追溯原始材料或可靠报道。

## 论文与研究：实验室

| 来源 | 优先级 | 检查方式 |
| --- | --- | --- |
| [Anthropic Engineering](https://www.anthropic.com/engineering) | 1 | 检查本周新文章；读取方法、案例和局限。 |
| [OpenAI Research](https://openai.com/research/) | 1 | 从研究索引进入技术报告、评测及系统卡。 |
| [Google DeepMind](https://deepmind.google/blog/) | 1 | 查本周模型、推理、多模态与 Agent 原始发布。 |
| [DeepSeek](https://github.com/deepseek-ai) | 1 | 查官方新仓库、论文与有实质内容的变更。 |
| [Qwen](https://github.com/QwenLM) | 1 | 查模型与 Agent 项目，返回论文及模型卡核实。 |
| [Google Research](https://research.google/blog/) | 1 | 检查研究博客与论文；研究方法进研究栏，产品与应用事件可进新闻，避免重复。 |
| [Meta AI Research](https://ai.meta.com/research/) | 2 | 追溯论文、模型卡和技术报告。 |
| [Microsoft Research](https://www.microsoft.com/en-us/research/blog/) | 2 | 从作者介绍回到论文与正式发表信息。 |
| [NVIDIA Research](https://research.nvidia.com/) | 2 | 涵盖机器人、视觉、多模态与训练推理，按论文范围选稿。 |

## 论文与研究：发现与录用核实

| 来源 | 优先级 | 检查方式 |
| --- | --- | --- |
| [Hugging Face Daily Papers](https://huggingface.co/papers) | 1 | 按对应 ISO 周浏览，热度只作线索；回原论文核查首次发布日期。 |
| [arXiv cs.AI / cs.CL / cs.LG](https://arxiv.org/list/cs.AI/recent) | 1 | 检索 agentic RL、tool use、memory、reasoning、evaluation；必要时扩展 cs.CL/cs.LG。 |
| [OpenReview](https://openreview.net/) | 2 | 对入选论文检查公开审稿与作者回应，保留预印本和录用状态区别。 |

## 补充项目观察

| 来源 | 优先级 | 检查方式 |
| --- | --- | --- |
| [OpenHands Releases](https://github.com/OpenHands/OpenHands/releases) | 2 | 按 published_at 筛选本周版本，读关联 PR，不跟踪所有依赖升级。 |
| [LangGraph Releases](https://github.com/langchain-ai/langgraph/releases) | 2 | 区分核心包、SDK 和 CLI 版本，关注执行、持久化与人工介入变化。 |
| [vLLM Releases](https://github.com/vllm-project/vllm/releases) | 2 | 关注影响 LLM/Agent 的推理、工具调用、成本与模型支持变化。 |
| [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) | 2 | 插件架构、工具扩展、上下文与任务执行；区分开发预览和稳定版。 |
| [Hermes Agent](https://github.com/NousResearch/hermes-agent) | 2 | 记忆与技能、跨端会话、子 Agent、持久运行与版本迁移。 |
| [Dify](https://github.com/langgenius/dify) | 2 | Agent 工作流、RAG、可观察性、集成与部署变化。 |
| [LangChain](https://github.com/langchain-ai/langchain) | 2 | 核心包的工具调用、Agent 接口与集成，区分子包版本。 |
| [Browser Use](https://github.com/browser-use/browser-use) | 2 | 浏览器操作、任务可靠性、会话与部署；区分开源库和云服务。 |
| [Ollama](https://github.com/ollama/ollama) | 2 | 本地模型支持、推理接口、工具调用及性能变化。 |
| [Firecrawl](https://github.com/firecrawl/firecrawl) | 2 | 抓取、搜索、结构化抽取和 Agent 数据接口。 |
| [n8n](https://github.com/n8n-io/n8n) | 2 | 关注全 AI 相关工作流与自动化；准确区分 fair-code、自定义许可和开源。 |
| [Awesome LLM Apps](https://github.com/Shubhamsaboo/awesome-llm-apps) | 2 | 发现 Agent、RAG 和技能案例；返回独立原始项目核实，不能继承合集 star。 |
| [Awesome AI Agents](https://github.com/e2b-dev/awesome-ai-agents) | 2 | 补充发现候选；该合集近期更新较少，每次核实子项目自身的活跃度与 star。 |

## 评测与可靠性

| 来源 | 优先级 | 检查方式 |
| --- | --- | --- |
| [mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent) | 2 | 作为最小执行系统、研究与评测工具的候选，按用途与文档质量选稿。 |
| [METR](https://metr.org/) | 1 | 查任务时间跨度、生产率与评测方法，区分研究、初步笔记和推断。 |
| [SWE-bench](https://www.swebench.com/) | 1 | 核查子集、harness、预算和验证方式，避免只引用排行榜名次。 |
| [τ²-bench](https://github.com/sierra-research/tau2-bench) | 2 | 关注工具、用户交互、成功率和重复运行可靠性。 |

## 新闻与人物：补充线索

| 来源 | 优先级 | 检查方式 |
| --- | --- | --- |
| [Simon Willison](https://simonwillison.net/) | 2 | 优先读作者亲测的技术记录，转述消息返回原出处。 |
| [Latent Space](https://latent.space/) | 2 | 选技术作者访谈与工程讨论；新闻摘要仅作发现入口。 |
| [机器之心](https://www.jiqizhixin.com/) | 2 | 中文研究和行业线索，技术结论回论文与作者来源。 |
| [Tibo 社区归档](https://codex-reset.com/tibo/x/) | 2 | 仅作找原帖线索，可能延迟；社区预测不作官方公告，不据此推断个人额度。 |

## 论文与研究：期刊

| 来源 | 优先级 | 检查方式 |
| --- | --- | --- |
| [Nature / Nature Machine Intelligence](https://www.nature.com/natmachintell/) | 1 | 结合 Nature 系列相关论文；核对在线发表日、摘要与方法，区分期刊版和早期预印本。 |
| [Nature Human Behaviour](https://www.nature.com/nathumbehav/) | 2 | 关注 AI 行为、评测与人机互动的相关研究。 |
| [TMLR](https://jmlr.org/tmlr/) | 1 | 核对正式接收状态、版本与公开评审。 |
| [JMLR](https://www.jmlr.org/papers/) | 2 | 检查近期正式论文，按 LLM／Agent 相关性筛选。 |

## 论文与研究：会议

| 来源 | 优先级 | 检查方式 |
| --- | --- | --- |
| [NeurIPS Proceedings](https://proceedings.neurips.cc/) | 1 | 以正式论文集或公开录用决定为准，不能凭投稿页写成已录用。 |
| [ICML / PMLR](https://proceedings.mlr.press/) | 1 | 从 ICML 正式卷检索近期相关成果，区分会议日期与首次公开日期。 |
| [ICLR / OpenReview](https://openreview.net/group?id=ICLR.cc) | 1 | 核对会议、年份与 decision，不能把 active submission 当成接收。 |
| [ACL / EMNLP Anthology](https://aclanthology.org/) | 1 | 核对 venue、年份和主会／Findings／Workshop 类型；其他 NLP 会议作补充。 |

## 新闻：官方发布

| 来源 | 优先级 | 检查方式 |
| --- | --- | --- |
| [OpenAI News](https://openai.com/news/) | 1 | 检查模型、产品、定价、额度、公司及算力公告；标明已上线与计划。 |
| [Anthropic News](https://www.anthropic.com/news) | 1 | 检查产品、公司与政策动态，回直接公告。 |
| [Thinking Machines Lab](https://thinkingmachines.ai/news/) | 2 | 核对产品上线、权重开放状态和技术细节。 |
| [NVIDIA Newsroom](https://nvidianews.nvidia.com/) | 1 | 关注芯片、机器人、产业合作和黄仁勋公开活动。 |

## 新闻：媒体报道

| 来源 | 优先级 | 检查方式 |
| --- | --- | --- |
| [Reuters](https://www.reuters.com/technology/) | 1 | AI 产业、政治、经济与社会；付费墙或访问受限如实记录，可核对有署名转载。 |
| [Associated Press](https://apnews.com/hub/artificial-intelligence) | 2 | 补充社会与公共事件，重要争议交叉核查。 |
| [TechCrunch AI](https://techcrunch.com/category/artificial-intelligence/) | 2 | 产品、创业与融资动态；传闻标清状态。 |
| [The Verge AI](https://www.theverge.com/ai-artificial-intelligence) | 2 | 消费产品、行业人物与社会影响。 |
| [Tom’s Hardware](https://www.tomshardware.com/) | 2 | 硬件、数据中心与行业报道；转引要标注原报道及实际可读范围。 |

## 新闻与人物：公开账号

| 来源 | 优先级 | 检查方式 |
| --- | --- | --- |
| [Tibo / Thibault Sottiaux · @thsottiaux](https://x.com/thsottiaux) | 1 | 固定关注 Codex 产品、额度与重置；保留原帖、UTC／北京时间和适用对象。无法确认不写成已到账。 |
| [Andrej Karpathy](https://x.com/karpathy) | 2 | 公开实验、观点和趣事可选；观点与事实分别归属，回原帖核实。 |
| [Sam Altman](https://x.com/sama) | 2 | 公开产品与公司动态，重要消息与官方公告交叉核查。 |

## 开源项目：发现

| 来源 | 优先级 | 检查方式 |
| --- | --- | --- |
| [HelloGitHub · Skills 与人工智能](https://hellogithub.com/periodical/volume/127) | 1 | 从最新期刊及 Skills／人工智能分类发现候选；回仓库核对，不照搬文案、图片或榜单。 |
| [HelloGitHub 推荐审核标准](https://github.com/521xueweihan/HelloGitHub/issues/271) | 2 | 参考文档、特色、上手入口、许可、维护与讨论；star 作参考，不设入刊硬门槛。 |
| [GitHub Trending](https://github.com/trending) | 2 | 补充全 AI 项目发现，避免固定重复大框架；热度不能替代用途与维护核查。 |
