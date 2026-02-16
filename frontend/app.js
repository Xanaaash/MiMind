const HOTLINES = [
  {
    locale: "en-US",
    title: "US/Canada 988 Suicide & Crisis Lifeline",
    action: "Call or text 988",
  },
  {
    locale: "zh-CN",
    title: "中国生命危机干预热线（示例）",
    action: "北京心理援助热线：800-810-1117",
  },
  {
    locale: "global",
    title: "Emergency services",
    action: "Call local emergency number immediately if there is immediate danger.",
  },
];

const TEXT = {
  zh: {
    "app.title": "温暖自我探索空间",
    "app.apiBase": "API 地址",
    "hero.kicker": "Constitution 对齐",
    "hero.title": "先被理解，再一起前进。",
    "hero.subtitle": "这里是心理教练产品，不是医疗诊疗服务。我们帮助你进行自我认知、情绪调节与成长练习。",
    "hero.pill1": "非医疗，不做诊断/处方",
    "hero.pill2": "风险优先，必要时暂停咨询",
    "hero.pill3": "中英双语，移动端可用",
    "onboarding.title": "1) 用户注册与基线测评",
    "onboarding.desc": "先注册，再一键提交低风险示例测评，获取分流结果。",
    "onboarding.locale": "语言偏好",
    "onboarding.register": "注册用户",
    "onboarding.userId": "当前 user_id",
    "onboarding.baseline": "提交基线测评示例",
    "tools.title": "2) 疗愈工具工作台",
    "tools.desc": "白噪音、呼吸练习、正念引导，支持快速体验。",
    "tools.load": "加载工具库",
    "tools.audio": "白噪音",
    "tools.minutes": "时长（分钟）",
    "tools.startAudio": "开始播放",
    "tools.cycles": "呼吸轮次",
    "tools.finishBreathing": "完成呼吸练习",
    "tools.meditation": "正念引导",
    "tools.startMeditation": "开始正念",
    "journal.title": "3) 情绪日记",
    "journal.desc": "记录当下情绪与能量，查看近 7 天趋势。",
    "journal.mood": "情绪标签",
    "journal.energy": "能量值 (0-10)",
    "journal.note": "笔记",
    "journal.notePlaceholder": "今天最明显的感受是什么？",
    "journal.save": "保存日记",
    "journal.trend": "加载 7 天趋势",
    "coach.title": "4) AI 心理教练",
    "coach.desc": "仅作心理教练陪伴，不提供临床诊断、药物与处方建议。",
    "coach.style": "风格",
    "coach.subscription": "模拟 coach 订阅有效",
    "coach.start": "开始会话",
    "coach.end": "结束会话",
    "coach.message": "消息",
    "coach.messagePlaceholder": "输入你想被倾听的一段内容...",
    "coach.send": "发送消息",
    "safety.title": "安全与求助资源",
    "safety.desc": "如果你正在经历紧急危险，请优先联系当地紧急服务或危机热线。以下号码为前端本地缓存示例。",
    "log.title": "活动日志",
    "log.desc": "展示前端对 API 的请求结果，便于开发调试。",
  },
  en: {
    "app.title": "A Warm Space For Self-Discovery",
    "app.apiBase": "API Base",
    "hero.kicker": "Constitution Aligned",
    "hero.title": "Feel understood first, then move forward.",
    "hero.subtitle": "This is a non-medical coaching product. It supports self-awareness, emotional regulation, and growth routines.",
    "hero.pill1": "Non-medical: no diagnosis or prescriptions",
    "hero.pill2": "Safety first: pause coaching on risk",
    "hero.pill3": "Bilingual and mobile friendly",
    "onboarding.title": "1) Registration And Baseline Assessment",
    "onboarding.desc": "Register first, then submit a low-risk sample assessment to get triage output.",
    "onboarding.locale": "Locale",
    "onboarding.register": "Register User",
    "onboarding.userId": "Current user_id",
    "onboarding.baseline": "Submit baseline sample",
    "tools.title": "2) Healing Tools Studio",
    "tools.desc": "White noise, breathing practice, and guided meditation in one place.",
    "tools.load": "Load libraries",
    "tools.audio": "White noise",
    "tools.minutes": "Minutes",
    "tools.startAudio": "Start audio",
    "tools.cycles": "Breathing cycles",
    "tools.finishBreathing": "Complete breathing",
    "tools.meditation": "Meditation",
    "tools.startMeditation": "Start meditation",
    "journal.title": "3) Mood Journal",
    "journal.desc": "Capture mood and energy, then inspect your 7-day trend.",
    "journal.mood": "Mood",
    "journal.energy": "Energy (0-10)",
    "journal.note": "Note",
    "journal.notePlaceholder": "What feeling stood out most today?",
    "journal.save": "Save entry",
    "journal.trend": "Load 7-day trend",
    "coach.title": "4) AI Coach",
    "coach.desc": "For psychological coaching only, not clinical diagnosis or medication advice.",
    "coach.style": "Style",
    "coach.subscription": "Simulate active coach subscription",
    "coach.start": "Start session",
    "coach.end": "End session",
    "coach.message": "Message",
    "coach.messagePlaceholder": "Type what you want to process right now...",
    "coach.send": "Send message",
    "safety.title": "Safety And Crisis Resources",
    "safety.desc": "If you are in immediate danger, contact local emergency services first. Numbers below are local-cache examples in UI.",
    "log.title": "Activity Log",
    "log.desc": "Shows frontend request results for easier prototype debugging.",
  },
};

