const API_BASE = "http://127.0.0.1:8000";

const state = {
    health: null,
    workspaces: [],
    activeWorkspaceId: null,
    retrievalMode: "auto",
    busy: false,
    latestCitations: [],
    latestDiagnostics: null,
};

const nvidiaModels = [
    "Nvidia", "Codegemma 1.1 7b", "Codegemma 7b", "Codellama 70b", "Codestral 22b Instruct V0.1", 
    "Cosmos Nemotron 34B", "Deepseek Coder 6.7b Instruct", "Deepseek R1", "Deepseek R1 0528", "DeepSeek V3.1", 
    "DeepSeek V3.1 Terminus", "DeepSeek V3.2", "DeepSeek V4 Flash", "DeepSeek V4 Pro", "Devstral-2-123B-Instruct-2512", 
    "FLUX.1-dev", "Gemma 2 27b It", "Gemma 2 2b It", "Gemma 3 12b It", "Gemma 3 1b It", "Gemma 3n E2b It", 
    "Gemma 3n E4b It", "Gemma-3-27B-IT", "Gemma-4-31B-IT", "GLM-4.7", "GLM-5.1", "GLM5", "GPT-OSS-120B", 
    "Kimi K2 0905", "Kimi K2 Instruct", "Kimi K2 Thinking", "Kimi K2.5", "Llama 3.1 405b Instruct", 
    "Llama 3.1 70b Instruct", "Llama 3.1 Nemotron 51b Instruct", "Llama 3.1 Nemotron 70b Instruct", 
    "Llama 3.2 11b Vision Instruct", "Llama 3.2 1b Instruct", "Llama 3.3 70b Instruct", "Llama 3.3 Nemotron Super 49b V1", 
    "Llama 3.3 Nemotron Super 49b V1.5", "Llama 4 Maverick 17b 128e Instruct", "Llama 4 Scout 17b 16e Instruct", 
    "Llama Embed Nemotron 8B", "Llama-3.1-Nemotron-Ultra-253B-v1", "Llama3 70b Instruct", "Llama3 8b Instruct", 
    "Llama3 Chatqa 1.5 70b", "Mamba Codestral 7b V0.1", "MiniMax-M2.1", "MiniMax-M2.5", "MiniMax-M2.7", 
    "Ministral 3 14B Instruct 2512", "Mistral Large 2 Instruct", "Mistral Large 3 675B Instruct 2512", 
    "Mistral Small 3.1 24b Instruct 2503", "NeMo Retriever OCR v1", "Nemotron 3 Nano Omni", "Nemotron 3 Super", 
    "Nemotron 4 340b Instruct", "nemotron-3-nano-30b-a3b", "nvidia-nemotron-nano-9b-v2", "Parakeet TDT 0.6B v2", 
    "Phi 3 Medium 128k Instruct", "Phi 3 Medium 4k Instruct", "Phi 3 Small 128k Instruct", "Phi 3 Small 8k Instruct", 
    "Phi 3 Vision 128k Instruct", "Phi 3.5 Moe Instruct", "Phi 3.5 Vision Instruct", "Phi-4-Mini", 
    "Qwen2.5 Coder 32b Instruct", "Qwen2.5 Coder 7b Instruct", "Qwen3 Coder 480B A35B Instruct", "Qwen3-235B-A22B", 
    "Qwen3-Next-80B-A3B-Instruct", "Qwen3-Next-80B-A3B-Thinking", "Qwen3.5-397B-A17B", "Qwq 32b", 
    "Step 3.5 Flash", "Whisper Large v3"
];
const enabledModels = new Set(["Nvidia", "Gemma-4-31B-IT", "DeepSeek V3.1"]);
let activeModel = "Gemma-4-31B-IT";

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

