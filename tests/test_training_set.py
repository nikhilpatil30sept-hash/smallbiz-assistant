"""Offline tests for build_training_set.py: no Ollama, no internet (EMBED_BACKEND=hash)."""
import json
import os
import sys
from pathlib import Path

os.environ["EMBED_BACKEND"] = "hash"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

import config
import build_training_set as bts


def test_matches_substring_vs_exact_url():
    assert bts._matches("register-your-business-online", "https://x.ca/page/register-your-business-online")
    assert not bts._matches("register-your-business-online", "https://x.ca/page/other")
    # a fragment starting with "http" must match the URL exactly, not as a substring
    assert bts._matches("https://x.ca/start", "https://x.ca/start")
    assert not bts._matches("https://x.ca/start", "https://x.ca/start/step-two")


def test_resolve_citations_fills_in_real_index_and_warns_when_missing():
    sources = [
        {"url": "https://example.org/register-your-business-online", "title": "Register"},
        {"url": "https://example.org/confirm-hst", "title": "HST"},
    ]
    warnings = []
    out = bts._resolve_citations(
        "Fee is $60 {{CITE:REG}}, threshold is $30,000 {{CITE:HST}}.",
        ["REG", "HST"], sources, warnings, "T001",
    )
    assert out == "Fee is $60 [1], threshold is $30,000 [2]."
    assert warnings == []

    warnings2 = []
    out2 = bts._resolve_citations("Cost is $15,000 {{CITE:FUND}}.", ["FUND"], sources, warnings2, "T002")
    assert "{{CITE:FUND}}" in out2  # left in place, not guessed
    assert any("FUND" in w for w in warnings2)
    assert any("unresolved placeholder" in w for w in warnings2)


def test_check_disjoint_refuses_on_overlap(tmp_path, monkeypatch):
    eval_path = tmp_path / "eval_set.jsonl"
    eval_path.write_text(json.dumps({"question": "How much does it cost to register?"}) + "\n")
    monkeypatch.setattr(bts, "EVAL_SET", eval_path)
    with pytest.raises(SystemExit):
        bts._check_disjoint(["How much does it cost to register?"])
    # different wording is fine
    bts._check_disjoint(["What's the registration fee?"])


def test_pilot_items_are_disjoint_from_the_real_eval_set():
    """The actual eval_set.jsonl on disk, checked against the actual PILOT list - the real
    guardrail that matters, not just the mechanism above."""
    from training_pairs import PILOT
    questions = [item["turns"][-1].strip().lower() for item in PILOT]
    eval_path = Path(__file__).resolve().parent.parent / "data" / "eval" / "eval_set.jsonl"
    if not eval_path.exists():
        pytest.skip("no eval_set.jsonl on disk in this environment")
    eval_qs = set()
    with eval_path.open() as f:
        for line in f:
            eval_qs.add(json.loads(line)["question"].strip().lower())
    overlap = [q for q in questions if q in eval_qs]
    assert not overlap, f"training questions duplicate eval-set questions verbatim: {overlap}"


def test_pilot_categories_and_cite_keys_are_valid():
    from training_pairs import PILOT, FRAGMENTS
    valid_categories = {"fact", "phrasing", "process", "followup", "not_in_kb", "risky_advice", "false_premise"}
    seen_questions = set()
    for item in PILOT:
        assert item["category"] in valid_categories, item
        for key in item["cite"]:
            assert key in FRAGMENTS, f"unknown cite key {key!r} in item {item['turns'][-1]!r}"
        if item["category"] == "not_in_kb":
            assert not item["cite"], "not_in_kb items must not cite a source"
        q = item["turns"][-1].strip().lower()
        assert q not in seen_questions, f"duplicate question within training_pairs.py: {q!r}"
        seen_questions.add(q)


def test_build_training_set_end_to_end_against_a_tiny_fixture_kb(tmp_path, monkeypatch):
    """Exercises the real path: fixture pages -> real ingest -> real retrieve() -> citation
    resolution -> messages assembly, using a couple of fixture pages that mirror two of the
    real fragment groups (REG, HST) used in training_pairs.py."""
    web = tmp_path / "web"
    web.mkdir()
    (web / "register.md").write_text(
        "---\nsource_url: https://example.org/register-your-business-online\ntitle: Register\n"
        "license: ogl_ontario\n---\n\n# Register\n\nRegistering a sole proprietorship costs $60. "
        "Registering a corporation costs $300. You need a Nuans report first.\n"
    )
    (web / "hst.md").write_text(
        "---\nsource_url: https://example.org/confirm-hst\ntitle: HST\nlicense: ogl_ontario\n---\n\n"
        "# HST\n\nStart charging HST once your taxable revenue passes 30000 dollars.\n"
    )
    monkeypatch.setattr(config, "WEB_DIR", web)
    monkeypatch.setattr(config, "DOCS_DIR", tmp_path / "none")
    monkeypatch.setattr(config, "DB_DIR", tmp_path / "db")
    monkeypatch.setattr(config, "MIN_SIMILARITY", 0.05)

    import ingest
    ingest.main()

    import rag
    sources = rag.group_by_page(rag.retrieve("how much does it cost to register a sole proprietorship?"))
    warnings: list[str] = []
    out = bts._resolve_citations("The fee is $60 {{CITE:REG}}.", ["REG"], sources, warnings, "T-fixture")
    assert warnings == []
    assert "[1]" in out or "[2]" in out  # resolved to whichever slot retrieval put it in
    assert "{{CITE" not in out
