"""
El "cerebro" de DOx / DOx's brain.

Orden de decisión para cada mensaje:
  1. ¿Es una orden del PC ("abre YouTube", "open YouTube")?  -> actions.py (instantáneo, sin IA)
  2. ¿Es hora o fecha?                                        -> respuesta directa (sin IA)
  3. Todo lo demás                                            -> agent.py: herramientas, investigación con fuentes o chat (Ollama)
  4. Si Ollama no está disponible                             -> respuestas de respaldo + instrucciones

Así la IA solo se despierta cuando de verdad hace falta y el consumo se mantiene bajo.
"""

import re
from datetime import datetime
from typing import Iterator

import actions
import agent
import config
import llm
import settings

DIAS = {"es": ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"],
        "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
MESES = {"es": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                "septiembre", "octubre", "noviembre", "diciembre"],
         "en": ["January", "February", "March", "April", "May", "June", "July", "August",
                "September", "October", "November", "December"]}

TXT = {
    "es": {
        "empty": "¿Me dijiste algo? Estoy atento.",
        "time": "Son las {t}.",
        "date": "Hoy es {d} {n} de {m} de {y}.",
        "hello": "¡Muuuy buenas! Soy DOx. ¿En qué te ayudo?",
        "thanks": "¡Con gusto!",
        "who": "Soy DOx, tu asistente de escritorio.",
        "no_ollama": "Aún no tengo cerebro conectado. Instala Ollama (ollama.com) y ejecuta: ollama pull {m}",
        "no_model": "Ollama está encendido pero me falta el modelo. Ejecuta: ollama pull {m}",
        "problem": "Tuve un problema pensando eso: {e}",
        "blank": "Me quedé en blanco, ¿me lo repites?",
        "slow": "El modelo tardó demasiado en responder.",
    },
    "en": {
        "empty": "Did you say something? I'm listening.",
        "time": "It's {t}.",
        "date": "Today is {d}, {m} {n}, {y}.",
        "hello": "Hey there! I'm DOx. How can I help?",
        "thanks": "You're welcome!",
        "who": "I'm DOx, your desktop assistant.",
        "no_ollama": "I don't have a brain connected yet. Install Ollama (ollama.com) and run: ollama pull {m}",
        "no_model": "Ollama is running but I'm missing the model. Run: ollama pull {m}",
        "problem": "I had a problem thinking that through: {e}",
        "blank": "I drew a blank, could you say that again?",
        "slow": "The model took too long to answer.",
    },
}


def _quick_reply(msg: str, lang: str) -> dict | None:
    t = msg.lower()
    now = datetime.now()
    s = TXT[lang]
    if re.search(r"qu[eé] hora es|me dices la hora|hora actual|what time|current time|what's the time", t):
        return {"reply": s["time"].format(t=f"{now:%H:%M}" if lang == "es" else f"{now:%I:%M %p}".lstrip("0")),
                "mood": "happy"}
    if re.search(r"qu[eé] (d[ií]a|fecha) es|fecha de hoy|what day|what's the date|today's date|what is the date", t):
        return {"reply": s["date"].format(d=DIAS[lang][now.weekday()], n=now.day,
                                          m=MESES[lang][now.month - 1], y=now.year), "mood": "happy"}
    return None


def _fallback(msg: str, hint: str, lang: str) -> dict:
    t = msg.lower()
    s = TXT[lang]
    if any(re.search(rf"\b{re.escape(w)}\b", t) for w in ("hola", "buenas", "hey", "hello", "hi", "qué más", "que mas")):
        return {"reply": s["hello"], "mood": "happy"}
    if any(w in t for w in ("gracias", "genial", "chévere", "chevere", "thanks", "thank you")):
        return {"reply": s["thanks"], "mood": "happy"}
    if any(w in t for w in ("quién eres", "quien eres", "qué eres", "que eres", "who are you", "what are you")):
        return {"reply": s["who"], "mood": "idle"}
    return {"reply": hint, "mood": "thinking"}


def _mood_for(reply: str) -> str:
    return "happy" if ("!" in reply or "¡" in reply) else "idle"


ollama_status = llm.status


def think_stream(message: str, history: list[dict], lang: str = "es", interactive: bool = True) -> Iterator[dict]:
    """Eventos: status, token, reset, tool, confirm y done ({'reply','mood','sources',...})."""
    lang = lang if lang in TXT else "es"
    s = TXT[lang]
    msg = message.strip()
    if not msg:
        yield {"type": "done", "reply": s["empty"], "mood": "surprised"}
        return

    direct = actions.try_action(msg, lang) or _quick_reply(msg, lang)
    extra: set[str] = set()
    if direct and direct.get("action") in ("unknown", "search") and config.AGENT:
        # "abre el listado de asistencia", "busca mi PDF…": no es una web ni un programa de la lista -> que lo resuelva el agente
        groups, _ = agent.detect(msg, "off")
        if groups or direct.get("action") == "unknown":
            extra = groups or {"files", "system"}
            direct = None
    if direct:
        yield {"type": "done", **direct}
        return

    try:
        yield from agent.run(msg, history, lang, settings.get()["research"], interactive, extra)
    except llm.OllamaDown:
        yield {"type": "done", **_fallback(msg, s["no_ollama"].format(m=config.MODEL), lang)}
    except llm.ModelMissing:
        yield {"type": "done", **_fallback(msg, s["no_model"].format(m=config.MODEL), lang)}
    except llm.OllamaError as e:
        yield {"type": "done", "reply": s["problem"].format(e=e), "mood": "surprised"}


def think(message: str, history: list[dict], lang: str = "es", interactive: bool = False) -> dict:
    """Versión sin streaming (voz): devuelve {'reply','mood',...}. Las acciones que piden permiso no se ejecutan."""
    result: dict = {}
    for ev in think_stream(message, history, lang, interactive):
        if ev["type"] == "done":
            result = {k: v for k, v in ev.items() if k != "type"}
    return result
