from .llm import generate
from .vector_store import CodeIndex

def _format_context(results: list[dict]) -> str:
    if not results:
        return "No matching repository code was retrieved."
    blocks = []
    for i, item in enumerate(results, 1):
        blocks.append(
            f"[SOURCE {i}: {item['path']}:{item['start_line']}-{item['end_line']} "
            f"| symbol={item['symbol']} | score={item['score']:.3f}]\n{item['text']}"
        )
    return "\n\n".join(blocks)

def answer_question(index: CodeIndex, question: str, limit: int = 5) -> dict:
    results = index.search(question, limit=limit)
    if not results:
        return {
            "answer": "I could not find relevant code. Index the repository first or try a more specific question.",
            "sources": []
        }

    context = _format_context(results)
    prompt = f"""You are DevPilot AI, a software repository assistant.
Answer the developer's question using ONLY the supplied repository context.
Do not invent files, functions, line numbers, behavior, or dependencies.
If the context is insufficient, say what cannot be determined.
Distinguish observed facts from hypotheses. Do not claim that a suggested fix was tested.
Cite evidence using the source labels, such as [SOURCE 1].

REPOSITORY CONTEXT:
{context}

QUESTION:
{question}

Answer clearly and technically:"""
    answer = generate(prompt)
    return {
        "answer": answer,
        "sources": [
            {
                "path": x["path"],
                "symbol": x["symbol"],
                "start_line": x["start_line"],
                "end_line": x["end_line"],
                "score": round(x["score"], 4)
            } for x in results
        ]
    }

def debug_stack_trace(index: CodeIndex, stack_trace: str, limit: int = 5) -> dict:
    query = f"Find code related to this exception or stack trace:\n{stack_trace}"
    results = index.search(query, limit=limit)
    if not results:
        return {"analysis": "No matching code was found. Index the repository first.", "sources": []}

    context = _format_context(results)
    prompt = f"""You are a careful software debugging assistant.
Analyze the stack trace using only the supplied repository context.
Return: (1) what the trace directly indicates, (2) likely causes ranked by confidence,
(3) relevant code evidence, (4) concrete checks to confirm the diagnosis.
Do not claim certainty without evidence. Do not claim to execute or test fixes.
Cite source labels like [SOURCE 1].

STACK TRACE:
{stack_trace}

REPOSITORY CONTEXT:
{context}

Technical analysis:"""
    return {
        "analysis": generate(prompt),
        "sources": [
            {
                "path": x["path"],
                "symbol": x["symbol"],
                "start_line": x["start_line"],
                "end_line": x["end_line"],
                "score": round(x["score"], 4)
            } for x in results
        ]
    }
