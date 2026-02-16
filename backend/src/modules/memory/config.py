import os
from dataclasses import dataclass


@dataclass
class MemoryRetrievalConfig:
    embedder_provider: str = "local"
    reranker_provider: str = "local"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_embedding_model: str = "text-embedding-3-small"


def load_memory_retrieval_config() -> MemoryRetrievalConfig:
    return MemoryRetrievalConfig(
        embedder_provider=os.getenv("MINDCOACH_MEMORY_EMBEDDER", "local").strip().lower(),
        reranker_provider=os.getenv("MINDCOACH_MEMORY_RERANKER", "local").strip().lower(),
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip(),
        openai_embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small").strip(),
    )
