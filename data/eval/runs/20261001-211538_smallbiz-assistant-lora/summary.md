# Evaluation summary - smallbiz-assistant-lora

- Run: 2026-10-01 21:15  |  questions: 9  |  judge: off
- Settings: MIN_SIMILARITY=0.52, TOP_K=5, NUM_CTX=8192, temperature=0.0
- **Overall pass rate: 67%** (6/9)
- Average seconds per question: 33.0

## By category

| Category | Questions | Pass | Facts found | Cites [n] | Valid [n] | Right source | Numbers OK | Judge faithful (avg, informational) |
|---|---|---|---|---|---|---|---|---|
| process | 4 | 50% | 50% | 100% | 100% | 100% | 100% | - |
| followup | 5 | 80% | 100% | 80% | 100% | 100% | 100% | - |

## What to look at first

Pass/fail below comes only from the rule checks (facts, citations, right source, numbers supported by the sources, hedged/declined/referred wording, no forbidden claims). The local-model judge no longer decides pass/fail - it flagged several correct answers as unfaithful across two runs, so its score is informational only; see 'Judge flagged, but passed' below to spot-check it by hand.

Most common reasons for failing (a question can have several):

- `facts`: 2
- `citation`: 1

## Failed questions

- **S101** (process) What do I need to think about before opening a restaurant in Ontario? -> facts, missing: food handler
- **S102** (process) What do I need to sort out about taxes when I start a business? -> facts, missing: CPP/Canada Pension Plan
- **U102** (followup) Does that apply to a home-based business too? -> citation

## Judge flagged, but passed (informational - spot-check these by hand)

None.
