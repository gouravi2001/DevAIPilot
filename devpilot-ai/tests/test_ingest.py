import ast
from pathlib import Path
from app.ingest import parse_python_file

def test_parser_extracts_function_and_class(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    file = repo / "sample.py"
    file.write_text(
        "class Greeter:\n"
        "    def hello(self, name):\n"
        "        return f'Hello {name}'\n\n"
        "def add(a, b):\n"
        "    return a + b\n",
        encoding="utf-8",
    )
    chunks = parse_python_file(file, repo)
    symbols = {chunk["symbol"] for chunk in chunks}
    assert "Greeter" in symbols
    assert "Greeter.hello" in symbols
    assert "add" in symbols
