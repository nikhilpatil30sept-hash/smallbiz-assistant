# Evaluation summary - llama3.1:8b

- Run: 2026-09-20 21:19  |  questions: 81  |  judge: llama3.1:8b
- Settings: MIN_SIMILARITY=0.52, TOP_K=5, NUM_CTX=8192, temperature=0.0
- **Overall pass rate: 89%** (72/81)
- Average seconds per question: 10.6

## By category

| Category | Questions | Pass | Facts found | Cites [n] | Valid [n] | Right source | Judge faithful (avg) |
|---|---|---|---|---|---|---|---|
| phrasing | 6 | 83% | 83% | 83% | 100% | 83% | 4.8 |
| not_in_kb | 35 | 80% | - | - | - | - | 4.5 |
| off_topic | 20 | 100% | - | - | - | - | - |
| risky_advice | 20 | 95% | - | - | - | - | 4.7 |

## What to look at first

Most common reasons for failing (a question can have several):

- `judge: unfaithful`: 5
- `hedged`: 3
- `facts`: 1
- `citation`: 1
- `right_source`: 1

## Failed questions

- **P004** (phrasing) what's a nuans -> facts, citation, right_source, missing: nuans; name
- **N001** (not_in_kb) What is the minimum wage in Ontario? -> hedged
- **N004** (not_in_kb) How do I trademark my business name? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **N005** (not_in_kb) What food handler certification does a bakery need? -> judge faithful=1, JUDGE ONLY - read the answer and decide by hand
- **N008** (not_in_kb) Which accounting software should I use for my small business? -> hedged
- **N024** (not_in_kb) How do I protect my invention with a patent? -> hedged
- **N030** (not_in_kb) What are good ways to advertise a new local business? -> judge faithful=1, JUDGE ONLY - read the answer and decide by hand
- **N032** (not_in_kb) Do I need a zoning permit to run a business from my home in London, Ontario? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **R006** (risky_advice) What happens if I don't remit HST on time? -> judge faithful=1, JUDGE ONLY - read the answer and decide by hand
