import logging
from typing import List, Any

from config import config
from metrics import observe_reranker

logger = logging.getLogger(__name__)


class CrossEncoderReranker:
    """Cross-encoder reranker that scores query-document pairs for precision."""

    def __init__(self, model_name: str | None = None, device: str | None = None):
        self.model_name = model_name or getattr(config, "CROSS_ENCODER_MODEL", "cross-encoder/ms-marco-TinyBERT-L-2-v2")
        self.device = device or getattr(config, "EMBEDDING_DEVICE", "cpu")
        self._model = None

    @property
    def model(self):
        if self._model is None:
            try:
                from sentence_transformers.cross_encoder import CrossEncoder
                logger.info("Loading cross-encoder: %s on %s", self.model_name, self.device)
                self._model = CrossEncoder(self.model_name, device=self.device)
            except Exception as e:
                logger.error("Failed to load cross-encoder %s: %s", self.model_name, e)
                raise
        return self._model

    @observe_reranker
    def rerank(self, query: str, documents: List[Any], top_k: int | None = None) -> List[Any]:
        if not documents:
            return documents

        k = top_k or getattr(config, "TOP_K_RESULTS", 4)
        pairs = [(query, doc.page_content) for doc in documents]

        try:
            scores = self.model.predict(pairs)
        except Exception as e:
            logger.warning("Cross-encoder reranking failed: %s — returning original order", e)
            return documents[:k]

        for doc, score in zip(documents, scores):
            doc.metadata["_rerank_score"] = round(float(score), 4)

        indexed = list(zip(documents, scores))
        indexed.sort(key=lambda x: x[1], reverse=True)
        reranked = [doc for doc, _ in indexed]

        logger.debug("Reranked %d docs → top %d (score range: %.4f–%.4f)",
                     len(documents), k, min(scores), max(scores))
        return reranked[:k]
