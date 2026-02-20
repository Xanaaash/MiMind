const HOTLINES = [
  "US/Canada 988 Suicide & Crisis Lifeline: call/text 988",
  "中国心理援助热线示例: 800-810-1117",
  "若有即时危险，请立即联系当地紧急服务。",
];

const BASELINE_RESPONSES = {
  phq9: Array(9).fill(0),
  gad7: Array(7).fill(0),
  pss10: Array(10).fill(0),
  cssrs: { q1: false, q2: false, q3: false, q4: false, q5: false, q6: false },
};

const state = {
  apiBase: "",
  isAuthenticated: false,
  activeModule: "home",
  authConfig: null,
  demoUserId: "",
  demoUserReady: false,
  demoAssessmentReady: false,
  scaleCatalog: null,
  selectedScaleId: "",
  selectedScale: null,
  scaleAnswers: {},
  scalePage: 0,
  testsCatalog: null,
  selectedTestId: "",
  selectedTest: null,
  testQuestionAnswers: {},
  coachSessionId: "",
  audioTracks: [],
  meditations: [],
};

const nodes = {
  globalAlert: document.getElementById("globalAlert"),
  authGate: document.getElementById("authGate"),
  adminApp: document.getElementById("adminApp"),
  apiBase: document.getElementById("apiBase"),
  loginForm: document.getElementById("loginForm"),
  loginUsername: document.getElementById("loginUsername"),
  loginPassword: document.getElementById("loginPassword"),
  loginError: document.getElementById("loginError"),
  logoutBtn: document.getElementById("logoutBtn"),
  moduleNav: document.getElementById("moduleNav"),
  jumpButtons: document.querySelectorAll(".jump-btn"),
  hotlineList: document.getElementById("hotlineList"),
  activityLog: document.getElementById("activityLog"),
  demoUserId: document.getElementById("demoUserId"),

  loadScaleCatalogBtn: document.getElementById("loadScaleCatalogBtn"),
  scaleCatalog: document.getElementById("scaleCatalog"),
  scaleWorkspace: document.getElementById("scaleWorkspace"),
  scaleTitle: document.getElementById("scaleTitle"),
  scaleProgress: document.getElementById("scaleProgress"),
  scaleForm: document.getElementById("scaleForm"),
  scalePrevBtn: document.getElementById("scalePrevBtn"),
  scaleNextBtn: document.getElementById("scaleNextBtn"),
  scaleSubmitBtn: document.getElementById("scaleSubmitBtn"),
  scaleResult: document.getElementById("scaleResult"),

  loadTestsCatalogBtn: document.getElementById("loadTestsCatalogBtn"),
  testsCatalog: document.getElementById("testsCatalog"),
  testWorkspace: document.getElementById("testWorkspace"),
  testTitle: document.getElementById("testTitle"),
  testForm: document.getElementById("testForm"),
  testSubmitBtn: document.getElementById("testSubmitBtn"),
  testResult: document.getElementById("testResult"),

  loadToolLibraryBtn: document.getElementById("loadToolLibraryBtn"),
  audioTrack: document.getElementById("audioTrack"),
  audioMinutes: document.getElementById("audioMinutes"),
  startAudioBtn: document.getElementById("startAudioBtn"),
  breathingCycles: document.getElementById("breathingCycles"),
  completeBreathingBtn: document.getElementById("completeBreathingBtn"),
  meditationId: document.getElementById("meditationId"),
  startMeditationBtn: document.getElementById("startMeditationBtn"),

  journalForm: document.getElementById("journalForm"),
  journalMood: document.getElementById("journalMood"),
  journalEnergy: document.getElementById("journalEnergy"),
  energyValue: document.getElementById("energyValue"),
  journalNote: document.getElementById("journalNote"),
  loadTrendBtn: document.getElementById("loadTrendBtn"),
  trendView: document.getElementById("trendView"),

  coachStyle: document.getElementById("coachStyle"),
  coachSubscription: document.getElementById("coachSubscription"),
  startCoachBtn: document.getElementById("startCoachBtn"),
  endCoachBtn: document.getElementById("endCoachBtn"),
  coachForm: document.getElementById("coachForm"),
  coachMessage: document.getElementById("coachMessage"),
  coachReply: document.getElementById("coachReply"),

  crisisBanner: document.getElementById("crisisBanner"),

  checkAdminUsersBtn: document.getElementById("checkAdminUsersBtn"),
  adminUsersResult: document.getElementById("adminUsersResult"),
};

