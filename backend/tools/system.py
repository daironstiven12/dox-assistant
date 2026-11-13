"""Sistema: info, volumen, brillo, captura, portapapeles, abrir y cerrar apps."""

import configparser
import glob
import os
import platform
import shutil
import signal
import subprocess
import time
from pathlib import Path

import config
from safety import ToolError, norm

from . import N, S, tool

PROTECTED = {"systemd", "init", "dbus-daemon", "kwin_wayland", "kwin_x11", "plasmashell", "sddm", "gdm", "Xorg", "Xwayland",
             "pipewire", "wireplumber", "ollama", "NetworkManager", "python", "python3", "dox", "desktop.py"}


def _run(argv, timeout=10) -> str:
    if config.DRY_RUN:
        return "(simulado)"
    r = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    return (r.stdout or r.stderr).strip()


@tool("system", "Muestra información del equipo: sistema, RAM, disco, batería y tiempo encendido.", {}, [])
def system_info() -> str:
    lines = [f"Sistema: {platform.system()} {platform.release()}", f"CPU núcleos: {os.cpu_count()}"]
    try:
        mem = {k: int(v.split()[0]) for k, v in (l.split(":", 1) for l in open("/proc/meminfo"))}
        tot, av = mem["MemTotal"] / 1048576, mem["MemAvailable"] / 1048576
        lines.append(f"RAM: {tot - av:.1f} GB usados de {tot:.1f} GB")
    except Exception:
        pass
    du = shutil.disk_usage(Path.home())
    lines.append(f"Disco: {du.used / 1e9:.0f} GB usados de {du.total / 1e9:.0f} GB ({du.free / 1e9:.0f} GB libres)")
    try:
        up = float(open("/proc/uptime").read().split()[0])
        lines.append(f"Encendido hace {int(up // 3600)} h {int(up % 3600 // 60)} min")
    except Exception:
        pass
    for bat in glob.glob("/sys/class/power_supply/BAT*"):
        try:
            lines.append(f"Batería: {Path(bat, 'capacity').read_text().strip()}% ({Path(bat, 'status').read_text().strip()})")
        except Exception:
            pass
    return "\n".join(lines)


@tool("system", "Consulta o cambia el volumen del sistema (0-100). Sin 'level' solo lo consulta.",
      {"level": N("volumen 0-100 (opcional)")}, [])
def volume(level: float | None = None) -> str:
    wp, pa = shutil.which("wpctl"), shutil.which("pactl")
    if level is None:
        if wp:
            return "Volumen: " + _run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"])
        if pa:
            return _run(["pactl", "get-sink-volume", "@DEFAULT_SINK@"])
        raise ToolError("No encontré wpctl ni pactl para controlar el volumen.")
    lv = int(max(0, min(100, float(level))))
    if wp:
        _run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{lv}%"])
    elif pa:
        _run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{lv}%"])
    else:
        raise ToolError("No encontré wpctl ni pactl para controlar el volumen.")
    return f"Volumen en {lv}%."


@tool("system", "Silencia o activa el sonido del sistema.", {}, [])
def toggle_mute() -> str:
    if shutil.which("wpctl"):
        _run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"])
    elif shutil.which("pactl"):
        _run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])
    else:
        raise ToolError("No encontré wpctl ni pactl.")
    return "Sonido silenciado/activado (alternado)."


@tool("system", "Cambia el brillo de pantalla (1-100).", {"level": N("brillo 1-100")}, ["level"])
def brightness(level: float) -> str:
    if not shutil.which("brightnessctl"):
        raise ToolError("Falta brightnessctl (sudo dnf install brightnessctl).")
    lv = int(max(1, min(100, float(level))))
    _run(["brightnessctl", "set", f"{lv}%"])
    return f"Brillo en {lv}%."


