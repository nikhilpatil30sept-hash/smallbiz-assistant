"""Offline tests for the Phase 2 evaluation code and question set."""
import json
import os
import sys
from pathlib import Path

os.environ["EMBED_BACKEND"] = "hash"
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pytest

import config
import evaluate
import scoring

EVAL_SET = ROOT / "data" / "eval" / "eval_set.jsonl"
VALID_EXPECT = {"answer", "no_source_general", "decline", "refer_professional"}


def items():
    return [json.loads(line) for line in EVAL_SET.read_text().splitlines() if line.strip()]


# ------------------------------------------------------------------ the question set
def test_eval_set_is_well_formed():
    data = items()
    assert 190 <= len(data) <= 220
    ids = [d["id"] for d in data]
    assert len(set(ids)) == len(ids)
    for d in data:
        assert d["expect"] in VALID_EXPECT, d["id"]
        assert d["turns"] and d["turns"][-1] == d["question"], d["id"]
        for g in d["expected_facts"]:
            assert isinstance(g, list) and g and all(isinstance(a, str) and a for a in g), d["id"]
        if d["expect"] == "answer":
            assert d["expected_facts"], f"{d['id']} has no expected facts"
        if d["category"] == "followup":
            assert len(d["turns"]) >= 2, d["id"]
    cats = {d["category"] for d in data}
    assert {"fact", "process", "followup", "not_in_kb", "off_topic", "risky_advice", "false_premise"} <= cats


def test_eval_set_matches_builder():
    """The .jsonl must be regenerated after editing build_eval_set.py."""
    import build_eval_set

    built = [json.dumps({k: it[k] for k in ["id", "category", "expect", "question", "turns",
                                            "expected_facts", "expected_sources", "forbidden"]},
                        ensure_ascii=False) for it in build_eval_set.items]
    assert built == [line for line in EVAL_SET.read_text().splitlines() if line.strip()]


def test_expected_facts_appear_in_the_knowledge_base_when_present():
    """On a machine with the downloaded pages, every fact we expect must really be in them,
    otherwise a correct answer could never pass."""
    web = list(config.WEB_DIR.glob("*.md")) if config.WEB_DIR.exists() else []
    if len(web) < 15:
        pytest.skip("the government pages have not been downloaded here (python fetch_sources.py)")
    docs = list(config.DOCS_DIR.glob("*.md")) if config.DOCS_DIR.exists() else []
    pages = web + docs
    corpus = scoring.norm(" ".join(p.read_text() for p in pages))
    bad = []
    for d in items():
        if d["expect"] != "answer":
            continue
        for group in d["expected_facts"]:
            if not any(scoring.norm(alt) in corpus for alt in group):
                bad.append((d["id"], group))
    assert not bad, f"facts not found in the knowledge base: {bad}"


# ------------------------------------------------------------------ scoring rules
def _item(**kw):
    base = {"id": "T1", "category": "fact", "expect": "answer", "question": "q", "turns": ["q"],
            "expected_facts": [], "expected_sources": [], "forbidden": []}
    base.update(kw)
    return base


def test_answer_needs_facts_citation_and_source():
    it = _item(expected_facts=[["$60"], ["ontario business registry"]], expected_sources=["register-your-business-online"])
    good = scoring.score_item(it, "It costs $60 at the Ontario Business Registry [1].",
                              ["https://www.ontario.ca/page/business/start/register-your-business-online"])
    assert good["auto_pass"] and good["facts_recall"] == 1.0
    no_cite = scoring.score_item(it, "It costs $60 at the Ontario Business Registry.",
                                 ["https://x/register-your-business-online"])
    assert not no_cite["auto_pass"] and not no_cite["checks"]["citation"]
    wrong_src = scoring.score_item(it, "It costs $60 at the Ontario Business Registry [1].", ["https://x/other"])
    assert not wrong_src["checks"]["right_source"]
    missing = scoring.score_item(it, "It costs $60 [1].", ["https://x/register-your-business-online"])
    assert missing["facts_recall"] == 0.5 and missing["missing"] == [["ontario business registry"]]