const state = {
  lang: "zh",
  apiBase: "",
  userId: "",
  coachSessionId: "",
  audioTracks: [],
  meditations: [],
};

const nodes = {
  apiBase: document.getElementById("apiBase"),
  langToggle: document.getElementById("langToggle"),
  registerForm: document.getElementById("registerForm"),
  regEmail: document.getElementById("regEmail"),
  regLocale: document.getElementById("regLocale"),
  userId: document.getElementById("userId"),
  baselineAssessBtn: document.getElementById("baselineAssessBtn"),
  triageBadge: document.getElementById("triageBadge"),
  loadLibrariesBtn: document.getElementById("loadLibrariesBtn"),
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
  hotlineList: document.getElementById("hotlineList"),
  crisisBanner: document.getElementById("crisisBanner"),
  activityLog: document.getElementById("activityLog"),
};

function defaultApiBase() {
  const hasHttpOrigin = window.location.protocol === "http:" || window.location.protocol === "https:";
  if (hasHttpOrigin && window.location.host) {
    return window.location.origin;
  }
  return "http://127.0.0.1:8000";
}

function normalizeBase(base) {
  return String(base || "").trim().replace(/\/$/, "");
}

function setLang(nextLang) {
  state.lang = nextLang;
  document.documentElement.lang = nextLang === "zh" ? "zh-CN" : "en-US";
  nodes.langToggle.textContent = nextLang === "zh" ? "EN" : "中";

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    const value = TEXT[nextLang][key];
    if (value) {
      el.textContent = value;
    }
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    const key = el.getAttribute("data-i18n-placeholder");
    const value = TEXT[nextLang][key];
    if (value) {
      el.setAttribute("placeholder", value);
    }
  });
}

function renderHotlines() {
  nodes.hotlineList.innerHTML = "";
  HOTLINES.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = `${item.title}: ${item.action}`;
    nodes.hotlineList.appendChild(li);
  });
}

function appendLog(title, payload, type = "info") {
  const li = document.createElement("li");
  const stamp = new Date().toLocaleTimeString();
  li.innerHTML = `<strong>[${stamp}] ${title}</strong><pre>${JSON.stringify(payload, null, 2)}</pre>`;
  if (type === "error") {
    li.style.borderColor = "#e8abab";
    li.style.background = "#fff0f0";
  }
  nodes.activityLog.prepend(li);
}

function showError(context, error) {
  const message = error instanceof Error ? error.message : String(error);
  appendLog(`${context} failed`, { error: message }, "error");
}