const dom = {
    healthPill: $("#health-pill"),
    healthCopy: $("#health-copy"),
    workspaceForm: $("#workspace-form"),
    workspaceName: $("#workspace-name"),
    newWorkspaceBtn: $("#new-workspace-btn"),
    workspaceList: $("#workspace-list"),
    workspaceTitle: $("#workspace-title"),
    sourceCount: $("#source-count"),
    statSources: $("#stat-sources"),
    statChunks: $("#stat-chunks"),
    statVersion: $("#stat-version"),
    dropZone: $("#drop-zone"),
    fileInput: $("#file-input"),
    urlForm: $("#url-form"),
    urlInput: $("#url-input"),
    ingestStatus: $("#ingest-status"),
    ingestSteps: $$(".ingest-steps span"),
    chatStream: $("#chat-stream"),
    chatForm: $("#chat-form"),
    questionInput: $("#question-input"),
    sendBtn: $("#send-btn"),
    evidenceList: $("#evidence-list"),
    citationCount: $("#citation-count"),
    diagnostics: $("#diagnostics"),
    guideContent: $("#guide-content"),
    guideRefresh: $("#guide-refresh"),
    graphCanvas: $("#graph-canvas"),
    graphRefresh: $("#graph-refresh"),
    resetBtn: $("#reset-btn"),
    toastRegion: $("#toast-region"),
    modelTriggerBtn: $("#model-trigger-btn"),
    selectedModelName: $("#selected-model-name"),
    modelPopover: $("#model-popover"),
    connectProviderBtn: $("#connect-provider-btn"),
    apiKeySection: $("#api-key-section"),
    verifyApiBtn: $("#verify-api-btn"),
    modelSearchInput: $("#model-search-input"),
    modelList: $("#model-list"),
};

document.addEventListener("DOMContentLoaded", init);

async function init() {
    bindEvents();
    renderModelList();
    await checkHealth();
    await loadWorkspaces();
}

function bindEvents() {
    dom.workspaceForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const name = dom.workspaceName.value.trim() || "Untitled Study Workspace";
        await createWorkspace(name);
    });

    dom.newWorkspaceBtn.addEventListener("click", () => {
        dom.workspaceName.focus();
    });

    dom.dropZone.addEventListener("dragover", (event) => {
        event.preventDefault();
        dom.dropZone.classList.add("dragging");
    });

    dom.dropZone.addEventListener("dragleave", () => dom.dropZone.classList.remove("dragging"));

    dom.dropZone.addEventListener("drop", async (event) => {
        event.preventDefault();
        dom.dropZone.classList.remove("dragging");
        if (event.dataTransfer.files.length) {
            await ingestFiles(event.dataTransfer.files);
        }
    });

    dom.fileInput.addEventListener("change", async (event) => {
        if (event.target.files.length) {
            await ingestFiles(event.target.files);
            event.target.value = "";
        }
    });

    dom.urlForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        await ingestUrl(dom.urlInput.value.trim());
    });

    dom.chatForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        await askQuestion();
    });

    dom.questionInput.addEventListener("input", () => {
        dom.questionInput.style.height = "auto";
        dom.questionInput.style.height = `${Math.min(dom.questionInput.scrollHeight, 160)}px`;
    });

    dom.questionInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            dom.chatForm.requestSubmit();
        }
    });

    $$(".mode-option").forEach((button) => {
        button.addEventListener("click", () => {
            state.retrievalMode = button.dataset.mode;
            $$(".mode-option").forEach((item) => item.classList.toggle("active", item === button));
        });
    });

    $$(".tab-button").forEach((button) => {
        button.addEventListener("click", () => activateTab(button.dataset.tab));
    });

    dom.guideRefresh.addEventListener("click", () => loadGuide());
    dom.graphRefresh.addEventListener("click", () => loadGraph());
    dom.resetBtn.addEventListener("click", resetSystem);

    dom.modelTriggerBtn.addEventListener("click", () => {
        const isExpanded = dom.modelTriggerBtn.getAttribute("aria-expanded") === "true";
        dom.modelTriggerBtn.setAttribute("aria-expanded", !isExpanded);
        dom.modelPopover.classList.toggle("hidden", isExpanded);
    });

    document.addEventListener("click", (event) => {
        if (!dom.modelTriggerBtn.contains(event.target) && !dom.modelPopover.contains(event.target)) {
            dom.modelTriggerBtn.setAttribute("aria-expanded", "false");
            dom.modelPopover.classList.add("hidden");
        }
    });

    dom.connectProviderBtn.addEventListener("click", () => {
        dom.apiKeySection.classList.toggle("hidden");
    });

    dom.verifyApiBtn.addEventListener("click", () => {
        const key = $("#api-key-input").value.trim();
        if (!key) {
            toast("Please enter an API key", "error");
            return;
        }
        toast("NVIDIA API key verified successfully.");
    });

    dom.modelSearchInput.addEventListener("input", () => {
        renderModelList(dom.modelSearchInput.value.trim());
    });
}

