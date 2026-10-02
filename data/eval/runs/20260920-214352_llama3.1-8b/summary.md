# Evaluation summary - llama3.1:8b

- Run: 2026-09-20 21:43  |  questions: 30  |  judge: llama3.1:8b
- Settings: MIN_SIMILARITY=0.52, TOP_K=5, NUM_CTX=8192, temperature=0.0
- **Overall pass rate: 93%** (28/30)
- Average seconds per question: 3.6

## By category

| Category | Questions | Pass | Facts found | Cites [n] | Valid [n] | Right source | Judge faithful (avg) |
|---|---|---|---|---|---|---|---|
| phrasing | 10 | 80% | 80% | 90% | 100% | 90% | 4.9 |
| off_topic | 20 | 100% | - | - | - | - | - |

## What to look at first

Most common reasons for failing (a question can have several):

- `facts`: 2
- `citation`: 1
- `right_source`: 1

## Failed questions

- **P008** (phrasing) futurpreneur?? -> facts, missing: loan
- **P010** (phrasing) digital main street -> facts, citation, right_source, missing: programs/funding
