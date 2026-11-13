"""Lanzador de escritorio de DOx.

  python desktop.py            abre DOx en su ventana
  python desktop.py --boot     arranca minimizado (burbuja a un lado) y saluda; para el inicio del PC
  python desktop.py --web      sin ventana propia: abre el navegador

DOx tiene dos ventanas: la principal (chat) y una burbuja pequeña, siempre visible,
con solo la mascota. Cerrar la ventana principal no cierra DOx: lo deja como burbuja.
"""

import argparse
import json
import sys
import threading
import time
import urllib.request
import webbrowser
from datetime import datetime
from pathlib import Path

import uvicorn

sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

import config  # noqa: E402
import settings  # noqa: E402
import speaker  # noqa: E402
import voice  # noqa: E402
from brain import think  # noqa: E402
from main import app  # noqa: E402

HOST, PORT = "127.0.0.1", 8765
URL = f"http://{HOST}:{PORT}"
ICON = Path(__file__).resolve().parent / "frontend" / "assets" / "icon-512.png"


def is_up() -> bool:
    try:
        urllib.request.urlopen(f"{URL}/api/health", timeout=1)
        return True
    except Exception:
        return False


def wait_until_ready(timeout=15) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        if is_up():
            return True
        time.sleep(0.2)
    return False


def greeting(lang: str) -> str:
    h = datetime.now().hour
    if lang == "en":
        hi = "Good morning" if h < 12 else "Good afternoon" if h < 19 else "Good evening"
        return f"{hi}. I'm DOx, ready to help."
    hi = "Buenos días" if h < 12 else "Buenas tardes" if h < 19 else "Buenas noches"
    return f"{hi}. Soy DOx, ya estoy listo para ayudarte."


def window_bg() -> str:
    """Color de fondo mientras carga la página (evita un destello del color equivocado)."""
    return "#f6f6ea" if settings.get()["theme"] == "light" else "#0f141b"


class Api:
    """Funciones que la interfaz llama con window.pywebview.api.<nombre>()"""

    def __init__(self, shell):
        self._shell = shell

    def minimize(self):
        self._shell.to_bubble()

    def open_full(self):
        self._shell.to_full()

    def quit(self):
        self._shell.quit()

    def listening(self):
        return self._shell.listener is not None

    def toggle_listen(self):
        """Enciende/apaga el micrófono (palabra de activación). Devuelve {'on': bool, 'error': str|None}."""
        return self._shell.set_listening(self._shell.listener is None)


