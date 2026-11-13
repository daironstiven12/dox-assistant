# DOx — Assistant / Asistente

Asistente de escritorio con IA **local y gratuita** (Ollama): burbuja minimizada con tu logo, voz,
órdenes para abrir webs y programas, modo claro/oscuro y español/inglés.

## Estructura

```
dox/
├── backend/
│   ├── main.py        API FastAPI (solo acepta peticiones de tu propio PC)
│   ├── brain.py       decide: orden del PC -> hora/fecha -> agente -> respaldo
│   ├── agent.py       agente: elige herramientas, investiga con fuentes, pide permisos
│   ├── llm.py         cliente de Ollama (streaming y herramientas)
│   ├── safety.py      carpetas permitidas, comandos bloqueados, confirmaciones
│   ├── tools/         files.py web.py system.py notes.py shell.py
│   ├── actions.py     lo que DOx puede abrir (lista blanca SITES / APPS), órdenes ES y EN
│   ├── config.py      perfiles de consumo, modelo, voz…
│   ├── settings.py    idioma / tema / voz guardados en ~/.config/dox/settings.json
│   ├── history.py     historial de conversaciones (solo en tu PC)
│   ├── speaker.py     voz: Piper (natural) con respaldo a espeak      voice.py  palabra de activación (Vosk)
├── frontend/          interfaz (React ya incluido, funciona SIN internet) + assets/ con tu logo
├── desktop.py         ventana principal + burbuja
├── install_voice.py   descarga las voces naturales de Piper
├── install_autostart.py   menú de aplicaciones + arranque con el PC
└── build_frontend.py      solo si editas frontend/src/app.jsx
```

