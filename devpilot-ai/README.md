# DevPilot AI — Intelligent Software Repository Assistant

A portfolio project demonstrating AST-based code ingestion, embeddings, Qdrant vector search, RAG, LLM integration, FastAPI, Pydantic, tests, and Docker.

## Prerequisites

- Python 3.11 or 3.12 recommended
- Ollama installed and running for `/ask` and `/debug`
- Enough memory for the embedding model and selected local LLM

## Setup on macOS

```bash
cd devpilot-ai
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

In another terminal, start Ollama and download a model:

```bash
ollama pull qwen2.5-coder:7b
ollama serve
```

If Ollama is already running as a background app, `ollama serve` may report that the port is already in use; that's okay. Set another model with `export OLLAMA_MODEL=your-installed-model`.

## Run the API

From the project root:

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for interactive API documentation.

## Index a repository

Use the `/index` endpoint with JSON:

```json
{"repo_path": "/absolute/path/to/a/python/repository"}
```

Only Python files are indexed in this first version. The index is rebuilt on each indexing run. Do not index private, confidential, or proprietary repositories unless you have permission and understand the data-handling implications.

## Try it

`POST /search`
```json
{"query": "Where is database connection pooling configured?", "limit": 5}
```

`POST /ask`
```json
{"question": "Explain how configuration is loaded and cite the relevant code.", "limit": 5}
```

`POST /debug`
```json
{"stack_trace": "Traceback ... ModuleNotFoundError: No module named 'example'", "limit": 5}
```

## Tests

```bash
pytest -q
```

## Docker

This Dockerfile runs the API, but local Ollama and persistent Qdrant storage require additional configuration when containerizing. For a first demo, run Ollama on the host and the API locally. If using Docker, configure `OLLAMA_URL`, mount a persistent volume for Qdrant, and set the host address appropriately.

## Current limitations

- Python-only ingestion; no cross-language parsing yet.
- Retrieval is based on embedding similarity; no reranker or hybrid search yet.
- LLM responses can be wrong; verify suggestions before applying them.
- The app does not execute code or automatically modify a repository.
- The initial prototype is not hardened for untrusted multi-user production use.
