import logging
from typing import List, Dict, Any

from config import config

logger = logging.getLogger(__name__)

EXPANSION_TEMPLATE = (
    "Generate {num} concise alternative phrasings of this query (one per line, "
    "no numbering, no explanation):\n\n{query}"
)


def expand_query(query: str, num: int = 3, llm=None) -> List[str]:
    """Expand a single query into multiple related queries for improved retrieval."""
    if not query.strip():
        return [query]

    if llm is None:
        logger.debug("No LLM provided for query expansion, returning original.")
        return [query]

    try:
        prompt = EXPANSION_TEMPLATE.format(num=num, query=query)
        response = llm.invoke(prompt)
        expansions = [
            line.strip().lstrip("0123456789.-) ")
            for line in response.strip().split("\n")
            if line.strip()
        ]
        combined = [query] + expansions[:num]
        logger.info("Query expansion: %d variants generated", len(combined))
        return combined
    except Exception as e:
        logger.warning("Query expansion failed: %s — falling back to original", e)
        return [query]


def deduplicate_results(
    all_docs: List[Any],
    score_key: str = "_vector_score",
) -> List[Any]:
    """Deduplicate documents by page_content, keeping highest-scored copy."""
    seen: Dict[str, Any] = {}
    for doc in all_docs:
        content = doc.page_content[:200]
        if content not in seen:
            seen[content] = doc
        else:
            existing = seen[content].metadata.get(score_key, 0) or 0
            current = doc.metadata.get(score_key, 0) or 0
            if current > existing:
                seen[content] = doc
    return list(seen.values())
