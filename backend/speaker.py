"""Voz de DOx, sin internet.

Motor preferido: Piper (voz neuronal, natural). Si no está instalado o falta la voz,
cae a espeak vía pyttsx3 (robótica, pero siempre disponible).

Las frases se sintetizan por separado y mientras suena una ya se prepara la siguiente,
así DOx empieza a hablar enseguida aunque la respuesta sea larga.
"""

import os
import queue
import re
import shutil
import subprocess
import tempfile
import threading
import time
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import config
import settings

_q: "queue.Queue[tuple[str, str]]" = queue.Queue()
_started = False
_speaking = threading.Event()
_last_end = 0.0
_voices: dict = {}          # lang -> PiperVoice (o None si no está disponible)
_voices_lock = threading.Lock()
_synth_pool = ThreadPoolExecutor(max_workers=1)

_VOICE_KEYS = {
    "es": ("spanish", "español", "espanol", "es-", "es_", "\\x05es"),
    "en": ("english", "en-us", "en-gb", "en_", "en-", "\\x05en"),
}


# ---------------------------------------------------------------- Piper
def _piper_files(lang: str):
    name = config.PIPER_VOICES.get(lang, "")
    model = config.PIPER_DIR / f"{name}.onnx"
    cfg = config.PIPER_DIR / f"{name}.onnx.json"
    return (model, cfg) if name and model.exists() and cfg.exists() else None


def _piper_voice(lang: str):
    """Carga (una sola vez) la voz de Piper para el idioma; None si no se puede."""
    with _voices_lock:
        if lang in _voices:
            return _voices[lang]
        voice = None
        files = _piper_files(lang)
        if files:
            try:
                from piper import PiperVoice

                voice = PiperVoice.load(str(files[0]), config_path=str(files[1]))
            except Exception as e:
                print(f"[DOx voz] No pude cargar Piper ({lang}): {e}")
        _voices[lang] = voice
        return voice


def _player_cmd():
    if config.PLAYER:
        return config.PLAYER.split()
    for cmd, args in (("pw-play", []), ("paplay", []), ("aplay", ["-q"]),
                      ("ffplay", ["-nodisp", "-autoexit", "-loglevel", "quiet"])):
        if shutil.which(cmd):
            return [cmd] + args
    return None


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?…])\s+|\n+", text)
    out, buf = [], ""
    for p in parts:                      # junta frases muy cortas para que no suene entrecortado
        buf = f"{buf} {p}".strip()
        if len(buf) >= 25:
            out.append(buf)
            buf = ""
    if buf:
        out.append(buf)
    return out or [text]


def _synth_to_wav(voice, text: str) -> str:
    from piper import SynthesisConfig

    fd, path = tempfile.mkstemp(suffix=".wav", prefix="dox_")
    os.close(fd)
    with wave.open(path, "wb") as wf:
        voice.synthesize_wav(text, wf, SynthesisConfig(length_scale=config.VOICE_SPEED))
    return path


def _speak_piper(text: str, lang: str) -> bool:
    voice = _piper_voice(lang)
    player = _player_cmd()
    if voice is None or player is None:
        return False
    futures = [_synth_pool.submit(_synth_to_wav, voice, s) for s in _split_sentences(text)]
    ok = True
    for fut in futures:
        try:
            path = fut.result(timeout=120)
        except Exception as e:
            print(f"[DOx voz] Piper falló: {e}")
            ok = False
            continue
        try:
            subprocess.run(player + [path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
        except Exception as e:
            print(f"[DOx voz] No pude reproducir el audio: {e}")
            ok = False
        finally:
            Path(path).unlink(missing_ok=True)
    return ok


# -------------------------------------------------------------- respaldo (espeak)
def _pick_voice(engine, lang: str):
    try:
        for v in engine.getProperty("voices"):
            blob = f"{v.id} {v.name} {v.languages}".lower()
            if any(k in blob for k in _VOICE_KEYS.get(lang, ())):
                return v.id
    except Exception:
        pass
    return None


def _speak_espeak(text: str, lang: str) -> None:
    try:
        import pyttsx3

        engine = pyttsx3.init()
        voice = _pick_voice(engine, lang)
        if voice:
            engine.setProperty("voice", voice)
        engine.setProperty("rate", 170)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:  # sin voz instalada, sin pyttsx3, etc.
        print(f"[DOx voz] no pude hablar / couldn't speak: {e}")


# ------------------------------------------------------------------ cola
def _worker():
    global _last_end
    while True:
        text, lang = _q.get()
        _speaking.set()
        try:
            if not _speak_piper(text, lang):
                _speak_espeak(text, lang)
        finally:
            _last_end = time.time()
            if _q.empty():
                _speaking.clear()


def say(text: str, lang: str | None = None) -> None:
    """Pone el texto en cola para leerlo en voz alta (no bloquea)."""
    global _started
    if not config.SPEAK or not text:
        return
    clean = re.sub(r"[*_`#>]", "", text).strip()[:800]
    if not clean:
        return
    if not _started:
        threading.Thread(target=_worker, daemon=True).start()
        _started = True
    _q.put((clean, lang or settings.lang()))


def busy() -> bool:
    """True mientras DOx habla (y un instante después), para que no se escuche a sí mismo."""
    return _speaking.is_set() or not _q.empty() or (time.time() - _last_end) < 1.0


def info() -> dict:
    """Qué motor de voz se usaría ahora mismo, para mostrarlo en Configuración."""
    lang = settings.lang()
    installed = sorted(p.name[:-5] for p in config.PIPER_DIR.glob("*.onnx")) if config.PIPER_DIR.exists() else []
    has_piper_pkg = True
    try:
        import piper  # noqa: F401
    except Exception:
        has_piper_pkg = False
    files = _piper_files(lang)
    if files and has_piper_pkg and _player_cmd():
        engine, voice = "piper", config.PIPER_VOICES[lang]
    else:
        engine, voice = "espeak", ""
    return {"engine": engine, "voice": voice, "installed": installed, "piper_package": has_piper_pkg,
            "player": bool(_player_cmd()), "wanted": config.PIPER_VOICES}
