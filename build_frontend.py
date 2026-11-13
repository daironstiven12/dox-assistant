"""Recompila la interfaz (frontend/src/app.jsx -> frontend/app.js).

Solo lo necesitas si EDITAS app.jsx. Requiere Node.js:  python build_frontend.py
"""

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC, OUT = ROOT / "frontend" / "src" / "app.jsx", ROOT / "frontend" / "app.js"

with tempfile.TemporaryDirectory() as tmp:
    print("Instalando compilador (@babel/standalone)…")
    subprocess.run(["npm", "init", "-y"], cwd=tmp, check=True, capture_output=True)
    subprocess.run(["npm", "i", "@babel/standalone@7.24.7"], cwd=tmp, check=True, capture_output=True)
    js = ("const B=require('@babel/standalone');const fs=require('fs');"
          "fs.writeFileSync(process.argv[2],B.transform(fs.readFileSync(process.argv[1],'utf8'),"
          "{presets:['react'],minified:false}).code);")
    subprocess.run(["node", "-e", js, str(SRC), str(OUT)], cwd=tmp, check=True)
print(f"Listo: {OUT}")
sys.exit(0)
