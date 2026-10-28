from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPO_PATH = Path(os.getenv("DEVPILOT_REPO", ".")).resolve()
DATA_PATH = PROJECT_ROOT / "data"
QDRANT_PATH = DATA_PATH / "qdrant"
COLLECTION_NAME = "devpilot_code"
EMBEDDING_MODEL = os.getenv("DEVPILOT_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