function defaultApiBase() {
  if ((window.location.protocol === "http:" || window.location.protocol === "https:") && window.location.host) {
    return window.location.origin;
  }
  return "http://127.0.0.1:8000";
}

function normalizeBase(base) {
  return String(base || "").trim().replace(/\/$/, "");
}

function showGlobalAlert(message) {
  nodes.globalAlert.textContent = message;
  nodes.globalAlert.classList.remove("hidden");
}

function hideGlobalAlert() {
  nodes.globalAlert.classList.add("hidden");
  nodes.globalAlert.textContent = "";
}

function logActivity(title, payload, isError = false) {
  const li = document.createElement("li");
  const stamp = new Date().toLocaleTimeString();
  li.innerHTML = `<strong>[${stamp}] ${title}</strong><pre>${JSON.stringify(payload, null, 2)}</pre>`;
  if (isError) {
    li.style.background = "#fff0f0";
    li.style.borderColor = "#e2aaaa";
  }
  nodes.activityLog.prepend(li);
}

function setAuthState(authenticated) {
  state.isAuthenticated = authenticated;
  if (authenticated) {
    nodes.authGate.classList.add("hidden");
    nodes.adminApp.classList.remove("hidden");
  } else {
    nodes.authGate.classList.remove("hidden");
    nodes.adminApp.classList.add("hidden");
    state.coachSessionId = "";
  }
}

function switchModule(moduleId) {
  state.activeModule = moduleId;
  document.querySelectorAll(".nav-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.module === moduleId);
  });
  document.querySelectorAll("[data-module-panel]").forEach((panel) => {
    panel.classList.toggle("active", panel.dataset.modulePanel === moduleId);
  });
}

async function api(path, options = {}, requireAuth = true) {
  state.apiBase = normalizeBase(nodes.apiBase.value);
  if (!state.apiBase) {
    throw new Error("API base is required");
  }

  const requestInit = {
    method: options.method || "GET",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    credentials: "include",
  };

  if (options.body !== undefined) {
    requestInit.body = JSON.stringify(options.body);
  }

  let response;
  try {
    response = await fetch(`${state.apiBase}${path}`, requestInit);
  } catch (error) {
    showGlobalAlert(`网络错误: ${String(error)}`);
    throw new Error(`Network error: ${String(error)}`);
  }

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = body.detail || body.error || "Request failed";
    if (response.status === 401 && requireAuth) {
      setAuthState(false);
    }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  hideGlobalAlert();
  return body;
}

function renderHotlines() {
  nodes.hotlineList.innerHTML = "";
  HOTLINES.forEach((line) => {
    const li = document.createElement("li");
    li.textContent = line;
    nodes.hotlineList.appendChild(li);
  });
}

async function restoreSession() {
  try {
    const data = await api("/api/admin/session", {}, false);
    state.authConfig = data.auth_config || null;
    setAuthState(true);
    logActivity("session restored", data);
    return true;
  } catch {
    setAuthState(false);
    return false;
  }
}

async function ensureDemoUser() {
  if (state.demoUserReady && state.demoUserId) {
    return state.demoUserId;
  }

  const payload = {
    email: `demo-${Date.now()}@example.com`,
    locale: "zh-CN",
    policy_version: "2026.02",
  };
  const data = await api("/api/register", { method: "POST", body: payload });
  state.demoUserId = data.user_id;
  state.demoUserReady = true;
  nodes.demoUserId.textContent = state.demoUserId;
  logActivity("demo user created", data);
  return state.demoUserId;
}

async function ensureDemoAssessment() {
  const userId = await ensureDemoUser();
  if (state.demoAssessmentReady) {
    return;
  }

  const data = await api(`/api/assessment/${userId}`, {
    method: "POST",
    body: {
      responses: BASELINE_RESPONSES,
    },
  });
  state.demoAssessmentReady = true;
  logActivity("demo baseline assessment submitted", data);
}

function inferNumericRange(answerRange) {
  const text = String(answerRange || "").toLowerCase();
  if (text.includes("-100 to 100")) {
    return { min: -100, max: 100, step: 1 };
  }
  if (text.includes("13 to 90")) {
    return { min: 13, max: 90, step: 1 };
  }
  return { min: 0, max: 100, step: 1 };
}

function scalePageSize(scaleId) {
  return scaleId === "scl90" ? 15 : 200;
}

function scaleQuestions() {
  return state.selectedScale?.question_bank?.questions || [];
}

