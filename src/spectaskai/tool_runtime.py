from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .nemotron_client import NemotronClient
from .rag_indexer import index_markdown_file, read_jsonl, write_jsonl
from .rag_search import search_chunks


DEFAULT_INDEX = Path("data/indexes/spec_index.jsonl")
DEFAULT_SPEC_DIR = Path("data/home-specs")


def ok(tool: str, data: dict[str, Any]) -> dict[str, Any]:
    return {"ok": True, "tool": tool, **data}


def fail(tool: str, message: str) -> dict[str, Any]:
    return {"ok": False, "tool": tool, "error": message}


def spec_list(params: dict[str, Any]) -> dict[str, Any]:
    spec_dir = Path(str(params.get("spec_dir") or DEFAULT_SPEC_DIR))
    if not spec_dir.exists():
        return ok("spec_list", {"specs": []})

    specs = []
    for path in sorted(spec_dir.glob("*.md")):
        specs.append({"path": str(path), "spec_id": path.stem, "format": "markdown"})
    return ok("spec_list", {"specs": specs})


def spec_ingest(params: dict[str, Any]) -> dict[str, Any]:
    markdown_file = params.get("markdown_file")
    if not markdown_file:
        return fail("spec_ingest", "Missing required parameter: markdown_file")

    output = Path(str(params.get("output") or DEFAULT_INDEX))
    chunks = index_markdown_file(
        Path(str(markdown_file)),
        spec_id=str(params["spec_id"]) if params.get("spec_id") else None,
        title=str(params["title"]) if params.get("title") else None,
    )
    write_jsonl(chunks, output)
    return ok(
        "spec_ingest",
        {
            "index": str(output),
            "chunk_count": len(chunks),
            "chunk_ids": [chunk.chunk_id for chunk in chunks],
        },
    )


def spec_search(params: dict[str, Any]) -> dict[str, Any]:
    query = str(params.get("query") or "").strip()
    if not query:
        return fail("spec_search", "Missing required parameter: query")

    index = Path(str(params.get("index") or DEFAULT_INDEX))
    limit = int(params.get("limit") or 5)
    chunks = read_jsonl(index)
    results = search_chunks(query, chunks, limit=limit)
    return ok("spec_search", {"query": query, "results": [result.to_json() for result in results]})


def spec_answer(params: dict[str, Any]) -> dict[str, Any]:
    question = str(params.get("question") or "").strip()
    if not question:
        return fail("spec_answer", "Missing required parameter: question")

    index = Path(str(params.get("index") or DEFAULT_INDEX))
    limit = int(params.get("limit") or 5)
    chunks = read_jsonl(index)
    results = search_chunks(question, chunks, limit=limit)
    answer = NemotronClient().answer_with_sources(question, results)
    return ok(
        "spec_answer",
        {
            "question": question,
            "answer": answer,
            "sources": [result.to_json() for result in results],
        },
    )


TOOLS = {
    "spec_list": spec_list,
    "spec_ingest": spec_ingest,
    "spec_search": spec_search,
    "spec_answer": spec_answer,
}


def execute_tool(name: str, params: dict[str, Any]) -> dict[str, Any]:
    tool = TOOLS.get(name)
    if tool is None:
        return fail(name, f"Unknown tool: {name}")
    try:
        return tool(params)
    except Exception as error:  # pragma: no cover - defensive runtime boundary
        return fail(name, str(error))


def main() -> int:
    parser = argparse.ArgumentParser(description="JSON runtime wrapper for SpecTaskAI tools")
    parser.add_argument("tool", choices=sorted(TOOLS))
    parser.add_argument("--params", help="JSON object with tool parameters. Defaults to stdin.")
    args = parser.parse_args()

    raw = args.params if args.params is not None else sys.stdin.read()
    params = json.loads(raw) if raw.strip() else {}
    if not isinstance(params, dict):
        print(json.dumps(fail(args.tool, "Tool params must be a JSON object"), ensure_ascii=False))
        return 2

    print(json.dumps(execute_tool(args.tool, params), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
