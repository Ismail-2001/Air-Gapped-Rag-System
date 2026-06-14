import re
import logging
from typing import List, Any

from langchain.docstore.document import Document
from config import config

logger = logging.getLogger(__name__)


def sentence_aware_chunk(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    metadata: dict | None = None,
) -> List[Document]:
    """Splits text at sentence/paragraph boundaries near chunk_size."""
    if not text:
        return []

    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks: List[str] = []
    current = []
    current_len = 0
    overlap_buffer: List[str] = []

    for sent in sentences:
        sent_len = len(sent)
        if current_len + sent_len > chunk_size and current:
            chunk_text = " ".join(current)
            chunks.append(chunk_text)
            overlap_text = " ".join(overlap_buffer) if overlap_buffer else ""
            # prepare overlap: last N sentences
            overlap_buf: List[str] = []
            overlap_len = 0
            for s in reversed(current):
                if overlap_len + len(s) >= chunk_overlap:
                    break
                overlap_buf.insert(0, s)
                overlap_len += len(s)
            overlap_buffer = overlap_buf
            current = list(overlap_buffer) if overlap_buffer else []
            current_len = sum(len(s) for s in current)

        current.append(sent)
        current_len += sent_len

    if current:
        chunk_text = " ".join(current)
        chunks.append(chunk_text)

    docs = []
    meta = dict(metadata) if metadata else {}
    for i, chunk in enumerate(chunks):
        doc_meta = dict(meta)
        doc_meta["chunk_index"] = i
        doc_meta["chunk_count"] = len(chunks)
        docs.append(Document(page_content=chunk, metadata=doc_meta))

    return docs


def semantic_chunk_documents(
    documents: List[Document],
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> List[Document]:
    """Chunk documents using sentence-aware splitting."""
    size = chunk_size or config.CHUNK_SIZE
    overlap = chunk_overlap or config.CHUNK_OVERLAP
    all_chunks: List[Document] = []
    for doc in documents:
        chunks = sentence_aware_chunk(
            doc.page_content,
            chunk_size=size,
            chunk_overlap=overlap,
            metadata=doc.metadata,
        )
        all_chunks.extend(chunks)
    logger.info(
        "Semantic chunking: %d docs → %d chunks (size=%d, overlap=%d)",
        len(documents), len(all_chunks), size, overlap,
    )
    return all_chunks
