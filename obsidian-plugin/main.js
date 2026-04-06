const {
  ItemView,
  MarkdownView,
  Notice,
  Plugin,
  PluginSettingTab,
  Setting,
  requestUrl,
} = require("obsidian");

const VIEW_TYPE = "ob-paper-read-chat";

const DEFAULT_SETTINGS = {
  mode: "bridge",
  apiBaseUrl: "https://api.openai.com/v1/chat/completions",
  apiKey: "",
  model: "",
  temperature: 0.2,
  memoryDir: ".ob-paper-read-memory",
  maxQuestionMemory: 5,
  systemPrompt:
    "你是论文阅读教练。请基于当前上下文，用中文为主、专业术语保留英文的方式回答。优先沿着当前阅读主线讲解，而不是只做摘要。",
};

function slugify(value) {
  return String(value || "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/-{2,}/g, "-")
    .replace(/^-|-$/g, "") || "item";
}

function clip(text, maxLength = 280) {
  const value = String(text || "").trim();
  if (value.length <= maxLength) {
    return value;
  }
  return value.slice(0, maxLength) + "...";
}

function uniquePush(list, value) {
  if (!value) {
    return;
  }
  if (!Array.isArray(list)) {
    return;
  }
  if (!list.includes(value)) {
    list.push(value);
  }
}

function containsAny(text, patterns) {
  const source = String(text || "").toLowerCase();
  return patterns.some((pattern) => source.includes(pattern));
}

function inferQuestionSignals(userMessage) {
  const text = String(userMessage || "");
  const signals = {
    conceptTags: [],
    focusMoreOn: [],
    preferredExplanationStyle: [],
    figurePriority: [],
    unresolvedConcepts: [],
    followUpPrompt: "",
  };

  if (containsAny(text, ["figure", "图", "图表", "表", "figure 1", "figure 2"])) {
    uniquePush(signals.focusMoreOn, "key figures");
    uniquePush(signals.preferredExplanationStyle, "figure-first");
    const match = text.match(/figure\s*\d+/i);
    if (match) {
      uniquePush(signals.figurePriority, match[0].replace(/\s+/g, " ").trim());
    } else {
      uniquePush(signals.figurePriority, "key figures");
    }
  }

  if (containsAny(text, ["why", "为什么", "直觉", "intuition"])) {
    uniquePush(signals.preferredExplanationStyle, "intuition-first");
  }

  if (containsAny(text, ["compare", "baseline", "对比", "区别", "相比"])) {
    uniquePush(signals.preferredExplanationStyle, "comparison-first");
    uniquePush(signals.focusMoreOn, "comparison and baseline");
  }

  const conceptRules = [
    { key: "self-attention", patterns: ["self-attention", "自注意力"] },
    { key: "multi-head attention", patterns: ["multi-head", "多头"] },
    { key: "positional encoding", patterns: ["positional", "位置编码"] },
    { key: "encoder-decoder", patterns: ["encoder-decoder", "编码器", "解码器"] },
    { key: "rnn", patterns: ["rnn", "循环神经", "循环网络"] },
    { key: "attention", patterns: ["attention", "注意力"] },
    { key: "experiment", patterns: ["实验", "evidence", "证据"] },
    { key: "baseline", patterns: ["baseline", "基线"] },
  ];

  for (const rule of conceptRules) {
    if (containsAny(text, rule.patterns.map((item) => item.toLowerCase()))) {
      uniquePush(signals.conceptTags, rule.key);
      uniquePush(signals.unresolvedConcepts, rule.key);
      uniquePush(signals.focusMoreOn, rule.key);
    }
  }

  if (signals.conceptTags.length) {
    signals.followUpPrompt = `下次继续时，优先确认这些概念是否真正讲透：${signals.conceptTags.join(" / ")}`;
  }

  return signals;
}

async function exists(adapter, path) {
  try {
    return await adapter.exists(path);
  } catch {
    return false;
  }
}

async function ensureDir(adapter, path) {
  const parts = path.split("/").filter(Boolean);
  let current = "";
  for (const part of parts) {
    current = current ? `${current}/${part}` : part;
    if (!(await exists(adapter, current))) {
      await adapter.mkdir(current);
    }
  }
}

class ObPaperReadView extends ItemView {
  constructor(leaf, plugin) {
    super(leaf);
    this.plugin = plugin;
    this.messages = [];
    this.contextPacket = null;
    this.sessionId = null;
  }

  getViewType() {
    return VIEW_TYPE;
  }

  getDisplayText() {
    return "OB Paper Read Chat";
  }

  getIcon() {
    return "message-square";
  }

  async onOpen() {
    await this.refreshContext();
    this.render();
  }

  async refreshContext() {
    this.contextPacket = await this.plugin.buildContextPacket();
    const paperId = this.contextPacket?.paper?.paper_id || "no-paper";
    if (!this.sessionId || !this.sessionId.endsWith(`__${paperId}`)) {
      this.sessionId = this.plugin.createSessionId(paperId);
    }
  }

  render() {
    const container = this.containerEl.children[1];
    container.empty();
    container.addClass("obpr-root");

    const toolbar = container.createDiv({ cls: "obpr-toolbar" });
    const refreshButton = toolbar.createEl("button", { text: "刷新上下文" });
    refreshButton.onclick = async () => {
      await this.refreshContext();
      this.render();
      new Notice("已刷新当前上下文。");
    };

    const copyButton = toolbar.createEl("button", { text: "复制上下文包" });
    copyButton.onclick = async () => {
      const packet = await this.plugin.buildContextPacket();
      await this.plugin.copyContextPacket(packet);
      new Notice("已复制当前上下文包。");
    };

    const summary = container.createDiv({ cls: "obpr-summary" });
    const packet = this.contextPacket || {};
    const paper = packet.paper || {};
    const activeFile = packet.active_file || {};
    const selection = packet.active_markdown?.selection || "";
    summary.createEl("div", { text: `当前文件: ${activeFile.path || "未检测到"}` });
    summary.createEl("div", { text: `当前论文: ${paper.title || "未检测到"}` });
    summary.createEl("div", { text: `论文状态: ${paper.status || "未知"}` });
    summary.createEl("div", { text: `当前选中文本: ${clip(selection || "无", 120)}` });
    summary.createEl("div", {
      text:
        this.plugin.settings.mode === "bridge"
          ? "聊天模式: Bridge（生成上下文给外部 agent）"
          : `聊天模式: API（${this.plugin.settings.model || "未配置模型"}）`,
    });

    const messageList = container.createDiv({ cls: "obpr-message-list" });
    if (!this.messages.length) {
      const empty = messageList.createDiv({ cls: "obpr-message obpr-message-assistant" });
      empty.createDiv({ cls: "obpr-message-meta", text: "系统" });
      empty.createDiv({
        text:
          "这里应该承接当前论文、当前选中内容和历史问题。你可以直接问概念、图表、实验，插件会把上下文打包后带给 AI。",
      });
    } else {
      for (const message of this.messages) {
        const item = messageList.createDiv({
          cls: `obpr-message ${message.role === "user" ? "obpr-message-user" : "obpr-message-assistant"}`,
        });
        item.createDiv({
          cls: "obpr-message-meta",
          text: message.role === "user" ? "你" : "AI",
        });
        item.createDiv({ text: message.content });
      }
      messageList.scrollTop = messageList.scrollHeight;
    }

    const inputWrap = container.createDiv({ cls: "obpr-input-wrap" });
    const textarea = inputWrap.createEl("textarea", {
      cls: "obpr-textarea",
      attr: { placeholder: "直接问当前论文。比如：Figure 1 该怎么读？为什么 self-attention 能替代 RNN？" },
    });

    const actions = inputWrap.createDiv({ cls: "obpr-actions" });
    const bridgeButton = actions.createEl("button", { text: "外部对话桥接" });
    bridgeButton.onclick = async () => {
      const prompt = await this.plugin.buildBridgePrompt(textarea.value || "");
      await this.plugin.copyText(prompt);
      new Notice("已复制桥接提示词，可以发给 Codex / Claude Code / OpenClaw。");
    };

    const sendButton = actions.createEl("button", { text: "发送" });
    sendButton.onclick = async () => {
      const userMessage = textarea.value.trim();
      if (!userMessage) {
        new Notice("先输入一个问题。");
        return;
      }

      sendButton.disabled = true;
      try {
        await this.refreshContext();
        this.messages.push({ role: "user", content: userMessage });
        this.render();

        const answer = await this.plugin.answerWithContext(userMessage, this.contextPacket, this.messages);
        this.messages.push({ role: "assistant", content: answer });
        await this.plugin.persistTurn(this.sessionId, this.contextPacket, userMessage, answer);
        textarea.value = "";
        this.render();
      } catch (error) {
        new Notice(`发送失败: ${error.message || error}`);
      } finally {
        sendButton.disabled = false;
      }
    };
  }
}

class ObPaperReadSettingTab extends PluginSettingTab {
  constructor(app, plugin) {
    super(app, plugin);
    this.plugin = plugin;
  }

  display() {
    const { containerEl } = this;
    containerEl.empty();

    containerEl.createEl("h2", { text: "OB Paper Read Chat" });

    new Setting(containerEl)
      .setName("聊天模式")
      .setDesc("bridge 会复制上下文给外部 agent；api 会直接调用 OpenAI-compatible 接口。")
      .addDropdown((dropdown) =>
        dropdown
          .addOption("bridge", "Bridge")
          .addOption("api", "API")
          .setValue(this.plugin.settings.mode)
          .onChange(async (value) => {
            this.plugin.settings.mode = value;
            await this.plugin.saveSettings();
          }),
      );

    new Setting(containerEl)
      .setName("API 地址")
      .setDesc("例如 OpenAI-compatible 的 /chat/completions 地址。")
      .addText((text) =>
        text
          .setPlaceholder("https://api.openai.com/v1/chat/completions")
          .setValue(this.plugin.settings.apiBaseUrl)
          .onChange(async (value) => {
            this.plugin.settings.apiBaseUrl = value.trim();
            await this.plugin.saveSettings();
          }),
      );

    new Setting(containerEl)
      .setName("API Key")
      .setDesc("仅在 API 模式下使用。")
      .addText((text) =>
        text
          .setPlaceholder("sk-...")
          .setValue(this.plugin.settings.apiKey)
          .onChange(async (value) => {
            this.plugin.settings.apiKey = value.trim();
            await this.plugin.saveSettings();
          }),
      );

    new Setting(containerEl)
      .setName("模型名")
      .setDesc("例如 gpt-4.1-mini、gpt-5、deepseek-chat 等。")
      .addText((text) =>
        text
          .setValue(this.plugin.settings.model)
          .onChange(async (value) => {
            this.plugin.settings.model = value.trim();
            await this.plugin.saveSettings();
          }),
      );

    new Setting(containerEl)
      .setName("Memory 目录")
      .setDesc("默认是 .ob-paper-read-memory。")
      .addText((text) =>
        text
          .setValue(this.plugin.settings.memoryDir)
          .onChange(async (value) => {
            this.plugin.settings.memoryDir = value.trim() || DEFAULT_SETTINGS.memoryDir;
            await this.plugin.saveSettings();
          }),
      );
  }
}

module.exports = class ObPaperReadPlugin extends Plugin {
  async onload() {
    await this.loadSettings();

    this.registerView(VIEW_TYPE, (leaf) => new ObPaperReadView(leaf, this));
    this.addCommand({
      id: "open-ob-paper-read-chat",
      name: "Open OB Paper Read Chat",
      callback: async () => {
        await this.activateView();
      },
    });
    this.addCommand({
      id: "copy-ob-paper-read-context",
      name: "Copy OB Paper Read Context Packet",
      callback: async () => {
        const packet = await this.buildContextPacket();
        await this.copyContextPacket(packet);
        new Notice("已复制上下文包。");
      },
    });

    this.addRibbonIcon("message-square", "OB Paper Read Chat", async () => {
      await this.activateView();
    });

    this.addSettingTab(new ObPaperReadSettingTab(this.app, this));
    this.registerDomEvent(document, "selectionchange", () => {});
  }

  async onunload() {
    await this.app.workspace.detachLeavesOfType(VIEW_TYPE);
  }

  async loadSettings() {
    this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
  }

  async saveSettings() {
    await this.saveData(this.settings);
  }

  async activateView() {
    const { workspace } = this.app;
    let leaf = workspace.getLeavesOfType(VIEW_TYPE)[0];
    if (!leaf) {
      leaf = workspace.getRightLeaf(false);
      await leaf.setViewState({ type: VIEW_TYPE, active: true });
    }
    workspace.revealLeaf(leaf);
  }

  createSessionId(paperId) {
    const stamp = new Date().toISOString().replace(/[:.]/g, "-");
    return `${stamp}__${paperId || "no-paper"}`;
  }

  async buildContextPacket() {
    const activeFile = this.app.workspace.getActiveFile();
    const markdownView = this.app.workspace.getActiveViewOfType(MarkdownView);
    const selection = markdownView?.editor?.getSelection?.() || "";
    const metadata = activeFile ? this.app.metadataCache.getFileCache(activeFile) || {} : {};
    const paperId =
      metadata.frontmatter?.paper_id ||
      this.resolvePaperIdFromPath(activeFile?.path || "") ||
      "";
    const paper = paperId ? await this.readPaperCard(paperId) : null;
    const relatedQuestions = paperId ? await this.readRecentQuestionMemory(paperId) : [];

    return {
      generated_at: new Date().toISOString(),
      active_file: {
        path: activeFile?.path || "",
        name: activeFile?.name || "",
        extension: activeFile?.extension || "",
      },
      active_markdown: {
        path: markdownView?.file?.path || "",
        selection,
        headings: (metadata.headings || []).slice(0, 10).map((item) => item.heading),
        frontmatter: metadata.frontmatter || {},
      },
      paper: paper
        ? {
            paper_id: paper.paper_id,
            title: paper.title,
            status: paper.status,
            domain: paper.domain,
            topic: paper.topic,
            role: paper.role,
            source_pdf: paper.source?.path || "",
            open_questions: paper.open_questions || [],
            reading_progress: paper.reading_progress || {},
            teaching_adjustments: paper.teaching_adjustments || {},
          }
        : null,
      related_questions: relatedQuestions,
    };
  }

  resolvePaperIdFromPath(path) {
    const match = String(path || "").match(/papers\/([^/]+)\/reading\.md$/);
    return match ? match[1] : "";
  }

  async readJson(relativePath) {
    if (!(await exists(this.app.vault.adapter, relativePath))) {
      return null;
    }
    const text = (await this.app.vault.adapter.read(relativePath)).replace(/^\uFEFF/, "");
    return JSON.parse(text);
  }

  async writeJson(relativePath, payload) {
    const parent = relativePath.split("/").slice(0, -1).join("/");
    await ensureDir(this.app.vault.adapter, parent);
    await this.app.vault.adapter.write(relativePath, JSON.stringify(payload, null, 2) + "\n");
  }

  async readPaperCard(paperId) {
    const memoryRoot = await this.resolveMemoryRoot();
    const path = `${memoryRoot}/papers/${paperId}.json`;
    return await this.readJson(path);
  }

  async readRecentQuestionMemory(paperId) {
    const memoryRoot = await this.resolveMemoryRoot();
    const dir = `${memoryRoot}/questions`;
    if (!(await exists(this.app.vault.adapter, dir))) {
      return [];
    }

    const files = await this.app.vault.adapter.list(dir);
    const results = [];
    for (const file of files.files || []) {
      if (!file.endsWith(".json")) {
        continue;
      }
      try {
        const payload = JSON.parse(await this.app.vault.adapter.read(file));
        if ((payload.papers || []).includes(paperId)) {
          results.push(payload);
        }
      } catch {}
    }
    return results
      .sort((a, b) => (b.ask_count || 0) - (a.ask_count || 0))
      .slice(0, this.settings.maxQuestionMemory);
  }

  async copyText(text) {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
      return;
    }
    const path = `${this.settings.memoryDir}/last-copied-context.txt`;
    await ensureDir(this.app.vault.adapter, this.settings.memoryDir);
    await this.app.vault.adapter.write(path, text);
  }

  async copyContextPacket(packet) {
    const text = JSON.stringify(packet, null, 2);
    await this.copyText(text);
    const memoryRoot = await this.resolveMemoryRoot();
    await ensureDir(this.app.vault.adapter, memoryRoot);
    await this.app.vault.adapter.write(`${memoryRoot}/last-context-packet.json`, text);
  }

  async buildBridgePrompt(userMessage) {
    const packet = await this.buildContextPacket();
    return [
      "Use the following Obsidian context packet to answer inside the current paper-reading session.",
      "",
      "Context packet:",
      "```json",
      JSON.stringify(packet, null, 2),
      "```",
      "",
      `User question: ${userMessage || "请沿着当前阅读主线继续讲解。"}`
    ].join("\n");
  }

  async answerWithContext(userMessage, contextPacket, messages) {
    if (this.settings.mode !== "api") {
      await this.copyContextPacket(contextPacket);
      return [
        "当前是 Bridge 模式，还没有直接在 Obsidian 内调用模型。",
        "我已经把上下文包复制好了，你可以把它发给 Codex / Claude Code / OpenClaw。",
        "如果你想直接在右侧对话，请在插件设置里切到 API 模式，并填入 OpenAI-compatible 接口、模型名和 API Key。",
      ].join("\n");
    }

    if (!this.settings.apiBaseUrl || !this.settings.model) {
      throw new Error("API 模式还没有配置完整，请先填写 API 地址和模型名。");
    }

    const history = messages.slice(-8).map((item) => ({
      role: item.role,
      content: item.content,
    }));

    const payload = {
      model: this.settings.model,
      temperature: this.settings.temperature,
      messages: [
        { role: "system", content: this.settings.systemPrompt },
        {
          role: "system",
          content:
            "当前 Obsidian 上下文包如下。你必须基于它回答，并尽量沿着当前阅读锚点继续讲，不要退化成普通摘要。\n```json\n" +
            JSON.stringify(contextPacket, null, 2) +
            "\n```",
        },
        ...history,
        { role: "user", content: userMessage },
      ],
    };

    const headers = { "Content-Type": "application/json" };
    if (this.settings.apiKey) {
      headers.Authorization = `Bearer ${this.settings.apiKey}`;
    }

    const response = await requestUrl({
      url: this.settings.apiBaseUrl,
      method: "POST",
      headers,
      body: JSON.stringify(payload),
    });

    const content =
      response.json?.choices?.[0]?.message?.content ||
      response.json?.output?.[0]?.content?.[0]?.text ||
      "";

    if (!content) {
      throw new Error("没有从接口返回可用内容。");
    }

    return content;
  }

  async persistTurn(sessionId, contextPacket, userMessage, answer) {
    const memoryDir = await this.resolveMemoryRoot();
    await ensureDir(this.app.vault.adapter, `${memoryDir}/questions`);
    await ensureDir(this.app.vault.adapter, `${memoryDir}/sessions`);

    const paperId = contextPacket?.paper?.paper_id || "no-paper";
    const sessionPath = `${memoryDir}/sessions/${sessionId}.json`;
    const questionId = slugify(userMessage).slice(0, 80);
    const questionPath = `${memoryDir}/questions/${questionId}.json`;

    const session =
      (await this.readJson(sessionPath)) || {
        session_id: sessionId,
        paper_id: paperId,
        started_at: new Date().toISOString(),
        status: "open",
        turns: [],
      };
    session.ended_at = new Date().toISOString();
    session.turns.push({
      asked_at: new Date().toISOString(),
      user: userMessage,
      assistant: answer,
      active_file: contextPacket?.active_file?.path || "",
      selection: contextPacket?.active_markdown?.selection || "",
    });
    await this.writeJson(sessionPath, session);

    const question =
      (await this.readJson(questionPath)) || {
        question_id: questionId,
        canonical_question: userMessage,
        variants: [],
        concept_tags: [],
        papers: [],
        sessions: [],
        ask_count: 0,
        status: "open",
        resolution_confidence: 0.0,
        last_asked_at: "",
        last_answer_note: "",
        follow_up_prompt: "",
        resolved_in_papers: [],
        unresolved_in_papers: [],
      };
    const signals = inferQuestionSignals(userMessage);
    question.ask_count += 1;
    question.last_asked_at = new Date().toISOString();
    question.last_answer_note = clip(answer, 220);
    question.status = question.status === "resolved" ? "reopened" : "open";
    question.resolution_confidence = Math.min(Number(question.resolution_confidence || 0), 0.4);
    question.follow_up_prompt = signals.followUpPrompt || question.follow_up_prompt || "";
    if (!question.papers.includes(paperId)) {
      question.papers.push(paperId);
    }
    if (!question.sessions.includes(sessionId)) {
      question.sessions.push(sessionId);
    }
    for (const variant of [userMessage]) {
      uniquePush(question.variants, variant);
    }
    for (const tag of signals.conceptTags) {
      uniquePush(question.concept_tags, tag);
    }
    uniquePush(question.unresolved_in_papers, paperId);
    await this.writeJson(questionPath, question);

    await this.bumpPaperMetrics(paperId, sessionId, questionId, userMessage, signals);
  }

  async bumpPaperMetrics(paperId, sessionId, questionId, userMessage, signals) {
    if (!paperId || paperId === "no-paper") {
      return;
    }
    const memoryRoot = await this.resolveMemoryRoot();
    const path = `${memoryRoot}/papers/${paperId}.json`;
    const card = await this.readJson(path);
    if (!card) {
      return;
    }
    const metrics = card.reading_metrics || {};
    metrics.qa_count = Number(metrics.qa_count || 0) + 1;
    metrics.last_read_at = new Date().toISOString();
    card.reading_metrics = metrics;
    card.open_questions = Array.isArray(card.open_questions) ? card.open_questions : [];
    uniquePush(card.open_questions, userMessage);
    card.question_refs = Array.isArray(card.question_refs) ? card.question_refs : [];
    card.session_refs = Array.isArray(card.session_refs) ? card.session_refs : [];
    uniquePush(card.question_refs, questionId);
    uniquePush(card.session_refs, sessionId);
    card.teaching_adjustments = card.teaching_adjustments || {
      focus_more_on: [],
      focus_less_on: [],
      preferred_explanation_style: [],
      figure_priority: [],
      unresolved_concepts: [],
      carry_into_next_generation: true,
      notes: "",
    };
    for (const item of signals.focusMoreOn || []) {
      uniquePush(card.teaching_adjustments.focus_more_on, item);
    }
    for (const item of signals.preferredExplanationStyle || []) {
      uniquePush(card.teaching_adjustments.preferred_explanation_style, item);
    }
    for (const item of signals.figurePriority || []) {
      uniquePush(card.teaching_adjustments.figure_priority, item);
    }
    for (const item of signals.unresolvedConcepts || []) {
      uniquePush(card.teaching_adjustments.unresolved_concepts, item);
    }
    if (card.status === "reading_generated") {
      card.status = "reading_in_progress";
    }
    await this.writeJson(path, card);
  }

  async resolveMemoryRoot() {
    const candidates = [
      this.settings.memoryDir,
      `ob-paper-read/${this.settings.memoryDir}`,
    ];
    for (const candidate of candidates) {
      if (await exists(this.app.vault.adapter, candidate)) {
        return candidate;
      }
    }
    return this.settings.memoryDir;
  }
};
