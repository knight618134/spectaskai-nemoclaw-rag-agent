from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class SpecChunk:
    spec_id: str
    title: str
    section: str
    chunk_id: str
    text: str
    page: int | None = None
    version: str = "unknown"

    def to_json(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "SpecChunk":
        return cls(
            spec_id=str(data["spec_id"]),
            title=str(data["title"]),
            section=str(data["section"]),
            chunk_id=str(data["chunk_id"]),
            text=str(data["text"]),
            page=data.get("page"),
            version=str(data.get("version", "unknown")),
        )


@dataclass(frozen=True)
class SearchResult:
    chunk: SpecChunk
    score: float
    matched_terms: list[str]

    def to_json(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "matched_terms": self.matched_terms,
            "chunk": self.chunk.to_json(),
        }
