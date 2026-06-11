# spec-rag-tool

This directory defines the first runtime-tool boundary for the project.

It is intentionally simple: each tool is exposed as a JSON command that can be called by an agent wrapper, a shell command, or a future OpenClaw plugin.

## Tools

| Tool | Purpose |
|---|---|
| `spec_list` | List local spec files |
| `spec_ingest` | Convert a Markdown spec into JSONL chunks |
| `spec_search` | Retrieve relevant chunks |
| `spec_answer` | Produce a grounded answer with sources |

## Local Calls

```bash
PYTHONPATH=src python3 -m spectaskai.tool_runtime spec_list
```

```bash
PYTHONPATH=src python3 -m spectaskai.tool_runtime spec_ingest \
  --params '{"markdown_file":"data/home-specs/router-demo.md"}'
```

```bash
PYTHONPATH=src python3 -m spectaskai.tool_runtime spec_search \
  --params '{"query":"GNSS timing priority","limit":3}'
```

```bash
PYTHONPATH=src python3 -m spectaskai.tool_runtime spec_answer \
  --params '{"question":"What should happen when PTP degrades and GNSS is locked?","limit":3}'
```

## Why This Shape

OpenClaw plugins and skills are different:

- A skill teaches the agent when to use a capability.
- A runtime tool performs the action.
- NemoClaw currently documents plugin installation as a sandbox image build step.

This JSON wrapper keeps the project useful before the final OpenClaw plugin packaging is chosen.
