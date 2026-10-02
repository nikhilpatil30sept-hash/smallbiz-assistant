# Evaluation summary - llama3.1:8b

- Run: 2026-09-23 14:30  |  questions: 6  |  judge: off
- Settings: MIN_SIMILARITY=0.52, TOP_K=5, NUM_CTX=8192, temperature=0.0
- **Overall pass rate: 17%** (1/6)
- Average seconds per question: 12.7

## By category

| Category | Questions | Pass | Facts found | Cites [n] | Valid [n] | Right source | Numbers OK | Judge faithful (avg, informational) |
|---|---|---|---|---|---|---|---|---|
| fact | 2 | 0% | 0% | 100% | 100% | 100% | 100% | - |
| followup | 1 | 0% | 0% | 100% | 100% | 100% | 100% | - |
| not_in_kb | 3 | 33% | - | - | - | - | - | - |

## What to look at first

Pass/fail below comes only from the rule checks (facts, citations, right source, numbers supported by the sources, hedged/declined/referred wording, no forbidden claims). The local-model judge no longer decides pass/fail - it flagged several correct answers as unfaithful across two runs, so its score is informational only; see 'Judge flagged, but passed' below to spot-check it by hand.

Most common reasons for failing (a question can have several):

- `facts`: 3
- `hedged`: 2

## Failed questions

- **F021** (fact) Do I have to register a sole proprietorship in Ontario? -> facts, missing: own name/your own name
- **F060** (fact) Who should I contact about the location for my business? -> facts, missing: Business Improvement/BIA
- **U015** (followup) How do I get a GST/HST number? -> facts, missing: Business Registration Online/BRO
- **N011** (not_in_kb) How often do I have to file my HST return? -> hedged
- **N019** (not_in_kb) How much does it cost to incorporate federally? -> hedged

## Judge flagged, but passed (informational - spot-check these by hand)

None.
