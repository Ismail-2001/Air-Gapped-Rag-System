"""
PDF Processing Module
Handles text extraction and chunking of PDF documents for the RAG system.
"""

import os
import io
import fitz  # PyMuPDF
from typing import List, Dict, Any, Union
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from config import config

def extract_text_from_pdf(file_source: Union[str, bytes]) -> List[Dict[str, Any]]:
    """
    Extracts text from each page of a PDF file.
    
    Args:
        file_source: Either a path to the file or the bytes content.
        
    Returns:
        A list of dictionaries containing 'text' and 'metadata' for each page.
    """
    pages = []
    
    try:
        if isinstance(file_source, bytes):
            doc = fitz.open(stream=file_source, filetype="pdf")
        else:
            doc = fitz.open(file_source)
            
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            
            if text.strip():
                pages.append({
                    "text": text,
                    "metadata": {
                        "page": page_num + 1,
                        "source": os.path.basename(file_source) if isinstance(file_source, str) else "uploaded_file"
                    }
                })
        
        doc.close()
    except Exception as e:
        print(f"Error processing PDF: {e}")
        
    return pages

def chunk_documents(pages: List[Dict[str, Any]]) -> List[Document]:
    """
    Splits page text into manageable chunks.
    
    Args:
        pages: List of dictionaries containing page text and metadata.
        
    Returns:
        A list of LangChain Document objects.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        length_function=len,
    )
    
    langchain_docs = []
    for page in pages:
        chunks = text_splitter.split_text(page["text"])
        for i, chunk in enumerate(chunks):
            metadata = page["metadata"].copy()
            metadata["chunk_index"] = i
            langchain_docs.append(Document(page_content=chunk, metadata=metadata))
            
    return langchain_docs

def process_uploaded_file(uploaded_file) -> List[Document]:
    """
    Handles PDF uploaded through Streamlit.
    
    Args:
        uploaded_file: The Streamlit UploadedFile object.
        
    Returns:
        A list of processed Document chunks.
    """
    file_bytes = uploaded_file.read()
    pages = extract_text_from_pdf(file_bytes)
    # Correct filename for metadata
    for page in pages:
        page["metadata"]["source"] = uploaded_file.name
    return chunk_documents(pages)

def process_directory(dir_path: str) -> List[Document]:
    """
    Processes all PDF files in a given directory.
    
    Args:
        dir_path: Path to the directory containing PDFs.
        
    Returns:
        A combined list of Document chunks from all PDFs.
    """
    all_chunks = []
    if not os.path.exists(dir_path):
        return all_chunks
        
    for filename in os.listdir(dir_path):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(dir_path, filename)
            pages = extract_text_from_pdf(file_path)
            all_chunks.extend(chunk_documents(pages))
            
    return all_chunks
