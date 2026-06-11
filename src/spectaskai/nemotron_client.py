from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from .models import SearchResult


class NemotronClient:
    """Small model client boundary.

    The default mode is offline so the repo can run without credentials. Set
    `NVIDIA_API_KEY` and `NVIDIA_NIM_BASE_URL` later to call a real endpoint.
    """

    def __init__(self, api_key: str | None = None, base_url: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.environ.get("NVIDIA_API_KEY")
        self.base_url = (base_url or os.environ.get("NVIDIA_NIM_BASE_URL") or "").rstrip("/")
        self.model = model or os.environ.get("NVIDIA_MODEL", "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning")

    def answer_with_sources(self, question: str, results: list[SearchResult]) -> str:
        if not results:
            return "I could not find relevant source chunks for this question."

        if not self.api_key or not self.base_url:
            return self._offline_answer(question, results)

        prompt = build_grounded_prompt(question, results)
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "Answer only from the provided sources. Cite section or page."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as error:
            raise RuntimeError(f"Nemotron request failed: {error}") from error

        return data["choices"][0]["message"]["content"]

    def _offline_answer(self, question: str, results: list[SearchResult]) -> str:
        top = results[0].chunk
        sources = []
        for result in results:
            chunk = result.chunk
            location = f"{chunk.spec_id}, section {chunk.section}"
            if chunk.page is not None:
                location = f"{location}, page {chunk.page}"
            sources.append(f"- {location}")

        return (
            "Offline grounded answer draft\n\n"
            f"Question: {question}\n\n"
            f"Most relevant finding: {top.text}\n\n"
            "Sources:\n"
            + "\n".join(sources)
        )


def build_grounded_prompt(question: str, results: list[SearchResult]) -> str:
    source_blocks = []
    for index, result in enumerate(results, start=1):
        chunk = result.chunk
        source_blocks.append(
            f"Source {index}\n"
            f"spec_id: {chunk.spec_id}\n"
            f"title: {chunk.title}\n"
            f"section: {chunk.section}\n"
            f"page: {chunk.page}\n"
            f"text:\n{chunk.text}"
        )

    return (
        f"Question:\n{question}\n\n"
        "Sources:\n"
        + "\n\n".join(source_blocks)
        + "\n\nAnswer with a concise summary and a Sources list."
    )
