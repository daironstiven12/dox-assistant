"""Archivos: buscar, abrir y leer son automáticos; crear, mover y borrar piden confirmación."""

import html
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

import config
import safety
from safety import ToolError, norm

from . import B, N, S, tool

_STOP = {"el", "la", "los", "las", "un", "una", "de", "del", "mi", "mis", "que", "tengo", "en", "mi", "computador",
         "pc", "archivo", "archivos", "documento", "carpeta", "the", "my", "file", "document", "folder", "a", "of", "on"}
_SKIP_DIRS = {"node_modules", "__pycache__", "venv", "site-packages", "dist", "build"}
_TEXT_EXT = {".txt", ".md", ".csv", ".json", ".log", ".py", ".js", ".ts", ".html", ".htm", ".css", ".xml", ".yaml",
             ".yml", ".ini", ".cfg", ".toml", ".tex", ".rst", ".sql", ".java", ".c", ".cpp", ".h", ".go", ".rs", ".php",
             ".rb", ".tsv", ".srt", ".conf"}


def _size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return str(n)


def _open_path(p: Path) -> None:
    if config.DRY_RUN:
        return
    if sys.platform.startswith("win"):
        os.startfile(str(p))  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(p)])
    else:
        subprocess.Popen(["xdg-open", str(p)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True)


@tool("files", "Busca archivos o carpetas por nombre en Documentos, Descargas, Escritorio e Imágenes. "
               "Devuelve rutas completas. Úsala SIEMPRE antes de abrir/leer/mover un archivo.",
      {"query": S("palabras del nombre, p. ej. 'listado asistencia'"), "folder": S("carpeta donde buscar (opcional, ruta completa)")},
      ["query"])
def find_files(query: str, folder: str | None = None) -> str:
    tokens = [t for t in norm(query).split() if t not in _STOP]
    if not tokens:
        raise ToolError("Dime al menos una palabra del nombre del archivo.")
    bases = [safety.resolve(folder)] if folder else safety.roots()
    if not bases:
        raise ToolError("No encontré carpetas de usuario permitidas (Documentos, Descargas…).")
    start, seen, hits = time.time(), 0, []
    for base in bases:
        for dirpath, dirnames, filenames in os.walk(base):
            depth = len(Path(dirpath).relative_to(base).parts)
            dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in _SKIP_DIRS] if depth < 6 else []
            for name in dirnames + filenames:
                seen += 1
                n = norm(name)
                found = sum(1 for t in tokens if t in n)
                if found and found >= max(1, (len(tokens) + 1) // 2):
                    hits.append((found / len(tokens), Path(dirpath) / name))
            if seen > 60000 or time.time() - start > 5:
                break
    if not hits:
        return f"No encontré nada parecido a «{query}» en las carpetas permitidas."
    def mtime(p: Path) -> float:
        try:
            return p.stat().st_mtime
        except OSError:
            return 0
    hits.sort(key=lambda h: (-h[0], -mtime(h[1])))
    lines = []
    for score, p in hits[:8]:
        try:
            st = p.stat()
            kind = "carpeta" if p.is_dir() else f"archivo, {_size(st.st_size)}"
            lines.append(f"- {p} ({kind}, modificado {time.strftime('%Y-%m-%d', time.localtime(st.st_mtime))})")
        except OSError:
            continue
    extra = f"\n(+{len(hits) - 8} más)" if len(hits) > 8 else ""
    return "Resultados (usa la ruta exacta):\n" + "\n".join(lines) + extra


@tool("files", "Abre un archivo o carpeta con el programa por defecto. Necesita la ruta completa (de find_files).",
      {"path": S("ruta completa")}, ["path"])
def open_file(path: str) -> str:
    p = safety.resolve(path)
    if p.is_file():
        safety.check_extension(p)
    _open_path(p)
    return f"Abierto: {p}"


def _read_docx(p: Path, member: str) -> str:
    with zipfile.ZipFile(p) as z:
        xml = z.read(member).decode("utf-8", "replace")
    xml = re.sub(r"</w:p>|</text:p>|<text:line-break/>|<w:br/>", "\n", xml)
    return html.unescape(re.sub(r"<[^>]+>", "", xml))


def _read_pdf(p: Path) -> str:
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(p))
        return "\n".join((pg.extract_text() or "") for pg in reader.pages[:30])
    except ImportError:
        pass
    if shutil.which("pdftotext"):
        out = subprocess.run(["pdftotext", "-layout", "-l", "30", str(p), "-"], capture_output=True, text=True, timeout=30)
        return out.stdout
    raise ToolError("Para leer PDF instala pypdf (pip install pypdf) o poppler-utils (pdftotext).")


@tool("files", "Lee el contenido de un archivo de texto, Word (.docx) o PDF. Necesita la ruta completa.",
      {"path": S("ruta completa"), "max_chars": N("máximo de caracteres (por defecto 4000)")}, ["path"])
