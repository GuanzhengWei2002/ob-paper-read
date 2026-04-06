# ob-paper-read

简体中文 | [English](./README.md)

`ob-paper-read` 是一个面向 Codex、Claude Code、OpenClaw 与 Obsidian 的论文阅读工作流。

它不是用来“顺手总结一篇论文”的，而是用来把 PDF 论文变成一个更适合认真阅读的过程：

- 把论文保存到本地论文库
- 给论文补一个轻量分类和阅读上下文
- 生成讲义风格的 `reading.md`
- 抽取关键图表到本地 `assets/`
- 持续记录阅读状态、提问历史和跨 session 记忆

它想提供的体验很简单：

- 左边看原始 PDF
- 中间看 `reading.md`
- 右边在 Obsidian 里直接和 AI 对话

## 为什么做这个

很多论文工具更擅长检索、收集和摘要。

`ob-paper-read` 更偏向“陪你把论文读进去”：

- 尽量贴近原文
- 按章节顺序解释
- 把关键图变成真正的讲解节点
- 让用户留下记忆，而不是只堆一堆碎片化笔记

## 它会产出什么

对每篇论文，核心产物是：

- `reading.md`：主讲义文件
- `assets/`：抽取出来的关键图表
- 本地 memory：记录论文状态、问题、session 等信息

目标不是多生成几个文件，而是让 `reading.md` 本身就足够像一份可读、可追问、可反思的带读讲稿。

## 核心设计

- `PDF-first`：V1 从 PDF 上传开始
- `local-first`：文件和 memory 默认都在用户本地
- `single-paper focus`：多篇上传时先选一篇主读
- `detailed reading by default`：默认详细讲解，而不是快速略读
- `Obsidian-native`：PDF、Markdown、聊天尽量放在同一个工作台里

## 仓库结构

- `SKILL.md`：主 skill 定义
- `scripts/`：memory 初始化、paper card、讲义生成、图表抽取、对比上下文等脚本
- `references/`：setup、输出规则、memory schema、插件说明、平台适配文档
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
5. 如有需要，用 `scripts/extract_pdf_figures.py` 抽取关键图表
6. 在 Obsidian 里打开 PDF、`reading.md` 和聊天栏

## 当前范围

V1 已覆盖：

- PDF 上传
- 本地存储
- 单篇主读流程
- 讲义风格 Markdown 输出
- 可选的图表抽取

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
