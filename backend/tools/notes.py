"""Notas, memoria y recordatorios (guardados solo en tu PC: ~/.config/dox/notes.json)."""

import json
import re
import threading
import time
import unicodedata
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from safety import ToolError

from . import S, tool

FILE = Path.home() / ".config" / "dox" / "notes.json"
_lock = threading.Lock()
_notifs: list[dict] = []


def _load() -> dict:
    try:
        d = json.loads(FILE.read_text(encoding="utf-8"))
    except Exception:
        d = {}
    d.setdefault("notes", []); d.setdefault("facts", []); d.setdefault("reminders", [])
    return d


def _save(d: dict) -> None:
    FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(FILE)


def _plain(t: str) -> str:
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


# ---------------------------------------------------------------- tiempo
_UNITS = {"seg": 1, "segundo": 1, "segundos": 1, "sec": 1, "second": 1, "seconds": 1,
          "min": 60, "minuto": 60, "minutos": 60, "minute": 60, "minutes": 60, "mins": 60,
          "h": 3600, "hora": 3600, "horas": 3600, "hour": 3600, "hours": 3600, "hr": 3600, "hrs": 3600,
          "dia": 86400, "dias": 86400, "day": 86400, "days": 86400}
_NUMW = {"un": 1, "una": 1, "uno": 1, "a": 1, "an": 1, "dos": 2, "two": 2, "tres": 3, "three": 3, "cinco": 5, "five": 5,
         "diez": 10, "ten": 10, "quince": 15, "fifteen": 15, "veinte": 20, "twenty": 20, "treinta": 30, "thirty": 30,
         "media": 0.5, "half": 0.5}


def parse_when(text: str, now: datetime | None = None) -> datetime:
    """Entiende «en 10 minutos», «in 2 hours», «mañana a las 8», «a las 15:30», «at 5pm», «2026-11-12 09:00»."""
    now = now or datetime.now()
    t = _plain(text).strip()
    m = re.search(r"\b(\d{4})-(\d{2})-(\d{2})(?:[ t](\d{1,2}):(\d{2}))?", t)
    if m:
        y, mo, d, h, mi = (int(x) if x else 0 for x in m.groups())
        return datetime(y, mo, d, h, mi)
    m = re.search(r"\b(?:en|in)\s+(\d+(?:[.,]\d+)?|[a-z]+)\s+(?:y\s+media\s+)?([a-z]+)", t)
    if m:
        raw, unit = m.group(1), m.group(2)
        num = float(raw.replace(",", ".")) if re.match(r"\d", raw) else _NUMW.get(raw)
        if num is not None and unit in _UNITS:
            return now + timedelta(seconds=num * _UNITS[unit])
    day = now
    if re.search(r"\b(manana|tomorrow)\b", t):
        day = now + timedelta(days=1)
    m = re.search(r"\b(?:a las|a la|at|para las)?\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm|a\.m\.|p\.m\.|h)?\b", t)
    if m and (m.group(2) or m.group(3) or re.search(r"\b(a las|a la|at|para las)\b", t)):
        h, mi, ap = int(m.group(1)), int(m.group(2) or 0), (m.group(3) or "")
        if ap.startswith("p") and h < 12:
            h += 12
        if ap.startswith("a") and h == 12:
            h = 0
        if not ap and re.search(r"\b(tarde|noche|evening|night)\b", t) and h < 12:
            h += 12
        if h > 23 or mi > 59:
            raise ToolError("Hora inválida.")
        w = day.replace(hour=h, minute=mi, second=0, microsecond=0)
        if w <= now and day.date() == now.date():
            w += timedelta(days=1)
        return w
    raise ToolError("No entendí cuándo. Prueba: «en 10 minutos», «mañana a las 8:00» o «a las 15:30».")


# ---------------------------------------------------------------- herramientas
@tool("notes", "Guarda una nota para el usuario.", {"text": S("contenido de la nota")}, ["text"])
def add_note(text: str) -> str:
    with _lock:
        d = _load()
        d["notes"].append({"id": uuid.uuid4().hex[:6], "text": str(text)[:1000], "at": time.strftime("%Y-%m-%d %H:%M")})
        d["notes"] = d["notes"][-200:]
        _save(d)
    return "Nota guardada."


@tool("notes", "Lista las notas guardadas (opcionalmente filtradas por una palabra).",
      {"query": S("palabra a buscar (opcional)")}, [])
