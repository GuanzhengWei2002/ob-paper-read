# ob-paper-read

简体中文 | [English](./README.md)

`ob-paper-read` 是一个面向 Obsidian 的论文阅读 skill 包。

它面向这样的使用方式：

- 用户在 Codex / Claude Code / OpenClaw 中上传一个或多个 PDF 论文
- skill 把 PDF 保存到本地论文库
- skill 生成讲义风格的 `reading.md`
- 用户在 Obsidian 里并排阅读 PDF 和 `reading.md`
- 对话记录、阅读状态、可复用问题会写入本地 memory

## 仓库内容

- `SKILL.md`：主 skill 协议
- `scripts/`：本地脚本，包括 memory 初始化、paper card、讲义生成、对比上下文、图表抽取
- `references/`：setup、memory、输出规范、兼容性、插件、平台适配等文档
- `obsidian-plugin/`：一个最小可用的 Obsidian 右侧聊天插件

## 当前 V1 范围

- 只支持 PDF 上传
- 只依赖本地论文库
- 一次只主读一篇论文
- 每篇论文一个主输出文件：`reading.md`
- 默认产出详细讲义风格，而不是短摘要
- 可选抽取关键图表到 `assets/`

当前不做：

- 把 URL 作为默认入口
- 把网页搜索作为硬依赖
- 做某个特定领域的知识图谱产品

## 产品形态

- 宿主聊天工具负责文件上传
- `ob-paper-read` 负责分类、memory 和输出结构
- Obsidian 负责阅读工作台

## 输出风格

主产物是 `reading.md`。

它应该更像：

- 讲义
- 带读讲稿
- 老师带着用户从标题、摘要、结论、正文、图表、证据、局限一路读下去

而不是：

- “帮你总结一下这篇论文”
- 扁平的 bullet list
- 一个空壳笔记模板

默认语言：

- 中文为主
- 专业术语保留标准英文
- 需要时使用 `English term（中文解释）`

## Obsidian 聊天

这个仓库自带 `OB Paper Read Chat` 插件，用来给 Obsidian 提供右侧聊天栏。

模式有两种：

- `Bridge`：把 Obsidian 上下文打包后交给 Codex / Claude Code / OpenClaw
- `API`：直接在 Obsidian 里调用 OpenAI-compatible 接口聊天

## 快速开始

1. 阅读 `references/setup.md`
2. 运行 `scripts/bootstrap_memory.py`
3. 创建或导入一篇论文的 paper card
4. 用 `scripts/create_reading_bundle.py` 生成 `reading.md`
5. 如有需要，用 `scripts/extract_pdf_figures.py` 抽取关键图表
6. 在 Obsidian 里打开 PDF、`reading.md` 和聊天插件

## 仓库说明

- 尽量不要提交机器相关路径
- 不要把 API key 写进仓库或本地 memory
- 原始 PDF 保持只读，不直接修改
