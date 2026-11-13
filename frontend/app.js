// Fuente de la interfaz. Se compila a frontend/app.js con: python build_frontend.py
const {
  useState,
  useRef,
  useEffect,
  useCallback
} = React;
const ICONS = {
  home: "M3 11l9-8 9 8v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1z",
  clock: "M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z M12 7v5l3 2",
  grid: "M4 4h6v6H4z M14 4h6v6h-6z M4 14h6v6H4z M14 14h6v6h-6z",
  gear: "M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0z M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z",
  globe: "M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z M3 12h18 M12 3a14 14 0 0 1 0 18 14 14 0 0 1 0-18z",
  sun: "M16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0z M12 1v2 M12 21v2 M4.2 4.2l1.4 1.4 M18.4 18.4l1.4 1.4 M1 12h2 M21 12h2 M4.2 19.8l1.4-1.4 M18.4 5.6l1.4-1.4",
  moon: "M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8z",
  mic: "M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z M19 10v2a7 7 0 0 1-14 0v-2 M12 19v4",
  minus: "M5 12h14",
  x: "M18 6L6 18 M6 6l12 12",
  mail: "M5 5h14a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2z M3 7l9 6 9-6",
  code: "M16 18l6-6-6-6 M8 6l-6 6 6 6",
  folder: "M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z",
  bolt: "M13 2L3 14h9l-1 8 10-12h-9l1-8z",
  dots: "M6 12h.01 M12 12h.01 M18 12h.01",
  send: "M5 12h14 M12 5l7 7-7 7",
  trash: "M3 6h18 M8 6V4h8v2 M19 6l-1 14H6L5 6",
  plus: "M12 5v14 M5 12h14",
  search: "M21 21l-4.3-4.3 M17 11a6 6 0 1 1-12 0 6 6 0 0 1 12 0z",
  play: "M6 4l14 8-14 8z",
  chat: "M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z",
  window: "M4 5h16a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1z M3 9h18",
  app: "M4 4h7v7H4z M13 4h7v7h-7z M4 13h7v7H4z M17 13v7 M13.5 16.5h7",
  chev: "M6 9l6 6 6-6"
};
function Icon({
  name,
  size
}) {
  return /*#__PURE__*/React.createElement("svg", {
    className: "ico",
    viewBox: "0 0 24 24",
    style: {
      ...(size ? {
        width: size,
        height: size
      } : {}),
      ...(name === "dots" ? {
        strokeWidth: 4
      } : {})
    },
    "aria-hidden": "true"
  }, /*#__PURE__*/React.createElement("path", {
    d: ICONS[name] || ""
  }));
}
function useSettings() {
  const [, bump] = useState(0);
  useEffect(() => {
    const h = () => bump(n => n + 1);
    window.addEventListener("doxsettings", h);
    DoxSettings.load();
    return () => window.removeEventListener("doxsettings", h);
  }, []);
  return DoxSettings;
}
const jget = url => fetch(url).then(r => r.json());
function App() {
  const S = useSettings();
  const t = (k, v) => S.t(k, v);
  const {
    lang,
    theme,
    speak,
    research
  } = S.data;
  const dark = S.resolved() === "dark";
  const [view, setView] = useState("home");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [mood, setMood] = useState("idle");
  const [busy, setBusy] = useState(false);
  const [ai, setAi] = useState(null);
  const [voiceInfo, setVoiceInfo] = useState(null);
  const [historyList, setHistoryList] = useState([]);
  const [confirmClear, setConfirmClear] = useState(false);
  const [desktop, setDesktop] = useState(!!(window.pywebview && window.pywebview.api));
  const [listening, setListening] = useState(false);
  const [menu, setMenu] = useState(false);
  const [toast, setToast] = useState("");
  const [agent, setAgent] = useState(null);
  const endRef = useRef(null);
  const inputRef = useRef(null);
  const convId = useRef(null);
  const toastTimer = useRef(null);
  const api = (name, ...args) => window.pywebview?.api?.[name]?.(...args);
  const say = msg => {
    setToast(msg);
    clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(""), 4500);
  };
  useEffect(() => {
    endRef.current?.scrollIntoView({
      behavior: "smooth"
    });
  }, [messages, busy, view]);
  useEffect(() => {
    const refresh = () => jget("/api/status").then(setAi).catch(() => {});
    refresh();
    const iv = setInterval(refresh, 15000);
    const ready = () => {
      setDesktop(true);
      api("listening")?.then(setListening);
    };
    window.addEventListener("pywebviewready", ready);
    if (window.pywebview && window.pywebview.api) ready();
    // Llamadas desde desktop.py (comandos de voz)
    window.doxIncoming = p => {
      setView("home");
      setMessages(m => [...m, ...(p.user ? [{
        role: "user",
        content: p.user
      }] : []), {
        role: "assistant",
        content: p.reply
      }]);
      setMood(p.mood || "idle");
    };
    window.doxListening = () => setMood("surprised");
    let since = Date.now() / 1000;
    const poll = () => jget("/api/notifications?since=" + since).then(r => {
      (r.items || []).forEach(n => {
        since = Math.max(since, n.ts);
        say("⏰ " + n.text);
      });
    }).catch(() => {});
    const iv2 = setInterval(poll, 8000);
    return () => {
      clearInterval(iv);
      clearInterval(iv2);
      window.removeEventListener("pywebviewready", ready);
    };
  }, []);
  useEffect(() => {
    if (view === "settings") {
      jget("/api/voice").then(setVoiceInfo).catch(() => {});
      jget("/api/agent/info").then(setAgent).catch(() => {});
    }
  }, [view, speak, lang]);
  useEffect(() => {
    if (view === "history") jget("/api/history").then(setHistoryList).catch(() => {});
  }, [view]);
  useEffect(() => {
    if (!menu) return;
    const close = () => setMenu(false);
    setTimeout(() => window.addEventListener("click", close), 0);
    return () => window.removeEventListener("click", close);
  }, [menu]);

  // Se duerme tras 60 s sin actividad
  useEffect(() => {
    const id = setTimeout(() => setMood("sleepy"), 60000);
    return () => clearTimeout(id);
  }, [messages, mood]);
  async function saveConversation(all) {
    try {
      const r = await fetch("/api/history", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          id: convId.current,
          messages: all
        })
      });
      convId.current = (await r.json()).id;
    } catch (e) {}
  }
  async function send(text) {
    const msg = (text ?? input).trim();
    if (!msg || busy) return;
    const base = [...messages, {
      role: "user",
      content: msg
    }];
    setView("home");
    setMessages([...base, {
      role: "assistant",
      content: "",
      pending: true
    }]);
    setInput("");
    setBusy(true);
    setMood("thinking");
    const patchLast = fn => setMessages(m => {
      const c = m.slice();
      c[c.length - 1] = fn(c[c.length - 1]);
      return c;
    });
    try {
      const res = await fetch("/api/chat/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          message: msg,
          history: messages
        })
      });
      const reader = res.body.getReader();
      const dec = new TextDecoder();
      let buf = "",
        acc = "";
      for (;;) {
        const {
          value,
          done
        } = await reader.read();
        if (done) break;
        buf += dec.decode(value, {
          stream: true
        });
        let nl;
        while ((nl = buf.indexOf("\n")) >= 0) {
          const line = buf.slice(0, nl).trim();
          buf = buf.slice(nl + 1);
          if (!line) continue;
          const ev = JSON.parse(line);
          if (ev.type === "token") {
            acc += ev.text;
            const a = acc;
            patchLast(p => ({
              ...p,
              content: a,
              status: ""
            }));
          } else if (ev.type === "reset") {
            acc = "";
            patchLast(p => ({
              ...p,
              content: ""
            }));
          } else if (ev.type === "status") {
            patchLast(p => ({
              ...p,
              status: ev.text
            }));
          } else if (ev.type === "tool") {
            patchLast(p => {
              const steps = (p.steps || []).slice();
              if (ev.state === "run") steps.push({
                name: ev.name,
                state: "run"
              });else {
                const k = steps.map(x => x.name === ev.name && x.state === "run").lastIndexOf(true);
                if (k >= 0) steps[k] = {
                  name: ev.name,
                  state: ev.state,
                  text: ev.text
                };
              }
              return {
                ...p,
                steps
              };
            });
          } else if (ev.type === "confirm") {
            patchLast(p => ({
              ...p,
              confirm: {
                id: ev.id,
                title: ev.title,
                detail: ev.detail,
                state: "pending"
              }
            }));
            setMood("surprised");
          } else if (ev.type === "done") {
            const fin = {
              role: "assistant",
              content: ev.reply,
              ...(ev.sources && ev.sources.length ? {
                sources: ev.sources
              } : {})
            };
            patchLast(p => ({
              ...fin,
              steps: p.steps,
              confirm: p.confirm && p.confirm.state === "pending" ? {
                ...p.confirm,
                state: "denied"
              } : p.confirm
            }));
            setMood(ev.mood || "idle");
            saveConversation([...base, fin]);
          }
        }
      }
    } catch (e) {
      patchLast(() => ({
        role: "assistant",
        content: t("error")
      }));
      setMood("surprised");
    } finally {
      setBusy(false);
    }
  }
  async function answer(id, ok) {
    setMessages(m => m.map(x => x.confirm && x.confirm.id === id ? {
      ...x,
      confirm: {
        ...x.confirm,
        state: ok ? "allowed" : "denied"
      }
    } : x));
    try {
      await fetch("/api/confirm", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          id,
          ok
        })
      });
    } catch (e) {}
    setMood("thinking");
  }
  const openUrl = url => fetch("/api/open-url", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      url
    })
  }).catch(() => {});
  function newChat() {
    setMessages([]);
    convId.current = null;
    setView("home");
    setMood("idle");
    setTimeout(() => inputRef.current?.focus(), 50);
  }
  async function openConversation(id) {
    try {
      const c = await jget("/api/history/" + id);
      convId.current = c.id;
      setMessages(c.messages || []);
      setView("home");
      setMood("idle");
    } catch (e) {}
  }
  async function deleteConversation(id) {
    await fetch("/api/history/" + id, {
      method: "DELETE"
    });
    if (convId.current === id) {
      convId.current = null;
    }
    setHistoryList(l => l.filter(c => c.id !== id));
  }
  async function clearHistory() {
    if (!confirmClear) {
      setConfirmClear(true);
      setTimeout(() => setConfirmClear(false), 3000);
      return;
    }
    await fetch("/api/history", {
      method: "DELETE"
    });
    setHistoryList([]);
    setConfirmClear(false);
  }
  function prefill(text) {
    setView("home");
    setInput(text);
    setTimeout(() => inputRef.current?.focus(), 50);
  }
  async function toggleMic() {
    if (!desktop) return say(t("mic.err.web"));
    const r = await api("toggle_listen");
    if (r && r.error) return say(t("mic.err." + r.error));
    setListening(!!(r && r.on));
  }
  async function testVoice() {
    try {
      const r = await (await fetch("/api/speak-test", {
        method: "POST"
      })).json();
      if (!r.ok) say(t("voice.test.web"));
    } catch (e) {
      say(t("error"));
    }
  }
  const statusOk = ai && ai.running && ai.model_installed;
  const statusTxt = !ai ? "…" : statusOk ? t("status.online") : ai.running ? t("status.nomodel") : t("status.noai");
  const chatting = messages.length > 0;
  const waiting = busy && chatting && messages[messages.length - 1].pending && !messages[messages.length - 1].content && !messages[messages.length - 1].confirm && !messages[messages.length - 1].status;
  const dateFmt = ts => new Date(ts * 1000).toLocaleString(lang === "es" ? "es-CO" : "en-US", {
    dateStyle: "medium",
    timeStyle: "short"
  });
  const NAV = [["home", "home", "nav.home"], ["history", "clock", "nav.history"], ["tools", "grid", "nav.tools"], ["settings", "gear", "nav.settings"]];
  const CARDS = [["mail", "card.mail", () => send(t("prompt.mail"))], ["code", "card.code", () => prefill(t("prompt.code"))], ["folder", "card.files", () => send(t("prompt.files"))], ["bolt", "card.tasks", () => setView("tools")], ["dots", "card.more", () => setView("settings")]];
  return /*#__PURE__*/React.createElement("div", {
    className: "shell"
  }, /*#__PURE__*/React.createElement("aside", {
    className: "side"
  }, /*#__PURE__*/React.createElement("div", {
    className: "brandbox"
  }, /*#__PURE__*/React.createElement("div", {
    className: "mini"
  }, /*#__PURE__*/React.createElement("img", {
    src: S.logoSrc(),
    alt: "DOx",
    draggable: "false"
  })), /*#__PURE__*/React.createElement("div", {
    className: "wordmark"
  }, "D", /*#__PURE__*/React.createElement("span", null, "O"), "x")), /*#__PURE__*/React.createElement("nav", {
    className: "nav"
  }, NAV.map(([id, icon, label]) => /*#__PURE__*/React.createElement("button", {
    key: id,
    className: view === id ? "on" : "",
    onClick: () => setView(id),
    title: t(label)
  }, /*#__PURE__*/React.createElement(Icon, {
    name: icon
  }), /*#__PURE__*/React.createElement("span", null, t(label))))), /*#__PURE__*/React.createElement("div", {
    className: "grow"
  }), /*#__PURE__*/React.createElement("div", {
    className: "pill",
    title: ai ? ai.model : ""
  }, /*#__PURE__*/React.createElement("i", {
    className: "dot " + (statusOk ? "ok" : "warn")
  }), /*#__PURE__*/React.createElement("span", null, statusTxt)), /*#__PURE__*/React.createElement("div", {
    className: "foot"
  }, ai && ai.running && !ai.model_installed && /*#__PURE__*/React.createElement("div", null, t("ai.missing"), " ", /*#__PURE__*/React.createElement("code", null, "ollama pull ", ai.model)), ai && !ai.running && /*#__PURE__*/React.createElement("div", null, t("ai.off")), ai ? ai.brand : "DOx", /*#__PURE__*/React.createElement("small", null, "v", ai ? ai.version : "1.0.0"))), /*#__PURE__*/React.createElement("main", {
    className: "main"
  }, /*#__PURE__*/React.createElement("div", {
    className: "topbar"
  }, /*#__PURE__*/React.createElement("div", {
    className: "left"
  }, chatting && view === "home" && /*#__PURE__*/React.createElement("button", {
    className: "ghost",
    onClick: newChat
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "plus",
    size: 16
  }), t("newchat"))), /*#__PURE__*/React.createElement("div", {
    className: "right"
  }, /*#__PURE__*/React.createElement("button", {
    className: "chipbtn",
    title: t("lang.tip"),
    onClick: e => {
      e.stopPropagation();
      setMenu(!menu);
    }
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "globe",
    size: 18
  }), lang.toUpperCase(), /*#__PURE__*/React.createElement(Icon, {
    name: "chev",
    size: 14
  })), /*#__PURE__*/React.createElement("span", {
    className: "sep"
  }), /*#__PURE__*/React.createElement("button", {
    className: "round",
    title: t("theme.tip"),
    onClick: () => S.save({
      theme: dark ? "light" : "dark"
    })
  }, /*#__PURE__*/React.createElement(Icon, {
    name: dark ? "moon" : "sun"
  })), /*#__PURE__*/React.createElement("button", {
    className: "round mic" + (listening ? " on" : ""),
    title: listening ? t("mic.on") : t("mic.off"),
    onClick: toggleMic
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "mic"
  })), desktop && /*#__PURE__*/React.createElement("button", {
    className: "round",
    title: t("minimize.tip"),
    onClick: () => api("minimize")
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "minus"
  })), desktop && /*#__PURE__*/React.createElement("button", {
    className: "round",
    title: t("quit.tip"),
    onClick: () => api("quit")
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "x"
  })))), menu && /*#__PURE__*/React.createElement("div", {
    className: "menu",
    onClick: e => e.stopPropagation()
  }, [["es", "Español"], ["en", "English"]].map(([code, name]) => /*#__PURE__*/React.createElement("button", {
    key: code,
    className: lang === code ? "on" : "",
    onClick: () => {
      S.save({
        lang: code
      });
      setMenu(false);
    }
  }, name, /*#__PURE__*/React.createElement("b", null, code.toUpperCase())))), view === "home" && /*#__PURE__*/React.createElement("div", {
    className: "view"
  }, !chatting ? /*#__PURE__*/React.createElement("div", {
    className: "hero"
  }, /*#__PURE__*/React.createElement("div", {
    className: "big",
    onClick: () => setMood(mood === "happy" ? "idle" : "happy")
  }, /*#__PURE__*/React.createElement("img", {
    className: "logo",
    "data-mood": mood,
    src: S.logoSrc(),
    alt: "DOx",
    draggable: "false"
  })), /*#__PURE__*/React.createElement("h1", null, t("hero.title").replace("DOx", ""), "D", /*#__PURE__*/React.createElement("span", null, "O"), "x"), /*#__PURE__*/React.createElement("p", null, t("hero.sub")), /*#__PURE__*/React.createElement("div", {
    className: "cards"
  }, CARDS.map(([icon, label, fn]) => /*#__PURE__*/React.createElement("button", {
    key: icon,
    className: "card",
    onClick: fn
  }, /*#__PURE__*/React.createElement(Icon, {
    name: icon
  }), /*#__PURE__*/React.createElement("span", null, t(label)))))) : /*#__PURE__*/React.createElement("div", {
    className: "msgs"
  }, messages.map((m, i) => m.pending && !m.content && !m.status && !(m.steps && m.steps.length) && !m.confirm ? null : /*#__PURE__*/React.createElement("div", {
    key: i,
    className: "msg " + (m.role === "user" ? "user" : "bot")
  }, m.steps && m.steps.length > 0 && /*#__PURE__*/React.createElement("div", {
    className: "steps"
  }, m.steps.map((s, k) => /*#__PURE__*/React.createElement("span", {
    key: k,
    className: "step " + s.state,
    title: s.text || ""
  }, s.state === "run" ? "…" : s.state === "ok" ? "✓" : "✗", " ", t("step." + s.name)))), m.status && !m.content && /*#__PURE__*/React.createElement("div", {
    className: "status"
  }, m.status), m.confirm && /*#__PURE__*/React.createElement("div", {
    className: "confirm " + m.confirm.state
  }, /*#__PURE__*/React.createElement("b", null, t("confirm.ask")), /*#__PURE__*/React.createElement("div", {
    className: "ct"
  }, m.confirm.title), m.confirm.detail && /*#__PURE__*/React.createElement("pre", null, m.confirm.detail), m.confirm.state === "pending" ? /*#__PURE__*/React.createElement("div", {
    className: "cbtn"
  }, /*#__PURE__*/React.createElement("button", {
    className: "btn ok",
    onClick: () => answer(m.confirm.id, true)
  }, t("confirm.allow")), /*#__PURE__*/React.createElement("button", {
    className: "btn",
    onClick: () => answer(m.confirm.id, false)
  }, t("confirm.deny"))) : /*#__PURE__*/React.createElement("small", null, m.confirm.state === "allowed" ? "✓ " + t("confirm.allowed") : "✗ " + t("confirm.denied"))), m.content, m.sources && m.sources.length > 0 && /*#__PURE__*/React.createElement("div", {
    className: "sources"
  }, /*#__PURE__*/React.createElement("small", null, t("sources")), m.sources.map((s, k) => /*#__PURE__*/React.createElement("button", {
    key: k,
    className: "src",
    title: s.url,
    onClick: () => openUrl(s.url)
  }, /*#__PURE__*/React.createElement("i", null, k + 1), s.title || s.url))))), waiting && /*#__PURE__*/React.createElement("div", {
    className: "msg bot typing"
  }, /*#__PURE__*/React.createElement("span", null), /*#__PURE__*/React.createElement("span", null), /*#__PURE__*/React.createElement("span", null)), /*#__PURE__*/React.createElement("div", {
    ref: endRef
  })), /*#__PURE__*/React.createElement("form", {
    className: "bar",
    onSubmit: e => {
      e.preventDefault();
      send();
    }
  }, /*#__PURE__*/React.createElement("input", {
    ref: inputRef,
    value: input,
    onChange: e => setInput(e.target.value),
    placeholder: t("placeholder"),
    autoFocus: true
  }), /*#__PURE__*/React.createElement("button", {
    className: "send",
    disabled: busy || !input.trim(),
    title: t("send")
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "send"
  })))), view === "history" && /*#__PURE__*/React.createElement("div", {
    className: "page"
  }, /*#__PURE__*/React.createElement("h2", null, t("history.title")), /*#__PURE__*/React.createElement("p", {
    className: "sub"
  }, t("history.sub")), historyList.length === 0 ? /*#__PURE__*/React.createElement("div", {
    className: "empty"
  }, t("history.empty")) : /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("div", {
    className: "list"
  }, historyList.map(c => /*#__PURE__*/React.createElement("div", {
    key: c.id,
    className: "row",
    onClick: () => openConversation(c.id)
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "chat"
  }), /*#__PURE__*/React.createElement("div", {
    className: "t"
  }, /*#__PURE__*/React.createElement("b", null, c.title), /*#__PURE__*/React.createElement("small", null, dateFmt(c.updated), " \xB7 ", t("history.msgs", {
    n: c.count
  }))), /*#__PURE__*/React.createElement("button", {
    className: "del",
    title: t("history.delete"),
    onClick: e => {
      e.stopPropagation();
      deleteConversation(c.id);
    }
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "trash",
    size: 18
  }))))), /*#__PURE__*/React.createElement("p", {
    style: {
      textAlign: "center",
      marginTop: 18
    }
  }, /*#__PURE__*/React.createElement("button", {
    className: "btn",
    onClick: clearHistory
  }, confirmClear ? t("history.sure") : t("history.clear"))))), view === "tools" && /*#__PURE__*/React.createElement("div", {
    className: "page"
  }, /*#__PURE__*/React.createElement("h2", null, t("tools.title")), /*#__PURE__*/React.createElement("p", {
    className: "sub"
  }, t("tools.sub")), /*#__PURE__*/React.createElement("div", {
    className: "tools"
  }, t("tools").map(tool => /*#__PURE__*/React.createElement("div", {
    key: tool.name,
    className: "tool"
  }, /*#__PURE__*/React.createElement("div", {
    className: "h"
  }, /*#__PURE__*/React.createElement(Icon, {
    name: tool.icon
  }), tool.name), /*#__PURE__*/React.createElement("span", {
    className: "badge " + tool.mode
  }, t("badge." + tool.mode)), /*#__PURE__*/React.createElement("p", null, tool.desc), /*#__PURE__*/React.createElement("div", {
    className: "ex"
  }, tool.ex.map(x => /*#__PURE__*/React.createElement("button", {
    key: x,
    onClick: () => send(x)
  }, x))))))), view === "settings" && /*#__PURE__*/React.createElement("div", {
    className: "page"
  }, /*#__PURE__*/React.createElement("h2", null, t("settings.title")), /*#__PURE__*/React.createElement("p", {
    className: "sub"
  }, t("settings.sub")), /*#__PURE__*/React.createElement("div", {
    className: "sect"
  }, /*#__PURE__*/React.createElement("h3", null, t("set.language")), /*#__PURE__*/React.createElement("div", {
    className: "seg"
  }, [["es", "Español"], ["en", "English"]].map(([c, n]) => /*#__PURE__*/React.createElement("button", {
    key: c,
    className: lang === c ? "on" : "",
    onClick: () => S.save({
      lang: c
    })
  }, n)))), /*#__PURE__*/React.createElement("div", {
    className: "sect"
  }, /*#__PURE__*/React.createElement("h3", null, t("set.appearance")), /*#__PURE__*/React.createElement("div", {
    className: "seg"
  }, ["system", "light", "dark"].map(th => /*#__PURE__*/React.createElement("button", {
    key: th,
    className: theme === th ? "on" : "",
    onClick: () => S.save({
      theme: th
    })
  }, t("theme." + th))))), /*#__PURE__*/React.createElement("div", {
    className: "sect"
  }, /*#__PURE__*/React.createElement("h3", null, t("set.voice")), /*#__PURE__*/React.createElement("div", {
    className: "line"
  }, /*#__PURE__*/React.createElement("div", null, t("voice.replies"), /*#__PURE__*/React.createElement("small", null, t("voice.replies.sub"))), /*#__PURE__*/React.createElement("button", {
    className: "switch" + (speak ? " on" : ""),
    onClick: () => S.save({
      speak: !speak
    }),
    "aria-label": t("voice.replies")
  })), /*#__PURE__*/React.createElement("div", {
    className: "line"
  }, /*#__PURE__*/React.createElement("div", null, voiceInfo && voiceInfo.engine === "piper" ? t("voice.piper", {
    voice: voiceInfo.voice
  }) : t("voice.espeak"), voiceInfo && voiceInfo.engine !== "piper" && /*#__PURE__*/React.createElement("small", null, t("voice.install"), " ", /*#__PURE__*/React.createElement("code", null, "pip install piper-tts"), " ", /*#__PURE__*/React.createElement("code", null, "python install_voice.py"))), /*#__PURE__*/React.createElement("button", {
    className: "btn",
    onClick: testVoice
  }, t("voice.test")))), /*#__PURE__*/React.createElement("div", {
    className: "sect"
  }, /*#__PURE__*/React.createElement("h3", null, t("set.mic")), /*#__PURE__*/React.createElement("div", {
    className: "line"
  }, /*#__PURE__*/React.createElement("div", null, t("mic.setting"), /*#__PURE__*/React.createElement("small", null, t("mic.setting.sub"))), /*#__PURE__*/React.createElement("button", {
    className: "switch" + (listening ? " on" : ""),
    onClick: toggleMic,
    "aria-label": t("mic.setting")
  }))), /*#__PURE__*/React.createElement("div", {
    className: "sect"
  }, /*#__PURE__*/React.createElement("h3", null, t("set.agent")), /*#__PURE__*/React.createElement("div", {
    className: "line"
  }, /*#__PURE__*/React.createElement("div", null, t("research.title"), /*#__PURE__*/React.createElement("small", null, t("research.sub"))), /*#__PURE__*/React.createElement("div", {
    className: "seg"
  }, ["auto", "always", "off"].map(r => /*#__PURE__*/React.createElement("button", {
    key: r,
    className: research === r ? "on" : "",
    onClick: () => S.save({
      research: r
    })
  }, t("research." + r))))), /*#__PURE__*/React.createElement("div", {
    className: "line"
  }, /*#__PURE__*/React.createElement("div", null, t("perm.sub"))), agent && agent.roots && agent.roots.length > 0 && /*#__PURE__*/React.createElement("div", {
    className: "line"
  }, /*#__PURE__*/React.createElement("div", null, t("perm.roots"), /*#__PURE__*/React.createElement("small", null, agent.roots.map(r => /*#__PURE__*/React.createElement("code", {
    key: r,
    style: {
      marginRight: 6
    }
  }, r)))))), /*#__PURE__*/React.createElement("div", {
    className: "sect"
  }, /*#__PURE__*/React.createElement("h3", null, t("set.ai")), /*#__PURE__*/React.createElement("div", {
    className: "line"
  }, /*#__PURE__*/React.createElement("span", null, t("ai.state")), /*#__PURE__*/React.createElement("b", {
    style: {
      color: statusOk ? "var(--ok)" : "var(--warn)"
    }
  }, statusOk ? t("ai.ok") : t("ai.down"))), /*#__PURE__*/React.createElement("div", {
    className: "line"
  }, /*#__PURE__*/React.createElement("span", null, t("ai.model")), /*#__PURE__*/React.createElement("code", null, ai ? ai.model : "…")), /*#__PURE__*/React.createElement("div", {
    className: "line"
  }, /*#__PURE__*/React.createElement("span", null, t("ai.profile")), /*#__PURE__*/React.createElement("code", null, ai ? ai.profile : "…"))), /*#__PURE__*/React.createElement("div", {
    className: "sect"
  }, /*#__PURE__*/React.createElement("h3", null, t("set.about")), /*#__PURE__*/React.createElement("div", {
    className: "line"
  }, /*#__PURE__*/React.createElement("span", null, t("about.text"))), /*#__PURE__*/React.createElement("div", {
    className: "line"
  }, /*#__PURE__*/React.createElement("span", null, ai ? ai.brand : ""), /*#__PURE__*/React.createElement("code", null, "v", ai ? ai.version : "")))), toast && /*#__PURE__*/React.createElement("div", {
    className: "toast"
  }, toast)));
}
ReactDOM.createRoot(document.getElementById("root")).render( /*#__PURE__*/React.createElement(App, null));