from typing import List, Protocol, Tuple


class EmbeddingProvider(Protocol):
    def embed(self, text: str) -> List[float]:
        ...


class RerankerProvider(Protocol):
    def rerank(self, query: str, candidates: List[str], limit: int) -> List[Tuple[str, float]]:
        ...
