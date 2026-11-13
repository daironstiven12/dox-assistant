"""Descarga las voces neuronales de Piper (natural, sin internet después de instalarlas).

  python install_voice.py                  voces por defecto (español y inglés)
  python install_voice.py es_ES-davefx-medium   una voz concreta (se usa con DOX_PIPER_ES=...)

Requiere:  pip install piper-tts
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEST = ROOT / "models" / "piper"
DEFAULTS = ["es_MX-claude-high", "en_US-lessac-medium"]

try:
    import piper  # noqa: F401
except ImportError:
    sys.exit("Falta Piper. Instálalo con:  pip install piper-tts")

voices = sys.argv[1:] or DEFAULTS
DEST.mkdir(parents=True, exist_ok=True)
for v in voices:
    print(f"\n== Descargando {v} …")
    r = subprocess.run([sys.executable, "-m", "piper.download_voices", "--download-dir", str(DEST), v])
    if r.returncode != 0:
        print(f"No pude descargar «{v}». Revisa el nombre en https://huggingface.co/rhasspy/piper-voices/tree/main/es")
print(f"\nListo. Voces en {DEST}. Reinicia DOx y usa Configuración > Probar voz.")
