import math
from typing import List, Optional

from modules.memory.config import MemoryRetrievalConfig, load_memory_retrieval_config
from modules.memory.models import MemoryVectorRecord
from modules.memory.providers.base import EmbeddingProvider, RerankerProvider
from modules.memory.providers.local_embedding import LocalHashEmbeddingProvider
from modules.memory.providers.local_reranker import LocalOverlapRerankerProvider
from modules.memory.providers.openai_embedding import OpenAIEmbeddingProvider
from modules.storage.in_memory import InMemoryStore


class MemoryService:
    def __init__(
        self,
        store: InMemoryStore,
        config: Optional[MemoryRetrievalConfig] = None,
        embedder: Optional[EmbeddingProvider] = None,
        reranker: Optional[RerankerProvider] = None,
    ) -> None:
        self._store = store
        self._config = config or load_memory_retrieval_config()
        self._embedder = embedder or self._build_embedder(self._config)
        self._reranker = reranker or self._build_reranker(self._config)

    def index_summary(self, user_id: str, summary: str) -> None:
        cleaned = str(summary).strip()
        if not cleaned:
            return
        self._store.save_memory_summary(user_id, cleaned)

        embedding = self._embedder.embed(cleaned)
        record = MemoryVectorRecord(
            user_id=user_id,
            text=cleaned,
            embedding=embedding,
        )
        self._store.save_memory_vector(record)

    def retrieve_recent(self, user_id: str, limit: int = 3) -> List[str]:
        items = self._store.list_memory_summaries(user_id)
        if limit <= 0:
            return []
        return items[-limit:]

    def retrieve_relevant(self, user_id: str, query: str, limit: int = 3) -> List[str]:
        if limit <= 0:
            return []

        query_text = str(query).strip()
        if not query_text:
            return self.retrieve_recent(user_id=user_id, limit=limit)

        vector_items = self._store.list_memory_vectors(user_id)
        if not vector_items:
            return self.retrieve_recent(user_id=user_id, limit=limit)

        query_embedding = self._embedder.embed(query_text)
        scored = sorted(
            (
                (
                    record.text,
                    self._cosine_similarity(query_embedding, record.embedding),
                )
                for record in vector_items
            ),
            key=lambda item: item[1],
            reverse=True,
        )

        candidate_limit = max(limit * 4, limit)
        candidates = [text for text, _ in scored[:candidate_limit]]
        reranked = self._reranker.rerank(query_text, candidates, limit=limit)
        if reranked:
            return [text for text, _ in reranked]

        return candidates[:limit]

    @staticmethod
    def _cosine_similarity(left: List[float], right: List[float]) -> float:
        if not left or not right:
            return 0.0
        size = min(len(left), len(right))
        left_values = left[:size]
        right_values = right[:size]

        dot = sum(left_values[idx] * right_values[idx] for idx in range(size))
        left_norm = math.sqrt(sum(value * value for value in left_values))
        right_norm = math.sqrt(sum(value * value for value in right_values))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return dot / (left_norm * right_norm)

    @staticmethod
    def _build_embedder(config: MemoryRetrievalConfig) -> EmbeddingProvider:
        if config.embedder_provider == "local":
            return LocalHashEmbeddingProvider()
        if config.embedder_provider == "openai":
            return OpenAIEmbeddingProvider(config)
        raise ValueError(f"Unknown memory embedder provider: {config.embedder_provider}")

    @staticmethod
    def _build_reranker(config: MemoryRetrievalConfig) -> RerankerProvider:
        if config.reranker_provider == "local":
            return LocalOverlapRerankerProvider()
        raise ValueError(f"Unknown memory reranker provider: {config.reranker_provider}")