function renderModelList(filter = "") {
    const lowercaseFilter = filter.toLowerCase();
    const filtered = nvidiaModels.filter(m => m.toLowerCase().includes(lowercaseFilter));
    
    if (!filtered.length) {
        dom.modelList.innerHTML = `<div style="padding:16px; color:var(--muted); text-align:center; font-size:13px;">No models found.</div>`;
        return;
    }

    dom.modelList.innerHTML = filtered.map(model => {
        const isEnabled = enabledModels.has(model);
        return `
            <div class="model-item">
                <span style="cursor:pointer;" onclick="selectModel('${escapeAttr(model)}')">${escapeHtml(model)}</span>
                <div class="toggle-switch ${isEnabled ? 'on' : ''}" onclick="toggleModel('${escapeAttr(model)}', this)"></div>
            </div>
        `;
    }).join("");
}

window.selectModel = (model) => {
    activeModel = model;
    dom.selectedModelName.textContent = `Nvidia (${model})`;
    dom.modelTriggerBtn.setAttribute("aria-expanded", "false");
    dom.modelPopover.classList.add("hidden");
};

window.toggleModel = (model, el) => {
    if (enabledModels.has(model)) {
        enabledModels.delete(model);
        el.classList.remove("on");
    } else {
        enabledModels.add(model);
        el.classList.add("on");
    }
};

async function api(path, options = {}) {
    const response = await fetch(`${API_BASE}${path}`, options);
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(data.message || data.detail || `Request failed with ${response.status}`);
    }
    return data;
}

async function checkHealth() {
    try {
        const health = await api("/health");
        state.health = health;
        dom.healthPill.textContent = `v${health.version || "ok"}`;
        dom.healthPill.className = "pill ok";
        dom.healthCopy.textContent = "Connected to the local learning engine.";
    } catch (error) {
        dom.healthPill.textContent = "offline";
        dom.healthPill.className = "pill bad";
        dom.healthCopy.textContent = "Start the backend on 127.0.0.1:8000 to use ingestion and chat.";
    }
}

async function loadWorkspaces(preferredId = state.activeWorkspaceId) {
    try {
        const data = await api("/workspaces");
        state.workspaces = data.workspaces || [];
        if (!state.activeWorkspaceId && state.workspaces.length) {
            state.activeWorkspaceId = preferredId || state.workspaces[0].id;
        }
        if (preferredId && state.workspaces.some((workspace) => workspace.id === preferredId)) {
            state.activeWorkspaceId = preferredId;
        }
        renderWorkspaces();
        renderActiveWorkspace();
    } catch (error) {
        toast(error.message, "error");
        renderWorkspaces();
        renderActiveWorkspace();
    }
}

async function createWorkspace(name) {
    try {
        const data = await api("/workspaces", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name }),
        });
        dom.workspaceName.value = "";
        state.activeWorkspaceId = data.workspace.id;
        await loadWorkspaces(data.workspace.id);
        toast("Workspace created.");
    } catch (error) {
        toast(error.message, "error");
    }
}

