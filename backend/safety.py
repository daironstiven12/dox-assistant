"""Seguridad del modo agente: carpetas permitidas, bloqueo de comandos peligrosos y confirmaciones.

Principios:
  * Leer, buscar y abrir son automáticos.
  * Todo lo que modifica algo (crear/mover/borrar archivos, comandos, cerrar apps) pide confirmación.
  * Solo se toca lo que está dentro de las carpetas permitidas (Documentos, Descargas, Escritorio, Imágenes).
  * Los comandos destructivos (rm, sudo, dd, mkfs, apagar…) están bloqueados siempre.
"""

import re
import shlex
import shutil
import subprocess
import threading
import unicodedata
import uuid
from pathlib import Path

import config


class ToolError(Exception):
    """Error "esperado" de una herramienta; el mensaje se le muestra al modelo y al usuario tal cual."""


# ------------------------------------------------------------------ texto
def norm(text: str) -> str:
    t = unicodedata.normalize("NFD", str(text).lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[\s_\-.]+", " ", t).strip()


# ------------------------------------------------------------------ carpetas permitidas
_roots_cache: list[Path] | None = None


def _xdg(name: str, *fallbacks: str) -> Path | None:
    if shutil.which("xdg-user-dir"):
        try:
            out = subprocess.run(["xdg-user-dir", name], capture_output=True, text=True, timeout=2).stdout.strip()
            if out and Path(out).is_dir() and Path(out) != Path.home():
                return Path(out)
        except Exception:
            pass
    for f in fallbacks:
        p = Path.home() / f
        if p.is_dir():
            return p
    return None


def roots() -> list[Path]:
    global _roots_cache
    if _roots_cache is None:
        found = [_xdg("DOCUMENTS", "Documentos", "Documents"), _xdg("DOWNLOAD", "Descargas", "Downloads"),
                 _xdg("DESKTOP", "Escritorio", "Desktop"), _xdg("PICTURES", "Imágenes", "Imagenes", "Pictures")]
        found += [Path(r).expanduser() for r in config.EXTRA_ROOTS]
        _roots_cache = []
        for p in found:
            if p and p.is_dir():
                rp = p.resolve()
                if rp not in _roots_cache:
                    _roots_cache.append(rp)
    return _roots_cache


def reset_roots() -> None:
    global _roots_cache
    _roots_cache = None


def resolve(path: str, must_exist: bool = True) -> Path:
    """Convierte una ruta del modelo en una ruta real SEGURA (dentro de las carpetas permitidas)."""
    if not path or not str(path).strip():
        raise ToolError("Falta la ruta.")
    p = Path(str(path).strip()).expanduser()
    if not p.is_absolute():
        raise ToolError("Usa la ruta completa que devolvió find_files (empieza con /).")
    rp = p.resolve()                      # resuelve «..» y enlaces simbólicos antes de comprobar
    for root in roots():
        if rp == root or root in rp.parents:
            rel = rp.relative_to(root)
            if any(part.startswith(".") for part in rel.parts):
                raise ToolError("No se permiten archivos ocultos.")
            if must_exist and not rp.exists():
                raise ToolError(f"No existe: {rp}")
            return rp
    allowed = ", ".join(str(r) for r in roots()) or "(ninguna)"
    raise ToolError(f"Esa ruta está fuera de las carpetas permitidas ({allowed}).")


BLOCKED_EXT = {".sh", ".bash", ".zsh", ".fish", ".desktop", ".exe", ".bat", ".cmd", ".msi", ".com", ".scr",
               ".ps1", ".vbs", ".appimage", ".run", ".bin", ".jar", ".dll", ".so", ".pyc", ".service", ".timer"}


def check_extension(path: Path) -> None:
    if path.suffix.lower() in BLOCKED_EXT:
        raise ToolError(f"Por seguridad no abro ni creo archivos «{path.suffix}» (programas o scripts).")


# ------------------------------------------------------------------ comandos
_META = re.compile(r"[;|&<>`$\n\r]")
_WRAPPERS = {"env", "nohup", "timeout", "nice", "ionice", "time", "xargs", "watch", "exec", "command", "busybox",
             "bash", "sh", "zsh", "fish", "dash", "ksh", "csh", "tcsh", "script", "setsid", "stdbuf", "flock", "strace", "ltrace"}
_DENY_BIN = {"sudo", "su", "doas", "pkexec", "rm", "rmdir", "unlink", "shred", "dd", "mkfs", "fdisk", "parted", "sfdisk",
             "wipefs", "mount", "umount", "chmod", "chown", "chgrp", "ln", "mv", "cp", "tee", "truncate", "install",
             "shutdown", "reboot", "poweroff", "halt", "init", "telinit", "kill", "killall", "pkill",
             "passwd", "useradd", "userdel", "usermod", "groupadd", "groupdel", "visudo", "crontab", "at", "batch",
             "curl", "wget", "nc", "ncat", "netcat", "ssh", "scp", "sftp", "rsync", "ftp", "telnet", "socat",
             "iptables", "nft", "ufw", "firewall-cmd", "modprobe", "insmod", "rmmod", "sysctl", "swapoff", "swapon",
             "gpg", "openssl", "base64", "eval", "source", "alias", "history", "export"}
_SAFE_SYSTEMCTL = {"status", "is-active", "is-enabled", "is-failed", "list-units", "list-unit-files", "show", "cat"}
_SAFE_DNF = {"list", "info", "search", "repoquery", "provides", "history", "check-update", "repolist"}
_SAFE_PIP = {"list", "show", "freeze", "check", "download", "install", "index"}


def check_command(command: str) -> list[str]:
    """Valida un comando y lo devuelve como lista de argumentos (sin shell). Lanza ToolError si es peligroso."""
    if not config.SHELL:
        raise ToolError("Los comandos de terminal están desactivados (DOX_SHELL=0).")
    command = (command or "").strip()
    if not command:
        raise ToolError("Falta el comando.")
    if len(command) > 400:
        raise ToolError("Comando demasiado largo.")
    if _META.search(command):
        raise ToolError("Por seguridad no se permiten pipes, redirecciones, «;», «&», «$» ni sustitución de comandos. "
                        "Ejecuta un solo comando simple.")
    try:
        argv = shlex.split(command)
    except ValueError:
        raise ToolError("Comando mal formado (comillas sin cerrar).")
    if not argv:
        raise ToolError("Falta el comando.")
    if re.search(r"\.ssh|\.gnupg|\.aws|\.kube|/etc/(shadow|sudoers|gshadow)|id_rsa|id_ed25519|\.config/dox|\.netrc|keyring|wallet|\.mozilla|\.pki|\.password|\bpasswd\b",
                 command.lower()):
        raise ToolError("Ese comando toca archivos secretos (claves, contraseñas); está bloqueado.")
    prog = Path(argv[0]).name.lower()
    if prog in _WRAPPERS:
        raise ToolError(f"«{prog}» no se permite (puede ejecutar otros comandos ocultos).")
    if prog in _DENY_BIN or prog.startswith("mkfs"):
        raise ToolError(f"«{prog}» está bloqueado por seguridad (destructivo, de red o de administración).")
    args = [a.lower() for a in argv[1:]]
    if prog == "systemctl":
        sub = next((a for a in args if not a.startswith("-")), "")
        if sub not in _SAFE_SYSTEMCTL:
            raise ToolError("De systemctl solo se permiten consultas: status, is-active, list-units…")
    if prog in ("dnf", "dnf5", "yum", "rpm", "apt", "apt-get", "zypper", "pacman"):
        sub = next((a for a in args if not a.startswith("-")), "")
        if prog in ("dnf", "dnf5", "yum") and sub in _SAFE_DNF:
            pass
        elif prog == "rpm" and ("-q" in args or "-qa" in args or any(a.startswith("-q") for a in args)):
            pass
        else:
            raise ToolError("Instalar o quitar paquetes del sistema requiere administrador (sudo), "
                            "y eso está bloqueado. Dime el comando y ejecútalo tú en la terminal.")
    if prog in ("pip", "pip3") or (prog.startswith("python") and args[:2] == ["-m", "pip"]):
        sub = next((a for a in (args[2:] if prog.startswith("python") else args) if not a.startswith("-")), "")
        if sub not in _SAFE_PIP:
            raise ToolError("De pip solo se permiten: list, show, freeze, check, install.")
    if prog.startswith("python") and args and args[0] not in ("-m", "--version", "-v") :
        raise ToolError("Python solo se permite para ver la versión o como «python -m pip …».")
    if prog == "find" and any(a in ("-delete", "-exec", "-execdir", "-ok", "-fprint", "-fls") for a in args):
        raise ToolError("find con -delete o -exec está bloqueado.")
    if prog == "sed" and any(a.startswith("-i") or a == "--in-place" for a in args):
        raise ToolError("sed -i (editar archivos) está bloqueado.")
    if prog == "git" and any(a in ("push", "reset", "clean", "checkout", "rebase", "commit", "merge", "pull") for a in args[:2]):
        raise ToolError("Ese subcomando de git modifica el repositorio; solo se permiten consultas (status, log, diff).")
    if prog == "flatpak" and (not args or args[0] not in ("list", "info", "search", "remotes", "ps")):
        raise ToolError("De flatpak solo se permiten: list, info, search, remotes, ps.")
    return argv


# ------------------------------------------------------------------ confirmaciones
_pending: dict[str, dict] = {}
_plock = threading.Lock()
CONFIRM_TIMEOUT = 120


def new_confirmation() -> str:
    cid = uuid.uuid4().hex[:10]
    with _plock:
        _pending[cid] = {"event": threading.Event(), "ok": False}
    return cid


def wait_confirmation(cid: str, timeout: float = CONFIRM_TIMEOUT) -> bool:
    entry = _pending.get(cid)
    if not entry:
        return False
    entry["event"].wait(timeout)
    with _plock:
        _pending.pop(cid, None)
    return bool(entry["ok"])


def answer_confirmation(cid: str, ok: bool) -> bool:
    with _plock:
        entry = _pending.get(cid)
        if not entry:
            return False
        entry["ok"] = bool(ok)
        entry["event"].set()
    return True
