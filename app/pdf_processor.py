"""
Procesador de documentos PDF para el sistema Fortaleza Digital.
Usa pdfplumber (licencia MIT) para extracción de texto.
Trata todo contenido como entrada no confiable.
"""

import os
import io
import logging
from typing import List, Dict, Any, Optional
import pdfplumber
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from prompt_shield import sanitize_text
from config import config
from chunking import semantic_chunk_documents

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_source: Any) -> Dict[str, Any]:
    """
    Extrae texto de un PDF usando pdfplumber.
    
    Args:
        file_source: Ruta al archivo o bytes del archivo (Streamlit UploadedFile).
        
    Returns:
        Dict con documentos, recuento de páginas y alertas.
    """
    documents = []
    alerts = []
    page_count = 0
    
    try:
        # Handle both file paths and uploaded file objects
        if isinstance(file_source, (str, bytes, io.BytesIO)):
            pdf_context = pdfplumber.open(file_source)
        else:
            pdf_context = pdfplumber.open(io.BytesIO(file_source.read()))
            
        with pdf_context as pdf:
            page_count = len(pdf.pages)
            source_name = getattr(file_source, 'name', 'unknown_source')
            
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if not text:
                    continue
                
                # Sanitize text
                sanitized_text, page_alerts = sanitize_text(text)
                if page_alerts:
                    alerts.extend([f"Pág {i+1}: {a}" for a in page_alerts])
                
                doc = Document(
                    page_content=sanitized_text,
                    metadata={
                        "source": source_name,
                        "page": i + 1
                    }
                )
                documents.append(doc)
                
    except Exception as e:
        logger.error(f"Error procesando PDF: {str(e)}")
        raise e
        
    return {
        "documents": documents,
        "page_count": page_count,
        "alerts": alerts
    }

def chunk_documents(documents: List[Document]) -> List[Document]:
    """Divide los documentos en fragmentos manejables para la base de datos vectorial."""
    if config.SEMANTIC_CHUNKING:
        return semantic_chunk_documents(documents)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    return text_splitter.split_documents(documents)

def process_source(file_source: Any) -> Dict[str, Any]:
    """
    Procesa un archivo fuente completo: extracción + división.
    """
    extraction = extract_text_from_pdf(file_source)
    chunks = chunk_documents(extraction["documents"])
    
    return {
        "chunks": chunks,
        "page_count": extraction["page_count"],
        "alerts": extraction["alerts"]
    }
