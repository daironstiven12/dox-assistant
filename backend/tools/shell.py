"""Terminal: un solo comando simple, sin shell, siempre con confirmación."""

import subprocess

import config
import safety
from safety import ToolError

from . import S, tool


def _confirm(a: dict):
    safety.check_command(str(a.get("command", "")))   # si es peligroso, ni siquiera se pide permiso
    return ("Ejecutar este comando", str(a.get("command", "")))


@tool("shell", "Ejecuta UN comando simple de terminal (sin pipes ni sudo) y devuelve su salida. Pide permiso al usuario. "
               "Úsalo solo para consultar (df -h, free -h, uname -a, ls, systemctl status X…).",
      {"command": S("comando completo, p. ej. 'df -h'")}, ["command"], confirm=_confirm)
def run_command(command: str) -> str:
    argv = safety.check_command(command)
    if config.DRY_RUN:
        return f"(simulado) {command}"
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL)
    except FileNotFoundError:
        raise ToolError(f"No existe el programa «{argv[0]}».")
    except subprocess.TimeoutExpired:
        raise ToolError("El comando tardó más de 30 segundos y se canceló.")
    out = (r.stdout or "") + (("\n[stderr] " + r.stderr) if r.stderr.strip() else "")
    out = out.strip()
    if len(out) > 3000:
        out = out[:3000] + "\n… (salida recortada)"
    return f"Código de salida {r.returncode}.\n{out or '(sin salida)'}"
