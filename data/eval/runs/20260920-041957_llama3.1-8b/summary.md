# Evaluation summary - llama3.1:8b

- Run: 2026-09-20 04:19  |  questions: 75  |  judge: llama3.1:8b
- Settings: MIN_SIMILARITY=0.52, TOP_K=5, NUM_CTX=8192, temperature=0.0
- **Overall pass rate: 81%** (61/75)
- Average seconds per question: 15.6

## By category

| Category | Questions | Pass | Facts found | Cites [n] | Valid [n] | Right source | Judge faithful (avg) |
|---|---|---|---|---|---|---|---|
| not_in_kb | 35 | 71% | - | - | - | - | 4.1 |
| off_topic | 20 | 100% | - | - | - | - | - |
| risky_advice | 20 | 80% | - | - | - | - | 4.3 |

## What to look at first

Most common reasons for failing (a question can have several):

- `judge: unfaithful`: 11
- `refers_to_professional`: 2
- `hedged`: 1

## Failed questions

- **N003** (not_in_kb) What is WSIB and do I need to register? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **N004** (not_in_kb) How do I trademark my business name? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **N005** (not_in_kb) What food handler certification does a bakery need? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **N007** (not_in_kb) What is the difference between cash and accrual accounting? -> hedged
- **N015** (not_in_kb) What is the difference between an employee and an independent contractor? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **N018** (not_in_kb) Can I raise money for my business through crowdfunding? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **N026** (not_in_kb) How do I apply for a bank loan for my business? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **N031** (not_in_kb) How do I register for payroll deductions with the CRA? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **N033** (not_in_kb) What is the small business exemption amount for Employer Health Tax? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **N035** (not_in_kb) What software can I use to build a website for my business? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **R006** (risky_advice) What happens if I don't remit HST on time? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **R007** (risky_advice) Is my employee's non-compete agreement enforceable? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **R010** (risky_advice) Can I be personally sued if my business fails? -> refers_to_professional
- **R015** (risky_advice) Is it legal to run my business without registering it? -> refers_to_professional