function scaleAnswerLabels() {
  const labels = state.selectedScale?.question_bank?.answer_labels;
  if (!labels) {
    return null;
  }
  return labels["zh-CN"] || labels["en-US"] || null;
}

function renderScaleCatalog() {
  nodes.scaleCatalog.innerHTML = "";
  if (!state.scaleCatalog) {
    return;
  }

  Object.entries(state.scaleCatalog).forEach(([scaleId, item]) => {
    const card = document.createElement("article");
    card.className = "catalog-item";
    card.innerHTML = `
      <h4>${scaleId.toUpperCase()}</h4>
      <p>${item.display_name}</p>
      <p>题数: ${item.item_count}</p>
      <button data-scale-id="${scaleId}" type="button">开始</button>
    `;
    nodes.scaleCatalog.appendChild(card);
  });

  nodes.scaleCatalog.querySelectorAll("button[data-scale-id]").forEach((btn) => {
    btn.addEventListener("click", () => startScale(btn.dataset.scaleId));
  });
}

function startScale(scaleId) {
  const item = state.scaleCatalog[scaleId];
  state.selectedScaleId = scaleId;
  state.selectedScale = item;
  state.scalePage = 0;

  const questions = item.question_bank.questions;
  questions.forEach((q) => {
    if (!(q.question_id in state.scaleAnswers)) {
      state.scaleAnswers[q.question_id] = scaleId === "cssrs" ? false : 0;
    }
  });

  nodes.scaleWorkspace.classList.remove("hidden");
  nodes.scaleTitle.textContent = `${scaleId.toUpperCase()} - ${item.display_name}`;
  renderScalePage();
  switchModule("clinical_scales");
}

function renderScalePage() {
  if (!state.selectedScale) {
    return;
  }

  const questions = scaleQuestions();
  const pageSize = scalePageSize(state.selectedScaleId);
  const start = state.scalePage * pageSize;
  const end = Math.min(start + pageSize, questions.length);
  const pageQuestions = questions.slice(start, end);
  const labels = scaleAnswerLabels();

  nodes.scaleProgress.textContent = `题目 ${start + 1}-${end} / ${questions.length}`;
  nodes.scaleForm.innerHTML = "";

  pageQuestions.forEach((q, index) => {
    const wrap = document.createElement("div");
    wrap.className = "question";

    const qText = q.text?.["zh-CN"] || q.text?.["en-US"] || q.question_id;
    const qNo = start + index + 1;

    if (state.selectedScaleId === "cssrs") {
      wrap.innerHTML = `
        <label>
          <strong>${qNo}. ${qText}</strong>
          <select data-scale-question-id="${q.question_id}">
            <option value="false">否</option>
            <option value="true">是</option>
          </select>
        </label>
      `;
      const select = wrap.querySelector("select");
      select.value = String(Boolean(state.scaleAnswers[q.question_id]));
      select.addEventListener("change", () => {
        state.scaleAnswers[q.question_id] = select.value === "true";
      });
    } else {
      const options = (labels || []).map((label, value) => `<option value="${value}">${value}: ${label}</option>`).join("");
      wrap.innerHTML = `
        <label>
          <strong>${qNo}. ${qText}</strong>
          <select data-scale-question-id="${q.question_id}">${options}</select>
        </label>
      `;
      const select = wrap.querySelector("select");
      select.value = String(Number(state.scaleAnswers[q.question_id] ?? 0));
      select.addEventListener("change", () => {
        state.scaleAnswers[q.question_id] = Number(select.value);
      });
    }

    nodes.scaleForm.appendChild(wrap);
  });

  nodes.scalePrevBtn.disabled = state.scalePage === 0;
  nodes.scaleNextBtn.disabled = end >= questions.length;
}

function scalePayload() {
  const questions = scaleQuestions();
  if (state.selectedScaleId === "cssrs") {
    const answers = {};
    questions.forEach((q) => {
      answers[q.question_id] = Boolean(state.scaleAnswers[q.question_id]);
    });
    return { scale_id: state.selectedScaleId, answers };
  }

  const answers = questions.map((q) => Number(state.scaleAnswers[q.question_id] ?? 0));
  return { scale_id: state.selectedScaleId, answers };
}

async function submitScale() {
  if (!state.selectedScaleId) {
    throw new Error("请先选择量表");
  }
  const payload = scalePayload();
  const data = await api("/api/scales/score", { method: "POST", body: payload });
  nodes.scaleResult.textContent = JSON.stringify(data, null, 2);
  logActivity(`scale scored: ${state.selectedScaleId}`, data);
}

