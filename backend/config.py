"""Ajustes de DOx / DOx settings. Todo se puede cambiar con variables de entorno."""

import os
from pathlib import Path


def _bool(name: str, default: bool) -> bool:
    v = os.getenv(name)
    return default if v is None else v.strip().lower() in ("1", "true", "si", "sí", "yes", "on")


ROOT = Path(__file__).resolve().parent.parent

# --- Perfiles de consumo ------------------------------------------------------
# eco     -> equipos con poca RAM (4 GB) o sin GPU; respuestas cortas y rápidas
# normal  -> equilibrio (punto de partida)
# potente -> 8 GB de RAM o más; respuestas más largas y mejor calidad
# num_ctx = memoria de conversación del modelo. Ollama usa 4096 por defecto;
# bajarlo ahorra RAM y acelera, y para un asistente de chat corto sobra.
PROFILES = {
    "eco":     dict(model="qwen3.5:0.8b", num_ctx=3072, max_tokens=150, keep_alive="1m", history=4),
    "normal":  dict(model="qwen3.5:2b",   num_ctx=4096, max_tokens=300, keep_alive="3m", history=8),
    "potente": dict(model="qwen3.5:4b",   num_ctx=6144, max_tokens=500, keep_alive="5m", history=12),
}
PROFILE = os.getenv("DOX_PROFILE", "normal").strip().lower()
_p = PROFILES.get(PROFILE, PROFILES["normal"])

# --- Cerebro: IA local con Ollama -------------------------------------------
MODEL = os.getenv("DOX_MODEL", _p["model"])
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
# Cuánto tiempo se queda el modelo en RAM después de la última pregunta.
KEEP_ALIVE = os.getenv("DOX_KEEP_ALIVE", _p["keep_alive"])
NUM_CTX = int(os.getenv("DOX_NUM_CTX", _p["num_ctx"]))
MAX_TOKENS = int(os.getenv("DOX_MAX_TOKENS", _p["max_tokens"]))
MAX_HISTORY = int(os.getenv("DOX_MAX_HISTORY", _p["history"]))
TIMEOUT = int(os.getenv("DOX_TIMEOUT", "90"))

# --- Idioma / tema (valores iniciales; luego se guardan desde la interfaz) -----
DEFAULT_LANG = os.getenv("DOX_LANG", "es") if os.getenv("DOX_LANG", "es") in ("es", "en") else "es"

# --- Voz ---------------------------------------------------------------------
SPEAK = _bool("DOX_SPEAK", True)        # DOx tiene permitido hablar (el usuario lo activa en la interfaz)
VOICE = _bool("DOX_VOICE", False)       # escuchar la palabra de activación (requiere vosk)
VOICE_MODELS = {
    "es": os.getenv("DOX_VOICE_MODEL", str(ROOT / "models" / "vosk-model-small-es-0.42")),
    "en": os.getenv("DOX_VOICE_MODEL_EN", str(ROOT / "models" / "vosk-model-small-en-us-0.15")),
}
# Vosk no conoce la palabra "DOx": escribe aquí las formas en que suele "oírla".
WAKE_WORDS = [w.strip().lower() for w in os.getenv("DOX_WAKE_WORDS", "dox,doks,docs,dock,docks").split(",") if w.strip()]
VOICE_DEBUG = _bool("DOX_VOICE_DEBUG", False)   # imprime lo que oye, para ajustar WAKE_WORDS

# --- Voz neuronal (Piper) ------------------------------------------------------
# Si las voces están instaladas (python install_voice.py), DOx las usa; si no, cae a la voz robótica de espeak.
PIPER_DIR = Path(os.getenv("DOX_PIPER_DIR", str(ROOT / "models" / "piper")))
PIPER_VOICES = {
    "es": os.getenv("DOX_PIPER_ES", "es_MX-claude-high"),
    "en": os.getenv("DOX_PIPER_EN", "en_US-lessac-medium"),
}
VOICE_SPEED = float(os.getenv("DOX_VOICE_SPEED", "1.0"))   # <1 más rápido, >1 más lento
PLAYER = os.getenv("DOX_PLAYER", "")                       # reproductor de audio (se detecta solo)

# --- Marca (barra lateral) ----------------------------------------------------
BRAND = os.getenv("DOX_BRAND", "Ingenio Digital DSJB")
VERSION = "1.0.0"

# --- Modo agente (herramientas) ------------------------------------------------
AGENT = _bool("DOX_AGENT", True)                 # herramientas de archivos, internet, sistema, notas
SHELL = _bool("DOX_SHELL", True)                 # comandos de terminal (siempre con confirmación)
RESEARCH = os.getenv("DOX_RESEARCH", "auto")     # auto | always | off  (valor inicial; luego se cambia en Configuración)
SEARXNG_URL = os.getenv("DOX_SEARXNG", "").rstrip("/")   # opcional: tu propio SearXNG
BRAVE_KEY = os.getenv("DOX_BRAVE_KEY", "")                 # opcional: clave de la API de Brave Search
EXTRA_ROOTS = [r for r in os.getenv("DOX_ROOTS", "").split(os.pathsep) if r]   # carpetas extra permitidas
AGENT_TEMPERATURE = float(os.getenv("DOX_AGENT_TEMP", "0.2"))   # bajo = menos invención
MAX_STEPS = int(os.getenv("DOX_MAX_STEPS", "6"))

# --- Pruebas -------------------------------------------------------------------
DRY_RUN = _bool("DOX_DRY_RUN", False)   # si es True, las acciones no abren nada de verdad

SYSTEM_PROMPTS = {
    "es": (
        "Eres DOx, un asistente que vive en el escritorio del usuario. "
        "Hablas siempre en español, con tono amable y cercano, con un toque sutil de humor. "
        "Responde breve: máximo 3 frases, salvo que te pidan más detalle. "
        "No inventes datos: si no sabes algo, dilo. "
        "Puedes abrir páginas web y programas cuando el usuario te lo pide (por ejemplo 'abre YouTube'), "
        "pero nunca afirmes haber hecho algo que no hiciste."
    ),
    "en": (
        "You are DOx, an assistant that lives on the user's desktop. "
        "You always speak in English, in a friendly, approachable tone with a light touch of humor. "
        "Keep answers short: at most 3 sentences unless asked for more detail. "
        "Don't make things up: if you don't know something, say so. "
        "You can open websites and programs when asked (for example 'open YouTube'), "
        "but never claim to have done something you didn't do."
    ),
}
