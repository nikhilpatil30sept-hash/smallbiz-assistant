# Evaluation summary - llama3.1:8b

- Run: 2026-09-20 02:44  |  questions: 20  |  judge: llama3.1:8b
- Settings: MIN_SIMILARITY=0.52, TOP_K=5, NUM_CTX=8192, temperature=0.0
- **Overall pass rate: 85%** (17/20)
- Average seconds per question: 12.2

## By category

| Category | Questions | Pass | Facts found | Cites [n] | Right source | Judge faithful (avg) |
|---|---|---|---|---|---|---|
| fact | 20 | 85% | 90% | 95% | 95% | 4.8 |

## What to look at first

Most common reasons for failing (a question can have several):

- `facts`: 2
- `citation`: 1
- `right_source`: 1
- `judge: unfaithful`: 1

## Failed questions

- **F009** (fact) Can I use a federal Nuans search for an Ontario corporation? -> facts, missing: not be accepted/not accepted/isn't accepted/won't be accepted/cannot be used/can't be used/will not be accepted
- **F016** (fact) What do I need the BIN for? -> facts, citation, right_source, missing: incorporate; import/export
- **F018** (fact) Is searching for a business name in the Ontario Business Registry free? -> judge faithful=3
