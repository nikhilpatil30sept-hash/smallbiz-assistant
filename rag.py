"""Retrieval-augmented answering: find relevant chunks, then ask the local model."""
import re
from typing import Iterator

import config
from chunking import load_file
from embeddings import embed
from ingest import get_collection
from lexical import LexicalIndex
from prompts import OUT_OF_SCOPE_REPLY, SCOPE_CHECK_PROMPT, SYSTEM_PROMPT, build_user_prompt


# Short acronyms carry almost no meaning for the embedding model, so "What do I need the BIN
# for?" matched nothing and was refused as off topic. We add the full name to the search
# query (the user's own wording is still searched too, and the model still sees it as typed).
ACRONYMS = {
    "BIN": "Ontario Business Identification Number",
    "BN": "CRA business number",
    "HST": "harmonized sales tax",
    "GST": "goods and services tax",
    "PST": "provincial sales tax",
    "CRA": "Canada Revenue Agency",
    "OBR": "Ontario Business Registry",
    "WSIB": "Workplace Safety and Insurance Board",
    "EHT": "Employer Health Tax",
    "ESA": "Employment Standards Act",
    "OHSA": "Occupational Health and Safety Act",
    "CPP": "Canada Pension Plan",
    "EI": "Employment Insurance",
    "ROE": "record of employment",
    "LLP": "limited liability partnership",
    "NAICS": "North American Industry Classification System",
}
_ACRONYM_RE = re.compile(r"\b(" + "|".join(ACRONYMS) + r")\b")


def expand_acronyms(text: str) -> str:
    """'the BIN' -> 'the BIN (Ontario Business Identification Number)'. Uppercase matches only."""
    def add(m: re.Match) -> str:
        full = ACRONYMS[m.group(1)]
        return m.group(0) if full.lower() in text.lower() else f"{m.group(0)} ({full})"

    return _ACRONYM_RE.sub(add, text)


def _last_user_message(history: list[dict] | None) -> str:
    for m in reversed(history or []):
        if m.get("role") == "user" and m.get("content"):
            return m["content"]
    return ""


_LEX_CACHE: dict = {}


def _lexical_index(col) -> tuple[LexicalIndex, list[dict]]:
    """Keyword index over every chunk, built once per knowledge base (rebuilt after re-ingest)."""
    key = (str(config.DB_DIR), col.count())
    if key not in _LEX_CACHE:
        _LEX_CACHE.clear()
        got = col.get(include=["documents", "metadatas"])
        rows = [{"id": i, "text": d, "meta": m} for i, d, m in zip(got["ids"], got["documents"], got["metadatas"])]
        _LEX_CACHE[key] = (LexicalIndex([r["text"] for r in rows]), rows)
    return _LEX_CACHE[key]


def _hit(cid: str, doc: str, meta: dict, similarity: float) -> dict:
    return {
        "id": cid,
        "text": doc,
        "title": meta.get("title", ""),
        "section": meta.get("section", ""),
        "url": meta.get("source_url", ""),
        "file": meta.get("file", ""),
        "license": meta.get("license", ""),
        "similarity": round(similarity, 3),
    }


def retrieve(question: str, k: int | None = None, history: list[dict] | None = None) -> list[dict]:
    """Return the top chunks (best first) that clear the similarity threshold.

    Short follow-ups like "Yes, I made $35,000. What next?" carry no topic on their own,
    so when there is a previous user message we search with BOTH the question alone and
    'previous question + this question', and keep each chunk's best score. Searching the
    question alone as well means a change of topic still works."""
    col = get_collection()
    if col.count() == 0:
        return []
    k = k or config.TOP_K
    expanded = expand_acronyms(question)
    queries = [question] + ([expanded] if expanded != question else [])
    prev = _last_user_message(history)
    if prev:
        queries.append(expand_acronyms(prev[:300]) + "\n" + expanded)

    res = col.query(query_embeddings=embed(queries), n_results=k)
    best: dict[str, dict] = {}
    for qi in range(len(queries)):
        for cid, doc, meta, dist in zip(
            res["ids"][qi], res["documents"][qi], res["metadatas"][qi], res["distances"][qi]
        ):
            similarity = 1.0 - dist  # cosine distance -> similarity
            if similarity < config.MIN_SIMILARITY:
                continue
            if cid not in best or similarity > best[cid]["similarity"]:
                best[cid] = _hit(cid, doc, meta, similarity)
    hits = sorted(best.values(), key=lambda h: h["similarity"], reverse=True)[:k]

    if config.KEYWORD_SEARCH:
        # Chunks holding the question's rare words (program names etc.) that the embedding
        # search missed. They are added on top of the top-k, at a modest score.
        index, rows = _lexical_index(col)
        seen = {h["id"] for h in hits}
        for i, _coverage in index.search(expanded, max_hits=config.LEX_MAX_HITS):
            r = rows[i]
            if r["id"] not in seen:
                seen.add(r["id"])
                hits.append(_hit(r["id"], r["text"], r["meta"], config.LEX_SIMILARITY))
        hits.sort(key=lambda h: h["similarity"], reverse=True)
    return hits


