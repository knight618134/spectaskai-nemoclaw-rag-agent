from __future__ import annotations

import argparse
import json
from pathlib import Path

from .nemotron_client import NemotronClient
from .rag_indexer import index_markdown_file, read_jsonl, write_jsonl
from .rag_search import format_results, search_chunks


def main() -> int:
    parser = argparse.ArgumentParser(description="SpecTaskAI lightweight RAG CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest = subparsers.add_parser("ingest", help="Index a Markdown spec into JSONL chunks")
    ingest.add_argument("markdown_file", type=Path)
    ingest.add_argument("--out", type=Path, default=Path("data/indexes/spec_index.jsonl"))
    ingest.add_argument("--spec-id")
    ingest.add_argument("--title")

    search = subparsers.add_parser("search", help="Search indexed spec chunks")
    search.add_argument("query")
    search.add_argument("--index", type=Path, default=Path("data/indexes/spec_index.jsonl"))
    search.add_argument("--limit", type=int, default=5)
    search.add_argument("--json", action="store_true")

    answer = subparsers.add_parser("answer", help="Answer a question from indexed chunks")
    answer.add_argument("question")
    answer.add_argument("--index", type=Path, default=Path("data/indexes/spec_index.jsonl"))
    answer.add_argument("--limit", type=int, default=5)
    answer.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.command == "ingest":
        chunks = index_markdown_file(args.markdown_file, spec_id=args.spec_id, title=args.title)
        write_jsonl(chunks, args.out)
        print(f"Wrote {len(chunks)} chunks to {args.out}")
        return 0

    if args.command == "search":
        chunks = read_jsonl(args.index)
        results = search_chunks(args.query, chunks, limit=args.limit)
        if args.json:
            print(json.dumps([result.to_json() for result in results], ensure_ascii=False, indent=2))
        else:
            print(format_results(results))
        return 0

    if args.command == "answer":
        chunks = read_jsonl(args.index)
        results = search_chunks(args.question, chunks, limit=args.limit)
        answer_text = NemotronClient().answer_with_sources(args.question, results)
        if args.json:
            print(
                json.dumps(
                    {
                        "question": args.question,
                        "answer": answer_text,
                        "sources": [result.to_json() for result in results],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print(answer_text)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
