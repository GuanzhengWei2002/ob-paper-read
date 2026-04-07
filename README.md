# ob-paper-read

简体中文 | [English](./README.en.md)

`ob-paper-read` 是一个面向 Codex、Claude Code、OpenClaw 与 Obsidian 的论文阅读工作流。

它不是用来“快速总结一篇论文”的，而是把 PDF 论文组织成一个更适合认真阅读、持续追问和长期沉淀的过程。

## 它解决什么问题

很多工具擅长搜论文、收论文、摘要论文。  
`ob-paper-read` 更关注另一件事：**怎么把一篇论文真正读进去。**

它希望提供的是这样一种体验：

- 左边看原始 PDF
- 中间看讲义风格的 `reading.md`
- 右边在 Obsidian 里直接和 AI 对话

## 核心能力

- 以 PDF 为起点，把论文保存到本地论文库
- 给论文建立轻量分类和阅读上下文
- 生成详细讲义风格的 `reading.md`
- 抽取关键图表到本地 `assets/`
- 记录阅读状态、问题历史和跨 session 记忆
- 让用户提问反向影响后续讲义重点，但不破坏通用讲解范式

## 输出结果

对每篇论文，核心产物是：

- `reading.md`
- `assets/`
- 本地 memory：记录论文状态、问题、session、教学调整项等信息

这里的目标不是“多生成几个文件”，而是让 `reading.md` 本身就像一份可以阅读、可以追问、可以反思的带读讲义。

## 产品思路

- `PDF-first`：V1 从 PDF 上传开始
- `local-first`：文件和 memory 默认都在本地
- `single-paper focus`：多篇上传时先选一篇主读
- `detailed reading by default`：默认详细讲解，不做浅层摘要
- `Obsidian-native`：PDF、Markdown、聊天尽量放在同一个工作台里

## 仓库结构

- `SKILL.md`：主 skill 定义
- `scripts/`：memory 初始化、paper card、讲义生成、图表抽取、对比上下文等脚本
- `references/`：setup、输出规则、memory schema、插件说明、平台适配文档、轻量概念层说明
- `obsidian-plugin/`：Obsidian 右侧聊天插件

## Obsidian 聊天

仓库里自带了一个 `OB Paper Read Chat` 插件，用来给 Obsidian 增加右侧聊天栏。

它支持两种模式：

- `Bridge`：把当前 Obsidian 上下文打包后，交给 Codex / Claude Code / OpenClaw 继续回答
- `API`：直接在 Obsidian 里通过 OpenAI-compatible 接口聊天

## 快速开始

1. 阅读 [`references/setup.md`](./references/setup.md)
2. 运行 `scripts/bootstrap_memory.py`
3. 创建或导入一篇论文的 paper card
4. 用 `scripts/create_reading_bundle.py` 生成 `reading.md`
   可选：加 `--suggest-concepts`，在生成后给出“是否沉淀概念卡片”的建议
5. 如有需要，用 `scripts/extract_pdf_figures.py` 抽取关键图表
6. 可选：用 `scripts/update_global_pages.py` 更新 `concepts/` 和 `overviews/index.md`
7. 在 Obsidian 里打开 PDF、`reading.md` 和聊天栏

## 当前范围

V1 已覆盖：

- PDF 上传
- 本地存储
- 单篇主读流程
- 讲义风格 Markdown 输出
- 可选的图表抽取
- 用户提问驱动的 `teaching_adjustments`
- 轻量概念层：`concepts/` 与 `overviews/index.md`

V1 暂时不追求：

- 做一个通用搜索引擎
- 做网页抓取器
- 做一个巨大的知识图谱产品

## 语言风格

默认输出风格是：

- 中文为主
- 在更准确的时候保留英文术语
- 需要时使用 `self-attention（自注意力）` 这类中英结合表达

## 说明

- 尽量不要把机器相关路径提交进仓库
- 不要把 API key 写进仓库或本地 memory
- 原始 PDF 保持只读，不直接修改