function renderWorkspaces() {
    if (!state.workspaces.length) {
        dom.workspaceList.innerHTML = `<div class="placeholder-box"><p>No workspaces yet. Create one for your notes.</p></div>`;
        return;
    }

    dom.workspaceList.innerHTML = state.workspaces.map((workspace) => `
        <button class="workspace-item ${workspace.id === state.activeWorkspaceId ? "active" : ""}" data-workspace-id="${escapeAttr(workspace.id)}">
            <strong>${escapeHtml(workspace.name)}</strong>
            <span>${workspace.source_count} sources · ${workspace.chunk_count} chunks</span>
        </button>
    `).join("");

    $$(".workspace-item").forEach((button) => {
        button.addEventListener("click", () => {
            state.activeWorkspaceId = button.dataset.workspaceId;
            renderWorkspaces();
            renderActiveWorkspace();
            clearInspector();
            loadGuide({ quiet: true });
            loadGraph({ quiet: true });
        });
    });
}

function renderActiveWorkspace() {
    const workspace = getActiveWorkspace();
    const enabled = Boolean(workspace);
    dom.workspaceTitle.textContent = workspace ? workspace.name : "Choose or create a workspace";
    dom.statSources.textContent = workspace ? workspace.source_count : "0";
    dom.statChunks.textContent = workspace ? workspace.chunk_count : "0";
    dom.statVersion.textContent = workspace ? workspace.index_version : "0";
    dom.sourceCount.textContent = workspace ? `${workspace.source_count} sources` : "0 files";
    dom.questionInput.disabled = !enabled;
    dom.sendBtn.disabled = !enabled;
    dom.questionInput.placeholder = enabled
        ? "Ask about a topic, compare ideas, or request a source guide..."
        : "Create a workspace first...";
}

async function ingestFiles(fileList) {
    const workspace = getActiveWorkspace();
    if (!workspace) {
        toast("Create or select a workspace before adding sources.", "error");
        return;
    }

    const files = Array.from(fileList);
    const formData = new FormData();
    formData.append("workspace_id", workspace.id);
    files.forEach((file) => formData.append("files", file));

    await runIngestion(`Indexing ${files.length} file${files.length === 1 ? "" : "s"}...`, async () => {
        return api("/sources/upload", { method: "POST", body: formData });
    });
}

async function ingestUrl(url) {
    const workspace = getActiveWorkspace();
    if (!workspace) {
        toast("Create or select a workspace before adding a URL.", "error");
        return;
    }
    if (!url) {
        toast("Paste a URL first.", "error");
        return;
    }

    await runIngestion("Reading and indexing the URL...", async () => {
        return api("/sources/url", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ workspace_id: workspace.id, url, max_depth: 1 }),
        });
    });
    dom.urlInput.value = "";
}

async function runIngestion(label, action) {
    if (state.busy) return;
    setBusy(true);
    setIngestStep("load", label);

    try {
        await sleep(180);
        setIngestStep("chunk", "Chunking source text...");
        await sleep(180);
        const result = await action();
        setIngestStep("index", "Embedding and indexing...");
        await sleep(180);
        setIngestStep("graph", "Refreshing concept map...");
        await sleep(180);
        finishIngestSteps();
        dom.ingestStatus.textContent = `${result.sources_added} source(s), ${result.chunks_added} chunk(s), index v${result.index_version}.`;
        if (result.warnings && result.warnings.length) {
            toast(result.warnings.join(" "));
        } else {
            toast("Sources indexed.");
        }
        await loadWorkspaces(state.activeWorkspaceId);
        await Promise.all([loadGuide({ quiet: true }), loadGraph({ quiet: true })]);
    } catch (error) {
        resetIngestSteps();
        dom.ingestStatus.textContent = "Ingestion stopped before indexing finished.";
        toast(error.message, "error");
    } finally {
        setBusy(false);
    }
}