def test_forbidden_text_fails_even_if_facts_present():
    it = _item(expected_facts=[["not mandatory", "isn't mandatory"]], forbidden=["insurance is mandatory"])
    ok = scoring.score_item(it, "Business insurance isn’t mandatory [1].", ["u"])
    assert ok["checks"]["no_forbidden"] and ok["checks"]["facts"]  # curly apostrophe is normalised
    bad = scoring.score_item(it, "Yes, insurance is mandatory, although it isn't mandatory for hobbies [1].", ["u"])
    assert not bad["checks"]["no_forbidden"]


def test_source_matching_exact_and_fragment():
    assert scoring.source_hit(["https://www.ontario.ca/page/business/start"], ["https://www.ontario.ca/page/business/start"])
    assert not scoring.source_hit(["https://www.ontario.ca/page/business/start/confirm-hst"],
                                  ["https://www.ontario.ca/page/business/start"])
    assert scoring.source_hit(["https://www.ontario.ca/page/business/start/confirm-hst"], ["confirm-hst"])
    assert scoring.source_hit([], [])


def test_decline_rules():
    it = _item(expect="decline", forbidden=["Paris"])
    reply = "I can only help with questions about starting, running, and growing a small business in Ontario."
    assert scoring.score_item(it, reply, [])["auto_pass"]
    assert not scoring.score_item(it, reply + " The capital is Paris.", [])["auto_pass"]
    assert not scoring.score_item(it, reply, ["https://x"])["auto_pass"]  # must show no sources
    assert not scoring.score_item(it, "The capital of France is a city.", [])["auto_pass"]  # no refusal


def test_no_source_and_professional_referral_rules():
    it = _item(expect="no_source_general")
    assert scoring.score_item(it, "I couldn't find an official source for this; generally, check with the CRA.", [])["auto_pass"]
    assert not scoring.score_item(it, "The rate is exactly 13% [1].", ["u"])["auto_pass"]
    rp = _item(expect="refer_professional")
    assert scoring.score_item(rp, "Talk to an accountant before deciding.", [])["auto_pass"]
    assert not scoring.score_item(rp, "Yes, do it.", [])["auto_pass"]


def test_judge_parsing_and_final_pass():
    assert scoring.parse_judge('{"faithful": 5, "helpful": 4, "unsupported": []}') == {
        "faithful": 5, "helpful": 4, "unsupported": []}
    assert scoring.parse_judge('Sure! {"faithful": "3", "helpful": 9, "unsupported": "made up fee"}') == {
        "faithful": 3, "helpful": 5, "unsupported": ["made up fee"]}
    assert scoring.parse_judge("not json") == {"faithful": None, "helpful": None, "unsupported": []}
    # The judge no longer decides pass/fail (see final_pass's docstring): only the rule
    # checks in `scored["auto_pass"]` do. A low or missing judge score never sinks an item,
    # and a rule failure isn't rescued by a high judge score.
    it, scored = _item(), {"auto_pass": True}
    assert scoring.final_pass(it, scored, {"faithful": 4})
    assert scoring.final_pass(it, scored, {"faithful": 3})
    assert scoring.final_pass(it, scored, {"faithful": None})
    assert scoring.final_pass(it, scored, None)
    assert not scoring.final_pass(it, {"auto_pass": False}, {"faithful": 5})
    assert scoring.final_pass(_item(expect="decline"), scored, {"faithful": 1})
    assert scoring.final_pass(_item(expect="no_source_general"), scored, {"faithful": 1})


# ------------------------------------------------------------------ the runner
def _fake_ask(item):
    q = item["question"]
    if item["expect"] == "decline":
        return "I can only help with small business topics.", []
    if "HST" in q or "hst" in q:
        return "You may need to charge HST once you pass $30,000 [1].", [
            {"title": "Confirm", "url": "https://x/confirm-hst", "similarity": 0.8, "text": "30,000"}]
    return "I couldn't find that in the sources; check with a lawyer or the CRA.", []


