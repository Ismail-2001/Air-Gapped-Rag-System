"""
RAG Integration Test
Verifies the end-to-end RAG pipeline from ingestion to query.
"""

import os
import sys
import time
import fitz  # PyMuPDF

# Add app directory to sys.path for importing local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

from rag_engine import RAGEngine
from pdf_processor import process_directory

def create_test_pdf(file_path: str, content: str):
    """Create a simple PDF for testing purposes."""
    print(f"Creating test PDF: {file_path}...")
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), content)
    doc.save(file_path)
    doc.close()

def run_integration_test():
    """Execute the full RAG integration test cycle."""
    test_pdf_path = "test_document.pdf"
    test_content = (
        "The secret code for the deep bunker is 812-XYZ-DELTA. "
        "The project name is AIR-GAP-ONE. Authorized personnel only."
    )
    
    try:
        # 1. Create PDF
        create_test_pdf(test_pdf_path, test_content)
        
        # 2. Init Engine
        print("Initializing RAG Engine...")
        engine = RAGEngine()
        
        # 3. Ingest
        print("Ingesting test document...")
        # Since process_directory processes all PDFs in a dir, we might need a temp dir
        os.makedirs("test_docs", exist_ok=True)
        os.rename(test_pdf_path, os.path.join("test_docs", test_pdf_path))
        
        from pdf_processor import process_directory
        docs = process_directory("test_docs")
        count = engine.ingest(docs)
        print(f"Ingested {count} chunks.")
        
        # 4. Query
        query = "What is the secret code for the deep bunker?"
        print(f"Querying: {query}...")
        result = engine.query(query)
        
        print("\n--- RESULTS ---")
        print(f"QUERY: {query}")
        print(f"ANSWER: {result['answer']}")
        print(f"SOURCES: {[s['source'] for s in result['sources']]}")
        print(f"TIME: {result['time']}")
        
        # 5. Assertions
        assert "812-XYZ-DELTA" in result["answer"].upper()
        assert "test_document.pdf" in [s["source"] for s in result["sources"]]
        
        print("\n[PASS] Integration Test Successful.")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Integration Test Failed: {str(e)}")
        return False
    finally:
        # Cleanup
        if os.path.exists("test_docs/test_document.pdf"):
            os.remove("test_docs/test_document.pdf")
        if os.path.exists("test_docs"):
            os.rmdir("test_docs")
        if os.path.exists("test_document.pdf"):
            os.remove("test_document.pdf")

if __name__ == "__main__":
    success = run_integration_test()
    sys.exit(0 if success else 1)