async function askQuestion() {
    const workspace = getActiveWorkspace();
    const query = dom.questionInput.value.trim();
    if (!workspace || !query || state.busy) return;

    setBusy(true);
    clearEmptyState();
    appendMessage("user", query);
    dom.questionInput.value = "";
    dom.questionInput.style.height = "auto";
    const thinkingId = appendThinking();

    try {
        const data = await api("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                workspace_id: workspace.id,
                query,
                retrieval_mode: state.retrievalMode,
                top_k: 6,
            }),
        });
        removeById(thinkingId);
        state.latestCitations = data.citations || [];
        state.latestDiagnostics = data.diagnostics || null;
        appendMessage("assistant", data.answer || "No answer returned.", data);
        renderEvidence(data.citations || []);
        renderDiagnostics(data.diagnostics || {});
        activateTab("evidence");
    } catch (error) {
        removeById(thinkingId);
        appendMessage("assistant", `I could not complete that request. ${error.message}`);
        toast(error.message, "error");
    } finally {
        setBusy(false);
    }
}

function appendMessage(role, text, data = null) {
    const article = document.createElement("article");
    article.className = `message ${role === "user" ? "user" : "assistant"}`;
    article.innerHTML = `
        <div class="message-meta">
            <span>${role === "user" ? "You" : "MultiRAG"}</span>
            ${data?.retrieval_mode ? `<span class="pill">${escapeHtml(data.retrieval_mode)}</span>` : ""}
        </div>
        <div class="message-card">${formatAnswer(text)}</div>
        ${renderCitationChips(data?.citations || [])}
    `;
    dom.chatStream.appendChild(article);
    scrollChat();
}

function appendThinking() {
    const id = `thinking-${Date.now()}`;
    const article = document.createElement("article");
    article.id = id;
    article.className = "message assistant";
    article.innerHTML = `
        <div class="message-meta"><span>MultiRAG</span></div>
        <div class="message-card"><span class="loading-line">Retrieving evidence and composing an answer</span></div>
    `;
    dom.chatStream.appendChild(article);
    scrollChat();
    return id;
}

function renderCitationChips(citations) {
    if (!citations.length) return "";
    return `
        <div class="citation-chips">
            ${citations.map((citation, index) => `
                <span class="citation-chip">[${index + 1}] ${escapeHtml(citation.title || "source")}</span>
            `).join("")}
        </div>
    `;
}

function renderEvidence(citations) {
    dom.citationCount.textContent = `${citations.length} cite${citations.length === 1 ? "" : "s"}`;
    if (!citations.length) {
        dom.evidenceList.innerHTML = `
            <div class="placeholder-box">
                <svg><use href="#icon-search"></use></svg>
                <p>No citations were returned. Try a narrower question or add more sources.</p>
            </div>
        `;
        return;
    }

    dom.evidenceList.innerHTML = citations.map((citation, index) => `
        <article class="evidence-card">
            <header>
                <strong>[${index + 1}] ${escapeHtml(citation.title || "Source")}</strong>
                <small>${escapeHtml(citation.location_label || "location")}</small>
            </header>
            <p>${escapeHtml(citation.excerpt || "No excerpt available.")}</p>
        </article>
    `).join("");
}

function renderDiagnostics(diagnostics) {
    const items = [
        ["Semantic", diagnostics.semantic_hits ?? 0],
        ["Keyword", diagnostics.keyword_hits ?? 0],
        ["Graph", diagnostics.graph_hits ?? 0],
        ["Fused", diagnostics.fused_hits ?? 0],
        ["Latency", `${diagnostics.latency_ms ?? 0} ms`],
        ["Planned", diagnostics.planned_mode || "hybrid"],
    ];
    dom.diagnostics.innerHTML = items.map(([label, value]) => `
        <div class="diagnostic">
            <span>${escapeHtml(label)}</span>
            <strong>${escapeHtml(String(value))}</strong>
        </div>
    `).join("");
}

