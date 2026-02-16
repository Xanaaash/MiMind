from typing import List

import httpx

from modules.memory.config import MemoryRetrievalConfig


class OpenAIEmbeddingProvider:
    def __init__(self, config: MemoryRetrievalConfig) -> None:
        self._config = config

    def embed(self, text: str) -> List[float]:
        if not self._config.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when memory embedder provider is openai")

        endpoint = f"{self._config.openai_base_url.rstrip('/')}/embeddings"
        response = httpx.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {self._config.openai_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self._config.openai_embedding_model,
                "input": text,
            },
            timeout=5.0,
        )
        response.raise_for_status()
        payload = response.json()
        data = payload.get("data", [])
        if not data:
            raise RuntimeError("OpenAI embedding provider returned empty data")
        embedding = data[0].get("embedding")
        if not isinstance(embedding, list):
            raise RuntimeError("OpenAI embedding provider returned invalid embedding")
        return [float(value) for value in embedding]
