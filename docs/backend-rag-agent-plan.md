# Backend RAG and Agent Implementation Plan

更新日期：2026-06-12

這份文件把履歷專案從純前端延伸成一個可展示的 AI application backend。第一版重點是讓 RAG pipeline 可以本地跑，不依賴公司 token 或正式服務。

## Why `nemotron_client.py` and `openproject_client.py`

`nemotron_client.py` 負責隔離模型呼叫：

```text
RAG / Agent logic
  -> NemotronClient
  -> NVIDIA NIM / Nemotron-3 or offline mock
```

這樣 `rag_search.py` 不需要知道 API key、endpoint、chat completion payload。之後如果從 Nemotron-3 換成其他模型，只改 client。

`openproject_client.py` 負責隔離任務系統 API：

```text
Agent tool
  -> OpenProjectClient
  -> OpenProject API v3
```

這樣「建立任務」「加 comment」不會散落在 agent 或 RAG 程式裡。之後如果要改成 GitHub Issues、Jira、Mantis，也可以保留上層流程。

## Current Scaffold

```text
src/spectaskai/
  models.py              shared chunk/search dataclasses
  rag_indexer.py         Markdown -> JSONL chunks
  rag_search.py          keyword retrieval
  nemotron_client.py     offline answer now, NIM-compatible boundary later
  openproject_client.py  OpenProject API v3 boundary
  cli.py                 local demo commands

data/home-specs/
  router-demo.md         safe toy spec
```

## Local Demo

Index the toy spec:

```bash
PYTHONPATH=src python3 -m spectaskai.cli ingest data/home-specs/router-demo.md
```

Search the index:

```bash
PYTHONPATH=src python3 -m spectaskai.cli search "GNSS timing priority"
```

Generate an offline grounded answer:

```bash
PYTHONPATH=src python3 -m spectaskai.cli answer "What should happen when PTP degrades and GNSS is locked?"
```

## Portfolio Story

```text
Built a lightweight RAG and agent-tool backend for an O-RAN operations console. The backend indexes technical runbooks, retrieves citation-bearing evidence, drafts grounded answers through a model client boundary, and prepares integration points for OpenProject task creation through controlled agent tools.
```

## Next Steps

- Add unit tests for Markdown indexing and retrieval.
- Add PDF ingestion behind the same chunk schema.
- Add a `spec-rag-tool` OpenClaw runtime tool wrapper.
- Add an `openproject-tool` wrapper that uses `OpenProjectClient`.
- Connect the static frontend to a local mock API or FastAPI server.
