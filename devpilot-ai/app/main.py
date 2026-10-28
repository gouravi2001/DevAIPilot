from fastapi import FastAPI, HTTPException
from .config import REPO_PATH
from .schemas import IndexRequest, SearchRequest, AskRequest, DebugRequest
from .ingest import ingest_repository
from .vector_store import CodeIndex
from .assistant import answer_question, debug_stack_trace

app = FastAPI(
    title="DevPilot AI",
    description="A repository-aware RAG and debugging assistant.",
    version="0.1.0",
)
index = CodeIndex()

@app.get("/health")
def health():
    return {"status": "ok", "default_repo": str(REPO_PATH)}

@app.post("/index")
def index_repository(request: IndexRequest):
    repo = request.repo_path or str(REPO_PATH)
    try:
        chunks = ingest_repository(repo)
        count = index.index_chunks(chunks)
        return {"repository": repo, "chunks_indexed": count}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {exc}") from exc

@app.post("/search")
def search_code(request: SearchRequest):
    try:
        results = index.search(request.query, request.limit)
        return {"query": request.query, "results": results}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@app.post("/ask")
def ask(request: AskRequest):
    try:
        return answer_question(index, request.question, request.limit)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@app.post("/debug")
def debug(request: DebugRequest):
    try:
        return debug_stack_trace(index, request.stack_trace, request.limit)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
