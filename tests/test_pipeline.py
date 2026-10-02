"""Offline tests: no Ollama, no internet. Run with:  pytest -q"""
import os
import sys
from pathlib import Path

os.environ["EMBED_BACKEND"] = "hash"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

import config
from chunking import chunk_document, load_file, parse_front_matter
from fetch_sources import html_to_markdown, slug_for

SAMPLE_HTML = """
<html><head><title>Ignored</title></head><body>
<nav>Menu Menu Menu</nav>
<main>
  <h1>Register your business</h1>
  <p>You must register your business name with the Ontario Business Registry if you operate under a name other than your own.</p>
  <h2>Fees</h2>
  <ul><li>Sole proprietorship: $60</li><li>Corporation: $300</li></ul>
  <script>alert('x')</script>
</main>
<footer>Footer junk</footer>
</body></html>
"""


def test_html_to_markdown_keeps_main_content_only():
    title, md = html_to_markdown(SAMPLE_HTML)
    assert title == "Register your business"
    assert "Ontario Business Registry" in md
    assert "## Fees" in md and "- Sole proprietorship: $60" in md
    assert "Menu" not in md and "Footer junk" not in md and "alert" not in md


def test_slug_for():
    assert slug_for("https://www.ontario.ca/page/business/start") == "www-ontario-ca-page-business-start"


def test_front_matter_roundtrip():
    meta, body = parse_front_matter("---\nsource_url: http://x\ntitle: T\n---\n\n# Hi\ntext")
    assert meta == {"source_url": "http://x", "title": "T"}
    assert body.startswith("# Hi")


def test_chunks_are_bounded_and_carry_headings():
    meta = {"title": "Doc", "file": "doc.md", "source_url": "", "license": "x"}
    text = "# Top\n\nintro\n\n## Sub\n\n" + "\n\n".join(f"Paragraph {i}. " + "word " * 60 for i in range(20))
    chunks = chunk_document(meta, text)
    assert len(chunks) > 3
    assert all(len(c.text) < config.CHUNK_CHARS * 1.6 for c in chunks)
    assert any("Top > Sub" in c.text for c in chunks)
    assert len({c.id for c in chunks}) == len(chunks)  # unique ids


def test_end_to_end_retrieval(tmp_path, monkeypatch):
    web = tmp_path / "web"
    web.mkdir()
    (web / "register.md").write_text(
        "---\nsource_url: https://example.org/register\ntitle: Register a business\nlicense: ogl_ontario\n---\n\n"
        "# Register a business\n\nRegister your business name with the Ontario Business Registry. Fees apply.\n"
    )
    (web / "hst.md").write_text(
        "---\nsource_url: https://example.org/hst\ntitle: HST\nlicense: ogl_ontario\n---\n\n"
        "# HST\n\nStart charging HST once your taxable revenue passes 30000 dollars over four calendar quarters.\n"
    )
    monkeypatch.setattr(config, "WEB_DIR", web)
    monkeypatch.setattr(config, "DOCS_DIR", tmp_path / "none")
    monkeypatch.setattr(config, "DB_DIR", tmp_path / "db")
    monkeypatch.setattr(config, "MIN_SIMILARITY", 0.05)

    import ingest
    import rag

    ingest.main()
    hits = rag.retrieve("when do I start charging HST revenue", k=2)
    assert hits and hits[0]["title"] == "HST"
    assert hits[0]["url"] == "https://example.org/hst"

    hits = rag.retrieve("register business name registry", k=2)
    assert hits[0]["title"] == "Register a business"

    md = rag.format_sources(hits)
    assert "https://example.org/register" in md


