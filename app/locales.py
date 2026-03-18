"""
Todas las cadenas de texto de la interfaz en español formal militar.
Centralizado para mantenimiento y consistencia lingüística.
"""

# ── Encabezados ──
TITLE = "▸ TERMINAL RAG SOBERANO"
SUBTITLE = "Sistema de Inteligencia Documental en Entorno Aislado"
SUBTITLE_DETAIL = "Cero conexiones externas // Procesamiento 100% local"

# ── Barra de Estado ──
STATUS_ONLINE = "● OPERATIVO"
STATUS_OFFLINE = "○ FUERA DE LÍNEA"
STATUS_OLLAMA = "Motor LLM"
STATUS_DOCS = "Documentos Cargados"
STATUS_MODEL = "Modelo Activo"
STATUS_EMBEDDINGS = "Modelo de Embeddings"

# ── Barra Lateral ──
SIDEBAR_HEADER = "INGESTA DE DOCUMENTOS"
SIDEBAR_UPLOAD = "Arrastre sus archivos PDF aquí"
SIDEBAR_UPLOAD_HELP = "Formatos aceptados: PDF. Tamaño máximo: 200MB."
BTN_INGEST = "⚡ PROCESAR DOCUMENTOS"
BTN_CLEAR = "🗑 PURGAR BASE DE DATOS"
CLEAR_CONFIRM = "¿Confirmar purga completa de la base de datos vectorial?"
SIDEBAR_INGESTED = "Documentos Procesados"
SIDEBAR_SYSTEM = "ESTADO DEL SISTEMA"
SIDEBAR_NO_DOCS = "Sin documentos procesados."

# ── Área Principal ──
QUERY_LABEL = "consulta▸"
QUERY_PLACEHOLDER = "Introduzca su consulta sobre los documentos cargados..."
BTN_EXECUTE = "EJECUTAR CONSULTA"
RESPONSE_HEADER = "RESPUESTA DEL SISTEMA"
SOURCES_HEADER = "▾ Documentos Fuente"
SOURCE_FILE = "Archivo"
SOURCE_PAGE = "Página"
RESPONSE_TIME = "Tiempo de respuesta"
NO_DOCS_WARNING = "⚠ Debe procesar al menos un documento antes de realizar consultas."
PROCESSING_QUERY = "Procesando consulta... Esto puede tardar hasta 2 minutos."
PROCESSING_INGEST = "Procesando documento"

# ── Historial ──
HISTORY_HEADER = "HISTORIAL DE CONSULTAS"
HISTORY_EMPTY = "Sin consultas previas en esta sesión."
HISTORY_Q = "P"
HISTORY_A = "R"

# ── Errores ──
ERR_OLLAMA_UNAVAILABLE = "ERROR: Motor Ollama no disponible. Verifique que el contenedor esté ejecutándose."
ERR_QUERY_EMPTY = "ERROR: La consulta no puede estar vacía."
ERR_INGEST_FAIL = "ERROR: Fallo en la ingesta del documento"
ERR_PDF_ENCRYPTED = "ADVERTENCIA: PDF cifrado detectado — omitido"
ERR_PDF_EMPTY = "ADVERTENCIA: PDF sin contenido de texto — omitido"
ERR_TIMEOUT = "ERROR: Tiempo de espera agotado. El modelo necesita más tiempo o recursos insuficientes."
ERR_INJECTION = "ALERTA: Patrón de inyección detectado y neutralizado en el documento."

# ── Ingesta ──
INGEST_SUCCESS = "documentos procesados exitosamente"
INGEST_CHUNKS = "fragmentos generados"
INGEST_PAGES = "páginas"

# ── Sistema ──
SYS_GPU_DETECTED = "GPU detectada"
SYS_CPU_MODE = "Modo CPU"
SYS_VRAM = "VRAM disponible"
SYS_CHUNKS_CONFIG = "Configuración de fragmentos"
