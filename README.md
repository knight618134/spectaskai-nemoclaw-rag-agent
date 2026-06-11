# SpecTaskAI NemoClaw RAG Agent

A portfolio backend project for experimenting with NemoClaw, OpenClaw-style agent tools, Nemotron-3 model integration, lightweight RAG, and project-management automation.

The goal is not to build another chatbot. The goal is to show how an AI agent can:

```text
technical specs / runbooks
  -> ingestion and chunking
  -> retrieval with citations
  -> grounded answer generation
  -> controlled tool calls
  -> OpenProject task/comment automation
```

## Why This Project Exists

Most portfolio AI demos stop at a frontend prompt box. This repo focuses on the backend pieces that make an AI application credible:

- document ingestion and chunk metadata
- retrieval before generation
- source-grounded answers
- model boundary through `NemotronClient`
- task-system boundary through `OpenProjectClient`
- future OpenClaw/NemoClaw runtime tool wrappers

## Current Status

Implemented:

- Markdown spec ingestion
- JSONL chunk schema
- keyword retrieval
- offline grounded answer mode
- OpenProject API v3 client boundary
- CLI demo
- basic unit tests

Planned:

- PDF ingestion
- OpenClaw runtime tools: `spec_list`, `spec_ingest`, `spec_search`, `spec_answer`
- NemoClaw sandbox demo
- OpenProject task/comment creation flow
- optional vector search and reranking

## Repository Structure

```text
src/spectaskai/
  models.py              shared chunk/search dataclasses
  rag_indexer.py         Markdown -> JSONL chunks
  rag_search.py          keyword retrieval
  nemotron_client.py     offline answer now, NIM-compatible boundary later
  openproject_client.py  OpenProject API v3 boundary
  cli.py                 local demo commands

data/home-specs/
  router-demo.md         safe toy spec for local RAG tests

docs/
  backend-rag-agent-plan.md
  nemoclaw-home-playground.md
  nemoclaw-nemotron3-skill-tool-rag-roadmap.md

tests/
  test_rag_pipeline.py
```

## Local Demo

Index the toy spec:

```bash
PYTHONPATH=src python3 -m spectaskai.cli ingest data/home-specs/router-demo.md
```

Search the local index:

```bash
PYTHONPATH=src python3 -m spectaskai.cli search "GNSS timing priority"
```

Generate an offline grounded answer:

```bash
PYTHONPATH=src python3 -m spectaskai.cli answer "What should happen when PTP degrades and GNSS is locked?"
```

Run tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Why `nemotron_client.py` and `openproject_client.py`

`nemotron_client.py` isolates model access:

```text
RAG / Agent logic
  -> NemotronClient
  -> NVIDIA NIM / Nemotron-3 or offline mock
```

`openproject_client.py` isolates task-system access:

```text
Agent tool
  -> OpenProjectClient
  -> OpenProject API v3
```

This keeps the core RAG and agent workflow independent from external service details. The project can later swap model providers or task systems without rewriting the whole pipeline.

## Portfolio Positioning

```text
Built a lightweight RAG and agent-tool backend for technical operations workflows. The backend indexes technical runbooks, retrieves citation-bearing evidence, drafts grounded answers through a model client boundary, and prepares integration points for OpenProject task creation through controlled NemoClaw/OpenClaw tools.
```

## Safety Notes

- Do not commit API tokens.
- Use toy specs or public documents for local demos.
- Keep generated indexes out of Git unless they are intentionally published fixtures.
- Treat write-capable agent tools as approval-gated operations.