def read_file(path: str, max_chars: float = 4000) -> str:
    p = safety.resolve(path)
    if not p.is_file():
        raise ToolError("Eso no es un archivo.")
    limit = int(min(max(float(max_chars), 200), 8000))
    ext = p.suffix.lower()
    if ext in _TEXT_EXT:
        with open(p, "rb") as f:
            text = f.read(400_000).decode("utf-8", "replace")
    elif ext == ".docx":
        text = _read_docx(p, "word/document.xml")
    elif ext == ".odt":
        text = _read_docx(p, "content.xml")
    elif ext == ".pdf":
        text = _read_pdf(p)
    else:
        raise ToolError(f"Todavía no sé leer archivos «{ext or 'sin extensión'}» (sí: texto, .docx, .odt, .pdf).")
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        raise ToolError("El archivo está vacío o no tiene texto legible (¿PDF escaneado?).")
    cut = len(text) > limit
    return f"Contenido de {p.name}{' (recortado)' if cut else ''}:\n{text[:limit]}"


@tool("files", "Lista el contenido de una carpeta. Sin ruta, muestra las carpetas permitidas.",
      {"path": S("ruta completa de la carpeta (opcional)")}, [])
def list_folder(path: str | None = None) -> str:
    if not path:
        return "Carpetas permitidas:\n" + "\n".join(f"- {r}" for r in safety.roots())
    p = safety.resolve(path)
    if not p.is_dir():
        raise ToolError("Eso no es una carpeta.")
    items = sorted((c for c in p.iterdir() if not c.name.startswith(".")), key=lambda c: (c.is_file(), c.name.lower()))
    lines = [f"- {c.name}{'/' if c.is_dir() else ''}" for c in items[:50]]
    return f"{p} ({len(items)} elementos):\n" + "\n".join(lines) + ("\n…" if len(items) > 50 else "")


def _confirm_create(a: dict):
    body = str(a.get("content", ""))
    return (f"Crear el archivo {a.get('path', '?')}", f"{len(body)} caracteres" + (f"\n\n{body[:300]}" if body else ""))


@tool("files", "Crea un archivo de texto con el contenido dado. Pide permiso al usuario.",
      {"path": S("ruta completa del archivo nuevo, dentro de Documentos/Descargas/Escritorio"), "content": S("contenido"),
       "overwrite": B("true para reemplazar si ya existe")}, ["path", "content"], confirm=_confirm_create)
def create_file(path: str, content: str, overwrite: bool = False) -> str:
    p = safety.resolve(path, must_exist=False)
    safety.check_extension(p)
    if not p.parent.is_dir():
        raise ToolError("La carpeta destino no existe.")
    if p.exists() and not overwrite:
        raise ToolError("Ya existe un archivo con ese nombre (usa overwrite=true solo si el usuario lo pidió).")
    p.write_text(str(content), encoding="utf-8")
    return f"Archivo creado: {p}"


@tool("files", "Crea una carpeta nueva. Pide permiso al usuario.", {"path": S("ruta completa de la carpeta nueva")}, ["path"],
      confirm=lambda a: (f"Crear la carpeta {a.get('path', '?')}", ""))
def create_folder(path: str) -> str:
    p = safety.resolve(path, must_exist=False)
    if p.exists():
        raise ToolError("Ya existe.")
    if not p.parent.is_dir():
        raise ToolError("La carpeta superior no existe.")
    p.mkdir()
    return f"Carpeta creada: {p}"


@tool("files", "Mueve o renombra un archivo o carpeta. Pide permiso al usuario.",
      {"source": S("ruta completa de origen"), "destination": S("ruta completa de destino (carpeta o nombre nuevo)")},
      ["source", "destination"],
      confirm=lambda a: (f"Mover {a.get('source', '?')}", f"→ {a.get('destination', '?')}"))
def move_file(source: str, destination: str) -> str:
    src = safety.resolve(source)
    dst = safety.resolve(destination, must_exist=False)
    if dst.is_dir():
        dst = dst / src.name
    if dst.exists():
        raise ToolError("El destino ya existe; no sobrescribo archivos.")
    if src.is_file():
        safety.check_extension(dst)
    shutil.move(str(src), str(dst))
    return f"Movido a {dst}"


@tool("files", "Envía un archivo o carpeta a la PAPELERA (recuperable). Pide permiso al usuario.",
      {"path": S("ruta completa")}, ["path"],
      confirm=lambda a: (f"Enviar a la papelera {a.get('path', '?')}", "Se puede recuperar desde la papelera."))
def delete_file(path: str) -> str:
    p = safety.resolve(path)
    if p in safety.roots():
        raise ToolError("No borro las carpetas principales.")
    if config.DRY_RUN:
        return f"(simulado) a la papelera: {p}"
    if shutil.which("gio"):
        r = subprocess.run(["gio", "trash", str(p)], capture_output=True, text=True, timeout=20)
        if r.returncode == 0:
            return f"Enviado a la papelera: {p.name}"
    trash = Path.home() / ".local" / "share" / "Trash" / "files"
    trash.mkdir(parents=True, exist_ok=True)
    dst = trash / f"{p.name}.{int(time.time())}"
    shutil.move(str(p), str(dst))
    return f"Enviado a la papelera: {p.name}"