def list_notes(query: str | None = None) -> str:
    notes = _load()["notes"]
    if query:
        q = _plain(query)
        notes = [n for n in notes if q in _plain(n["text"])]
    if not notes:
        return "No hay notas" + (" con eso." if query else " guardadas.")
    return "Notas:\n" + "\n".join(f"- [{n['id']}] {n['at']}: {n['text']}" for n in notes[-15:])


@tool("notes", "Borra una nota por su id.", {"id": S("id de la nota (de list_notes)")}, ["id"])
def delete_note(id: str) -> str:
    with _lock:
        d = _load()
        before = len(d["notes"])
        d["notes"] = [n for n in d["notes"] if n["id"] != id]
        _save(d)
    if len(d["notes"]) == before:
        raise ToolError("No existe una nota con ese id.")
    return "Nota borrada."


@tool("notes", "Recuerda un dato permanente sobre el usuario (nombre, gustos, datos útiles) para futuras conversaciones.",
      {"fact": S("dato corto, p. ej. 'Se llama Stiven' o 'Prefiere respuestas cortas'")}, ["fact"])
def remember(fact: str) -> str:
    with _lock:
        d = _load()
        d["facts"] = [f for f in d["facts"] if f != fact][-29:] + [str(fact)[:200]]
        _save(d)
    return "Lo recordaré."


@tool("notes", "Olvida un dato recordado (por palabra clave).", {"keyword": S("palabra del dato")}, ["keyword"])
def forget(keyword: str) -> str:
    k = _plain(keyword)
    with _lock:
        d = _load()
        keep = [f for f in d["facts"] if k not in _plain(f)]
        removed = len(d["facts"]) - len(keep)
        d["facts"] = keep
        _save(d)
    return f"Olvidé {removed} dato(s)." if removed else "No tenía nada guardado con esa palabra."


@tool("notes", "Programa un recordatorio. 'when' en lenguaje natural: «en 10 minutos», «mañana a las 8:00», «a las 15:30».",
      {"text": S("qué recordar"), "when": S("cuándo")}, ["text", "when"])
def set_reminder(text: str, when: str) -> str:
    at = parse_when(when)
    with _lock:
        d = _load()
        d["reminders"].append({"id": uuid.uuid4().hex[:6], "text": str(text)[:300], "at": at.isoformat(timespec="minutes"), "done": False})
        _save(d)
    return f"Recordatorio programado para {at.strftime('%Y-%m-%d %H:%M')}: {text}"


@tool("notes", "Lista los recordatorios pendientes.", {}, [])
def list_reminders() -> str:
    rs = [r for r in _load()["reminders"] if not r["done"]]
    if not rs:
        return "No hay recordatorios pendientes."
    return "Recordatorios:\n" + "\n".join(f"- [{r['id']}] {r['at'].replace('T', ' ')}: {r['text']}" for r in sorted(rs, key=lambda r: r["at"]))


@tool("notes", "Cancela un recordatorio por su id.", {"id": S("id del recordatorio")}, ["id"])
def cancel_reminder(id: str) -> str:
    with _lock:
        d = _load()
        n = len(d["reminders"])
        d["reminders"] = [r for r in d["reminders"] if r["id"] != id]
        _save(d)
    if len(d["reminders"]) == n:
        raise ToolError("No existe un recordatorio con ese id.")
    return "Recordatorio cancelado."


# ---------------------------------------------------------------- memoria y avisos
def facts() -> list[str]:
    return _load()["facts"]


def _tick() -> None:
    now = datetime.now()
    with _lock:
        d = _load()
        changed = False
        for r in d["reminders"]:
            if not r["done"] and datetime.fromisoformat(r["at"]) <= now:
                r["done"] = True
                changed = True
                _notifs.append({"id": uuid.uuid4().hex[:8], "ts": time.time(), "text": r["text"]})
        if changed:
            d["reminders"] = [r for r in d["reminders"] if not r["done"] or
                              now - datetime.fromisoformat(r["at"]) < timedelta(days=1)]
            _save(d)
        del _notifs[:-50]


_started = False


def start_scheduler() -> None:
    global _started
    if _started:
        return
    _started = True

    def loop():
        while True:
            try:
                _tick()
            except Exception:
                pass
            time.sleep(15)
    threading.Thread(target=loop, daemon=True, name="dox-reminders").start()


def notifications(since: float = 0.0) -> list[dict]:
    return [n for n in _notifs if n["ts"] > since]