def _full_page_text(file: str) -> str | None:
    """The whole saved page (without its front matter) for a chunk's source file."""
    if not file:
        return None
    for d in (config.WEB_DIR, config.DOCS_DIR):
        path = d / file
        if path.exists():
            try:
                body = load_file(path)[1].strip()
            except Exception:
                return None
            # "# 3. Decide on..." -> "# Decide on...": step numbers made the model say "step 4"
            return re.sub(r"(?m)^(#{1,6})\s+\d+\.\s*", r"\1 ", body)
    return None


def group_by_page(hits: list[dict], max_chars: int | None = None) -> list[dict]:
    """Merge chunks from the same page into one numbered source (best page first).

    The model cites [1], [2]... and the UI lists the same numbers, so each number must
    mean exactly one page. A short page is given whole (so the model sees every list item
    and neighbouring sentence); otherwise the retrieved chunks are used, capped per source.
    A total budget keeps five long pages from swamping the small model's context window."""
    max_chars = max_chars or config.MAX_SOURCE_CHARS
    pages: dict[str, dict] = {}
    for h in hits:
        key = h["url"] or h["title"]
        if key not in pages:
            pages[key] = dict(h)
        elif len(pages[key]["text"]) < max_chars:
            pages[key]["text"] += "\n\n" + h["text"]
    used = 0
    for page in pages.values():
        whole = _full_page_text(page.get("file", ""))
        if whole and len(whole) <= config.FULL_PAGE_MAX_CHARS and used + len(whole) <= config.MAX_TOTAL_SOURCE_CHARS:
            page["text"] = whole
        else:
            page["text"] = page["text"][:max_chars]
        used += len(page["text"])
    return list(pages.values())


def _messages(question: str, sources: list[dict], history: list[dict] | None):
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    # Keep only the last two exchanges, and trim long earlier answers, so the sources
    # (the part that matters) always fit in the model's context window.
    for m in (history or [])[-4:]:
        msgs.append({"role": m["role"], "content": m["content"][:700]})
    msgs.append({"role": "user", "content": build_user_prompt(question, sources)})
    return msgs


def is_in_scope(client, question: str, history: list[dict] | None = None) -> bool:
    """Cheap yes/no check used only when retrieval found nothing relevant.
    Small models often ignore 'decline off-topic questions' instructions inside a long
    prompt, but they classify reliably when asked a single narrow question. Any doubt or
    error counts as in scope, so a real business question is never wrongly refused."""
    prev = ""
    for m in reversed(history or []):
        if m.get("role") == "user":
            prev = m["content"][:300]
            break
    question = expand_acronyms(question)  # "the BIN" is a business term the classifier may not know
    content = (f"Previous message: {prev}\n" if prev else "") + f"Current message: {question}"
    try:
        resp = client.chat(
            model=config.CHAT_MODEL,
            messages=[
                {"role": "system", "content": SCOPE_CHECK_PROMPT},
                {"role": "user", "content": content},
            ],
            options={"temperature": 0, "num_predict": 4, "num_ctx": config.NUM_CTX},
        )
        return not resp["message"]["content"].strip().upper().startswith("NO")
    except Exception:
        return True


def answer_stream(question: str, history: list[dict] | None = None) -> tuple[list[dict], Iterator[str]]:
    """Return (sources, token_iterator). Sources are known before generation starts."""
    import ollama

    sources = group_by_page(retrieve(question, history=history))
    client = ollama.Client(host=config.OLLAMA_HOST, timeout=config.REQUEST_TIMEOUT)

    weak_match = not sources or max(s["similarity"] for s in sources) < config.SCOPE_CHECK_BELOW
    if weak_match and not is_in_scope(client, question, history):
        return [], iter([OUT_OF_SCOPE_REPLY])

    stream = client.chat(
        model=config.CHAT_MODEL,
        messages=_messages(question, sources, history),
        stream=True,
        options={
            "temperature": config.TEMPERATURE,
            "num_ctx": config.NUM_CTX,
            "num_predict": config.MAX_ANSWER_TOKENS,
        },
    )

    def tokens() -> Iterator[str]:
        for chunk in stream:
            yield chunk["message"]["content"]

    return sources, tokens()


def strip_invalid_citations(text: str, n_sources: int) -> str:
    """Remove [n] markers that point at a source that was not shown (the model sometimes
    cites [4] when only three sources exist). Better no marker than one that links to the
    wrong page."""
    def keep(m: re.Match) -> str:
        return m.group(0) if 1 <= int(m.group(1)) <= n_sources else ""

    return re.sub(r"[ \t]?\[(\d+)\]", keep, text)


def format_sources(sources: list[dict]) -> str:
    """Markdown list of the sources behind an answer, numbered to match the citations.
    Expects one entry per page (see group_by_page)."""
    lines = []
    for i, s in enumerate(sources, 1):
        name = s["title"]
        link = f"[{name}]({s['url']})" if s["url"] else name
        lines.append(f"[{i}] {link}  \n<sub>relevance {s['similarity']}</sub>")
    return "\n\n".join(lines)
