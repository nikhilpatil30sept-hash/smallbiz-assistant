# Evaluation summary - llama3.1:8b

- Run: 2026-09-20 23:04  |  questions: 65  |  judge: llama3.1:8b
- Settings: MIN_SIMILARITY=0.52, TOP_K=5, NUM_CTX=8192, temperature=0.0
- **Overall pass rate: 98%** (64/65)
- Average seconds per question: 9.7

## By category

| Category | Questions | Pass | Facts found | Cites [n] | Valid [n] | Right source | Judge faithful (avg) |
|---|---|---|---|---|---|---|---|
| phrasing | 10 | 90% | 90% | 90% | 100% | 90% | 4.9 |
| not_in_kb | 35 | 100% | - | - | - | - | 4.5 |
| off_topic | 20 | 100% | - | - | - | - | - |

## What to look at first

Most common reasons for failing (a question can have several):

- `facts`: 1
- `citation`: 1
- `right_source`: 1

## Failed questions

- **P010** (phrasing) digital main street -> facts, citation, right_source, missing: programs/funding
