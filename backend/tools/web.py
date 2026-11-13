"""Internet: buscar y leer páginas. Se usa para investigar con fuentes en vez de inventar."""

import html
import ipaddress
import json
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

import config
from safety import ToolError

from . import S, tool

UA = "Mozilla/5.0 (X11; Linux x86_64) DOx/1.0"
MAX_BYTES = 1_500_000


# ---------------------------------------------------------------- seguridad de red (SSRF)
def _check_url(url: str) -> str:
    u = urllib.parse.urlparse(url)
    if u.scheme not in ("http", "https") or not u.hostname:
        raise ToolError("Solo se permiten direcciones http/https.")
    try:
        infos = socket.getaddrinfo(u.hostname, u.port or (443 if u.scheme == "https" else 80))
    except socket.gaierror:
        raise ToolError("No pude resolver esa dirección.")
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise ToolError("No accedo a direcciones internas de tu red.")
    return url


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


_opener = urllib.request.build_opener(_NoRedirect)


def _get(url: str, timeout: float = 10, headers: dict | None = None) -> tuple[bytes, str]:
    """GET validando cada redirección (máx. 4)."""
    for _ in range(5):
        _check_url(url)
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "es,en;q=0.8", **(headers or {})})
        try:
            with _opener.open(req, timeout=timeout) as r:
                ctype = r.headers.get("Content-Type", "")
                return r.read(MAX_BYTES), ctype
        except urllib.error.HTTPError as e:
            if e.code in (301, 302, 303, 307, 308) and e.headers.get("Location"):
                url = urllib.parse.urljoin(url, e.headers["Location"])
                continue
            raise ToolError(f"La página respondió con error {e.code}.")
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            raise ToolError(f"No pude conectar: {getattr(e, 'reason', e)}")
    raise ToolError("Demasiadas redirecciones.")


# ---------------------------------------------------------------- HTML -> texto
class _Text(HTMLParser):
    SKIP = {"script", "style", "noscript", "nav", "footer", "header", "aside", "form", "svg", "iframe"}
    BLOCK = {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "tr", "section", "article"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip = 0
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        if tag == "title":
            self._in_title = True
        if tag in self.BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        elif not self.skip and data.strip():
            self.parts.append(data.strip() + " ")


def html_to_text(raw: str) -> tuple[str, str]:
    p = _Text()
    try:
        p.feed(raw)
    except Exception:
        pass
    text = re.sub(r"[ \t]+", " ", "".join(p.parts))
    text = re.sub(r"\n\s*\n+", "\n", text).strip()
    lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 40]   # descarta menús y migas
    return p.title.strip(), "\n".join(lines)


def _decode(body: bytes, ctype: str) -> str:
    m = re.search(r"charset=([\w-]+)", ctype, re.I) or re.search(rb"charset=[\"']?([\w-]+)", body[:2000], re.I)
    enc = (m.group(1).decode() if m and isinstance(m.group(1), bytes) else m.group(1)) if m else "utf-8"
    try:
        return body.decode(enc, "replace")
    except LookupError:
        return body.decode("utf-8", "replace")


def fetch_text(url: str, limit: int = 3000) -> tuple[str, str]:
    body, ctype = _get(url)
    if "html" not in ctype.lower() and "text" not in ctype.lower() and "json" not in ctype.lower():
        raise ToolError(f"Ese enlace no es una página de texto ({ctype or 'desconocido'}).")
    raw = _decode(body, ctype)
    if "html" in ctype.lower() or raw.lstrip().lower().startswith(("<!doc", "<html")):
        title, text = html_to_text(raw)
    else:
        title, text = "", raw
    return title, text[:limit]


# ---------------------------------------------------------------- buscadores
def _brave(q: str, n: int) -> list[dict]:
    body, _ = _get("https://api.search.brave.com/res/v1/web/search?" + urllib.parse.urlencode({"q": q, "count": n}),
                   headers={"X-Subscription-Token": config.BRAVE_KEY, "Accept": "application/json"})
    return [{"title": r.get("title", ""), "url": r["url"], "snippet": html.unescape(re.sub("<[^>]+>", "", r.get("description", "")))}
            for r in json.loads(body).get("web", {}).get("results", [])[:n]]


