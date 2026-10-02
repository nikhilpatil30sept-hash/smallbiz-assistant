"""Scoring rubric for the Phase 2 evaluation. Everything here is a plain function so it can
be tested offline. See README ("Phase 2") for the rubric in words.

Each question is checked against rules that depend on what a good answer looks like
(its `expect` value):

  answer             the facts are present, the answer cites [n], and a page that really
                     contains the facts was shown as a source
  no_source_general  in scope but not in the knowledge base: the assistant must say it has no
                     official source (or clearly label its advice as general)
  decline            off topic: a short polite refusal, no sources, no answer to the question
  refer_professional legal/tax risk: points the person to a lawyer/accountant/CRA and does
                     not overpromise

Every question also fails if any `forbidden` string appears (a wrong claim or a leaked
off-topic answer). A local-model judge adds a faithfulness score (see evaluate.py).
"""
import json
import re

CITATION_RE = re.compile(r"\[\d+\]")

HEDGE_PHRASES = [
    "couldn't find", "could not find", "couldn't locate", "no official source", "not in the sources",
    "sources do not", "sources don't", "don't have", "do not have", "isn't covered", "not covered",
    "not mentioned", "isn't mentioned", "no specific", "general guidance", "general information",
    "in general", "generally", "not from the sources", "general terms", "general advice",
    "i don't see", "i do not see", "not addressed", "no information",
    "do not mention", "does not mention", "don't mention", "doesn't mention", "not mention",
    "do not address", "does not address", "do not provide", "does not provide", "do not contain",
    "does not contain", "do not include", "does not include", "not specifically",
    "none of the sources", "neither [", "not address", "no source", "do not answer", "does not answer",
    "no mention", "no direct answer", "do not cover", "does not cover", "don't cover", "doesn't cover", "not found", "could not find an official",
    "neither of the sources", "neither source", "none of the provided sources",
    "not specified in the sources", "not specified in the source", "not explicitly mentioned",
    "not explicitly stated", "not explicitly addressed", "not explicitly covered",
    "no direct information", "it is not clear", "is not clear if", "is not clear whether",
    "not clear from the sources", "unclear from the sources", "does not specify", "do not specify",
    "doesn't specify", "don't specify", "not clearly stated", "not clearly addressed",
]
DECLINE_PHRASES = [
    "only help", "can only", "only able", "not able to help", "unable to help", "can't help with",
    "cannot help with", "outside", "small business topics", "small-business topics",
    "small business questions", "focus on small business", "not related to", "isn't related to",
    "not about starting", "isn't about",
]
# The prompt forbids these when no source covers the question, so a match means the model
# invented a specific (a phone number, a web address, or the name of a law).
INVENTED_SPECIFICS_RE = re.compile(
    r"(\b1[- .]?\d{3}[- .]\d{3}[- .]\d{4}\b|\b\d{3}[- .]\d{3}[- .]\d{4}\b"   # phone numbers
    r"|https?://|\bwww\.|\b[a-z0-9-]+\.(?:ca|gc\.ca|com|org)\b"                   # web addresses
    r"|\b(?:[A-Z][a-z]+ ){1,4}Act\b(?:,? \d{4})?)"                                     # "Employment Standards Act"
)

REFER_PHRASES = [
    "lawyer", "accountant", "tax professional", "tax advisor", "legal advice", "legal professional",
    "professional advisor", "professional advice", "financial advisor", "cra", "canada revenue agency",
    "bookkeeper", "legal counsel", "consult",
]

# A dollar amount or percentage in the answer, e.g. "$60", "$15,000", "13%". This catches
# invented figures the judge missed (it let "Futurpreneur lends up to $45,000" through, when
# no source says that - the real figure is $15,000).
MONEY_PERCENT_RE = re.compile(r"\$\s?\d[\d,]*(?:\.\d+)?|\b\d[\d,]*(?:\.\d+)?\s?%")


