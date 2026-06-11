# spec-rag-agent

Use this skill when the user asks about technical specifications, requirements, SOPs, runbooks, source-backed answers, or turning document evidence into an action plan.

## Intent Mapping

When the user asks what documents are available:

```text
spec_list
```

When the user asks to index, import, ingest, or refresh a Markdown/PDF spec:

```text
spec_ingest
```

When the user asks to find relevant sections, evidence, citations, requirements, or matching passages:

```text
spec_search
```

When the user asks a question that should be answered from a spec or runbook:

```text
spec_answer
```

## Response Rules

- Prefer source-grounded answers over general model knowledge.
- Include `spec_id`, section, and page when available.
- If retrieval returns no relevant chunks, say that no matching source was found.
- Do not invent citations.
- For write-capable downstream actions such as creating OpenProject tasks, ask for confirmation unless the user explicitly requested the action.

## Tool Parameters

`spec_ingest`:

```json
{
  "markdown_file": "data/home-specs/router-demo.md",
  "spec_id": "router-demo",
  "title": "Router Demo Spec",
  "output": "data/indexes/spec_index.jsonl"
}
```

`spec_search`:

```json
{
  "query": "GNSS timing priority",
  "index": "data/indexes/spec_index.jsonl",
  "limit": 5
}
```

`spec_answer`:

```json
{
  "question": "What should happen when PTP degrades and GNSS is locked?",
  "index": "data/indexes/spec_index.jsonl",
  "limit": 5
}
```
