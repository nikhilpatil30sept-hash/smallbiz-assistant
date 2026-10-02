# Evaluation summary - 20260920-211915_llama3.1-8b (rescored)

- Run: 2026-09-21 01:40  |  questions: 81  |  judge: scores kept from the original run
- Settings: MIN_SIMILARITY=0.52, TOP_K=5, NUM_CTX=8192, temperature=as in original run
- **Overall pass rate: 98%** (79/81)
- Average seconds per question: 10.6

## By category

| Category | Questions | Pass | Facts found | Cites [n] | Valid [n] | Right source | Judge faithful (avg) |
|---|---|---|---|---|---|---|---|
| phrasing | 6 | 83% | 83% | 83% | 100% | 83% | 4.8 |
| not_in_kb | 35 | 100% | - | - | - | - | 4.5 |
| off_topic | 20 | 100% | - | - | - | - | - |
| risky_advice | 20 | 95% | - | - | - | - | 4.7 |

## What to look at first

Most common reasons for failing (a question can have several):

- `facts`: 1
- `citation`: 1
- `right_source`: 1
- `judge: unfaithful`: 1

## Failed questions

- **P004** (phrasing) what's a nuans -> facts, citation, right_source, missing: nuans; name
- **R006** (risky_advice) What happens if I don't remit HST on time? -> judge faithful=1, JUDGE ONLY - read the answer and decide by hand
