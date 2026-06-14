"""
Escudo contra inyecciones de prompt en documentos PDF.
Trata todo texto de documento como entrada no confiable.
"""

import re
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

# Patterns that indicate prompt injection attempts
INJECTION_PATTERNS = [
    # Direct instruction override attempts
    r"(?i)ignore\s+(all\s+)?previous\s+instructions",
    r"(?i)ignore\s+(all\s+)?above\s+instructions",
    r"(?i)disregard\s+(all\s+)?previous",
    r"(?i)forget\s+(all\s+)?previous",
    r"(?i)override\s+system\s+prompt",
    r"(?i)new\s+instructions?\s*:",
    r"(?i)you\s+are\s+now\s+a",
    r"(?i)act\s+as\s+if\s+you\s+are",
    r"(?i)pretend\s+you\s+are",
    r"(?i)your\s+new\s+role\s+is",

    # Role switching attempts
    r"(?i)\[system\]",
    r"(?i)\[assistant\]",
    r"(?i)\[user\]",
    r"(?i)<\s*system\s*>",
    r"(?i)###\s*system",
    r"(?i)###\s*instruction",

    # Delimiter escape attempts
    r"(?i)```\s*system",
    r"(?i)---\s*system",
    r"(?i)END\s*OF\s*DOCUMENT",
    r"(?i)BEGIN\s*NEW\s*PROMPT",

    # Spanish variants
    r"(?i)ignora\s+(todas?\s+)?las?\s+instrucciones?\s+anteriores?",
    r"(?i)olvida\s+(todo\s+)?lo\s+anterior",
    r"(?i)nuevas?\s+instrucciones?\s*:",
    r"(?i)ahora\s+eres\s+un",

    # DAN (Do Anything Now) jailbreak variants
    r"(?i)\bDAN\b",
    r"(?i)do\s+anything\s+now",
    r"(?i)jail\s*(?:break|broke)",
    r"(?i)unlocked\s+mode",
    r"(?i)freedom\s+mode",

    # System prompt extraction
    r"(?i)(reveal|output|print|show|display|leak|dump)\s+(the\s+)?(system|initial)\s+(prompt|instructions|message)",
    r"(?i)(what\s+is|what\s+are|tell\s+me)\s+(your\s+)?(system\s+)?(prompt|instructions)\s*\?",

    # Unicode / homoglyph attack indicators
    r"(?i)(?:\\u[0-9a-f]{4}|\\x[0-9a-f]{2})\s*(?:system|prompt|instruction)",

    # Step-by-step reasoning jailbreaks
    r"(?i)lets\s+think\s+step\s+by\s+step.*ignore",
    r"(?i)work\s+through\s+this\s+carefully.*ignore",

    # Token smuggling / base64 encoded payloads
    r"(?i)base64\s*(?:decode|encod)",
    r"(?i)(?:ZX|ZQ|aW).{4,}={0,2}\s*(?:system|prompt)",

    # French variants (for multilingual documents)
    r"(?i)ignore\s+(toutes\s+)?les\s+instructions\s+pr[c\u00e9]c[c\u00e9]dentes",
    r"(?i)oublie\s+(tout\s+)?ce\s+qui\s+pr[c\u00e9]c[c\u00e9]de",
    r"(?i)nouvelles?\s+instructions?\s*:",
    r"(?i)tu\s+es\s+maintenant\s+un",

    # Context manipulation
    r"(?i)this\s+is\s+(not\s+)?a\s+test",
    r"(?i)the\s+above\s+text\s+is",
    r"(?i)regardless\s+of\s+the\s+previous",
]

COMPILED_PATTERNS = [re.compile(p) for p in INJECTION_PATTERNS]


def sanitize_text(text: str) -> Tuple[str, List[str]]:
    """
    Sanitiza texto extraído de documentos PDF.
    
    Args:
        text: Texto crudo extraído del PDF.
        
    Returns:
        Tuple de (texto_sanitizado, lista_de_alertas).
        Alertas contienen descripciones de patrones detectados.
    """
    if not text:
        return "", []
        
    alerts = []
    sanitized = text
    
    for pattern in COMPILED_PATTERNS:
        matches = pattern.findall(sanitized)
        if matches:
            for match in matches:
                alerts.append(f"Patrón detectado: '{match}'")
            # Replace injection attempts with harmless marker
            sanitized = pattern.sub("[CONTENIDO FILTRADO]", sanitized)
    
    if alerts:
        logger.warning(
            f"Inyección de prompt detectada y neutralizada: "
            f"{len(alerts)} patrones encontrados."
        )
    
    return sanitized, alerts


def build_safe_context(chunks: List[str]) -> str:
    """
    Construye contexto seguro para el LLM con delimitadores claros
    que impiden que texto inyectado en documentos anule el system prompt.
    
    Args:
        chunks: Lista de fragmentos de texto recuperados.
        
    Returns:
        Contexto formateado con barreras de seguridad.
    """
    safe_chunks = []
    for i, chunk in enumerate(chunks):
        sanitized, _ = sanitize_text(chunk)
        safe_chunks.append(
            f"[FRAGMENTO_DOC_{i+1}_INICIO]\n"
            f"{sanitized}\n"
            f"[FRAGMENTO_DOC_{i+1}_FIN]"
        )
    
    return "\n\n".join(safe_chunks)
