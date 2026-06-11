from __future__ import annotations

import math
import re
from collections import Counter

from .models import SearchResult, SpecChunk


TOKEN_RE = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_-]*")
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "for",
    "in",
    "is",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text) if token.lower() not in STOP_WORDS]


def search_chunks(query: str, chunks: list[SpecChunk], limit: int = 5) -> list[SearchResult]:
    query_terms = tokenize(query)
    if not query_terms:
        return []

    query_counts = Counter(query_terms)
    results: list[SearchResult] = []

    for chunk in chunks:
        haystack = " ".join([chunk.title, chunk.section, chunk.text])
        chunk_terms = tokenize(haystack)
        chunk_counts = Counter(chunk_terms)
        matched_terms = sorted(set(query_counts).intersection(chunk_counts))
        if not matched_terms:
            continue

        term_score = sum(query_counts[term] * chunk_counts[term] for term in matched_terms)
        section_bonus = 1.5 if any(term in tokenize(chunk.section) for term in query_counts) else 1.0
        length_penalty = math.log(len(chunk_terms) + 10)
        score = section_bonus * term_score / length_penalty
        results.append(SearchResult(chunk=chunk, score=round(score, 4), matched_terms=matched_terms))

    return sorted(results, key=lambda result: result.score, reverse=True)[:limit]


def format_results(results: list[SearchResult]) -> str:
    lines: list[str] = []
    for index, result in enumerate(results, start=1):
        chunk = result.chunk
        source = f"{chunk.spec_id}, section {chunk.section}"
        if chunk.page is not None:
            source = f"{source}, page {chunk.page}"
        lines.append(
            f"[{index}] score={result.score} source={source}\n"
            f"matched={', '.join(result.matched_terms)}\n"
            f"{chunk.text}"
        )
    return "\n\n".join(lines)
