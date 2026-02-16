import math
import re
from typing import List


class LocalHashEmbeddingProvider:
    def __init__(self, dimension: int = 64) -> None:
        self._dimension = max(8, int(dimension))

    def embed(self, text: str) -> List[float]:
        normalized = str(text).lower().strip()
        if not normalized:
            return [0.0] * self._dimension

        tokens = re.findall(r"[a-z0-9]+", normalized)
        if not tokens:
            return [0.0] * self._dimension

        vector = [0.0] * self._dimension
        for token in tokens:
            index = hash(token) % self._dimension
            vector[index] += 1.0

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]
