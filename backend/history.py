"""Historial de conversaciones, guardado solo en tu computador (junto a settings.json)."""

import json
import re
import threading
import time
import uuid

import settings

PATH = settings.PATH.with_name("history.json")
MAX_CONVERSATIONS = 60
MAX_MESSAGES = 120
_lock = threading.Lock()


def _load() -> list[dict]:
    try:
        data = json.loads(PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, ValueError):
        return []


def _save(items: list[dict]) -> None:
    try:
        PATH.parent.mkdir(parents=True, exist_ok=True)
        PATH.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
    except OSError as e:
        print(f"[DOx] no pude guardar el historial: {e}")


def _title(messages: list[dict]) -> str:
    for m in messages:
        if m.get("role") == "user" and m.get("content"):
            t = re.sub(r"\s+", " ", m["content"]).strip()
            return t[:60] + ("…" if len(t) > 60 else "")
    return "…"


def list_all() -> list[dict]:
    with _lock:
        items = sorted(_load(), key=lambda c: c.get("updated", 0), reverse=True)
    return [{"id": c["id"], "title": c.get("title", "…"), "updated": c.get("updated", 0),
             "count": len(c.get("messages", []))} for c in items]


def get(cid: str) -> dict | None:
    with _lock:
        return next((c for c in _load() if c.get("id") == cid), None)


def save(cid: str | None, messages: list[dict]) -> dict:
    clean = []
    for m in messages:
        if m.get("role") in ("user", "assistant") and m.get("content"):
            item = {"role": m["role"], "content": str(m["content"])[:8000]}
            src = [{"title": str(x.get("title", ""))[:120], "url": str(x.get("url", ""))[:500]}
                   for x in (m.get("sources") or [])[:5] if isinstance(x, dict) and str(x.get("url", "")).startswith("http")]
            if src:
                item["sources"] = src
            clean.append(item)
    clean = clean[-MAX_MESSAGES:]
    with _lock:
        items = _load()
        conv = next((c for c in items if c.get("id") == cid), None) if cid else None
        if conv is None:
            conv = {"id": uuid.uuid4().hex[:12]}
            items.append(conv)
        conv.update(title=_title(clean), updated=time.time(), messages=clean)
        items = sorted(items, key=lambda c: c.get("updated", 0), reverse=True)[:MAX_CONVERSATIONS]
        _save(items)
    return {"id": conv["id"], "title": conv["title"]}


def delete(cid: str) -> bool:
    with _lock:
        items = _load()
        kept = [c for c in items if c.get("id") != cid]
        if len(kept) != len(items):
            _save(kept)
            return True
    return False


def clear() -> None:
    with _lock:
        _save([])