def test_irrelevant_question_returns_no_sources(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_DIR", tmp_path / "db2")
    monkeypatch.setattr(config, "WEB_DIR", tmp_path / "w")
    monkeypatch.setattr(config, "DOCS_DIR", tmp_path / "d")
    (tmp_path / "d").mkdir()
    (tmp_path / "d" / "a.md").write_text("# Cash\n\nForecast your monthly cash inflows and outflows.\n")
    monkeypatch.setattr(config, "MIN_SIMILARITY", 0.35)
    import ingest
    import rag

    ingest.main()
    assert rag.retrieve("quantum chromodynamics gluon plasma") == []


def test_prompt_marks_missing_sources():
    from prompts import build_user_prompt

    assert "No sufficiently relevant sources" in build_user_prompt("q?", [])
    p = build_user_prompt("q?", [{"title": "T", "section": "S", "text": "body"}])
    assert p.startswith("SOURCES:") and "[1] T\nbody" in p


def test_html_to_markdown_removes_repeated_blocks():
    html = (
        "<main><h1>Title</h1><h1>Title</h1><p>Lead text here.</p><p>Lead text here.</p>"
        "<p>Different text.</p></main>"
    )
    _, md = html_to_markdown(html)
    assert md.count("Title") == 1 and md.count("Lead text here.") == 1
    assert "Different text." in md


def test_group_by_page_merges_chunks_and_numbers_pages():
    import rag

    hits = [
        {"text": "a", "title": "P1", "section": "", "url": "u1", "license": "", "similarity": 0.9},
        {"text": "b", "title": "P2", "section": "", "url": "u2", "license": "", "similarity": 0.8},
        {"text": "c", "title": "P1", "section": "", "url": "u1", "license": "", "similarity": 0.7},
    ]
    pages = rag.group_by_page(hits)
    assert [p["title"] for p in pages] == ["P1", "P2"]
    assert "a" in pages[0]["text"] and "c" in pages[0]["text"]
    md = rag.format_sources(pages)
    assert md.startswith("[1]") and "[2]" in md and "[3]" not in md


def test_chunk_prefix_does_not_repeat_title():
    meta = {"title": "Register", "file": "r.md", "source_url": "", "license": "x"}
    chunks = chunk_document(meta, "# 4. Register\n\nSome body text.\n")
    assert chunks[0].text.startswith("[Register]\n")
    assert chunks[0].metadata["section"] == ""


def test_step_numbers_are_removed_from_titles(tmp_path):
    from chunking import clean_title

    assert clean_title("6. Confirm if you need to charge HST") == "Confirm if you need to charge HST"
    assert clean_title("Choosing a business name") == "Choosing a business name"
    f = tmp_path / "p.md"
    f.write_text("---\ntitle: 6. Confirm HST\nsource_url: u\n---\n\n# 6. Confirm HST\n\nbody\n")
    meta, _ = load_file(f)
    assert meta["title"] == "Confirm HST"


def test_followup_uses_previous_question_for_retrieval(tmp_path, monkeypatch):
    d = tmp_path / "d"
    d.mkdir()
    (d / "hst.md").write_text("# HST registration\n\nRegister for an HST account with the CRA once revenue passes the threshold.\n")
    (d / "ins.md").write_text("# Insurance\n\nGet quotes from an insurance broker for liability coverage.\n")
    monkeypatch.setattr(config, "WEB_DIR", tmp_path / "w")
    monkeypatch.setattr(config, "DOCS_DIR", d)
    monkeypatch.setattr(config, "DB_DIR", tmp_path / "db3")
    monkeypatch.setattr(config, "MIN_SIMILARITY", 0.2)
    import ingest
    import rag

    ingest.main()
    followup = "Yes it did. What should I do next?"  # no topic words on its own
    alone = rag.retrieve(followup, k=1)
    history = [{"role": "user", "content": "Do I have to register for HST with the CRA?"}]
    with_ctx = rag.retrieve(followup, k=1, history=history)
    assert with_ctx and with_ctx[0]["section"] == "HST registration"
    assert not alone or alone[0]["similarity"] < with_ctx[0]["similarity"]


class _FakeClient:
    """Stands in for ollama.Client so no server is needed."""

    scope_answer = "YES"
    calls: list = []

    def __init__(self, host=None, **kwargs):
        pass

    def chat(self, model, messages, stream=False, options=None):
        _FakeClient.calls.append({"stream": stream, "options": options, "messages": messages})
        if stream:
            return iter([{"message": {"content": "answer"}}])
        return {"message": {"content": _FakeClient.scope_answer}}


def _empty_kb(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_DIR", tmp_path / "empty_db")
    monkeypatch.setattr(config, "WEB_DIR", tmp_path / "w")
    monkeypatch.setattr(config, "DOCS_DIR", tmp_path / "d")
    (tmp_path / "d").mkdir()
    (tmp_path / "d" / "a.md").write_text("# Cash\n\nForecast your monthly cash inflows and outflows.\n")
    import ingest

    ingest.main()


def test_off_topic_question_is_declined_without_generating(tmp_path, monkeypatch):
    import ollama
    import rag
    from prompts import OUT_OF_SCOPE_REPLY

    _empty_kb(tmp_path, monkeypatch)
    monkeypatch.setattr(ollama, "Client", _FakeClient)
    _FakeClient.scope_answer, _FakeClient.calls = "NO", []
    sources, tokens = rag.answer_stream("quantum chromodynamics gluon plasma")
    assert sources == [] and "".join(tokens) == OUT_OF_SCOPE_REPLY
    assert len(_FakeClient.calls) == 1 and _FakeClient.calls[0]["stream"] is False


def test_in_scope_question_without_sources_still_gets_answered(tmp_path, monkeypatch):
    import ollama
    import rag

    _empty_kb(tmp_path, monkeypatch)
    monkeypatch.setattr(ollama, "Client", _FakeClient)
    _FakeClient.scope_answer, _FakeClient.calls = "YES", []
    sources, tokens = rag.answer_stream("quantum chromodynamics gluon plasma")
    assert sources == [] and "".join(tokens) == "answer"
    assert _FakeClient.calls[-1]["stream"] is True
    assert _FakeClient.calls[-1]["options"]["num_ctx"] == config.NUM_CTX


def test_scope_check_errors_fail_open():
    import rag

    class Boom:
        def chat(self, **kw):
            raise RuntimeError("server down")

    assert rag.is_in_scope(Boom(), "anything") is True


def test_sources_are_capped_and_history_trimmed():
    import rag

    long_text = "x" * 5000
    hits = [{"text": long_text, "title": "P", "section": "", "url": "u", "license": "", "similarity": 0.9}]
    assert len(rag.group_by_page(hits)[0]["text"]) <= config.MAX_SOURCE_CHARS
    history = [{"role": "assistant" if i % 2 else "user", "content": "y" * 3000} for i in range(10)]
    msgs = rag._messages("q", [], history)
    assert len(msgs) == 1 + 4 + 1  # system + last 4 history + new question
    assert all(len(m["content"]) <= 3000 for m in msgs[1:5]) and len(msgs[1]["content"]) == 700


def test_acronyms_are_expanded_for_search_and_scope_check(tmp_path, monkeypatch):
    import rag

    assert rag.expand_acronyms("What do I need the BIN for?") == \
        "What do I need the BIN (Ontario Business Identification Number) for?"
    assert rag.expand_acronyms("Do I charge HST?") == "Do I charge HST (harmonized sales tax)?"
    already = "the Ontario Business Identification Number (BIN)"
    assert rag.expand_acronyms(already) == already          # not expanded twice
    assert rag.expand_acronyms("the bin outside") == "the bin outside"  # lowercase words untouched

    _empty_kb(tmp_path, monkeypatch)
    monkeypatch.setattr("ollama.Client", _FakeClient, raising=False)
    _FakeClient.calls = []
    assert rag.is_in_scope(_FakeClient(), "What do I need the BIN for?")
    sent = _FakeClient.calls[0]["messages"][1]["content"]
    assert "Ontario Business Identification Number" in sent


def test_weak_sources_still_go_through_the_scope_check(tmp_path, monkeypatch):
    """Off-topic questions can score just above MIN_SIMILARITY against some page; they must
    still be declined, and no sources shown."""
    import rag

    monkeypatch.setattr(config, "SCOPE_CHECK_BELOW", 0.62)
    weak = [{"text": "t", "title": "T", "section": "", "url": "u", "license": "", "similarity": 0.55}]
    strong = [{"text": "t", "title": "T", "section": "", "url": "u", "license": "", "similarity": 0.80}]
    monkeypatch.setattr("ollama.Client", _FakeClient, raising=False)

    _FakeClient.scope_answer = "NO"
    monkeypatch.setattr(rag, "retrieve", lambda *a, **k: weak)
    sources, tokens = rag.answer_stream("Give me a recipe for lasagna.")
    assert sources == [] and "".join(tokens) == rag.OUT_OF_SCOPE_REPLY

    _FakeClient.calls = []
    monkeypatch.setattr(rag, "retrieve", lambda *a, **k: strong)  # confident match: no scope call at all
    sources, tokens = rag.answer_stream("How much is registration?")
    assert sources and not [c for c in _FakeClient.calls if not c["stream"]]

    _FakeClient.scope_answer = "YES"  # weak match but on topic: answered normally
    monkeypatch.setattr(rag, "retrieve", lambda *a, **k: weak)
    sources, tokens = rag.answer_stream("What is Digital Main Street?")
    assert sources and "".join(tokens) == "answer"


def test_prompt_forbids_invented_specifics_and_requires_professional_referral():
    from prompts import NO_SOURCE_NOTE, SYSTEM_PROMPT

    for text in (SYSTEM_PROMPT, NO_SOURCE_NOTE):
        assert "phone numbers" in text and "own knowledge" in text
    assert "lawyer" in SYSTEM_PROMPT and "legal, tax, or accounting" in SYSTEM_PROMPT
    assert "[1]" in SYSTEM_PROMPT  # the citation rule must survive the rewrite


def test_scope_prompt_only_refuses_clearly_unrelated_and_knows_business_terms():
    from prompts import SCOPE_CHECK_PROMPT

    assert "clearly unrelated" in SCOPE_CHECK_PROMPT and "Nuans" in SCOPE_CHECK_PROMPT
    assert "YES or NO" in SCOPE_CHECK_PROMPT


def test_invalid_citation_markers_are_removed():
    import rag

    assert rag.strip_invalid_citations("Fee is $60 [1]. Also see [4] and [2].", 2) == "Fee is $60 [1]. Also see and [2]."
    assert rag.strip_invalid_citations("Fee is $60 [1].", 0) == "Fee is $60."
    assert rag.strip_invalid_citations("Keep [1][2].", 2) == "Keep [1][2]."


# ------------------------------------------------------------------ Phase 2 retrieval upgrades
def _kb_with_named_program(tmp_path, monkeypatch, name="kb"):
    web = tmp_path / name / "web"
    web.mkdir(parents=True)
    (web / "funding.md").write_text(
        "---\nsource_url: https://example.ca/funding\ntitle: Funding\nlicense: ogl_ontario\n---\n\n"
        "# Funding\n\n## Support\n\n- Apply for training and a grant through Starter Company Plus.\n"
        "- Digital Main Street delivers programs to businesses.\n\n## Loans\n\n- Futurpreneur offers loans.\n"
    )
    (web / "structures.md").write_text(
        "---\nsource_url: https://example.ca/structures\ntitle: Structures\nlicense: ogl_ontario\n---\n\n"
        "# Structures\n\nThere are four types of business structures.\n\n## Sole proprietorships\n\nOne owner.\n\n"
        "## Partnerships\n\nTwo or more owners.\n\n## Corporations\n\nA legal entity.\n\n## Co-operatives\n\nOwned by members.\n"
    )
    monkeypatch.setattr(config, "WEB_DIR", web)
    monkeypatch.setattr(config, "DOCS_DIR", tmp_path / name / "docs")
    monkeypatch.setattr(config, "DB_DIR", tmp_path / name / "db")
    import ingest

    ingest.main()


def test_lexical_index_matches_rare_words_and_ignores_off_topic():
    from lexical import LexicalIndex

    texts = [
        "Apply for a grant through Starter Company Plus.",
        "Register your business with the Ontario Business Registry.",
        "Business insurance is recommended for every business.",
        "Your business plan should explain your business.",
    ]
    texts += [f"Filler page {i} about running a business." for i in range(10)]  # "business" is now common
    idx = LexicalIndex(texts)
    assert [i for i, _ in idx.search("What is Starter Company Plus?")] == [0]
    assert idx.search("What is the capital of France?") == []      # unknown words count against coverage
    assert [i for i, _ in idx.search("Do I need business insurance?")] == [2]   # rare word + full coverage
    assert idx.search("Do I need business plan tips for France?") == []          # unseen word drags coverage down
    assert idx.search("business") == []                             # common words never trigger it


def test_keyword_search_finds_named_program_that_embeddings_miss(tmp_path, monkeypatch):
    _kb_with_named_program(tmp_path, monkeypatch)
    import rag

    monkeypatch.setattr(config, "MIN_SIMILARITY", 0.99)  # pretend the embedding search found nothing
    monkeypatch.setattr(config, "KEYWORD_SEARCH", True)
    hits = rag.retrieve("What is Starter Company Plus?")
    assert hits and "Starter Company Plus" in hits[0]["text"]
    assert hits[0]["similarity"] == config.LEX_SIMILARITY < config.SCOPE_CHECK_BELOW
    monkeypatch.setattr(config, "KEYWORD_SEARCH", False)
    assert rag.retrieve("What is Starter Company Plus?") == []
    monkeypatch.setattr(config, "KEYWORD_SEARCH", True)
    assert rag.retrieve("What is the capital of France?") == []


def test_short_pages_are_given_whole_within_a_budget(tmp_path, monkeypatch):
    _kb_with_named_program(tmp_path, monkeypatch, name="kb2")
    import rag

    hits = [{"id": "x", "text": "[Structures]\nThere are four types", "title": "Structures", "section": "",
             "url": "https://example.ca/structures", "file": "structures.md", "license": "", "similarity": 0.9},
            {"id": "y", "text": "[Funding]\nfragment", "title": "Funding", "section": "",
             "url": "https://example.ca/funding", "file": "funding.md", "license": "", "similarity": 0.8}]
    pages = rag.group_by_page(hits)
    assert "Co-operatives" in pages[0]["text"] and "Corporations" in pages[0]["text"]   # the full list
    assert "Starter Company Plus" in pages[1]["text"]

    monkeypatch.setattr(config, "MAX_TOTAL_SOURCE_CHARS", len(pages[0]["text"]) + 5)    # no room for page two
    pages = rag.group_by_page(hits)
    assert pages[1]["text"] == "[Funding]\nfragment"                                     # falls back to the chunk
    monkeypatch.setattr(config, "FULL_PAGE_MAX_CHARS", 10)                               # pages too long to send whole
    assert rag.group_by_page(hits)[0]["text"] == "[Structures]\nThere are four types"


def test_whole_page_text_drops_step_numbers_from_headings(tmp_path, monkeypatch):
    import rag

    web = tmp_path / "w"
    web.mkdir()
    (web / "p.md").write_text("---\ntitle: 3. Decide\nsource_url: u\n---\n\n# 3. Decide on the structure\n\n## 12. Sole proprietorships\n\nCost is 3. Not a heading.\n")
    monkeypatch.setattr(config, "WEB_DIR", web)
    monkeypatch.setattr(config, "DOCS_DIR", tmp_path / "d")
    text = rag._full_page_text("p.md")
    assert text.startswith("# Decide on the structure") and "## Sole proprietorships" in text
    assert "Cost is 3. Not a heading." in text
