import requests
from .config import OLLAMA_URL, OLLAMA_MODEL

def generate(prompt: str) -> str:
    """Call Ollama's local generate API; no tool/function-calling support required."""
    url = f"{OLLAMA_URL.rstrip('/')}/api/generate"
    try:
        response = requests.post(
            url,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1}
            },
            timeout=180,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Could not reach Ollama at {url}. Start Ollama and pull "
            f"'{OLLAMA_MODEL}'. Details: {exc}"
        ) from exc
    data = response.json()
    return data.get("response", "").strip()
