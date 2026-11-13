"""Cliente de Ollama (chat en streaming, con soporte de herramientas)."""

import json
import urllib.error
import urllib.request
from typing import Iterator

import config

SLOW = {"es": "El modelo tardó demasiado en responder.", "en": "The model took too long to answer."}


class OllamaError(Exception):
    pass


class OllamaDown(OllamaError):
    pass


class ModelMissing(OllamaError):
    pass


def status() -> dict:
    """Consulta rápida: ¿Ollama está encendido y tiene el modelo?"""
    try:
        with urllib.request.urlopen(config.OLLAMA_URL + "/api/tags", timeout=1.5) as r:
            names = [m.get("name", "") for m in json.load(r).get("models", [])]
        installed = any(n == config.MODEL or n == config.MODEL + ":latest" for n in names)
        return {"running": True, "model": config.MODEL, "model_installed": installed, "profile": config.PROFILE}
    except Exception:
        return {"running": False, "model": config.MODEL, "model_installed": False, "profile": config.PROFILE}


def _open(payload: dict, lang: str):
    """Abre la conexión; reintenta sin 'think' si el modelo no lo soporta."""
    for attempt in (1, 2):
        req = urllib.request.Request(config.OLLAMA_URL + "/api/chat", data=json.dumps(payload).encode("utf-8"),
                                     headers={"Content-Type": "application/json"})
        try:
            return urllib.request.urlopen(req, timeout=config.TIMEOUT)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "ignore")
            if e.code == 404:
                raise ModelMissing(body)
            if e.code == 400 and "think" in payload and attempt == 1:
                payload.pop("think")
                continue
            raise OllamaError(body[:200])
        except TimeoutError:
            raise OllamaError(SLOW[lang])
        except OSError as e:
            raise OllamaDown(str(e))
    raise OllamaError("?")


def stream_chat(messages: list[dict], lang: str = "es", tools: list[dict] | None = None,
                temperature: float = 0.5, num_predict: int | None = None) -> Iterator[dict]:
    """Genera {'content': str} por cada trozo de texto y {'tool_calls': [...]} cuando el modelo pide herramientas."""
    payload = {
        "model": config.MODEL,
        "messages": messages,
        "stream": True,
        "think": False,  # sin "razonamiento" largo: más rápido y barato en CPU
        "keep_alive": config.KEEP_ALIVE,
        "options": {"num_predict": num_predict or config.MAX_TOKENS, "num_ctx": config.NUM_CTX,
                    "temperature": temperature},
    }
    if tools:
        payload["tools"] = tools
    resp = _open(payload, lang)
    try:
        for raw in resp:
            line = raw.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except ValueError:
                continue
            if data.get("error"):
                raise OllamaError(str(data["error"])[:200])
            msg = data.get("message") or {}
            if msg.get("content"):
                yield {"content": msg["content"]}
            if msg.get("tool_calls"):
                yield {"tool_calls": msg["tool_calls"]}
            if data.get("done"):
                break
    except TimeoutError:
        raise OllamaError(SLOW[lang])
    finally:
        resp.close()
