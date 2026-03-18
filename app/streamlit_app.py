"""
Air-Gapped RAG Terminal UI
Streamlit-based dashboard for secure, offline document intelligence.
"""

import streamlit as st
import time
import os
from rag_engine import RAGEngine
from pdf_processor import process_uploaded_file
from config import config

# Page Config
st.set_page_config(
    page_title="SECURE RAG TERMINAL",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Terminal Aesthetic)
st.markdown("""
<style>
    /* Main Font Override */
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code&family=JetBrains+Mono&display=swap');
    
    * {
        font-family: 'Fira Code', 'JetBrains Mono', 'Courier New', monospace !important;
    }

    /* Overall Background */
    .stApp {
        background-color: #0a0a0a;
        color: #c0c0c0;
    }

    /* Sidebar Background */
    section[data-testid="stSidebar"] {
        background-color: #111111;
        border-right: 1px solid #1a1a1a;
    }

    /* Green Monospace Headers */
    h1, h2, h3 {
        color: #00ff41 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* Flat Green Buttons */
    .stButton > button {
        background-color: transparent !important;
        color: #00ff41 !important;
        border: 1px solid #00ff41 !important;
        border-radius: 0px !important;
        text-transform: uppercase !important;
        padding: 0.5rem 2rem !important;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: rgba(0, 255, 65, 0.1) !important;
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
    }

    /* Response Container Style */
    .response-card {
        padding: 1.5rem;
        background-color: #111111;
        border: 1px solid #1a1a1a;
        border-left: 4px solid #00ff41;
        margin-bottom: 1rem;
    }

    /* Blinking Cursor for Terminal Inputs */
    .stTextInput input::after {
        content: '_';
        animation: blink 1s step-end infinite;
    }
    
    @keyframes blink {
        from, to { color: transparent; }
        50% { color: #00ff41; }
    }

    /* Scanner Animation for Header */
    .scanner-line {
        width: 100%;
        height: 1px;
        background: linear-gradient(to right, transparent, #00ff41, transparent);
        position: absolute;
        top: 0;
        left: 0;
        animation: scanner 5s infinite;
        opacity: 0.3;
    }

    @keyframes scanner {
        0% { top: 0; }
        100% { top: 100%; }
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 5px;
    }
    ::-webkit-scrollbar-track {
        background: #0a0a0a;
    }
    ::-webkit-scrollbar-thumb {
        background: #1a1a1a;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #00ff41;
    }

    /* Status Indicators */
    .status-online { color: #00ff41; }
    .status-offline { color: #ff4444; }
    .status-warning { color: #ffaa00; }
</style>
""", unsafe_allow_html=True)

# Application Logic
def initialize_engine():
    """Load the RAG Engine into session state."""
    if "rag_engine" not in st.session_state:
        st.session_state.rag_engine = RAGEngine()
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "ingested_files" not in st.session_state:
        st.session_state.ingested_files = []

# Header
st.markdown("<div class='scanner-line'></div>", unsafe_allow_html=True)
st.title("▸ SECURE RAG TERMINAL")
st.caption("Air-Gapped Document Intelligence System (Local GPU/CPU Execution)")

initialize_engine()
engine = st.session_state.rag_engine

# System Health Check
health = engine.health_check()
stats = engine.get_stats()

# Status Bar
hdr_cols = st.columns([1, 1, 1, 1])
hdr_cols[0].markdown(f"**STATUS:** {'● ONLINE' if health['status'] == 'online' else '● OFFLINE'}", help="Connectivity check to local Ollama API")
hdr_cols[1].markdown(f"**DOCS:** {stats['count']}", help="Total number of text chunks currently indexed")
hdr_cols[2].markdown(f"**MODEL:** `{config.LLM_MODEL.split(':')[0]}`")
hdr_cols[3].markdown(f"**EMBED:** `{config.EMBEDDING_MODEL.split('-')[0]}`")

st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("DOCUMENT INGEST")
    
    uploaded_files = st.file_uploader(
        "UPLOAD PDF DOCUMENTS",
        type="pdf",
        accept_multiple_files=True,
    )
    
    if st.button("EXECUTE INGESTION") and uploaded_files:
        with st.status("PROCESSING...", expanded=True) as status_box:
            for uploaded_file in uploaded_files:
                st.write(f"▸ Indexing `{uploaded_file.name}`...")
                chunks = process_uploaded_file(uploaded_file)
                count = engine.ingest(chunks)
                st.session_state.ingested_files.append({
                    "name": uploaded_file.name,
                    "pages": "PDF", # In progress would be better with real counts
                    "chunks": count,
                    "time": time.strftime("%H:%M:%S")
                })
            status_box.update(label="INGESTION COMPLETED", state="complete", expanded=False)
            st.rerun()

    st.markdown("---")
    st.header("INGESTED INDEX")
    if not st.session_state.ingested_files:
        st.caption("No documents in index")
    else:
        for file in st.session_state.ingested_files:
            st.markdown(f"• `{file['name']}` ({file['chunks']} chunks)")
            
    if st.button("CLEAR LOCAL DATABASE"):
        engine.clear()
        st.session_state.ingested_files = []
        st.session_state.chat_history = []
        st.rerun()
    
    st.markdown("---")
    st.header("SYSTEM SPECS")
    st.code(f"""
    LLM: {config.LLM_MODEL}
    EMBED: {config.EMBEDDING_MODEL}
    CHUNKS: {config.CHUNK_SIZE}/{config.CHUNK_OVERLAP}
    TOP_K: {config.TOP_K_RESULTS}
    TIMEOUT: {config.REQUEST_TIMEOUT}s
    """, language="markdown")

# Main Interface
query = st.text_input("query▸", placeholder="Enter your query here...", help="Type natural language questions about your uploaded documents.")

if st.button("EXECUTE") and query:
    with st.spinner("Processing request through local intelligence pipeline..."):
        result = engine.query(query)
        st.session_state.chat_history.insert(0, {
            "query": query,
            "answer": result["answer"],
            "sources": result["sources"],
            "time": result["time"]
        })

# Display Chat History
for chat in st.session_state.chat_history:
    with st.container():
        st.markdown(f"**Q: {chat['query']}**")
        st.markdown(f"""
        <div class="response-card">
            {chat['answer']}
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("▸ SOURCE CITATIONS"):
            if not chat["sources"]:
                st.write("No source documents referenced.")
            for i, src in enumerate(chat["sources"]):
                st.markdown(f"[{i+1}] `{src['source']}` (Page {src['page']})")
                st.caption(f"Context: ...{src['content']}...")
                
        st.caption(f"Response Latency: {chat['time']} | Secure Local Cache Execution")
        st.markdown("<br>", unsafe_allow_html=True)