class Shell:
    def __init__(self, webview, boot: bool):
        self.webview = webview
        self.mode = "bubble" if boot else "full"
        self.boot = boot
        self.quitting = False
        self.history: list[dict] = []
        self.listener = None
        self.main = self.bubble = None

    # ---------- ventanas ----------
    def create_windows(self):
        api = Api(self)
        x = y = None
        try:
            s = self.webview.screens[0]
            x, y = s.width - 230, s.height - 340
        except Exception:
            pass
        self.main = self.webview.create_window(
            "DOx", URL, js_api=api, width=1000, height=680, min_size=(700, 500),
            hidden=(self.mode == "bubble"), background_color=window_bg())
        self.bubble = self.webview.create_window(
            "DOx burbuja", URL + "/bubble", js_api=api, width=170, height=210, x=x, y=y,
            frameless=True, on_top=True, easy_drag=True, resizable=False,
            hidden=(self.mode == "full"), background_color=window_bg())
        self.main.events.closing += self._on_main_closing

    def _on_main_closing(self):
        if self.quitting:
            return True
        self.to_bubble()      # cerrar la ventana = dejar a DOx en la burbuja
        return False

    def to_bubble(self):
        self.mode = "bubble"
        self.bubble.show()
        self.main.hide()

    def to_full(self):
        self.mode = "full"
        self.main.show()
        self.bubble.hide()

    def run_ui(self, ui):
        if ui == "minimize":
            self.to_bubble()
        elif ui == "show":
            self.to_full()
        elif ui == "fullscreen":
            self.to_full()
            self.main.toggle_fullscreen()

    def quit(self):
        self.quitting = True
        if self.listener:
            self.listener.stop()
        for w in list(self.webview.windows):
            w.destroy()

    # ---------- comunicación con las páginas ----------
    def _eval(self, js: str):
        w = self.main if self.mode == "full" else self.bubble
        try:
            w.evaluate_js(js)
        except Exception as e:
            print(f"[DOx] no pude actualizar la ventana: {e}")

    def push(self, payload: dict):
        self._eval(f"window.doxIncoming && window.doxIncoming({json.dumps(payload, ensure_ascii=False)})")

    # ---------- eventos ----------
    def on_ready(self):
        """Se ejecuta cuando la interfaz ya está viva."""
        time.sleep(1.5)
        if self.boot:
            text = greeting(settings.lang())      # saludo fijo: no despierta a la IA, no gasta recursos
            self.push({"reply": text, "mood": "happy"})
            speaker.say(text)
        if config.VOICE:
            self.set_listening(True)
        threading.Thread(target=self.watch_reminders, daemon=True).start()

    def watch_reminders(self):
        """Cuando vence un recordatorio, DOx lo dice en voz alta y lo muestra en la burbuja."""
        from tools import notes
        seen = time.time()
        while True:
            time.sleep(5)
            for n in notes.notifications(seen):
                seen = max(seen, n["ts"])
                text = ("Recordatorio: " if settings.lang() == "es" else "Reminder: ") + n["text"]
                self.push({"reply": "⏰ " + text, "mood": "surprised"})
                if settings.get()["speak"]:
                    speaker.say(text)

    def set_listening(self, on: bool) -> dict:
        if not on:
            if self.listener:
                self.listener.stop()
            self.listener = None
            return {"on": False, "error": None}
        try:
            import sounddevice  # noqa: F401
            import vosk  # noqa: F401
        except ImportError:
            return {"on": False, "error": "deps"}
        if not Path(config.VOICE_MODELS.get(settings.lang(), "")).exists():
            return {"on": False, "error": "model"}
        self.listener = voice.VoiceListener(
            settings.lang, config.VOICE_MODELS, config.WAKE_WORDS,
            on_wake=self.on_wake, on_command=self.on_voice_command, debug=config.VOICE_DEBUG)
        self.listener.start()
        return {"on": True, "error": None}

    def on_wake(self):
        self._eval("window.doxListening && window.doxListening()")
        speaker.say("Yes?" if settings.lang() == "en" else "¿Sí?")

    def on_voice_command(self, text: str):
        result = think(text, self.history[-config.MAX_HISTORY:], settings.lang())
        self.history += [{"role": "user", "content": text},
                         {"role": "assistant", "content": result["reply"]}]
        self.history = self.history[-20:]
        self.push({"user": text, "reply": result["reply"], "mood": result.get("mood", "idle")})
        speaker.say(result["reply"])
        if result.get("ui"):
            threading.Timer(1.0, self.run_ui, [result["ui"]]).start()


def run_server():
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")


def main():
    ap = argparse.ArgumentParser(description="DOx, tu buey robot asistente")
    ap.add_argument("--boot", action="store_true", help="arrancar minimizado y saludar")
    ap.add_argument("--web", action="store_true", help="abrir en el navegador en vez de ventana propia")
    args = ap.parse_args()

    if is_up():
        sys.exit("DOx ya está en ejecución.")
    threading.Thread(target=run_server, daemon=True).start()
    if not wait_until_ready():
        sys.exit("El servidor de DOx no arrancó a tiempo.")

    try:
        if args.web:
            raise ImportError
        import webview
    except ImportError:
        print(f"Abriendo DOx en el navegador: {URL}")
        webbrowser.open(URL)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            return

    shell = Shell(webview, boot=args.boot)
    app.state.speak = speaker.say
    app.state.ui_handler = shell.run_ui
    shell.create_windows()
    try:
        webview.start(shell.on_ready, icon=str(ICON))      # icono de la ventana (Qt/GTK)
    except TypeError:
        webview.start(shell.on_ready)


if __name__ == "__main__":
    main()
