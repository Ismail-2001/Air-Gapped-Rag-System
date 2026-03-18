"""
Interfaz de usuario de Fortaleza Digital - Terminal RAG Táctico en Español.
Estética monocromo, 100% aire-gapped.
"""

import streamlit as st
import time
import logging
from typing import List, Dict, Any
from config import config
import locales
from pdf_processor import process_source
from rag_engine import RAGEngine

# Configuración de página con estética terminal
st.set_page_config(
    page_title=locales.TITLE,
    page_icon="▸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para estética militar táctica
st.markdown("""
<style>
/* Font-family fallback para entorno offline */
* { font-family: "Courier New", Courier, monospace !important; }

/* Ocultar elementos de Streamlit branding */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
.stDeployButton { display: none; }

/* Fondo negro puro */
.stApp { background-color: #000000; }
[data-testid="stSidebar"] { 
    background-color: #050505; 
    border-right: 1px solid #00FF00; 
}

/* Texto verde fosforito */
.stMarkdown, .stText, p, span, label, h1, h2, h3 { 
    color: #00FF00 !important; 
}

/* Botones terminales */
.stButton > button {
    background-color: transparent !important;
    color: #00FF00 !important;
    border: 1px solid #00FF00 !important;
    border-radius: 0 !important;
    text-transform: uppercase;
    font-weight: 600;
    letter-spacing: 2px;
    width: 100%;
}
.stButton > button:hover {
    background-color: #00FF00 !important;
    color: #000000 !important;
}

/* Campos de entrada */
.stTextInput input, .stTextArea textarea {
    background-color: #0a0a0a !important;
    color: #00FF00 !important;
    border: 1px solid #1a3a1a !important;
    border-radius: 0 !important;
}

/* Expander con estilo militar */
.streamlit-expanderHeader { 
    color: #00FF00 !important; 
    background-color: #050505 !important;
    border: 1px solid #1a3a1a !important;
    border-radius: 0 !important;
}

/* Respuesta destacada */
.response-box {
    background-color: #050505;
    border-left: 3px solid #00FF00;
    padding: 1.5rem;
    margin: 1rem 0;
    border-bottom: 1px solid #1a3a1a;
}

.cursor-blink::after {
    content: "█";
    animation: blink 1s step-end infinite;
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0; }
}

/* Alertas */
.error-text { color: #FF0000 !important; font-weight: bold; }
.warning-text { color: #FFAA00 !important; }

/* Efecto scanline en cabecera */
.scanline-header {
    border-bottom: 2px solid #00FF00;
    padding-bottom: 10px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.scanline-header::after {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(0deg, rgba(0, 255, 0, 0.05) 50%, transparent 50%);
    background-size: 100% 4px;
    pointer-events: none;
}
</style>
""", unsafe_allow_html=True)

# ── Estado de Sesión ──
if 'rag_engine' not in st.session_state:
    try:
        with st.spinner(locales.PROCESSING_INGEST):
            st.session_state.rag_engine = RAGEngine()
    except Exception as e:
        st.error(locales.ERR_OLLAMA_UNAVAILABLE)

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'ingested_docs' not in st.session_state:
    st.session_state.ingested_docs = []

# ── Barra Lateral ──
st.sidebar.markdown(f"### {locales.SIDEBAR_HEADER}")
uploaded_files = st.sidebar.file_uploader(
    locales.SIDEBAR_UPLOAD,
    type=["pdf"],
    accept_multiple_files=True,
    help=locales.SIDEBAR_UPLOAD_HELP
)

if st.sidebar.button(locales.BTN_INGEST) and uploaded_files:
    for uploaded_file in uploaded_files:
        with st.spinner(f"{locales.PROCESSING_INGEST}: {uploaded_file.name}"):
            try:
                result = process_source(uploaded_file)
                st.session_state.rag_engine.ingest_documents(result["chunks"])
                st.session_state.ingested_docs.append({
                    "name": uploaded_file.name,
                    "pages": result["page_count"],
                    "chunks": len(result["chunks"]),
                    "alerts": result["alerts"]
                })
                st.sidebar.success(f"✓ {uploaded_file.name}")
            except Exception as e:
                st.sidebar.error(f"{locales.ERR_INGEST_FAIL}: {uploaded_file.name}")

st.sidebar.divider()

if st.sidebar.button(locales.BTN_CLEAR):
    if st.sidebar.checkbox(locales.CLEAR_CONFIRM):
        st.session_state.rag_engine.purge_database()
        st.session_state.ingested_docs = []
        st.session_state.chat_history = []
        st.rerun()

st.sidebar.markdown(f"### {locales.SIDEBAR_INGESTED}")
if not st.session_state.ingested_docs:
    st.sidebar.info(locales.SIDEBAR_NO_DOCS)
else:
    for doc in st.session_state.ingested_docs:
        with st.sidebar.expander(f"📄 {doc['name']}"):
            st.write(f"{locales.INGEST_PAGES}: {doc['pages']}")
            st.write(f"{locales.INGEST_CHUNKS}: {doc['chunks']}")
            for alert in doc['alerts']:
                st.markdown(f"<span class='warning-text'>⚠ {alert}</span>", unsafe_allow_html=True)

st.sidebar.divider()
st.sidebar.markdown(f"### {locales.SIDEBAR_SYSTEM}")
st.sidebar.text(f"{locales.STATUS_MODEL}: {config.LLM_MODEL}")
st.sidebar.text(f"{locales.STATUS_EMBEDDINGS}: {config.EMBEDDING_MODEL}")
st.sidebar.text(f"{locales.STATUS_ONLINE if st.session_state.rag_engine else locales.STATUS_OFFLINE}")


# ── Área Principal ──
st.markdown(f"<div class='scanline-header'><h1>{locales.TITLE}</h1><p>{locales.SUBTITLE}</p></div>", unsafe_allow_html=True)
st.markdown(f"*{locales.SUBTITLE_DETAIL}*")

query = st.text_input(locales.QUERY_LABEL, placeholder=locales.QUERY_PLACEHOLDER)

col1, col2, _ = st.columns([1, 1, 2])
with col1:
    execute_btn = st.button(locales.BTN_EXECUTE)

if execute_btn:
    if not query:
        st.error(locales.ERR_QUERY_EMPTY)
    elif not st.session_state.ingested_docs:
        st.warning(locales.NO_DOCS_WARNING)
    else:
        start_time = time.time()
        with st.spinner(locales.PROCESSING_QUERY):
            try:
                response = st.session_state.rag_engine.query(query)
                end_time = time.time()
                
                # Almacenar en historial
                st.session_state.chat_history.insert(0, {
                    "question": query,
                    "answer": response["result"],
                    "sources": response["source_documents"],
                    "time": round(end_time - start_time, 2)
                })
            except Exception as e:
                st.error(f"{locales.ERR_OLLAMA_UNAVAILABLE}")

# ── Mostrar Resultados ──
if st.session_state.chat_history:
    latest = st.session_state.chat_history[0]
    
    st.markdown(f"### {locales.RESPONSE_HEADER}")
    st.markdown(f"<div class='response-box'>{latest['answer']}</div>", unsafe_allow_html=True)
    
    st.markdown(f"*{locales.RESPONSE_TIME}: {latest['time']}s*")
    
    with st.expander(locales.SOURCES_HEADER):
        for doc in latest["sources"]:
            st.markdown(f"**[{locales.SOURCE_FILE}: {doc.metadata['source']} | {locales.SOURCE_PAGE}: {doc.metadata['page']}]**")
            st.text(doc.page_content)
            st.divider()

st.divider()

# ── Historial ──
st.markdown(f"### {locales.HISTORY_HEADER}")
if not st.session_state.chat_history:
    st.info(locales.HISTORY_EMPTY)
else:
    for i, entry in enumerate(st.session_state.chat_history[1:]): # Mostrar anteriores al actual
        with st.expander(f"Q: {entry['question'][:50]}..."):
            st.write(f"**{locales.HISTORY_Q}:** {entry['question']}")
            st.write(f"**{locales.HISTORY_A}:** {entry['answer']}")