def _digits(text: str) -> str:
    return re.sub(r"[^\d.]", "", text)


def norm(text: str) -> str:
    text = text.lower().replace("’", "'").replace("‘", "'").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", text)


_NUMBER_WORDS = {"two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7",
                 "eight": "8", "nine": "9", "ten": "10", "twelve": "12"}
_NUMBER_RE = re.compile(r"\b(" + "|".join(_NUMBER_WORDS) + r")\b")
NEGATION_RE = re.compile(r"\b(no|not|never|incorrect|false|wrong|isn't|aren't|doesn't|don't|cannot|can't|"
                         r"won't|neither|nor|untrue|myth)\b|n't\b")


def norm_num(text: str) -> str:
    """norm() plus number words as digits, so 'four quarters' and '4 quarters' match."""
    return _NUMBER_RE.sub(lambda m: _NUMBER_WORDS[m.group(1)], norm(text))


def _contains_any(answer_n: str, phrases: list[str]) -> bool:
    return any(norm(p) in answer_n for p in phrases)


def _facts_present(answer: str, group: list[str]) -> bool:
    a = norm_num(answer)
    return any(norm_num(alt) in a for alt in group)


def _affirms(answer: str, phrase: str) -> bool:
    """True if the answer states `phrase` in a sentence with no negation. Used for
    false-premise questions, where a correct answer often repeats the wrong claim
    while denying it ("No, that is not correct: it is $15,000, not $1 million")."""
    p = norm_num(phrase)
    for sentence in re.split(r"(?<=[.!?])\s+|\n+", answer):
        n = norm_num(sentence)
        if p in n and not NEGATION_RE.search(n):
            return True
    return False


def facts_recall(answer: str, groups: list[list[str]]) -> tuple[float, list[list[str]]]:
    """Fraction of fact groups present (a group is present if ANY alternative appears)."""
    if not groups:
        return 1.0, []
    missing = [g for g in groups if not _facts_present(answer, g)]
    return (len(groups) - len(missing)) / len(groups), missing


def source_hit(source_urls: list[str], expected: list[str]) -> bool:
    """`source_urls` holds each shown source's URL (or its title when it has no URL, as
    with your own documents). A full https:// pattern must match exactly; anything else is
    a case-insensitive fragment."""
    if not expected:
        return True
    for pat in expected:
        for url in source_urls:
            if (pat.startswith("http") and url == pat) or (not pat.startswith("http") and pat.lower() in url.lower()):
                return True
    return False


def citations_valid(answer: str, n_sources: int) -> bool:
    """Every [n] in the answer must point at a source that was actually shown."""
    return all(1 <= int(n) <= n_sources for n in re.findall(r"\[(\d+)\]", answer))


def numbers_supported(answer: str, source_text: str) -> tuple[bool, list[str]]:
    """Every dollar amount / percentage in the answer must appear (as digits) somewhere in
    the source text shown. Catches an invented figure even when it reads fluently and the
    judge waves it through. `source_text` empty/None means "not checked" (True, [])."""
    if not source_text:
        return True, []
    found = MONEY_PERCENT_RE.findall(answer)
    src_digits = _digits(source_text)
    bad = [f for f in found if _digits(f) not in src_digits]
    return not bad, bad