function updateTriage(channel) {
  const tag = nodes.triageBadge;
  tag.className = "tag";
  if (channel === "green" || channel === "yellow" || channel === "red") {
    tag.classList.add(channel);
    tag.textContent = channel.toUpperCase();
    return;
  }
  tag.classList.add("neutral");
  tag.textContent = "-";
}

function ensureUser() {
  if (!state.userId) {
    throw new Error("Please register user first.");
  }
}

async function request(path, options = {}) {
  state.apiBase = normalizeBase(nodes.apiBase.value);
  if (!state.apiBase) {
    throw new Error("API base is required.");
  }

  const config = {
    method: options.method || "GET",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  };
  if (options.body !== undefined) {
    config.body = JSON.stringify(options.body);
  }

  let response;
  try {
    response = await fetch(`${state.apiBase}${path}`, config);
  } catch (error) {
    throw new Error(`Network error: ${String(error)}`);
  }

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = body.detail || body.error || "Request failed";
    throw new Error(message);
  }
  return body;
}

function maybeShowCrisisBanner(payload) {
  const mode = payload.mode;
  if (mode !== "crisis" && mode !== "safety_pause") {
    nodes.crisisBanner.classList.add("hidden");
    nodes.crisisBanner.textContent = "";
    return;
  }

  const detection = payload.safety?.detection;
  const hotlineText = payload.safety?.hotline?.text;
  const message = payload.coach_message || payload.safety?.action?.message || "";
  const summary = [message, detection ? `risk=${detection.level}` : "", hotlineText || ""].filter(Boolean).join(" | ");

  nodes.crisisBanner.classList.remove("hidden");
  nodes.crisisBanner.textContent = summary;
}

async function loadToolLibraries() {
  const [audioData, meditationData] = await Promise.all([
    request("/api/tools/audio/library"),
    request("/api/tools/meditation/library"),
  ]);

  state.audioTracks = Object.entries(audioData).map(([trackId, value]) => ({ trackId, ...value }));
  state.meditations = Object.entries(meditationData).map(([meditationId, value]) => ({
    meditationId,
    ...value,
  }));

  nodes.audioTrack.innerHTML = state.audioTracks
    .map((item) => `<option value="${item.trackId}">${item.trackId} - ${item.name}</option>`)
    .join("");
  nodes.meditationId.innerHTML = state.meditations
    .map((item) => `<option value="${item.meditationId}">${item.meditationId} - ${item.name}</option>`)
    .join("");

  appendLog("Loaded tool libraries", {
    audioTracks: state.audioTracks.length,
    meditations: state.meditations.length,
  });
}

function baselineResponses() {
  return {
    phq9: Array(9).fill(0),
    gad7: Array(7).fill(0),
    pss10: Array(10).fill(0),
    cssrs: [false, false, false, false, false],
  };
}

