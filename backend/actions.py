"""Acciones que DOx puede ejecutar en tu computador (órdenes en español o inglés).

SEGURIDAD: DOx NO ejecuta comandos arbitrarios. Solo abre páginas web y los
programas de una lista blanca (APPS). Para permitir más, agrégalos a SITES o APPS.
"""

import os
import re
import shutil
import subprocess
import sys
import unicodedata
import webbrowser
from urllib.parse import quote_plus

import config

PLAT = "windows" if sys.platform.startswith("win") else "mac" if sys.platform == "darwin" else "linux"

SITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "correo": "https://mail.google.com",
    "email": "https://mail.google.com",
    "drive": "https://drive.google.com",
    "maps": "https://maps.google.com",
    "google maps": "https://maps.google.com",
    "whatsapp": "https://web.whatsapp.com",
    "tiktok": "https://www.tiktok.com",
    "instagram": "https://www.instagram.com",
    "facebook": "https://www.facebook.com",
    "github": "https://github.com",
    "claude": "https://claude.ai",
    "chatgpt": "https://chatgpt.com",
    "spotify": "https://open.spotify.com",
    "netflix": "https://www.netflix.com",
    "traductor": "https://translate.google.com",
    "translator": "https://translate.google.com",
}

# nombre -> cómo abrirlo en cada sistema
APPS = {
    "calculadora": {"windows": "calc", "mac": "Calculator",
                    "linux": ["gnome-calculator", "kcalc", "galculator", "qalculate-gtk"]},
    "bloc de notas": {"windows": "notepad", "mac": "TextEdit",
                      "linux": ["gnome-text-editor", "gedit", "kate", "mousepad"]},
    "explorador": {"windows": "explorer", "mac": "Finder",
                   "linux": ["dolphin", "nautilus", "thunar", "nemo"]},
    "paint": {"windows": "mspaint", "mac": "Preview", "linux": ["gimp", "kolourpaint"]},
}

ALIASES = {
    "archivos": "explorador", "carpetas": "explorador", "explorador de archivos": "explorador",
    "files": "explorador", "file manager": "explorador", "explorer": "explorador",
    "notas": "bloc de notas", "notepad": "bloc de notas", "notes": "bloc de notas",
    "text editor": "bloc de notas", "calc": "calculadora", "calculator": "calculadora",
    "internet": "navegador", "chrome": "navegador", "edge": "navegador", "firefox": "navegador",
    "browser": "navegador",
}

# (acción de ventana, patrón, respuesta es, respuesta en)
UI_PATTERNS = [
    ("fullscreen", r"\b(pantalla completa|maximizate|maximiza la ventana|ponte en grande|full ?screen|maximize)\b",
     "Listo, pantalla completa.", "Done, going fullscreen."),
    ("minimize", r"\b(minimizate|minimiza|ocultate|escondete|modo burbuja|a un lado|ponte pequeno|minimize|hide yourself|bubble mode|shrink)\b",
     "Listo, me hago pequeño y me quedo a un lado.", "Done, shrinking down to the side."),
    ("show", r"\b(abre la ventana|abre el chat|muestrate|abrete|ven aca|show yourself|open the window|come here|open chat)\b",
     "Aquí estoy.", "I'm here."),
]

T = {
    "es": {
        "opening": "Abriendo {x}…",
        "fail": "No logré abrir {x} en este equipo.",
        "unknown": "No tengo «{x}» en mi lista de programas. Puedes agregarlo en backend/actions.py (SITES o APPS).",
        "google": "Buscando «{x}» en Google…",
        "youtube": "Buscando «{x}» en YouTube…",
    },
    "en": {
        "opening": "Opening {x}…",
        "fail": "I couldn't open {x} on this computer.",
        "unknown": "I don't have “{x}” in my list of programs. You can add it in backend/actions.py (SITES or APPS).",
        "google": "Searching “{x}” on Google…",
        "youtube": "Searching “{x}” on YouTube…",
    },
}


def _norm(text: str) -> str:
    t = unicodedata.normalize("NFD", text.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = re.sub(r"[¿?¡!,;:]", " ", t)
    t = re.sub(r"\.(?=\s|$)", " ", t)   # quita puntos de frase, pero conserva los de "youtube.com"
    return re.sub(r"\s+", " ", t).strip()


def _open_url(url: str) -> None:
    if not config.DRY_RUN:
        webbrowser.open(url)


def _launch_app(name: str) -> bool:
    spec = APPS[name]
    if config.DRY_RUN:
        return True
    try:
        if PLAT == "windows":
            os.startfile(spec["windows"])  # type: ignore[attr-defined]
            return True
        if PLAT == "mac":
            subprocess.Popen(["open", "-a", spec["mac"]])
            return True
        for cmd in spec["linux"]:
            if shutil.which(cmd):
                subprocess.Popen([cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                 start_new_session=True)
                return True
    except OSError:
        pass
    return False


def _open(target: str, lang: str) -> dict:
    s = T[lang]
    shown = target
    target = ALIASES.get(target, target)
    ok = lambda action: {"reply": s["opening"].format(x=shown), "mood": "happy", "action": action}
    if target in SITES:
        _open_url(SITES[target])
        return ok("open_site")
    if target == "navegador":
        _open_url("https://www.google.com")
        return ok("open_site")
    if target in APPS:
        if _launch_app(target):
            return ok("open_app")
        return {"reply": s["fail"].format(x=shown), "mood": "surprised", "action": "error"}
    if re.fullmatch(r"[a-z0-9-]+(\.[a-z0-9-]+)+(/\S*)?", target):
        _open_url("https://" + target)
        return ok("open_site")
    return {"reply": s["unknown"].format(x=shown), "mood": "thinking", "action": "unknown"}


def _search(query: str, engine: str | None, lang: str) -> dict:
    if engine == "youtube":
        _open_url("https://www.youtube.com/results?search_query=" + quote_plus(query))
        key = "youtube"
    else:
        _open_url("https://www.google.com/search?q=" + quote_plus(query))
        key = "google"
    return {"reply": T[lang][key].format(x=query), "mood": "happy", "action": "search"}


def try_action(text: str, lang: str = "es") -> dict | None:
    """Devuelve {'reply','mood',...} si el texto es una orden que DOx sabe ejecutar; si no, None."""
    lang = lang if lang in T else "es"
    t = _norm(text)
    t = re.sub(r"^(hey |oye |ey )?(dox|doks|docs|dock|docks)\b ?", "", t)

    for ui, pattern, es, en in UI_PATTERNS:
        if re.search(pattern, t):
            return {"reply": es if lang == "es" else en, "mood": "happy", "action": "ui", "ui": ui}

    m = re.match(r"^(?:por favor |please )?(?:abre|abrir|abreme|inicia|iniciar|lanza|ejecuta|open|launch|start|run) "
                 r"(?:el |la |los |las |un |una |mi |the |my |a )?(.+?)(?: por favor| please)?$", t)
    if m:
        return _open(m.group(1).strip(), lang)

    m = re.match(r"^(?:por favor |please )?(?:busca|buscar|buscame|googlea|investiga|search for|search|google|look up) "
                 r"(.+?)(?: (?:en|on|in) (google|youtube))?$", t)
    if m:
        return _search(m.group(1).strip(), m.group(2), lang)

    m = re.match(r"^(?:por favor |please )?(?:pon|ponme|reproduce|reproducir|play) (.+)$", t)
    if m:
        return _search(m.group(1).strip(), "youtube", lang)

    return None