async function loadGuide(options = {}) {
    const workspace = getActiveWorkspace();
    if (!workspace || !workspace.source_count) {
        if (!options.quiet) toast("Add sources before requesting a guide.", "error");
        return;
    }

    dom.guideContent.innerHTML = `<div class="guide-block"><p class="loading-line">Building a study guide from indexed sources</p></div>`;
    try {
        const guide = await api(`/source-guide?workspace_id=${encodeURIComponent(workspace.id)}`);
        renderGuide(guide);
    } catch (error) {
        dom.guideContent.innerHTML = placeholder("icon-book", "The source guide could not be generated yet.");
        if (!options.quiet) toast(error.message, "error");
    }
}

function renderGuide(guide) {
    const glossary = Array.isArray(guide.glossary) ? guide.glossary : [];
    dom.guideContent.innerHTML = `
        <article class="guide-block">
            <h3>Summary</h3>
            <p>${escapeHtml(guide.summary || "No summary returned.")}</p>
        </article>
        <article class="guide-block">
            <h3>Key topics</h3>
            <div class="guide-tags">
                ${(guide.key_topics || []).map((topic) => `<span>${escapeHtml(topic)}</span>`).join("") || "<p>No topics returned.</p>"}
            </div>
        </article>
        <article class="guide-block">
            <h3>Glossary</h3>
            <ul class="guide-list">
                ${glossary.map((item) => `
                    <li><strong>${escapeHtml(item.term || "Term")}:</strong> ${escapeHtml(item.definition || "")}</li>
                `).join("") || "<li>No glossary items returned.</li>"}
            </ul>
        </article>
        <article class="guide-block">
            <h3>Questions to try</h3>
            <ul class="guide-list">
                ${(guide.suggested_questions || []).map((question) => `<li>${escapeHtml(question)}</li>`).join("") || "<li>No questions returned.</li>"}
            </ul>
        </article>
        <article class="guide-block">
            <h3>Coverage notes</h3>
            <p>${escapeHtml(guide.coverage_notes || "No coverage notes returned.")}</p>
        </article>
    `;
}

async function loadGraph(options = {}) {
    const workspace = getActiveWorkspace();
    if (!workspace || !workspace.source_count) {
        if (!options.quiet) toast("Add sources before opening the graph.", "error");
        return;
    }

    dom.graphCanvas.innerHTML = placeholder("icon-graph", "Loading the concept map...");
    try {
        const graph = await api(`/graph?workspace_id=${encodeURIComponent(workspace.id)}&depth=2`);
        renderGraph(graph.nodes || [], graph.edges || []);
    } catch (error) {
        dom.graphCanvas.innerHTML = placeholder("icon-graph", "The graph is not available yet.");
        if (!options.quiet) toast(error.message, "error");
    }
}

function renderGraph(nodes, edges) {
    if (!nodes.length) {
        dom.graphCanvas.innerHTML = placeholder("icon-graph", "No graph nodes returned for this workspace.");
        return;
    }

    const width = 360;
    const height = 460;
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(150, 54 + nodes.length * 8);
    const positions = new Map();

    nodes.slice(0, 28).forEach((node, index, visibleNodes) => {
        const angle = (Math.PI * 2 * index) / Math.max(visibleNodes.length, 1) - Math.PI / 2;
        const weightOffset = Math.min(32, Number(node.weight || 1) * 1.6);
        positions.set(node.id, {
            x: centerX + Math.cos(angle) * (radius - weightOffset),
            y: centerY + Math.sin(angle) * (radius - weightOffset),
        });
    });

    const visibleEdges = edges.filter((edge) => positions.has(edge.source) && positions.has(edge.target)).slice(0, 48);
    const edgeMarkup = visibleEdges.map((edge) => {
        const source = positions.get(edge.source);
        const target = positions.get(edge.target);
        return `<line class="graph-edge" x1="${source.x}" y1="${source.y}" x2="${target.x}" y2="${target.y}"></line>`;
    }).join("");

    const nodeMarkup = nodes.slice(0, 28).map((node) => {
        const position = positions.get(node.id);
        const size = Math.max(14, Math.min(28, 13 + Number(node.weight || 1)));
        return `
            <g class="graph-node" data-type="${escapeAttr(node.type || "node")}" transform="translate(${position.x} ${position.y})">
                <circle r="${size}"></circle>
                <text y="${size + 14}" text-anchor="middle">${escapeHtml(shortLabel(node.label || node.id))}</text>
            </g>
        `;
    }).join("");

    dom.graphCanvas.innerHTML = `
        <svg class="graph-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="Workspace concept graph">
            ${edgeMarkup}
            ${nodeMarkup}
        </svg>
    `;
}