def score_item(item: dict, answer: str, source_urls: list[str], source_text: str = "") -> dict:
    """Return {'checks': {name: bool}, 'auto_pass': bool, 'facts_recall': float, 'missing': [...]}.
    `source_text` (optional): the shown sources' text concatenated, for numbers_supported()."""
    a = norm(answer)
    expect = item["expect"]
    checks: dict[str, bool] = {}
    recall, missing = facts_recall(answer, item.get("expected_facts", []))

    if item.get("category") in ("false_premise", "risky_advice"):  # "there is no guarantee" is not a guarantee
        bad = [f for f in item.get("forbidden", []) if _affirms(answer, f)]
    else:
        bad = [f for f in item.get("forbidden", []) if norm_num(f) in norm_num(answer)]
    checks["no_forbidden"] = not bad

    numbers_ok, bad_numbers = numbers_supported(answer, source_text)

    if expect == "answer":
        checks["facts"] = recall == 1.0
        checks["citation"] = bool(CITATION_RE.search(answer))
        checks["citations_valid"] = citations_valid(answer, len(source_urls))
        checks["right_source"] = source_hit(source_urls, item.get("expected_sources", []))
        checks["numbers_supported"] = numbers_ok
    elif expect == "no_source_general":
        checks["hedged"] = _contains_any(a, HEDGE_PHRASES)
        checks["no_invented_specifics"] = not INVENTED_SPECIFICS_RE.search(answer)
    elif expect == "decline":
        checks["declined"] = _contains_any(a, DECLINE_PHRASES)
        checks["no_sources"] = not source_urls
        checks["short"] = len(answer) < 600
    elif expect == "refer_professional":
        checks["refers_to_professional"] = _contains_any(a, REFER_PHRASES)
        checks["numbers_supported"] = numbers_ok
    else:
        raise ValueError(f"unknown expect value: {expect}")

    return {
        "checks": checks,
        "auto_pass": all(checks.values()),
        "facts_recall": recall,
        "bad_numbers": bad_numbers,
        "missing": missing,
        "forbidden_found": bad,
    }


# ---------------------------------------------------------------- local-model judge
JUDGE_SYSTEM = """You are a strict grader of an assistant that answers small-business questions using numbered SOURCES.
Score the ANSWER on:
- faithful (1-5): 5 = every specific fact, number, fee, deadline or step is supported by the SOURCES or is clearly labelled as general guidance / not from the sources. 3 = mostly supported but contains one unsupported detail stated as fact. 1 = invents facts or contradicts the sources. If there are no sources, the answer must not present specific figures or rules as official.
- helpful (1-5): 5 = directly and clearly answers the question. 1 = evasive, wrong, or off target.
List every unsupported or invented claim in "unsupported" (empty list if none).
Reply with JSON only: {"faithful": <1-5>, "helpful": <1-5>, "unsupported": ["..."]}"""


def build_judge_prompt(question: str, sources: list[dict], answer: str) -> str:
    if sources:
        src = "\n\n".join(f"[{i}] {s['title']}\n{s['text']}" for i, s in enumerate(sources, 1))
    else:
        src = "(none - no official source was found)"
    return f"QUESTION:\n{question}\n\nSOURCES:\n{src}\n\nANSWER:\n{answer}"


def parse_judge(raw: str) -> dict:
    """Tolerant JSON parsing; returns {'faithful': int|None, 'helpful': int|None, 'unsupported': [...]}."""
    out = {"faithful": None, "helpful": None, "unsupported": []}
    match = re.search(r"\{.*\}", raw, re.S)
    if not match:
        return out
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return out
    for key in ("faithful", "helpful"):
        try:
            v = int(round(float(data.get(key))))
            out[key] = min(5, max(1, v))
        except (TypeError, ValueError):
            pass
    uns = data.get("unsupported", [])
    out["unsupported"] = [str(u) for u in uns] if isinstance(uns, list) else [str(uns)]
    return out


FAITHFUL_PASS = 4  # still used to flag low judge scores for a human to read; it no longer fails anything


def final_pass(item: dict, scored: dict, judge: dict | None) -> bool:
    """Pass/fail is decided entirely by the rule checks (facts, citations, right source,
    numbers_supported, hedged/declined/referred wording, no forbidden claims).

    The judge does NOT gate pass/fail any more. Across two runs it flagged several correct
    answers (faithful=3 for "if you incorporate federally your name is protected", which is
    exactly what the source says) while missing a real invented figure ($45,000 for a loan
    the source caps at $15,000 - numbers_supported() catches that instead). Its score is
    still recorded on every record so you can spot-check low ones by hand."""
    return bool(scored["auto_pass"])
