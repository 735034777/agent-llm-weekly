# 信息源目录

[返回首页](README.md) · [高 star 项目池](PROJECTS.md) · [编辑准则](docs/EDITORIAL.md)

下面是计划追踪的入口。每期实际检查情况记录在该期 JSON 的 source_checks 中；列入目录不代表每期都能完整访问。优先级 1 每周优先检查，优先级 2 用于补充。

## 一手研究与工程

| 来源 | 优先级 | 检查方式 |
| --- | --- | --- |
| [Anthropic Engineering](https://www.anthropic.com/engineering) | 1 | 检查本周新文章；读取方法、案例和局限。 |
| [OpenAI Research](https://openai.com/research/) | 1 | 从研究索引进入技术报告、评测及系统卡。 |
| [Google DeepMind](https://deepmind.google/blog/) | 1 | 查本周模型、推理、多模态与 Agent 原始发布。 |
| [DeepSeek](https://github.com/deepseek-ai) | 1 | 查官方新仓库、论文与有实质内容的变更。 |
| [Qwen](https://github.com/QwenLM) | 1 | 查模型与 Agent 项目，返回论文及模型卡核实。 |

## 论文发现

| 来源 | 优先级 | 检查方式 |
| --- | --- | --- |
| [Hugging Face Daily Papers](https://huggingface.co/papers) | 1 | 按对应 ISO 周浏览，热度只作线索；回原论文核查首次发布日期。 |
| [arXiv cs.AI / cs.CL / cs.LG](https://arxiv.org/list/cs.AI/recent) | 1 | 检索 agentic RL、tool use、memory、reasoning、evaluation；必要时扩展 cs.CL/cs.LG。 |
| [OpenReview](https://openreview.net/) | 2 | 对入选论文检查公开审稿与作者回应，保留预印本和录用状态区别。 |

## 开源工程

| 来源 | 优先级 | 检查方式 |
| --- | --- | --- |
| [OpenHands Releases](https://github.com/OpenHands/OpenHands/releases) | 1 | 按 published_at 筛选本周版本，读关联 PR，不跟踪所有依赖升级。 |
| [LangGraph Releases](https://github.com/langchain-ai/langgraph/releases) | 1 | 区分核心包、SDK 和 CLI 版本，关注执行、持久化与人工介入变化。 |
| [vLLM Releases](https://github.com/vllm-project/vllm/releases) | 1 | 关注影响 LLM/Agent 的推理、工具调用、成本与模型支持变化。 |

## 评测与可靠性

| 来源 | 优先级 | 检查方式 |
| --- | --- | --- |
| [mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent) | 2 | 作为最小执行系统与评测方法的研究参考，不进入高 star 项目推荐栏。 |
| [METR](https://metr.org/) | 1 | 查任务时间跨度、生产率与评测方法，区分研究、初步笔记和推断。 |
| [SWE-bench](https://www.swebench.com/) | 1 | 核查子集、harness、预算和验证方式，避免只引用排行榜名次。 |
| [τ²-bench](https://github.com/sierra-research/tau2-bench) | 2 | 关注工具、用户交互、成功率和重复运行可靠性。 |

## 实践与访谈

| 来源 | 优先级 | 检查方式 |
| --- | --- | --- |
| [Simon Willison](https://simonwillison.net/) | 2 | 优先读作者亲测的技术记录，转述消息返回原出处。 |
| [Latent Space](https://latent.space/) | 2 | 选技术作者访谈与工程讨论；新闻摘要仅作发现入口。 |

## 高 star 项目

| 来源 | 优先级 | 检查方式 |
| --- | --- | --- |
| [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) | 1 | 插件架构、工具扩展、上下文与任务执行；区分开发预览和稳定版。 |
| [Hermes Agent](https://github.com/NousResearch/hermes-agent) | 1 | 记忆与技能、跨端会话、子 Agent、持久运行与版本迁移。 |
| [Dify](https://github.com/langgenius/dify) | 1 | Agent 工作流、RAG、可观察性、集成与部署变化。 |
| [LangChain](https://github.com/langchain-ai/langchain) | 1 | 核心包的工具调用、Agent 接口与集成，区分子包版本。 |
| [Browser Use](https://github.com/browser-use/browser-use) | 1 | 浏览器操作、任务可靠性、会话与部署；区分开源库和云服务。 |
| [Ollama](https://github.com/ollama/ollama) | 1 | 本地模型支持、推理接口、工具调用及性能变化。 |
| [Firecrawl](https://github.com/firecrawl/firecrawl) | 1 | 抓取、搜索、结构化抽取和 Agent 数据接口。 |
| [n8n](https://github.com/n8n-io/n8n) | 1 | 只选与 Agent、LLM、工具集成有关的实质更新；保留 fair-code 许可区别。 |

## 项目发现合集

| 来源 | 优先级 | 检查方式 |
| --- | --- | --- |
| [Awesome LLM Apps](https://github.com/Shubhamsaboo/awesome-llm-apps) | 2 | 发现 Agent、RAG 和技能案例；返回独立原始项目核实，不能继承合集 star。 |
| [Awesome AI Agents](https://github.com/e2b-dev/awesome-ai-agents) | 2 | 补充发现候选；该合集近期更新较少，每次核实子项目自身的活跃度与 star。 |
