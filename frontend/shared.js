/* Idiomas (ES/EN), preferencias y tema. Compartido por la ventana principal y la burbuja. */
const DOX_I18N = {
  es: {
    "nav.home": "Inicio", "nav.history": "Historial", "nav.tools": "Herramientas", "nav.settings": "Configuración",
    "status.online": "En línea", "status.noai": "Sin IA conectada", "status.nomodel": "Falta el modelo",
    "ai.missing": "Ejecuta:", "ai.off": "Instala Ollama (ollama.com)",
    "hero.title": "Hola, soy DOx", "hero.sub": "¿En qué puedo ayudarte hoy?",
    "card.mail": "Enviar un correo", "card.code": "Modificar código", "card.files": "Gestionar archivos",
    "card.tasks": "Ejecutar tareas", "card.more": "Más opciones",
    "prompt.mail": "abre gmail", "prompt.code": "Ayúdame a modificar este código:\n", "prompt.files": "abre el explorador",
    placeholder: "Escribe tu petición…", send: "Enviar",
    newchat: "Nueva conversación",
    "lang.tip": "Idioma", "theme.tip": "Cambiar tema", "mic.on": "Escuchando: di «DOx…» (clic para apagar)",
    "mic.off": "Activar micrófono (palabra de activación)", "minimize.tip": "Minimizar a la burbuja", "quit.tip": "Salir de DOx",
    "mic.err.deps": "Falta instalar la voz: pip install -r backend/requirements-voice.txt",
    "mic.err.model": "Falta el modelo de voz de Vosk (mira el README, sección Voz).",
    "mic.err.web": "El micrófono solo funciona en la app de escritorio.",
    "history.title": "Historial", "history.sub": "Tus conversaciones, guardadas solo en este computador.",
    "history.empty": "Aún no hay conversaciones guardadas.", "history.clear": "Borrar todo", "history.sure": "¿Seguro? Toca de nuevo",
    "history.msgs": "{n} mensajes", "history.delete": "Borrar",
    "tools.title": "Herramientas", "tools.sub": "Esto es lo que DOx puede hacer por ti. Toca un ejemplo para probarlo.", "badge.auto": "Automático", "badge.ask": "Con tu permiso",
    "settings.title": "Configuración", "settings.sub": "Todo se guarda solo.",
    "set.language": "Idioma", "set.appearance": "Apariencia", "set.voice": "Voz", "set.mic": "Micrófono", "set.ai": "Inteligencia artificial", "set.about": "Acerca de",
    "theme.system": "Sistema", "theme.light": "Claro", "theme.dark": "Oscuro",
    "voice.replies": "Respuestas por voz", "voice.replies.sub": "DOx lee sus respuestas en voz alta.",
    "voice.piper": "Voz neuronal natural (Piper): {voice}", "voice.espeak": "Voz básica (suena robótica)",
    "voice.install": "Para una voz natural ejecuta:", "voice.test": "Probar voz", "voice.test.web": "La prueba de voz solo funciona en la app de escritorio.",
    "mic.setting": "Palabra de activación", "mic.setting.sub": "Di «DOx» seguido de una orden. Requiere los modelos de voz.",
    "ai.model": "Modelo", "ai.profile": "Perfil de consumo", "ai.state": "Estado", "ai.ok": "Conectado", "ai.down": "Sin conectar",
    "about.text": "DOx — asistente de escritorio con IA local, sin enviar tus datos a internet.",
    "set.agent": "Investigación y permisos", "research.title": "Investigar en internet", "research.auto": "Automático", "research.always": "Siempre", "research.off": "Nunca",
    "research.sub": "Automático: busca cuando preguntas por datos o noticias. Así DOx no inventa.",
    "perm.sub": "Leer, buscar y abrir es automático. Todo lo que cambia algo (crear, mover, borrar, comandos, cerrar programas) pide tu permiso.",
    "perm.roots": "Carpetas permitidas", "confirm.allow": "Permitir", "confirm.deny": "Cancelar", "confirm.allowed": "Permitido", "confirm.denied": "Cancelado",
    "confirm.ask": "DOx pide permiso", "sources": "Fuentes", "reminder": "Recordatorio",
    "step.find_files": "Buscando archivos", "step.open_file": "Abriendo archivo", "step.read_file": "Leyendo archivo", "step.list_folder": "Listando carpeta",
    "step.create_file": "Creando archivo", "step.create_folder": "Creando carpeta", "step.move_file": "Moviendo", "step.delete_file": "Enviando a la papelera",
    "step.system_info": "Revisando el sistema", "step.volume": "Volumen", "step.toggle_mute": "Silenciar", "step.brightness": "Brillo", "step.screenshot": "Captura de pantalla",
    "step.clipboard_copy": "Copiando", "step.open_app": "Abriendo programa", "step.close_app": "Cerrando programa", "step.run_command": "Terminal",
    "step.add_note": "Guardando nota", "step.list_notes": "Leyendo notas", "step.delete_note": "Borrando nota", "step.remember": "Recordando", "step.forget": "Olvidando",
    "step.set_reminder": "Programando recordatorio", "step.list_reminders": "Leyendo recordatorios", "step.cancel_reminder": "Cancelando recordatorio",
    error: "No pude conectar con mi servidor. ¿Está encendido?",
    "bubble.open": "Abrir DOx", "bubble.quit": "Cerrar DOx", "bubble.tip": "Toca para abrir DOx",
    listening: "¿Sí? Te escucho…",
    tools: [
      { icon: "search", mode: "auto", name: "Investigar en internet", desc: "Busca, lee páginas y responde SOLO con lo que encuentra, citando las fuentes. Si no lo encuentra, te lo dice.", ex: ["¿quién es el presidente de Colombia?", "investiga el precio del dólar hoy"] },
      { icon: "folder", mode: "auto", name: "Archivos: buscar, abrir y leer", desc: "Busca por nombre en Documentos, Descargas, Escritorio e Imágenes; abre y lee texto, Word y PDF.", ex: ["abre el listado de asistencia", "lee el PDF de mi contrato", "qué hay en mi carpeta Descargas"] },
      { icon: "folder", mode: "ask", name: "Archivos: crear, mover, borrar", desc: "Crea archivos y carpetas, mueve o renombra. Borrar solo manda a la papelera. Te muestra qué hará y espera tu permiso.", ex: ["crea un archivo notas.txt en Documentos con mi lista del súper"] },
      { icon: "gear", mode: "auto", name: "Sistema", desc: "RAM, disco, batería, volumen, brillo, capturas de pantalla, portapapeles y abrir programas.", ex: ["cuánta RAM y disco tengo", "sube el volumen a 40", "toma una captura de pantalla"] },
      { icon: "gear", mode: "ask", name: "Cerrar programas", desc: "Cierra un programa tuyo en ejecución (con tu permiso).", ex: ["cierra Firefox"] },
      { icon: "clock", mode: "auto", name: "Recordatorios", desc: "Te avisa con la burbuja y en voz alta a la hora indicada.", ex: ["recuérdame en 10 minutos tomar agua", "recuérdame mañana a las 8 la reunión"] },
      { icon: "chat", mode: "auto", name: "Notas y memoria", desc: "Guarda notas y datos que quieres que recuerde. Todo queda solo en tu PC.", ex: ["anota: comprar cable HDMI", "recuerda que prefiero respuestas cortas", "muéstrame mis notas"] },
      { icon: "bolt", mode: "ask", name: "Terminal", desc: "Ejecuta UN comando simple de consulta y te muestra el comando exacto antes. Nunca sudo, rm, formatear ni apagar.", ex: ["ejecuta el comando df -h", "qué versión de python tengo"] },
      { icon: "globe", mode: "auto", name: "Abrir páginas y programas", desc: "YouTube, Gmail, WhatsApp, GitHub, la calculadora y más. Búsquedas en Google o YouTube.", ex: ["abre YouTube", "abre la calculadora", "pon música de salsa"] },
      { icon: "window", mode: "auto", name: "Controlar la ventana", desc: "Minimiza a la burbuja o pasa a pantalla completa.", ex: ["minimízate", "pantalla completa"] },
    ],
  },
  en: {
    "nav.home": "Home", "nav.history": "History", "nav.tools": "Tools", "nav.settings": "Settings",
    "status.online": "Online", "status.noai": "AI not connected", "status.nomodel": "Model missing",
    "ai.missing": "Run:", "ai.off": "Install Ollama (ollama.com)",
    "hero.title": "Hi, I'm DOx", "hero.sub": "How can I help you today?",
    "card.mail": "Send an email", "card.code": "Edit code", "card.files": "Manage files",
    "card.tasks": "Run tasks", "card.more": "More options",
    "prompt.mail": "open gmail", "prompt.code": "Help me edit this code:\n", "prompt.files": "open files",
    placeholder: "Type your request…", send: "Send",
    newchat: "New conversation",
    "lang.tip": "Language", "theme.tip": "Change theme", "mic.on": "Listening: say “DOx…” (click to turn off)",
    "mic.off": "Turn on microphone (wake word)", "minimize.tip": "Minimize to the bubble", "quit.tip": "Quit DOx",
    "mic.err.deps": "Voice packages missing: pip install -r backend/requirements-voice.txt",
    "mic.err.model": "The Vosk voice model is missing (see the README, Voice section).",
    "mic.err.web": "The microphone only works in the desktop app.",
    "history.title": "History", "history.sub": "Your conversations, stored only on this computer.",
    "history.empty": "No saved conversations yet.", "history.clear": "Clear all", "history.sure": "Sure? Tap again",
    "history.msgs": "{n} messages", "history.delete": "Delete",
    "tools.title": "Tools", "tools.sub": "Here's what DOx can do for you. Tap an example to try it.", "badge.auto": "Automatic", "badge.ask": "Needs your permission",
    "settings.title": "Settings", "settings.sub": "Everything saves automatically.",
    "set.language": "Language", "set.appearance": "Appearance", "set.voice": "Voice", "set.mic": "Microphone", "set.ai": "Artificial intelligence", "set.about": "About",
    "theme.system": "System", "theme.light": "Light", "theme.dark": "Dark",
    "voice.replies": "Spoken replies", "voice.replies.sub": "DOx reads its answers aloud.",
    "voice.piper": "Natural neural voice (Piper): {voice}", "voice.espeak": "Basic voice (sounds robotic)",
    "voice.install": "For a natural voice run:", "voice.test": "Test voice", "voice.test.web": "Voice test only works in the desktop app.",
    "mic.setting": "Wake word", "mic.setting.sub": "Say “DOx” followed by a command. Needs the voice models.",
    "ai.model": "Model", "ai.profile": "Resource profile", "ai.state": "Status", "ai.ok": "Connected", "ai.down": "Not connected",
    "about.text": "DOx — desktop assistant with local AI; your data never leaves your computer.",
    "set.agent": "Research and permissions", "research.title": "Research the web", "research.auto": "Automatic", "research.always": "Always", "research.off": "Never",
    "research.sub": "Automatic: searches when you ask for facts or news. That's how DOx avoids making things up.",
    "perm.sub": "Reading, searching and opening is automatic. Anything that changes something (create, move, delete, commands, closing programs) asks your permission.",
    "perm.roots": "Allowed folders", "confirm.allow": "Allow", "confirm.deny": "Cancel", "confirm.allowed": "Allowed", "confirm.denied": "Cancelled",
    "confirm.ask": "DOx asks permission", "sources": "Sources", "reminder": "Reminder",
    "step.find_files": "Finding files", "step.open_file": "Opening file", "step.read_file": "Reading file", "step.list_folder": "Listing folder",
    "step.create_file": "Creating file", "step.create_folder": "Creating folder", "step.move_file": "Moving", "step.delete_file": "Moving to trash",
    "step.system_info": "Checking the system", "step.volume": "Volume", "step.toggle_mute": "Mute", "step.brightness": "Brightness", "step.screenshot": "Screenshot",
    "step.clipboard_copy": "Copying", "step.open_app": "Opening program", "step.close_app": "Closing program", "step.run_command": "Terminal",
    "step.add_note": "Saving note", "step.list_notes": "Reading notes", "step.delete_note": "Deleting note", "step.remember": "Remembering", "step.forget": "Forgetting",
    "step.set_reminder": "Setting reminder", "step.list_reminders": "Reading reminders", "step.cancel_reminder": "Cancelling reminder",
    error: "I couldn't reach my server. Is it running?",
    "bubble.open": "Open DOx", "bubble.quit": "Quit DOx", "bubble.tip": "Tap to open DOx",
    listening: "Yes? I'm listening…",
    tools: [
      { icon: "search", mode: "auto", name: "Research the web", desc: "Searches, reads pages and answers ONLY from what it finds, citing sources. If it can't find it, it says so.", ex: ["who is the president of France?", "research the dollar price today"] },
      { icon: "folder", mode: "auto", name: "Files: find, open and read", desc: "Finds by name in Documents, Downloads, Desktop and Pictures; opens and reads text, Word and PDF.", ex: ["open the attendance list", "read the PDF of my contract", "what's in my Downloads folder"] },
      { icon: "folder", mode: "ask", name: "Files: create, move, delete", desc: "Creates files and folders, moves or renames. Delete only sends to trash. It shows what it will do and waits for your permission.", ex: ["create a file notes.txt in Documents with my shopping list"] },
      { icon: "gear", mode: "auto", name: "System", desc: "RAM, disk, battery, volume, brightness, screenshots, clipboard and opening programs.", ex: ["how much RAM and disk do I have", "set volume to 40", "take a screenshot"] },
      { icon: "gear", mode: "ask", name: "Close programs", desc: "Closes one of your running programs (with your permission).", ex: ["close Firefox"] },
      { icon: "clock", mode: "auto", name: "Reminders", desc: "Alerts you with the bubble and out loud at the right time.", ex: ["remind me in 10 minutes to drink water", "remind me tomorrow at 8 about the meeting"] },
      { icon: "chat", mode: "auto", name: "Notes and memory", desc: "Saves notes and facts you want remembered. Everything stays on your PC.", ex: ["note: buy an HDMI cable", "remember I prefer short answers", "show my notes"] },
      { icon: "bolt", mode: "ask", name: "Terminal", desc: "Runs ONE simple read-only command and shows you the exact command first. Never sudo, rm, format or shutdown.", ex: ["run the command df -h", "what python version do I have"] },
      { icon: "globe", mode: "auto", name: "Open sites and programs", desc: "YouTube, Gmail, WhatsApp, GitHub, the calculator and more. Google or YouTube searches.", ex: ["open YouTube", "open the calculator", "play salsa music"] },
      { icon: "window", mode: "auto", name: "Control the window", desc: "Shrink to the bubble or go fullscreen.", ex: ["minimize", "fullscreen"] },
    ],
  },
};

