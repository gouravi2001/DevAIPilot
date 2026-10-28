import ast
from pathlib import Path
from typing import Iterator

IGNORED_DIRS = {
    ".git", ".venv", "venv", "__pycache__", "node_modules",
    ".mypy_cache", ".pytest_cache", "dist", "build"
}
MAX_FILE_BYTES = 1_000_000

def python_files(repo_path: Path) -> Iterator[Path]:
    for path in repo_path.rglob("*.py"):
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        try:
            if path.is_file() and path.stat().st_size <= MAX_FILE_BYTES:
                yield path
        except OSError:
            continue

def _source_segment(lines: list[str], start: int, end: int) -> str:
    return "".join(lines[start - 1:end]).strip()

def parse_python_file(path: Path, repo_root: Path) -> list[dict]:
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, UnicodeDecodeError, SyntaxError):
        return []

    lines = source.splitlines(keepends=True)
    relative = str(path.relative_to(repo_root))
    chunks = []

    # Include top-level functions, async functions, and classes. Methods are
    # indexed separately so they can be retrieved independently.
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if not hasattr(node, "lineno") or not hasattr(node, "end_lineno"):
            continue
        start, end = node.lineno, node.end_lineno
        code = _source_segment(lines, start, end)
        if not code:
            continue

        kind = "class" if isinstance(node, ast.ClassDef) else "function"
        name = getattr(node, "name", "<unknown>")
        parent_names = []
        # Find enclosing class/function names by source range.
        for parent in ast.walk(tree):
            if parent is node or not isinstance(parent, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if (getattr(parent, "lineno", 0) <= start
                    and getattr(parent, "end_lineno", -1) >= end):
                parent_names.append((parent.end_lineno - parent.lineno, parent.name))
        parent = min(parent_names)[1] if parent_names else None
        qualified_name = f"{parent}.{name}" if parent else name

        chunks.append({
            "text": f"File: {relative}\nSymbol: {qualified_name} ({kind})\nLines: {start}-{end}\n\n{code}",
            "path": relative,
            "symbol": qualified_name,
            "kind": kind,
            "start_line": start,
            "end_line": end,
        })

    # If the file contains no definitions, retain a bounded file-level chunk.
    if not chunks and source.strip():
        chunks.append({
            "text": f"File: {relative}\nLines: 1-{len(lines)}\n\n{source[:12000]}",
            "path": relative,
            "symbol": path.name,
            "kind": "module",
            "start_line": 1,
            "end_line": len(lines),
        })
    return chunks

def ingest_repository(repo_path: str) -> list[dict]:
    root = Path(repo_path).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Repository path does not exist or is not a directory: {root}")

    all_chunks = []
    for file_path in python_files(root):
        all_chunks.extend(parse_python_file(file_path, root))
    return all_chunks