def _searxng(q: str, n: int) -> list[dict]:
    body, _ = _get(config.SEARXNG_URL + "/search?" + urllib.parse.urlencode({"q": q, "format": "json"}))
    return [{"title": r.get("title", ""), "url": r["url"], "snippet": r.get("content", "")} for r in json.loads(body).get("results", [])[:n]]


def _ddgs(q: str, n: int) -> list[dict]:
    try:
        from ddgs import DDGS
    except ImportError:
        try:
            from duckduckgo_search import DDGS  # type: ignore
        except ImportError:
            raise ToolError("sin ddgs")
    with DDGS() as d:
        return [{"title": r.get("title", ""), "url": r.get("href", ""), "snippet": r.get("body", "")}
                for r in d.text(q, max_results=n) if r.get("href")]


def parse_ddg_html(page: str, n: int) -> list[dict]:
    out = []
    for m in re.finditer(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>(.*?)(?=<a[^>]+class="result__a"|$)', page, re.S):
        href, title, rest = m.groups()
        if "uddg=" in href:
            href = urllib.parse.unquote(href.split("uddg=")[1].split("&")[0])
        elif href.startswith("//"):
            href = "https:" + href
        sm = re.search(r'class="result__snippet"[^>]*>(.*?)</a>', rest, re.S)
        clean = lambda s: html.unescape(re.sub(r"<[^>]+>", "", s)).strip()
        if href.startswith("http") and "duckduckgo.com/y.js" not in href:
            out.append({"title": clean(title), "url": href, "snippet": clean(sm.group(1)) if sm else ""})
        if len(out) >= n:
            break
    return out


def _ddg_html(q: str, n: int) -> list[dict]:
    body, ctype = _get("https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({"q": q}))
    return parse_ddg_html(_decode(body, ctype), n)


def search(q: str, n: int = 5) -> list[dict]:
    backends = []
    if config.BRAVE_KEY:
        backends.append(_brave)
    if config.SEARXNG_URL:
        backends.append(_searxng)
    backends += [_ddgs, _ddg_html]
    last = None
    for fn in backends:
        try:
            res = fn(q, n)
            if res:
                return res
        except ToolError as e:
            last = e
        except Exception as e:   # red, JSON, etc.
            last = ToolError(str(e)[:120])
    raise ToolError("No pude buscar en internet" + (f" ({last})." if last else "."))


# ---------------------------------------------------------------- investigación con fuentes
def research(query: str, pages: int = 2) -> tuple[str, list[dict]]:
    """Busca, lee las mejores páginas y devuelve (contexto numerado [1],[2]…, fuentes)."""
    results = search(query, 6)
    sources, blocks = [], []
    for r in results:
        if len(sources) >= max(pages, 1) + 1:
            break
        text = ""
        if len(sources) < pages:
            try:
                _, text = fetch_text(r["url"], 1800)
            except ToolError:
                text = ""
        body = text or r["snippet"]
        if not body:
            continue
        sources.append({"title": r["title"] or r["url"], "url": r["url"]})
        blocks.append(f"[{len(sources)}] {r['title']}\n{body}")
    if not blocks:
        raise ToolError("Encontré resultados pero ninguno tenía texto legible.")
    return "\n\n".join(blocks), sources


# ---------------------------------------------------------------- herramientas (las usa el modelo)
@tool("web", "Busca en internet y devuelve títulos, enlaces y fragmentos. Úsala para datos actuales o que no conozcas.",
      {"query": S("consulta de búsqueda")}, ["query"])
def web_search(query: str) -> str:
    return "\n".join(f"- {r['title']} — {r['url']}\n  {r['snippet'][:240]}" for r in search(query, 5))


@tool("web", "Lee el texto de una página web (URL completa devuelta por web_search).",
      {"url": S("URL http/https")}, ["url"])
def read_page(url: str) -> str:
    title, text = fetch_text(url, 3000)
    return f"{title}\n{text}" if text else "La página no tiene texto legible."
