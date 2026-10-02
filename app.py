"""Chat interface.   python app.py   ->   open http://127.0.0.1:7860"""
import gradio as gr

from rag import answer_stream, format_sources, strip_invalid_citations

ATTRIBUTION = (
    "Prototype for general information only, not legal, tax or accounting advice. "
    "Sources include the Government of Ontario and Government of Canada websites "
    "(Ontario content: Contains information licensed under the Open Government "
    "Licence - Ontario). Always confirm details with the official source."
)


def _as_text(content) -> str:
    """Gradio may hand back plain strings or a list of content blocks; keep just the text."""
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        return str(content.get("text", ""))
    if isinstance(content, (list, tuple)):
        return "".join(_as_text(c) for c in content)
    return str(content)


def respond(message, history):
    # History is a list of {"role": ..., "content": ...} messages.
    clean = [
        # Drop the "Sources" footer we appended, so the model only sees its own answer.
        {"role": m["role"], "content": _as_text(m["content"]).split("\n\n---\n")[0]}
        for m in history
        if m.get("role") in ("user", "assistant")
    ]
    message = _as_text(message)
    try:
        sources, tokens = answer_stream(message, clean)
    except Exception as e:
        yield (
            f"Could not reach the local model ({e}).\n\n"
            "Is Ollama running, and have you pulled the models? See the README."
        )
        return
    text = ""
    for t in tokens:
        text += t
        yield strip_invalid_citations(text, len(sources))
    text = strip_invalid_citations(text, len(sources))
    cited = format_sources(sources)
    yield text + ("\n\n---\n**Sources**\n\n" + cited if cited else "\n\n---\n*No official source matched this question.*")


demo = gr.ChatInterface(
    respond,
    title="Small Business Assistant (Ontario) - Phase 1 prototype",
    description=ATTRIBUTION,
    examples=[
        "I want to start a small bakery in Ontario. What are the first steps?",
        "Do I need to register a business name if I operate as a sole proprietor?",
        "When do I have to start charging HST?",
        "What insurance should a new small business consider?",
    ],
)

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
