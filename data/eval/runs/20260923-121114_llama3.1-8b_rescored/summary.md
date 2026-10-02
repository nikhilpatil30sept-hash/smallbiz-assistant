# Evaluation summary - 20260923-121114_llama3.1-8b (rescored)

- Run: 2026-09-23 12:16  |  questions: 10  |  judge: scores kept from the original run
- Settings: MIN_SIMILARITY=0.52, TOP_K=5, NUM_CTX=8192, temperature=as in original run
- **Overall pass rate: 100%** (10/10)
- Average seconds per question: 10.4

## By category

| Category | Questions | Pass | Facts found | Cites [n] | Valid [n] | Right source | Numbers OK | Judge faithful (avg, informational) |
|---|---|---|---|---|---|---|---|---|
| fact | 1 | 100% | 100% | 100% | 100% | 100% | 100% | - |
| not_in_kb | 5 | 100% | - | - | - | - | - | - |
| risky_advice | 2 | 100% | - | - | - | - | 100% | - |
| false_premise | 2 | 100% | 100% | 100% | 100% | 100% | 100% | - |

## What to look at first

Pass/fail below comes only from the rule checks (facts, citations, right source, numbers supported by the sources, hedged/declined/referred wording, no forbidden claims). The local-model judge no longer decides pass/fail - it flagged several correct answers as unfaithful across two runs, so its score is informational only; see 'Judge flagged, but passed' below to spot-check it by hand.

No failures.

## Failed questions


## Judge flagged, but passed (informational - spot-check these by hand)

None.
