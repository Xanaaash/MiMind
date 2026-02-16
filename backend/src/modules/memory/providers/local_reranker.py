import re
from typing import List, Tuple


class LocalOverlapRerankerProvider:
    def rerank(self, query: str, candidates: List[str], limit: int) -> List[Tuple[str, float]]:
        normalized_query = str(query).lower().strip()
        query_tokens = set(re.findall(r"[a-z0-9]+", normalized_query))
        if limit <= 0:
            return []
        if not candidates:
            return []

        scored: List[Tuple[str, float]] = []
        for candidate in candidates:
            text = str(candidate)
            tokens = set(re.findall(r"[a-z0-9]+", text.lower()))
            if not tokens and not query_tokens:
                score = 0.0
            else:
                overlap = len(query_tokens.intersection(tokens))
                union = len(query_tokens.union(tokens)) or 1
                jaccard = overlap / union
                bonus = 0.15 if normalized_query and normalized_query in text.lower() else 0.0
                score = jaccard + bonus
            scored.append((text, score))

        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:limit]