const DoxSettings = {
  data: { lang: "es", theme: "system", speak: true, research: "auto" },
  _dark: window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null,

  resolved() {
    const th = this.data.theme;
    if (th === "light" || th === "dark") return th;
    return this._dark && this._dark.matches ? "dark" : "light";
  },
  apply() {
    document.documentElement.dataset.theme = this.resolved();
    document.documentElement.lang = this.data.lang;
    window.dispatchEvent(new Event("doxsettings"));
  },
  async load() {
    try { this.data = { ...this.data, ...(await (await fetch("/api/settings")).json()) }; } catch (e) {}
    this.apply();
    return this.data;
  },
  async save(patch) {
    this.data = { ...this.data, ...patch };
    this.apply();
    try {
      await fetch("/api/settings", { method: "POST", headers: { "Content-Type": "application/json" },
                                     body: JSON.stringify(patch) });
    } catch (e) {}
  },
  t(key, vars) {
    const dict = DOX_I18N[this.data.lang] || DOX_I18N.es;
    let s = dict[key] !== undefined ? dict[key] : key;
    if (vars && typeof s === "string") for (const k in vars) s = s.replace("{" + k + "}", vars[k]);
    return s;
  },
  logoSrc() {
    return this.resolved() === "dark" ? "/static/assets/mark-wave-dark.png" : "/static/assets/mark-wave.png";
  },
};
if (DoxSettings._dark) DoxSettings._dark.addEventListener("change", () => DoxSettings.apply());