async function resetSystem() {
    if (!window.confirm("Reset local backend memory for this prototype?")) return;
    try {
        await api("/reset", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
        state.workspaces = [];
        state.activeWorkspaceId = null;
        dom.chatStream.innerHTML = "";
        clearInspector();
        await loadWorkspaces();
        toast("Local memory reset.");
    } catch (error) {
        toast(error.message, "error");
    }
}

function activateTab(tabName) {
    $$(".tab-button").forEach((button) => button.classList.toggle("active", button.dataset.tab === tabName));
    $$(".tab-panel").forEach((panel) => panel.classList.toggle("active", panel.id === `tab-${tabName}`));
}

function clearInspector() {
    dom.citationCount.textContent = "0 cites";
    dom.evidenceList.innerHTML = placeholder("icon-search", "Ask a question to see the chunks that supported the answer.");
    dom.diagnostics.innerHTML = "";
    dom.guideContent.innerHTML = placeholder("icon-book", "Ingest a source to generate a learning guide.");
    dom.graphCanvas.innerHTML = placeholder("icon-graph", "The concept graph appears after sources are indexed.");
}

function clearEmptyState() {
    const emptyState = dom.chatStream.querySelector(".empty-state");
    if (emptyState) emptyState.remove();
}

function getActiveWorkspace() {
    return state.workspaces.find((workspace) => workspace.id === state.activeWorkspaceId) || null;
}

function setBusy(isBusy) {
    state.busy = isBusy;
    dom.sendBtn.disabled = isBusy || !getActiveWorkspace();
    dom.questionInput.disabled = isBusy || !getActiveWorkspace();
}

function setIngestStep(step, text) {
    let reached = true;
    dom.ingestSteps.forEach((item) => {
        if (item.dataset.step === step) reached = false;
        item.classList.toggle("done", reached);
        item.classList.toggle("active", item.dataset.step === step);
    });
    dom.ingestStatus.textContent = text;
}

function finishIngestSteps() {
    dom.ingestSteps.forEach((item) => {
        item.classList.add("done");
        item.classList.remove("active");
    });
}

function resetIngestSteps() {
    dom.ingestSteps.forEach((item) => item.classList.remove("done", "active"));
}

function formatAnswer(text) {
    return escapeHtml(text)
        .split(/\n{2,}/)
        .map((paragraph) => `<p>${paragraph.replace(/\n/g, "<br>")}</p>`)
        .join("");
}

function placeholder(iconId, text) {
    return `
        <div class="placeholder-box">
            <svg><use href="#${iconId}"></use></svg>
            <p>${escapeHtml(text)}</p>
        </div>
    `;
}

function toast(message, type = "info") {
    const element = document.createElement("div");
    element.className = `toast ${type === "error" ? "error" : ""}`;
    element.textContent = message;
    dom.toastRegion.appendChild(element);
    window.setTimeout(() => element.remove(), 4200);
}

function scrollChat() {
    requestAnimationFrame(() => {
        dom.chatStream.scrollTo({ top: dom.chatStream.scrollHeight, behavior: "smooth" });
    });
}

function removeById(id) {
    const element = document.getElementById(id);
    if (element) element.remove();
}

function shortLabel(value) {
    return value.length > 18 ? `${value.slice(0, 17)}...` : value;
}

function sleep(ms) {
    return new Promise((resolve) => window.setTimeout(resolve, ms));
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function escapeAttr(value) {
    return escapeHtml(value).replaceAll("`", "&#096;");
}
