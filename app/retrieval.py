import math
import re
import logging
from collections import Counter
from typing import List, Dict, Any
from config import config

logger = logging.getLogger(__name__)

STOP_WORDS: set = {
    "el", "la", "los", "las", "un", "una", "unos", "unas", "y", "e", "o", "u",
    "de", "del", "en", "por", "para", "con", "sin", "a", "ante", "bajo",
    "cabe", "como", "contra", "da", "de", "desde", "di", "do", "durante",
    "e", "el", "ella", "ellas", "ellos", "en", "entre", "era", "erais",
    "eran", "eras", "eres", "es", "esa", "esas", "ese", "eso", "esos",
    "esta", "estaba", "estabais", "estaban", "estabas", "estad", "estada",
    "estadas", "estado", "estados", "estamos", "estando", "estar", "estaremos",
    "estará", "estarán", "estarás", "estaré", "estaréis", "estaría",
    "estaríais", "estaríamos", "estarían", "estarías", "estas", "este",
    "estemos", "esto", "estos", "estoy", "estuve", "estuviera", "estuvierais",
    "estuvieran", "estuvieras", "estuvieron", "estuviese", "estuvieseis",
    "estuviesen", "estuvieses", "estuvimos", "estuviste", "estuvisteis",
    "estuviéramos", "estuviésemos", "esta", "estábamos", "estáis", "están",
    "estás", "esté", "estéis", "estén", "estés", "fue", "fuera", "fuerais",
    "fueran", "fueras", "fueron", "fuese", "fueseis", "fuesen", "fueses",
    "fui", "fuimos", "fuiste", "fuisteis", "fuéramos", "fuésemos", "ha",
    "habida", "habidas", "habido", "habidos", "habiendo", "habremos",
    "habrá", "habrán", "habrás", "habré", "habréis", "habría", "habríais",
    "habríamos", "habrían", "habrías", "habéis", "había", "habíais",
    "habíamos", "habían", "habías", "han", "has", "hasta", "hay", "haya",
    "hayamos", "hayan", "hayas", "hayáis", "he", "hemos", "hube", "hubiera",
    "hubierais", "hubieran", "hubieras", "hubieron", "hubiese", "hubieseis",
    "hubiesen", "hubieses", "hubimos", "hubiste", "hubisteis", "hubiéramos",
    "hubiésemos", "la", "las", "le", "les", "lo", "los", "me", "mi",
    "mis", "mucho", "muchos", "muy", "más", "mí", "mía", "mías", "mío",
    "míos", "no", "nos", "nosotras", "nosotros", "nuestra", "nuestras",
    "nuestro", "nuestros", "os", "otra", "otras", "otro", "otros", "para",
    "pero", "poco", "por", "porque", "que", "se", "sea", "seamos", "sean",
    "seas", "seáis", "será", "serán", "serás", "seré", "seréis", "sería",
    "seríais", "seríamos", "serían", "serías", "si", "sido", "siendo",
    "sin", "sino", "sobre", "sois", "somos", "son", "soy", "su", "sus",
    "suyo", "suyos", "sé", "sí", "tal", "también", "tanto", "te", "tenemos",
    "tengo", "tengáis", "tenida", "tenidas", "tenido", "tenidos", "teniendo",
    "tenéis", "tenía", "teníais", "teníamos", "tenían", "tenías", "ti",
    "tiene", "tienen", "tienes", "todo", "tus", "tuvo", "tuya", "tuyo",
    "tuyos", "tú", "un", "una", "uno", "unos", "vosotras", "vosotros",
    "vuestra", "vuestras", "vuestro", "vuestros", "y", "ya", "yo", "él",
    "éramos", "ésa", "ésas", "ése", "ésos", "ésta", "éstas", "éste",
    "éstos", "ú",
}


def tokenize(text: str) -> List[str]:
    text = text.lower()
    tokens = re.findall(r"\w+", text)
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 1]


class BM25:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_freqs: List[Counter] = []
        self.doc_len: List[int] = []
        self.avgdl: float = 0.0
        self.idf: Dict[str, float] = {}
        self.documents: List[str] = []
        self.num_docs: int = 0

    def fit(self, documents: List[str]):
        self.documents = documents
        self.num_docs = len(documents)
        self.doc_freqs = [Counter(tokenize(doc)) for doc in documents]
        self.doc_len = [sum(freqs.values()) for freqs in self.doc_freqs]
        self.avgdl = sum(self.doc_len) / self.num_docs if self.num_docs else 0.0

        df: Dict[str, int] = {}
        for freqs in self.doc_freqs:
            for term in freqs:
                df[term] = df.get(term, 0) + 1

        self.idf = {
            term: math.log(1 + (self.num_docs - freq + 0.5) / (freq + 0.5))
            for term, freq in df.items()
        }

    def score(self, query: str, doc_index: int) -> float:
        query_tokens = tokenize(query)
        freqs = self.doc_freqs[doc_index]
        doc_len = self.doc_len[doc_index]

        score = 0.0
        for term in set(query_tokens):
            if term not in self.idf:
                continue
            tf = freqs.get(term, 0)
            if tf == 0:
                continue
            idf = self.idf[term]
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl)
            score += idf * (numerator / denominator)
        return score

    def search(self, query: str, top_k: int = 10) -> List[tuple[int, float]]:
        scores = [(i, self.score(query, i)) for i in range(self.num_docs)]
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


def reciprocal_rank_fusion(
    vector_results: List[tuple[int, float]],
    bm25_results: List[tuple[int, float]],
    k: int = 60,
    top_k: int = 4,
) -> List[int]:
    rrf_scores: Dict[int, float] = {}
    for rank, (doc_id, _) in enumerate(vector_results):
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1 / (k + rank + 1)
    for rank, (doc_id, _) in enumerate(bm25_results):
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1 / (k + rank + 1)
    ranked = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    return [doc_id for doc_id, _ in ranked[:top_k]]


class HybridRetriever:
    """Combines Chroma vector search with BM25 keyword search via RRF."""

    def __init__(self, vectorstore, bm25: BM25 | None = None):
        self.vectorstore = vectorstore
        self.bm25 = bm25
        self.top_k = config.TOP_K_RESULTS
        self.score_threshold = config.SIMILARITY_THRESHOLD

    def invoke(self, query: str) -> List[Any]:
        try:
            from langchain_core.documents import Document
        except ImportError:
            Document = Any

        docs = self.vectorstore.similarity_search_with_relevance_scores(
            query, k=self.top_k, score_threshold=self.score_threshold
        )
        if not docs:
            return []

        chroma_docs = []
        for i, (doc, score) in enumerate(docs):
            doc.metadata["_vector_score"] = round(float(score), 4)
            doc.metadata["_vector_rank"] = i
            chroma_docs.append(doc)

        if self.bm25 is not None and self.bm25.num_docs > 0:
            texts = [doc.page_content for doc in chroma_docs]
            self.bm25.fit(texts)
            bm25_results = self.bm25.search(query, top_k=self.top_k)
            vector_indices = list(range(len(chroma_docs)))

            vector_ranked = [(i, chroma_docs[i].metadata.get("_vector_score", 0)) for i in vector_indices]
            bm25_ranked = [(idx, 1.0) for idx, score in bm25_results if score > 0]

            fused_indices = reciprocal_rank_fusion(
                vector_ranked, bm25_ranked, top_k=min(self.top_k, len(chroma_docs))
            )
            return [chroma_docs[i] for i in fused_indices]

        return chroma_docs

    def get_relevant_documents(self, query: str) -> List[Any]:
        return self.invoke(query)
