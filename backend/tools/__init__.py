"""Herramientas que DOx puede usar. Cada una declara su grupo, su esquema y si pide confirmación."""

from dataclasses import dataclass
from typing import Callable

from safety import ToolError


@dataclass
class Tool:
    name: str
    group: str                    # files | system | notes | shell
    description: str
    params: dict
    required: list
    fn: Callable
    confirm: Callable | None = None   # args -> (resumen, detalle). Si existe, se pide permiso antes de ejecutar.

    def schema(self) -> dict:
        return {"type": "function", "function": {
            "name": self.name, "description": self.description,
            "parameters": {"type": "object", "properties": self.params, "required": self.required}}}


REGISTRY: dict[str, Tool] = {}


def S(desc: str) -> dict:
    return {"type": "string", "description": desc}


def N(desc: str) -> dict:
    return {"type": "number", "description": desc}


def B(desc: str) -> dict:
    return {"type": "boolean", "description": desc}


def tool(group: str, description: str, params: dict, required=(), confirm=None):
    def deco(fn):
        REGISTRY[fn.__name__] = Tool(fn.__name__, group, description, params, list(required), fn, confirm)
        return fn
    return deco


def schemas(groups) -> list[dict]:
    return [t.schema() for t in REGISTRY.values() if t.group in groups]


def get(name: str) -> Tool | None:
    return REGISTRY.get(name)


def call(name: str, args: dict) -> str:
    t = REGISTRY.get(name)
    if t is None:
        raise ToolError(f"No existe la herramienta «{name}».")
    if not isinstance(args, dict):
        raise ToolError("Argumentos inválidos.")
    clean = {k: v for k, v in args.items() if k in t.params and v is not None}
    missing = [r for r in t.required if clean.get(r) in (None, "")]
    if missing:
        raise ToolError(f"Faltan argumentos: {', '.join(missing)}.")
    return str(t.fn(**clean))


from . import files, notes, shell, system, web  # noqa: E402,F401  (registran sus herramientas)