## Instalar y abrir

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
pip install "pywebview[qt]"        # ventana propia en Linux
python desktop.py                  # o: python desktop.py --web  (navegador)
```

## IA local: perfiles de consumo

Elige según tu RAM con la variable `DOX_PROFILE`:

| Perfil | Modelo | Memoria de conversación | Respuesta máx. | Se descarga de la RAM tras |
|---|---|---|---|---|
| `eco` | `qwen3.5:0.8b` | 3072 | 150 tokens | 1 min |
| `normal` (por defecto) | `qwen3.5:2b` | 4096 | 300 tokens | 3 min |
| `potente` | `qwen3.5:4b` | 6144 | 500 tokens | 5 min |

```bash
ollama pull qwen3.5:0.8b          # el que corresponda a tu perfil
DOX_PROFILE=eco python desktop.py
```

Todo se puede afinar suelto: `DOX_MODEL`, `DOX_NUM_CTX`, `DOX_MAX_TOKENS`, `DOX_KEEP_ALIVE`.

Qué lo hace liviano:
- Saludo, hora/fecha y órdenes ("abre YouTube") **no usan IA**.
- La respuesta llega **en streaming**: ves el texto desde el primer segundo, no al final.
- `num_ctx` reducido (Ollama usa 4096 por defecto) ahorra RAM y acelera en CPU.
- El modelo se descarga solo de la RAM cuando no lo usas.
- Interfaz 100 % local (sin descargar React ni compilar en el navegador).

Ahorro extra en Ollama (opcional, en el servicio): `OLLAMA_FLASH_ATTENTION=1` y
`OLLAMA_KV_CACHE_TYPE=q8_0` (`sudo systemctl edit ollama`, sección `[Service]`, líneas `Environment="..."`).

## Pantallas

**Inicio** (conversación y accesos rápidos), **Historial** (conversaciones guardadas solo en tu PC, en
`~/.config/dox/history.json`), **Herramientas** (qué puede hacer DOx, con ejemplos para probar) y
**Configuración** (idioma, tema, voz, micrófono, estado de la IA).

## Idioma y tema

Arriba a la derecha: **ES | EN** y el botón de tema (**Sistema → Claro → Oscuro**). Se guardan solos y la
burbuja, las respuestas, la voz y el reconocimiento de voz usan el mismo idioma. Las órdenes
("abre", "open", "busca", "search", "minimízate", "minimize"…) funcionan en ambos idiomas.

## Logo e icono

El logo está en `frontend/assets/` (`mark-wave.png` para claro, `mark-wave-dark.png` para oscuro,
`icon-512.png` para el ícono de la app). Para cambiarlo, reemplaza esos archivos conservando el nombre.

## Voz natural (Piper) — recomendado

La voz por defecto (espeak) suena robótica. Piper es una voz neuronal que funciona sin internet y en CPU:

```bash
pip install -r backend/requirements-piper.txt
python install_voice.py            # descarga es_MX-claude-high y en_US-lessac-medium (~150 MB)
```

Reinicia DOx y en **Configuración > Voz > Probar voz** debe decir "Voz neuronal natural (Piper)".
Otras voces en español: `python install_voice.py es_ES-davefx-medium` y luego
`DOX_PIPER_ES=es_ES-davefx-medium python desktop.py` (también `es_MX-ald-medium`). Si la voz "high" va lenta en tu CPU,
usa una "medium". Velocidad: `DOX_VOICE_SPEED=0.9` (más rápida) o `1.1` (más lenta).
El audio se reproduce con `pw-play`, `paplay`, `aplay` o `ffplay` (se detecta solo).

## Micrófono / palabra de activación (opcional)

```bash
pip install -r backend/requirements-voice.txt
```
Modelos de Vosk (https://alphacephei.com/vosk/models) descomprimidos en `dox/models/`:
`vosk-model-small-es-0.42` (español) y `vosk-model-small-en-us-0.15` (inglés).
Luego toca el botón del micrófono (arriba a la derecha) o arranca con `DOX_VOICE=1 python desktop.py`.
Si no entiende el nombre: `DOX_VOICE_DEBUG=1` y agrega lo que oiga a `DOX_WAKE_WORDS`.

## Arranque con el PC

```bash
python install_autostart.py            # crea el acceso en el menú y el autoarranque
python install_autostart.py --remove
```

## Modo agente (hace cosas y no inventa)

| Grupo | Qué hace | Permiso |
|---|---|---|
| Internet | Busca, lee páginas y responde SOLO con lo encontrado, con fuentes [1] [2] | automático |
| Archivos | Buscar, abrir, leer (texto, .docx, .pdf), listar | automático |
| Archivos | Crear, mover, borrar (a la papelera) | **pide permiso** |
| Sistema | RAM/disco/batería, volumen, brillo, captura, portapapeles, abrir programas | automático |
| Sistema | Cerrar un programa | **pide permiso** |
| Notas | Notas, memoria permanente, recordatorios con aviso en voz | automático |
| Terminal | UN comando simple (sin pipes, sin sudo/rm/dd…) | **pide permiso**, muestra el comando exacto |

Para no inventar: temperatura baja, reglas de honestidad en el prompt, investigación automática para datos
(modo en Configuración: Automático / Siempre / Nunca), fuentes agregadas por el código, citas inexistentes
eliminadas y, en turnos de investigación, el modelo no tiene herramientas (una web no puede darle órdenes).
Con un modelo de 4B se reduce mucho, pero no se elimina: verifica lo importante en las fuentes.

Mejor búsqueda (opcional): `pip install -r backend/requirements-agent.txt` (ddgs, pypdf), o tu propio
SearXNG (`DOX_SEARXNG=http://localhost:8080`) o Brave (`DOX_BRAVE_KEY`). Otras variables: `DOX_AGENT=0`,
`DOX_SHELL=0`, `DOX_RESEARCH=auto|always|off`, `DOX_ROOTS=/ruta1:/ruta2` (carpetas extra permitidas),
`DOX_AGENT_TEMP`, `DOX_MAX_STEPS`. Notas y recordatorios: `~/.config/dox/notes.json`.
Por voz, las acciones que piden permiso no se ejecutan (se pide desde la ventana).

## Seguridad

Solo toca Documentos, Descargas, Escritorio e Imágenes (sin archivos ocultos ni enlaces que escapen), nunca
abre scripts/ejecutables, bloquea comandos destructivos y de red, y el servidor solo responde a tu propio equipo.
