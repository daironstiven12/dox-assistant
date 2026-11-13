"""Preferencias del usuario (idioma, tema, voz). Se guardan en un archivo JSON pequeño
para que la ventana, la burbuja y la escucha por voz usen siempre lo mismo."""

import json
import os
import sys
import threading
from pathlib import Path

import config


def _dir() -> Path:
    if sys.platform.startswith("win"):
        base = Path(os.environ.get("APPDATA", Path.home()))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "dox"


PATH = _dir() / "settings.json"
LANGS = ("es", "en")
THEMES = ("light", "dark", "system")
RESEARCH = ("auto", "always", "off")
_lock = threading.Lock()


def _defaults() -> dict:
    return {"lang": config.DEFAULT_LANG, "theme": "system", "speak": True,
            "research": config.RESEARCH if config.RESEARCH in RESEARCH else "auto"}


def get() -> dict:
    data = _defaults()
    try:
        saved = json.loads(PATH.read_text(encoding="utf-8"))
        if saved.get("lang") in LANGS:
            data["lang"] = saved["lang"]
        if saved.get("theme") in THEMES:
            data["theme"] = saved["theme"]
        if isinstance(saved.get("speak"), bool):
            data["speak"] = saved["speak"]
        if saved.get("research") in RESEARCH:
            data["research"] = saved["research"]
    except (OSError, ValueError):
        pass
    return data


def update(patch: dict) -> dict:
    with _lock:
        data = get()
        if patch.get("lang") in LANGS:
            data["lang"] = patch["lang"]
        if patch.get("theme") in THEMES:
            data["theme"] = patch["theme"]
        if isinstance(patch.get("speak"), bool):
            data["speak"] = patch["speak"]
        if patch.get("research") in RESEARCH:
            data["research"] = patch["research"]
        try:
            PATH.parent.mkdir(parents=True, exist_ok=True)
            PATH.write_text(json.dumps(data), encoding="utf-8")
        except OSError as e:
            print(f"[DOx] no pude guardar las preferencias: {e}")
        return data


def lang() -> str:
    return get()["lang"]
