"""Hace que DOx arranque solo al encender el computador (minimizado, saludando).

  python install_autostart.py            instalar
  python install_autostart.py --remove   quitar
"""

import os
import plistlib
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().with_name("desktop.py")


def windows(remove: bool):
    startup = Path(os.environ["APPDATA"]) / "Microsoft/Windows/Start Menu/Programs/Startup"
    target = startup / "DOx.vbs"
    if remove:
        target.unlink(missing_ok=True)
        return print("Autoarranque de DOx eliminado.")
    pythonw = Path(sys.executable).with_name("pythonw.exe")   # sin ventana negra de consola
    exe = pythonw if pythonw.exists() else Path(sys.executable)
    vbs = f'CreateObject("Wscript.Shell").Run """{exe}"" ""{SCRIPT}"" --boot", 0, False'
    target.write_text(vbs, encoding="utf-16")
    print(f"Listo. DOx arrancará con Windows ({target}).")


def mac(remove: bool):
    target = Path.home() / "Library/LaunchAgents/com.dox.assistant.plist"
    if remove:
        target.unlink(missing_ok=True)
        return print("Autoarranque de DOx eliminado.")
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "wb") as f:
        plistlib.dump({"Label": "com.dox.assistant", "RunAtLoad": True,
                       "ProgramArguments": [sys.executable, str(SCRIPT), "--boot"]}, f)
    print(f"Listo. DOx arrancará al iniciar sesión ({target}).")


def linux(remove: bool):
    autostart = Path.home() / ".config/autostart/dox.desktop"
    menu = Path.home() / ".local/share/applications/dox.desktop"
    if remove:
        autostart.unlink(missing_ok=True)
        menu.unlink(missing_ok=True)
        return print("Autoarranque y acceso del menú de DOx eliminados.")
    icon = SCRIPT.with_name("frontend") / "assets" / "icon-512.png"
    entry = ("[Desktop Entry]\nType=Application\nName=DOx\nComment=DOx Assistant\n"
             f"Icon={icon}\nExec=\"{sys.executable}\" \"{SCRIPT}\"%s\nTerminal=false\nCategories=Utility;\n")   # comillas: rutas con espacios
    for target, extra in ((autostart, " --boot"), (menu, "")):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(entry % extra)
    print(f"Listo. DOx aparece en tu menú de aplicaciones ({menu})\n"
          f"y arrancará al iniciar sesión ({autostart}).")


if __name__ == "__main__":
    remove = "--remove" in sys.argv
    if sys.platform.startswith("win"):
        windows(remove)
    elif sys.platform == "darwin":
        mac(remove)
    else:
        linux(remove)