@tool("system", "Toma una captura de pantalla y la guarda en Imágenes/DOx.", {}, [])
def screenshot() -> str:
    out_dir = Path.home() / "Imágenes" / "DOx"
    if not (Path.home() / "Imágenes").is_dir():
        out_dir = Path.home() / "Pictures" / "DOx"
    out_dir.mkdir(parents=True, exist_ok=True)
    f = out_dir / time.strftime("captura-%Y%m%d-%H%M%S.png")
    for argv in (["spectacle", "-b", "-n", "-f", "-o", str(f)], ["gnome-screenshot", "-f", str(f)],
                 ["grim", str(f)], ["scrot", str(f)]):
        if shutil.which(argv[0]):
            if config.DRY_RUN:
                return f"(simulado) {f}"
            subprocess.run(argv, capture_output=True, timeout=15)
            if f.exists():
                return f"Captura guardada en {f}"
    raise ToolError("No encontré spectacle, gnome-screenshot, grim ni scrot.")


@tool("system", "Copia un texto al portapapeles.", {"text": S("texto")}, ["text"])
def clipboard_copy(text: str) -> str:
    for argv in (["wl-copy"], ["xclip", "-selection", "clipboard"], ["xsel", "-ib"]):
        if shutil.which(argv[0]):
            if not config.DRY_RUN:
                subprocess.run(argv, input=str(text), text=True, timeout=5)
            return "Copiado al portapapeles."
    raise ToolError("Falta wl-clipboard o xclip.")


def _desktop_entries() -> list[tuple[str, str, str]]:
    dirs = [Path.home() / ".local/share/applications", Path("/usr/share/applications"),
            Path("/var/lib/flatpak/exports/share/applications"), Path.home() / ".local/share/flatpak/exports/share/applications"]
    out = []
    for d in dirs:
        for f in d.glob("*.desktop") if d.is_dir() else []:
            cp = configparser.ConfigParser(interpolation=None, strict=False)
            try:
                cp.read(f, encoding="utf-8")
                e = cp["Desktop Entry"]
            except Exception:
                continue
            if e.get("NoDisplay", "").lower() == "true" or e.get("Type") != "Application":
                continue
            out.append((norm(e.get("Name", "")), e.get("Name", f.stem), str(f)))
    return out


@tool("system", "Abre un programa instalado por su nombre (Firefox, Calculadora, Spotify…).",
      {"name": S("nombre del programa")}, ["name"])
def open_app(name: str) -> str:
    q = norm(name)
    entries = _desktop_entries()
    exact = [e for e in entries if e[0] == q] or [e for e in entries if q and q in e[0]]
    if not exact:
        raise ToolError(f"No encontré un programa llamado «{name}» instalado.")
    _, label, path = sorted(exact, key=lambda e: len(e[0]))[0]
    if not config.DRY_RUN:
        launcher = ["gio", "launch", path] if shutil.which("gio") else ["gtk-launch", Path(path).stem]
        subprocess.Popen(launcher, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    return f"Abriendo {label}."


def _confirm_close(a: dict):
    return (f"Cerrar el programa «{a.get('name', '?')}»", "Se le pedirá que cierre (SIGTERM); podrías perder cambios sin guardar.")


@tool("system", "Cierra un programa en ejecución por su nombre. Pide permiso al usuario.",
      {"name": S("nombre del proceso, p. ej. firefox")}, ["name"], confirm=_confirm_close)
def close_app(name: str) -> str:
    q = norm(name).replace(" ", "")
    if len(q) < 3:
        raise ToolError("Nombre demasiado corto.")
    me = os.getpid()
    hits = []
    for p in Path("/proc").iterdir():
        if not p.name.isdigit() or int(p.name) == me:
            continue
        try:
            comm = (p / "comm").read_text().strip()
            if Path(p / "stat").stat().st_uid != os.getuid():
                continue
        except Exception:
            continue
        if comm in PROTECTED:
            continue
        if q in norm(comm).replace(" ", ""):
            hits.append((int(p.name), comm))
    if not hits:
        raise ToolError(f"No encontré ningún programa tuyo llamado «{name}» en ejecución.")
    if not config.DRY_RUN:
        for pid, _ in hits:
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError:
                pass
    return f"Pedí cerrar {hits[0][1]} ({len(hits)} proceso(s))."
