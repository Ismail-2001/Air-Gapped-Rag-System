"""
RAG Engine Core
Handles the RAG pipeline including embeddings, vector store management, and LLM querying.
"""

import time
import requests
from typing import List, Dict, Any
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import config

class RAGEngine:
    def __init__(self):
        # LOCAL embeddings — sentence-transformers runs on CPU
        # Pre-downloaded in Dockerfile or runs on first use
        self.embeddings = HuggingFaceEmbeddings(
            model_name=config.EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )

        # LOCAL vector store — ChromaDB in-process
        # Using persistent directory if it exists, otherwise in-memory by default if no path passed
        self.vectorstore = Chroma(
            collection_name="airgap_docs",
            embedding_function=self.embeddings,
            persist_directory=config.CHROMA_PERSIST_DIR
        )

        # LOCAL LLM — Ollama on internal Docker network
        self.llm = Ollama(
            base_url=config.OLLAMA_BASE_URL,
            model=config.LLM_MODEL,
            temperature=0.2,
            request_timeout=config.REQUEST_TIMEOUT,
        )

        # RAG chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": config.TOP_K_RESULTS}
            ),
            return_source_documents=True,
        )

    def ingest(self, documents: List[Any]) -> int:
        """
        Add document chunks to vector store.
        
        Args:
            documents: List of LangChain Document chunks.
            
        Returns:
            The number of chunks added.
        """
        if not documents:
            return 0
            
        self.vectorstore.add_documents(documents)
        # Persistent storage update
        self.vectorstore.persist()
        return len(documents)

    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the RAG chain.
        
        Args:
            question: The user query string.
            
        Returns:
            A dictionary containing answer, sources, and response time.
        """
        start_time = time.time()
        
        try:
            response = self.qa_chain.invoke({"query": question})
            answer = response["result"]
            sources = []
            
            for doc in response["source_documents"]:
                sources.append({
                    "source": doc.metadata.get("source", "unknown"),
                    "page": doc.metadata.get("page", "unknown"),
                    "content": doc.page_content[:200] + "..."
                })
                
            response_time = time.time() - start_time
            
            return {
                "answer": answer,
                "sources": sources,
                "time": f"{response_time:.2f}s"
            }
        except Exception as e:
            return {
                "answer": f"ERROR: Failed to process query. Details: {str(e)}",
                "sources": [],
                "time": "0.00s"
            }

    def get_stats(self) -> Dict[str, Any]:
        """
        Return collection count and status.
        
        Returns:
            A dictionary with the number of documents and DB status.
        """
        try:
            count = self.vectorstore._collection.count()
            return {
                "count": count,
                "status": "online" if count >= 0 else "offline"
            }
        except Exception:
            return {"count": 0, "status": "error"}

    def clear(self):
        """Reset the vector store by deleting all documents."""
        # Note: Chroma's delete all can be tricky, re-initing might be safer for MVP
        self.vectorstore.delete_collection()
        self.vectorstore = Chroma(
            collection_name="airgap_docs",
            embedding_function=self.embeddings,
            persist_directory=config.CHROMA_PERSIST_DIR
        )

    def health_check(self) -> Dict[str, Any]:
        """
        Check Ollama connectivity and model availability.
        
        Returns:
            A dictionary indicating status and loaded models.
        """
        try:
            resp = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=5)
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                model_names = [m["name"] for m in models]
                status = "online" if config.LLM_MODEL in model_names else "model_missing"
                return {"status": status, "models": model_names}
            return {"status": "offline", "models": []}
        except Exception:
            return {"status": "offline", "models": []}