function renderTestsCatalog() {
  nodes.testsCatalog.innerHTML = "";
  if (!state.testsCatalog) {
    return;
  }

  Object.entries(state.testsCatalog).forEach(([testId, item]) => {
    const card = document.createElement("article");
    card.className = "catalog-item";
    card.innerHTML = `
      <h4>${testId}</h4>
      <p>${item.display_name}</p>
      <p>维度: ${item.input_dimension_count}</p>
      <button data-test-id="${testId}" type="button">开始</button>
    `;
    nodes.testsCatalog.appendChild(card);
  });

  nodes.testsCatalog.querySelectorAll("button[data-test-id]").forEach((btn) => {
    btn.addEventListener("click", () => startTest(btn.dataset.testId));
  });
}

async function startTest(testId) {
  const data = await api(`/api/tests/catalog/${testId}`);
  state.selectedTestId = testId;
  state.selectedTest = data;
  state.testQuestionAnswers = {};

  nodes.testWorkspace.classList.remove("hidden");
  nodes.testTitle.textContent = `${testId} - ${data.display_name}`;

  const range = inferNumericRange(data.answer_range);
  nodes.testForm.innerHTML = "";
  data.question_bank.questions.forEach((q, idx) => {
    const text = q.text?.["zh-CN"] || q.text?.["en-US"] || q.question_id;
    const initial = q.dimension_key === "chronological_age" ? 25 : Math.round((range.min + range.max) / 2);
    state.testQuestionAnswers[q.question_id] = initial;

    const wrap = document.createElement("div");
    wrap.className = "question";
    wrap.innerHTML = `
      <label>
        <strong>${idx + 1}. ${text}</strong>
        <input data-test-question-id="${q.question_id}" type="range" min="${range.min}" max="${range.max}" step="${range.step}" value="${initial}" />
        <span id="test-value-${q.question_id}">${initial}</span>
      </label>
    `;
    nodes.testForm.appendChild(wrap);
  });

  nodes.testForm.querySelectorAll("input[data-test-question-id]").forEach((input) => {
    input.addEventListener("input", () => {
      const qid = input.dataset.testQuestionId;
      state.testQuestionAnswers[qid] = Number(input.value);
      const view = document.getElementById(`test-value-${qid}`);
      if (view) {
        view.textContent = String(input.value);
      }
    });
  });

  switchModule("interactive_tests");
}

function buildInteractiveAnswers() {
  const definition = state.selectedTest;
  const questions = definition.question_bank.questions;

  const sums = {};
  const counts = {};
  questions.forEach((q) => {
    const value = Number(state.testQuestionAnswers[q.question_id] ?? 0);
    const key = q.dimension_key;
    sums[key] = (sums[key] || 0) + value;
    counts[key] = (counts[key] || 0) + 1;
  });

  const answers = {};
  definition.required_answer_keys.forEach((key) => {
    if (counts[key]) {
      answers[key] = Math.round(sums[key] / counts[key]);
    } else {
      answers[key] = 0;
    }
  });
  return answers;
}

async function submitInteractiveTest() {
  if (!state.selectedTestId) {
    throw new Error("请先选择互动测试");
  }
  const userId = await ensureDemoUser();
  const answers = buildInteractiveAnswers();

  const data = await api(`/api/tests/${userId}/submit`, {
    method: "POST",
    body: {
      test_id: state.selectedTestId,
      answers,
    },
  });
  nodes.testResult.textContent = JSON.stringify(data, null, 2);
  logActivity(`interactive test submitted: ${state.selectedTestId}`, data);
}

async function loadToolLibraries() {
  const [audioData, meditationData] = await Promise.all([
    api("/api/tools/audio/library"),
    api("/api/tools/meditation/library"),
  ]);

  state.audioTracks = Object.entries(audioData).map(([trackId, value]) => ({ trackId, ...value }));
  state.meditations = Object.entries(meditationData).map(([meditationId, value]) => ({ meditationId, ...value }));

  nodes.audioTrack.innerHTML = state.audioTracks
    .map((item) => `<option value="${item.trackId}">${item.trackId} - ${item.name}</option>`)
    .join("");
  nodes.meditationId.innerHTML = state.meditations
    .map((item) => `<option value="${item.meditationId}">${item.meditationId} - ${item.name}</option>`)
    .join("");

  logActivity("tool libraries loaded", { audio_count: state.audioTracks.length, meditation_count: state.meditations.length });
}