def test_runner_writes_reports_and_can_resume(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(evaluate, "ask", _fake_ask)
    monkeypatch.setattr(evaluate, "judge", lambda *a, **k: {"faithful": 5, "helpful": 4, "unsupported": []})
    monkeypatch.setattr(evaluate, "RUNS_DIR", tmp_path)
    run = tmp_path / "run1"
    assert evaluate.main(["--sample", "12", "--resume", str(run)]) == 0
    assert (run / "results.jsonl").exists() and (run / "results.csv").exists()
    summary = (run / "summary.md").read_text()
    assert "Overall pass rate" in summary and "| Category |" in summary
    lines_before = (run / "results.jsonl").read_text().splitlines()
    assert len(lines_before) == 12

    calls = []
    monkeypatch.setattr(evaluate, "ask", lambda item: calls.append(item["id"]) or _fake_ask(item))
    assert evaluate.main(["--sample", "12", "--resume", str(run)]) == 0
    assert calls == []  # everything was already done
    assert len((run / "results.jsonl").read_text().splitlines()) == 12


def test_runner_survives_errors_and_no_judge(tmp_path, monkeypatch):
    def boom(item):
        raise RuntimeError("ollama is down")

    monkeypatch.setattr(evaluate, "ask", boom)
    monkeypatch.setattr(evaluate, "RUNS_DIR", tmp_path)
    run = tmp_path / "run2"
    assert evaluate.main(["--limit", "3", "--no-judge", "--resume", str(run)]) == 0
    recs = [json.loads(l) for l in (run / "results.jsonl").read_text().splitlines()]
    assert len(recs) == 3 and all(r["error"] and not r["pass"] for r in recs)
    assert "error while answering" in (run / "summary.md").read_text()


def test_per_category_smoke_test_is_balanced(tmp_path, monkeypatch):
    monkeypatch.setattr(evaluate, "ask", _fake_ask)
    monkeypatch.setattr(evaluate, "RUNS_DIR", tmp_path)
    run = tmp_path / "run3"
    assert evaluate.main(["--per-category", "2", "--no-judge", "--resume", str(run)]) == 0
    recs = [json.loads(l) for l in (run / "results.jsonl").read_text().splitlines()]
    cats = {r["category"] for r in recs}
    assert len(cats) == 8 and len(recs) == 16


def test_scoring_fixes_from_the_first_full_run():
    # "4" and "four" are the same fact
    it = _item(expected_facts=[["four"]], expected_sources=[])
    assert scoring.score_item(it, "It looks at 4 consecutive quarters [1].", ["u"])["checks"]["facts"]
    # own documents have no URL: the title is used, case-insensitively
    assert scoring.source_hit(["Cash flow basics for a new small business"], ["cash flow basics"])
    # "the sources do not mention" counts as saying there is no official source
    ns = _item(expect="no_source_general")
    assert scoring.score_item(ns, "The sources do not mention the current HST rate; check the CRA.", [])["auto_pass"]
    # a false-premise answer may repeat the wrong claim while denying it ...
    fp = _item(category="false_premise", forbidden=["$1 million"])
    assert scoring.score_item(fp, "No, that is not correct: it is $15,000, not $1 million [1].", ["u"])["checks"]["no_forbidden"]
    # ... but not affirm it
    assert not scoring.score_item(fp, "Yes, Futurpreneur gives up to $1 million [1].", ["u"])["checks"]["no_forbidden"]
    # citing a source number that was never shown is caught
    assert not scoring.score_item(_item(), "It costs $60 [6].", ["u", "v"])["checks"]["citations_valid"]
    assert scoring.score_item(_item(), "It costs $60 [2].", ["u", "v"])["checks"]["citations_valid"]


def test_rescore_reapplies_current_rules_without_model_calls(tmp_path, monkeypatch):
    monkeypatch.setattr(evaluate, "ask", _fake_ask)
    monkeypatch.setattr(evaluate, "RUNS_DIR", tmp_path)
    run = tmp_path / "run4"
    assert evaluate.main(["--per-category", "1", "--no-judge", "--resume", str(run)]) == 0
    monkeypatch.setattr(evaluate, "ask", lambda item: (_ for _ in ()).throw(AssertionError("must not ask the model")))
    assert evaluate.main(["--rescore", str(run)]) == 0
    out = tmp_path / "run4_rescored"
    assert (out / "results.jsonl").exists() and "Overall pass rate" in (out / "summary.md").read_text()
    assert len((out / "results.jsonl").read_text().splitlines()) == 8


def test_no_source_answers_must_not_invent_specifics_and_new_hedge_wording():
    ns = _item(expect="no_source_general")
    ok = "None of the sources address this. Contact the Ministry of Labour or a lawyer."
    assert scoring.score_item(ns, ok, [])["auto_pass"]
    assert scoring.score_item(ns, "Neither [1] nor [2] provides guidance on this; ask an accountant.", ["a", "b"])["checks"]["hedged"]
    for bad in ("None of the sources cover it. Call 1-800-959-5525.",
                "None of the sources cover it. See www.cra-arc.gc.ca.",
                "None of the sources cover it. It is governed by the Employment Standards Act, 2000."):
        assert not scoring.score_item(ns, bad, [])["checks"]["no_invented_specifics"], bad


def test_negated_forbidden_words_in_risky_advice_are_not_flagged():
    it = _item(category="risky_advice", expect="refer_professional", forbidden=["guarantee"])
    assert scoring.score_item(it, "There is no guarantee you will pay less tax; ask an accountant.", [])["auto_pass"]
    assert not scoring.score_item(it, "Incorporating will guarantee lower tax.", [])["checks"]["no_forbidden"]
    assert scoring.score_item(_item(expect="no_source_general"), "There is no mention of it in the sources.", [])["checks"]["hedged"]


def test_numbers_supported_catches_invented_figures_the_judge_missed():
    # the real regression: the model said "up to $45,000" when the source caps it at $15,000
    src = "Futurpreneur offers up to $15,000 in loan financing for a side business."
    ok, bad = scoring.numbers_supported("Futurpreneur lends up to $15,000 [1].", src)
    assert ok and bad == []
    ok, bad = scoring.numbers_supported("Futurpreneur lends up to $45,000 [1].", src)
    assert not ok and bad == ["$45,000"]
    # percentages, and commas/spacing don't matter for matching
    ok, _ = scoring.numbers_supported("The rate is 13%.", "HST is charged at a rate of 13 %.")
    assert ok
    ok, _ = scoring.numbers_supported("The rate is 15%.", "HST is charged at a rate of 13%.")
    assert not ok
    # no source text at all (e.g. a rescore) means "not checked", never a failure
    assert scoring.numbers_supported("It costs $999.", "") == (True, [])


def test_score_item_fails_an_answer_with_an_invented_number():
    it = _item(expected_facts=[["loan"]], expected_sources=["u"])
    src = "Futurpreneur offers up to $15,000 in loan financing."
    good = scoring.score_item(it, "Futurpreneur offers a loan of up to $15,000 [1].", ["u"], src)
    assert good["auto_pass"] and good["checks"]["numbers_supported"]
    bad = scoring.score_item(it, "Futurpreneur offers a loan of up to $45,000 [1].", ["u"], src)
    assert not bad["auto_pass"] and not bad["checks"]["numbers_supported"] and bad["bad_numbers"] == ["$45,000"]


def test_evaluate_item_checks_numbers_against_the_live_sources(monkeypatch):
    def bad_ask(item):
        return "Futurpreneur lends up to $45,000 [1].", [
            {"title": "Funding", "url": "https://x/funding", "similarity": 0.8,
             "text": "Futurpreneur offers up to $15,000 in loan financing."}]

    monkeypatch.setattr(evaluate, "ask", bad_ask)
    it = _item(expected_facts=[["loan"]], expected_sources=["funding"])
    rec = evaluate.evaluate_item(it, use_judge=False, judge_model="x")
    assert not rec["pass"] and not rec["checks"]["numbers_supported"] and rec["bad_numbers"] == ["$45,000"]
