from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

from .models import SpecChunk


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "untitled"


def split_markdown_sections(markdown: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, list[str]]] = []
    current_title = "Overview"
    current_lines: list[str] = []

    for line in markdown.splitlines():
        match = HEADING_RE.match(line)
        if match:
            if current_lines:
                sections.append((current_title, current_lines))
            current_title = match.group(2).strip()
            current_lines = []
            continue
        current_lines.append(line)

    if current_lines:
        sections.append((current_title, current_lines))

    return [(title, "\n".join(lines).strip()) for title, lines in sections if "\n".join(lines).strip()]


def chunk_text(text: str, max_chars: int = 900) -> list[str]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        if not current:
            current = paragraph
            continue
        if len(current) + len(paragraph) + 2 <= max_chars:
            current = f"{current}\n\n{paragraph}"
        else:
            chunks.append(current)
            current = paragraph

    if current:
        chunks.append(current)

    return chunks


def index_markdown_file(path: Path, spec_id: str | None = None, title: str | None = None) -> list[SpecChunk]:
    markdown = path.read_text(encoding="utf-8")
    inferred_title = title or infer_title(markdown) or path.stem
    inferred_spec_id = spec_id or slugify(path.stem)
    chunks: list[SpecChunk] = []

    for section_title, section_text in split_markdown_sections(markdown):
        for index, chunk in enumerate(chunk_text(section_text), start=1):
            section_slug = slugify(section_title)
            chunks.append(
                SpecChunk(
                    spec_id=inferred_spec_id,
                    title=inferred_title,
                    section=section_title,
                    chunk_id=f"{inferred_spec_id}:{section_slug}:{index:03d}",
                    text=chunk,
                )
            )

    return chunks


def infer_title(markdown: str) -> str | None:
    for line in markdown.splitlines():
        match = HEADING_RE.match(line)
        if match and len(match.group(1)) == 1:
            return match.group(2).strip()
    return None


def write_jsonl(chunks: Iterable[SpecChunk], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for chunk in chunks:
            file.write(json.dumps(chunk.to_json(), ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[SpecChunk]:
    chunks: list[SpecChunk] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                chunks.append(SpecChunk.from_json(json.loads(line)))
    return chunks
