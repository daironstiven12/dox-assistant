"""Servidor de DOx: API de chat (FastAPI) + sirve la interfaz."""

import json
import re
import threading
import webbrowser
from pathlib import Path
from typing import Iterator
from urllib.parse import urlparse

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import config
import history
import settings
import speaker
import safety
import tools
from brain import ollama_status, think_stream
from tools import notes

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
LOCAL_HOSTS = {"127.0.0.1", "localhost"}

app = FastAPI(title="DOx")


@app.middleware("http")
async def only_local(request: Request, call_next):
    """DOx puede abrir programas en tu PC: solo acepta peticiones de tu propio equipo
    y de su propia interfaz (evita que una página web cualquiera le dé órdenes)."""
    host = request.headers.get("host", "").rsplit(":", 1)[0]
    origin = request.headers.get("origin")
    if host not in LOCAL_HOSTS or (origin and urlparse(origin).hostname not in LOCAL_HOSTS):
        return JSONResponse({"error": "no permitido"}, status_code=403)
    return await call_next(request)


class Source(BaseModel):
    title: str = ""
    url: str


class Turn(BaseModel):
    role: str  # "user" | "assistant"
    content: str
    sources: list[Source] | None = None


class ChatRequest(BaseModel):
    message: str
    history: list[Turn] = []


class SettingsPatch(BaseModel):
    lang: str | None = None
    theme: str | None = None
    speak: bool | None = None
    research: str | None = None


@app.get("/api/health")
def health():
    return {"ok": True, "name": "DOx"}


@app.get("/api/status")
def status():
    return {**ollama_status(), "brand": config.BRAND, "version": config.VERSION}


@app.get("/api/voice")
def voice_info():
    return {**speaker.info(), "can_speak": bool(getattr(app.state, "speak", None))}


@app.post("/api/speak-test")
def speak_test():
    """Botón "Probar voz" de Configuración (solo en la app de escritorio)."""
    speak = getattr(app.state, "speak", None)
    if not speak:
        return {"ok": False}
    lang = settings.get()["lang"]
    speak("Hola, soy DOx. ¿Me escuchas bien?" if lang == "es" else "Hi, I'm DOx. Can you hear me clearly?")
    return {"ok": True}


class HistorySave(BaseModel):
    id: str | None = None
    messages: list[Turn]


@app.get("/api/history")
def history_list():
    return history.list_all()


@app.get("/api/history/{cid}")
def history_get(cid: str):
    conv = history.get(cid)
    return conv if conv else JSONResponse({"error": "no existe"}, status_code=404)


@app.post("/api/history")
def history_save(body: HistorySave):
    return history.save(body.id, [m.model_dump() for m in body.messages])


@app.delete("/api/history/{cid}")
def history_delete(cid: str):
    return {"ok": history.delete(cid)}


@app.delete("/api/history")
def history_clear():
    history.clear()
    return {"ok": True}


@app.get("/api/settings")
def get_settings():
    return settings.get()


@app.post("/api/settings")
def set_settings(patch: SettingsPatch):
    return settings.update(patch.model_dump(exclude_none=True))


def _after(result: dict) -> None:
    """Hablar y mover ventanas (enlaces que pone desktop.py; en modo web no existen y se ignoran)."""
    speak = getattr(app.state, "speak", None)
    if speak and settings.get()["speak"]:
        speak(re.sub(r"\s*\[\d+\]", "", result["reply"]))
    ui_handler = getattr(app.state, "ui_handler", None)
    if result.get("ui") and ui_handler:
        threading.Timer(0.8, ui_handler, [result["ui"]]).start()


@app.post("/api/chat/stream")
def chat_stream(req: ChatRequest):
    """Respuesta en streaming (una línea JSON por evento): el texto aparece mientras el modelo lo escribe."""
    history = [t.model_dump() for t in req.history]
    lang = settings.get()["lang"]

    def gen() -> Iterator[str]:
        for ev in think_stream(req.message, history, lang, interactive=True):
            if ev["type"] == "done":
                _after(ev)
            yield json.dumps(ev, ensure_ascii=False) + "\n"

    return StreamingResponse(gen(), media_type="application/x-ndjson",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


class ConfirmBody(BaseModel):
    id: str
    ok: bool


class OpenUrl(BaseModel):
    url: str


@app.post("/api/confirm")
def confirm(body: ConfirmBody):
    """El usuario pulsó Permitir / Cancelar en una tarjeta de confirmación."""
    return {"ok": safety.answer_confirmation(body.id, body.ok)}


@app.post("/api/open-url")
def open_url(body: OpenUrl):
    """Abre una fuente en el navegador, solo http/https."""
    if not body.url.startswith(("http://", "https://")):
        return JSONResponse({"error": "url inválida"}, status_code=400)
    if not config.DRY_RUN:
        webbrowser.open(body.url)
    return {"ok": True}


@app.get("/api/notifications")
def notifications(since: float = 0.0):
    return {"now": __import__("time").time(), "items": notes.notifications(since)}


@app.get("/api/agent/info")
def agent_info():
    return {"agent": config.AGENT, "shell": config.SHELL, "roots": [str(r) for r in safety.roots()],
            "research": settings.get()["research"],
            "tools": [{"name": t.name, "group": t.group, "confirm": bool(t.confirm)}
                      for t in tools.REGISTRY.values() if t.group != "web"]}


@app.on_event("startup")
def _startup():
    notes.start_scheduler()


@app.get("/")
def index():
    return FileResponse(FRONTEND / "index.html")


@app.get("/bubble")
def bubble():
    return FileResponse(FRONTEND / "bubble.html")


app.mount("/static", StaticFiles(directory=FRONTEND), name="static")