function maybeShowCrisisBanner(payload) {
  const mode = payload.mode;
  if (mode !== "crisis" && mode !== "safety_pause") {
    nodes.crisisBanner.classList.add("hidden");
    nodes.crisisBanner.textContent = "";
    return;
  }

  const detection = payload.safety?.detection;
  const hotline = payload.safety?.hotline?.text || "";
  const message = payload.coach_message || payload.safety?.action?.message || "";
  nodes.crisisBanner.textContent = [message, detection ? `risk=${detection.level}` : "", hotline].filter(Boolean).join(" | ");
  nodes.crisisBanner.classList.remove("hidden");
}

function bindNavigation() {
  nodes.moduleNav.querySelectorAll(".nav-btn").forEach((btn) => {
    btn.addEventListener("click", () => switchModule(btn.dataset.module));
  });
  nodes.jumpButtons.forEach((btn) => {
    btn.addEventListener("click", () => switchModule(btn.dataset.jump));
  });
}

function bindEvents() {
  nodes.loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    nodes.loginError.classList.add("hidden");
    nodes.loginError.textContent = "";

    try {
      const login = await api(
        "/api/admin/login",
        {
          method: "POST",
          body: {
            username: nodes.loginUsername.value,
            password: nodes.loginPassword.value,
          },
        },
        false,
      );
      logActivity("admin login success", login);
      await restoreSession();
      switchModule("home");
      nodes.loginPassword.value = "";
    } catch (error) {
      nodes.loginError.textContent = error instanceof Error ? error.message : String(error);
      nodes.loginError.classList.remove("hidden");
      logActivity("admin login failed", { error: nodes.loginError.textContent }, true);
    }
  });

  nodes.logoutBtn.addEventListener("click", async () => {
    try {
      const data = await api("/api/admin/logout", { method: "POST" }, false);
      logActivity("admin logout", data);
    } finally {
      setAuthState(false);
    }
  });

  nodes.loadScaleCatalogBtn.addEventListener("click", async () => {
    try {
      const data = await api("/api/scales/catalog");
      state.scaleCatalog = data;
      renderScaleCatalog();
      logActivity("scale catalog loaded", { scale_count: Object.keys(data).length });
    } catch (error) {
      logActivity("scale catalog failed", { error: String(error) }, true);
    }
  });

  nodes.scalePrevBtn.addEventListener("click", () => {
    if (state.scalePage > 0) {
      state.scalePage -= 1;
      renderScalePage();
    }
  });

  nodes.scaleNextBtn.addEventListener("click", () => {
    const pageSize = scalePageSize(state.selectedScaleId);
    if ((state.scalePage + 1) * pageSize < scaleQuestions().length) {
      state.scalePage += 1;
      renderScalePage();
    }
  });

  nodes.scaleSubmitBtn.addEventListener("click", async () => {
    try {
      await submitScale();
    } catch (error) {
      logActivity("submit scale failed", { error: String(error) }, true);
    }
  });

  nodes.loadTestsCatalogBtn.addEventListener("click", async () => {
    try {
      const data = await api("/api/tests/catalog");
      state.testsCatalog = data;
      renderTestsCatalog();
      logActivity("tests catalog loaded", { test_count: Object.keys(data).length });
    } catch (error) {
      logActivity("tests catalog failed", { error: String(error) }, true);
    }
  });

  nodes.testSubmitBtn.addEventListener("click", async () => {
    try {
      await submitInteractiveTest();
    } catch (error) {
      logActivity("submit interactive test failed", { error: String(error) }, true);
    }
  });

  nodes.loadToolLibraryBtn.addEventListener("click", async () => {
    try {
      await loadToolLibraries();
    } catch (error) {
      logActivity("load tool library failed", { error: String(error) }, true);
    }
  });

  nodes.startAudioBtn.addEventListener("click", async () => {
    try {
      const userId = await ensureDemoUser();
      const data = await api(`/api/tools/audio/${userId}/start`, {
        method: "POST",
        body: {
          track_id: nodes.audioTrack.value,
          minutes: Number(nodes.audioMinutes.value),
        },
      });
      logActivity("audio started", data);
    } catch (error) {
      logActivity("audio start failed", { error: String(error) }, true);
    }
  });

  nodes.completeBreathingBtn.addEventListener("click", async () => {
    try {
      const userId = await ensureDemoUser();
      const data = await api(`/api/tools/breathing/${userId}/complete`, {
        method: "POST",
        body: { cycles: Number(nodes.breathingCycles.value) },
      });
      logActivity("breathing completed", data);
    } catch (error) {
      logActivity("breathing failed", { error: String(error) }, true);
    }
  });

  nodes.startMeditationBtn.addEventListener("click", async () => {
    try {
      const userId = await ensureDemoUser();
      const data = await api(`/api/tools/meditation/${userId}/start`, {
        method: "POST",
        body: { meditation_id: nodes.meditationId.value },
      });
      logActivity("meditation started", data);
    } catch (error) {
      logActivity("meditation failed", { error: String(error) }, true);
    }
  });

  nodes.journalEnergy.addEventListener("input", () => {
    nodes.energyValue.textContent = nodes.journalEnergy.value;
  });

  nodes.journalForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const userId = await ensureDemoUser();
      const data = await api(`/api/tools/journal/${userId}/entries`, {
        method: "POST",
        body: {
          mood: nodes.journalMood.value,
          energy: Number(nodes.journalEnergy.value),
          note: nodes.journalNote.value,
        },
      });
      logActivity("journal saved", data);
    } catch (error) {
      logActivity("journal save failed", { error: String(error) }, true);
    }
  });

  nodes.loadTrendBtn.addEventListener("click", async () => {
    try {
      const userId = await ensureDemoUser();
      const data = await api(`/api/tools/journal/${userId}/trend?days=7`);
      nodes.trendView.textContent = JSON.stringify(data, null, 2);
      logActivity("journal trend loaded", data);
    } catch (error) {
      logActivity("journal trend failed", { error: String(error) }, true);
    }
  });

  nodes.startCoachBtn.addEventListener("click", async () => {
    try {
      const userId = await ensureDemoUser();
      await ensureDemoAssessment();
      const data = await api(`/api/coach/${userId}/start`, {
        method: "POST",
        body: {
          style_id: nodes.coachStyle.value,
          subscription_active: nodes.coachSubscription.checked,
        },
      });
      state.coachSessionId = data.session?.session_id || "";
      nodes.coachReply.textContent = JSON.stringify(data, null, 2);
      maybeShowCrisisBanner({ mode: "coaching" });
      logActivity("coach session started", data);
    } catch (error) {
      logActivity("coach start failed", { error: String(error) }, true);
    }
  });

  nodes.coachForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      if (!state.coachSessionId) {
        throw new Error("请先开始会话");
      }
      const data = await api(`/api/coach/${state.coachSessionId}/chat`, {
        method: "POST",
        body: {
          user_message: nodes.coachMessage.value,
        },
      });
      nodes.coachReply.textContent = JSON.stringify(data, null, 2);
      maybeShowCrisisBanner(data);
      logActivity("coach chat", data);
      if (data.halted) {
        state.coachSessionId = "";
      }
    } catch (error) {
      logActivity("coach chat failed", { error: String(error) }, true);
    }
  });

  nodes.endCoachBtn.addEventListener("click", async () => {
    try {
      if (!state.coachSessionId) {
        throw new Error("当前没有活跃会话");
      }
      const data = await api(`/api/coach/${state.coachSessionId}/end`, { method: "POST" });
      state.coachSessionId = "";
      nodes.coachReply.textContent = JSON.stringify(data, null, 2);
      maybeShowCrisisBanner({ mode: "coaching" });
      logActivity("coach session ended", data);
    } catch (error) {
      logActivity("coach end failed", { error: String(error) }, true);
    }
  });

  nodes.checkAdminUsersBtn.addEventListener("click", async () => {
    try {
      const data = await api("/api/admin/users");
      nodes.adminUsersResult.textContent = JSON.stringify(data, null, 2);
      logActivity("admin users endpoint", data);
    } catch (error) {
      const content = { error: String(error), note: "Expected 501 not implemented in this phase." };
      nodes.adminUsersResult.textContent = JSON.stringify(content, null, 2);
      logActivity("admin users endpoint response", content, true);
    }
  });
}

async function init() {
  nodes.apiBase.value = defaultApiBase();
  state.apiBase = normalizeBase(nodes.apiBase.value);

  renderHotlines();
  bindNavigation();
  bindEvents();
  switchModule("home");

  const restored = await restoreSession();
  if (!restored) {
    setAuthState(false);
  }

  logActivity("frontend initialized", {
    apiBase: state.apiBase,
    auth_restored: restored,
    safety_boundary: "non-medical coaching only",
  });
}

init();
