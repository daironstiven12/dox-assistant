"""Escucha por voz, 100 % offline (Vosk): palabra de activación + comando (español o inglés).

Flujo:  "DOx, abre YouTube"        -> ejecuta el comando directamente
        "DOx" ... (pausa) "abre…"  -> responde "¿Sí?" y toma la siguiente frase

El modelo de voz se cambia solo cuando cambias el idioma en la interfaz.
Consumo: el modelo pequeño ocupa ~50 MB en disco y unos 150-250 MB de RAM,
con muy poco uso de CPU mientras escucha.
"""

import json
import queue
import threading
import time
from pathlib import Path

import speaker


def _tokens(text: str) -> list[str]:
    return text.lower().replace(",", " ").replace(".", " ").split()


def extract_command(text: str, wake_words: list[str]) -> tuple[bool, str]:
    """(¿se dijo la palabra de activación?, resto de la frase como comando)."""
    words = _tokens(text)
    for i, w in enumerate(words):
        if w in wake_words:
            return True, " ".join(words[i + 1:])
    return False, ""


class VoiceListener:
    def __init__(self, get_lang, model_paths: dict, wake_words, on_wake, on_command, window=7.0, debug=False):
        self.get_lang = get_lang
        self.model_paths = {k: Path(v) for k, v in model_paths.items()}
        self.wake_words = wake_words
        self.on_wake = on_wake
        self.on_command = on_command
        self.window = window
        self.debug = debug
        self._stop = threading.Event()

    def start(self) -> None:
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self) -> None:
        self._stop.set()

    @staticmethod
    def _spawn(fn, *args) -> None:
        threading.Thread(target=fn, args=args, daemon=True).start()

    def _run(self) -> None:
        try:
            import sounddevice as sd
            from vosk import KaldiRecognizer, Model, SetLogLevel
        except ImportError:
            print("[DOx voz] Falta instalar / missing: pip install -r backend/requirements-voice.txt")
            return
        SetLogLevel(-1)

        models: dict = {}   # se cargan bajo demanda; solo se queda en RAM el del idioma activo

        def recognizer_for(lang: str):
            path = self.model_paths.get(lang)
            if not path or not path.exists():
                print(f"[DOx voz] No encuentro el modelo de voz '{lang}' en {path} (mira el README).")
                return None
            for other in [k for k in models if k != lang]:
                del models[other]
            if lang not in models:
                models[lang] = Model(str(path))
            return KaldiRecognizer(models[lang], 16000)

        lang = self.get_lang()
        rec = recognizer_for(lang)
        if rec is None:
            return

        audio: "queue.Queue[bytes]" = queue.Queue()
        waiting_until = 0.0
        last_check = time.time()

        def callback(indata, frames, time_info, status):
            audio.put(bytes(indata))

        try:
            with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16",
                                   channels=1, callback=callback):
                print(f"[DOx voz] Escuchando ({lang}). Palabras: {', '.join(self.wake_words)}")
                while not self._stop.is_set():
                    if time.time() - last_check > 2:       # ¿cambió el idioma?
                        last_check = time.time()
                        new_lang = self.get_lang()
                        if new_lang != lang:
                            new_rec = recognizer_for(new_lang)
                            if new_rec is not None:
                                lang, rec = new_lang, new_rec
                                print(f"[DOx voz] Idioma de escucha: {lang}")
                            else:
                                lang = new_lang          # no reintentar cada 2 s
                    try:
                        data = audio.get(timeout=0.5)
                    except queue.Empty:
                        continue
                    if speaker.busy():          # no escucharse a sí mismo
                        rec.Reset()
                        continue
                    if not rec.AcceptWaveform(data):
                        continue
                    text = json.loads(rec.Result()).get("text", "").strip()
                    if not text:
                        continue
                    if self.debug:
                        print(f"[DOx oyó] {text}")

                    woke, command = extract_command(text, self.wake_words)
                    now = time.time()
                    if woke and command:
                        waiting_until = 0.0
                        self._spawn(self.on_command, command)
                    elif woke:
                        waiting_until = now + self.window
                        self._spawn(self.on_wake)
                    elif now < waiting_until:
                        waiting_until = 0.0
                        self._spawn(self.on_command, text)
        except Exception as e:
            print(f"[DOx voz] No pude usar el micrófono / mic error: {e}")