function bindEvents() {
  nodes.langToggle.addEventListener("click", () => {
    setLang(state.lang === "zh" ? "en" : "zh");
  });

  nodes.registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const payload = {
        email: nodes.regEmail.value,
        locale: nodes.regLocale.value,
        policy_version: "2026.02",
      };
      const data = await request("/api/register", { method: "POST", body: payload });
      state.userId = data.user_id;
      nodes.userId.textContent = data.user_id;
      appendLog("Registered user", data);
    } catch (error) {
      showError("register", error);
    }
  });

  nodes.baselineAssessBtn.addEventListener("click", async () => {
    try {
      ensureUser();
      const payload = { responses: baselineResponses() };
      const data = await request(`/api/assessment/${state.userId}`, {
        method: "POST",
        body: payload,
      });
      updateTriage(data.triage?.channel);
      appendLog("Submitted baseline assessment", data);
    } catch (error) {
      showError("assessment", error);
    }
  });

  nodes.loadLibrariesBtn.addEventListener("click", async () => {
    try {
      await loadToolLibraries();
    } catch (error) {
      showError("load libraries", error);
    }
  });

  nodes.startAudioBtn.addEventListener("click", async () => {
    try {
      ensureUser();
      const payload = {
        track_id: nodes.audioTrack.value,
        minutes: Number(nodes.audioMinutes.value),
      };
      const data = await request(`/api/tools/audio/${state.userId}/start`, {
        method: "POST",
        body: payload,
      });
      appendLog("Started audio", data);
    } catch (error) {
      showError("start audio", error);
    }
  });

  nodes.completeBreathingBtn.addEventListener("click", async () => {
    try {
      ensureUser();
      const payload = { cycles: Number(nodes.breathingCycles.value) };
      const data = await request(`/api/tools/breathing/${state.userId}/complete`, {
        method: "POST",
        body: payload,
      });
      appendLog("Completed breathing", data);
    } catch (error) {
      showError("breathing", error);
    }
  });

  nodes.startMeditationBtn.addEventListener("click", async () => {
    try {
      ensureUser();
      const payload = { meditation_id: nodes.meditationId.value };
      const data = await request(`/api/tools/meditation/${state.userId}/start`, {
        method: "POST",
        body: payload,
      });
      appendLog("Started meditation", data);
    } catch (error) {
      showError("meditation", error);
    }
  });

  nodes.journalEnergy.addEventListener("input", () => {
    nodes.energyValue.textContent = nodes.journalEnergy.value;
  });

  nodes.journalForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      ensureUser();
      const payload = {
        mood: nodes.journalMood.value,
        energy: Number(nodes.journalEnergy.value),
        note: nodes.journalNote.value,
      };
      const data = await request(`/api/tools/journal/${state.userId}/entries`, {
        method: "POST",
        body: payload,
      });
      appendLog("Saved journal entry", data);
    } catch (error) {
      showError("journal", error);
    }
  });

  nodes.loadTrendBtn.addEventListener("click", async () => {
    try {
      ensureUser();
      const data = await request(`/api/tools/journal/${state.userId}/trend?days=7`);
      nodes.trendView.textContent = JSON.stringify(data, null, 2);
      appendLog("Loaded journal trend", data);
    } catch (error) {
      showError("journal trend", error);
    }
  });

  nodes.startCoachBtn.addEventListener("click", async () => {
    try {
      ensureUser();
      const payload = {
        style_id: nodes.coachStyle.value,
        subscription_active: nodes.coachSubscription.checked,
      };
      const data = await request(`/api/coach/${state.userId}/start`, {
        method: "POST",
        body: payload,
      });
      state.coachSessionId = data.session?.session_id || "";
      nodes.coachReply.textContent = JSON.stringify(data, null, 2);
      maybeShowCrisisBanner({ mode: "coaching" });
      appendLog("Started coach session", data);
    } catch (error) {
      showError("start coach", error);
    }
  });

  nodes.coachForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      if (!state.coachSessionId) {
        throw new Error("Start a coach session first.");
      }
      const payload = { user_message: nodes.coachMessage.value };
      const data = await request(`/api/coach/${state.coachSessionId}/chat`, {
        method: "POST",
        body: payload,
      });
      nodes.coachReply.textContent = JSON.stringify(data, null, 2);
      maybeShowCrisisBanner(data);
      appendLog("Coach chat", data);
      if (data.halted) {
        state.coachSessionId = "";
      }
    } catch (error) {
      showError("coach chat", error);
    }
  });

  nodes.endCoachBtn.addEventListener("click", async () => {
    try {
      if (!state.coachSessionId) {
        throw new Error("No active coach session.");
      }
      const data = await request(`/api/coach/${state.coachSessionId}/end`, {
        method: "POST",
      });
      state.coachSessionId = "";
      nodes.coachReply.textContent = JSON.stringify(data, null, 2);
      maybeShowCrisisBanner({ mode: "coaching" });
      appendLog("Ended coach session", data);
    } catch (error) {
      showError("end coach", error);
    }
  });
}

function init() {
  nodes.apiBase.value = defaultApiBase();
  state.apiBase = normalizeBase(nodes.apiBase.value);
  setLang("zh");
  renderHotlines();
  bindEvents();
  appendLog("Frontend initialized", {
    apiBase: state.apiBase,
    note: "Non-medical coaching prototype UI",
  });
}

init();
