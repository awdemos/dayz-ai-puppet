"""Simple location-proximity vector store for lesson retrieval."""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class Document:
    doc_id: str
    position: tuple[float, float, float]
    features: dict[str, float] = field(default_factory=dict)
    text: str = ""


class SimpleVectorStore:
    def add(self, doc: Document) -> None:
        self._docs.append(doc)

    def query_by_position(
        self,
        position: tuple[float, float, float],
        k: int = 5,
        max_distance: float = 1000.0,
    ) -> list[tuple[Document, float]]:
        px, _, pz = position
        scored: list[tuple[Document, float]] = []
        for doc in self._docs:
            dx, _, dz = doc.position
            dist = math.sqrt((px - dx) ** 2 + (pz - dz) ** 2)
            if dist <= max_distance:
                scored.append((doc, dist))
        scored.sort(key=lambda x: x[1])
        return scored[:k]

    def query_by_features(
        self,
        features: dict[str, float],
        k: int = 5,
    ) -> list[tuple[Document, float]]:
        scored: list[tuple[Document, float]] = []
        for doc in self._docs:
            sim = _cosine_similarity(features, doc.features)
            scored.append((doc, sim))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]

    def __init__(self) -> None:
        self._docs: list[Document] = []

    def __len__(self) -> int:
        return len(self._docs)


def _cosine_similarity(a: dict[str, float], b: dict[str, float]) -> float:
    all_keys = set(a.keys()) | set(b.keys())
    if not all_keys:
        return 0.0
    dot = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in all_keys)
    mag_a = math.sqrt(sum(a.get(k, 0.0) ** 2 for k in all_keys))
    mag_b = math.sqrt(sum(b.get(k, 0.0) ** 2 for k in all_keys))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)
