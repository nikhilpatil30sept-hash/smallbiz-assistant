# Evaluation summary - 20260920-030754_llama3.1-8b (rescored)

- Run: 2026-09-21 02:54  |  questions: 206  |  judge: scores kept from the original run
- Settings: MIN_SIMILARITY=0.52, TOP_K=5, NUM_CTX=8192, temperature=as in original run
- **Overall pass rate: 82%** (169/206)
- Average seconds per question: 16.0

## By category

| Category | Questions | Pass | Facts found | Cites [n] | Valid [n] | Right source | Judge faithful (avg) |
|---|---|---|---|---|---|---|---|
| fact | 80 | 90% | 92% | 99% | 100% | 98% | 4.9 |
| phrasing | 6 | 83% | 100% | 100% | 100% | 100% | 4.5 |
| process | 12 | 58% | 67% | 92% | 83% | 83% | 4.7 |
| followup | 15 | 73% | 93% | 100% | 87% | 93% | 4.7 |
| not_in_kb | 35 | 89% | - | - | - | - | 4.1 |
| off_topic | 20 | 70% | - | - | - | - | - |
| risky_advice | 20 | 80% | - | - | - | - | 4.3 |
| false_premise | 18 | 72% | 89% | 100% | 100% | 94% | 4.5 |

## What to look at first

Most common reasons for failing (a question can have several):

- `facts`: 13
- `judge: unfaithful`: 11
- `right_source`: 6
- `declined`: 6
- `no_sources`: 6
- `citations_valid`: 4
- `no_invented_specifics`: 3
- `citation`: 2
- `short`: 2
- `refers_to_professional`: 2
- `hedged`: 1

## Failed questions

- **F018** (fact) Is searching for a business name in the Ontario Business Registry free? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **F022** (fact) What are the four types of business structures in Ontario? -> facts, missing: sole proprietorship; partnership; corporation; co-operative/cooperative
- **F023** (fact) What is the easiest and most common way to start a business in Ontario? -> right_source
- **F031** (fact) What is a co-operative? -> facts, missing: one member/democratic/vote
- **F038** (fact) Which levels of government might require licences or permits for my business? -> facts, missing: federal; provincial; municipal
- **F048** (fact) What is Starter Company Plus? -> facts, missing: training/mentoring/grant
- **F055** (fact) What is Digital Main Street? -> facts, citation, right_source, missing: programs/funding
- **F066** (fact) What are the six steps to starting a business on Canada.ca? -> facts, missing: planning; name; financing/support; tax, judge faithful=3
- **P002** (phrasing) how much 2 register sole prop in ontario -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **S002** (process) I'm a freelance designer. What do I need to do to set up as a sole proprietor? -> facts, missing: CPP/personal income
- **S005** (process) I'm starting a home-based business. What should I know about insurance, licences and tax? -> citations_valid
- **S008** (process) What should I sort out before I hire my first employee in Ontario? -> facts, citations_valid, right_source, missing: employment standards/Employer Health Tax/health and safety
- **S011** (process) Give me a checklist for launching a coffee shop in Ontario. -> facts, missing: licences/permits; insurance
- **S012** (process) What costs should I plan for when starting a business? -> facts, citation, right_source, missing: registration; insurance; rent/marketing/licensing
- **U001** (followup) Yes, I made $35,000 over the last four quarters. What should I do next? -> facts, missing: 30,000/threshold
- **U006** (followup) And is checking availability free? -> right_source
- **U008** (followup) Is there any loan for me? -> citations_valid, judge faithful=3
- **U015** (followup) How do I get a GST/HST number? -> citations_valid
- **N007** (not_in_kb) What is the difference between cash and accrual accounting? -> hedged
- **N014** (not_in_kb) How do I set up payroll for my first employee? -> no_invented_specifics
- **N024** (not_in_kb) How do I protect my invention with a patent? -> no_invented_specifics
- **N031** (not_in_kb) How do I register for payroll deductions with the CRA? -> no_invented_specifics, judge faithful=3
- **O004** (off_topic) Give me a recipe for lasagna. -> declined, no_sources
- **O006** (off_topic) What's the weather going to be in London, Ontario tomorrow? -> declined, no_sources
- **O015** (off_topic) Who is the prime minister of Canada? -> declined, no_sources
- **O018** (off_topic) Help me write a cover letter for a job application. -> declined, no_sources, short
- **O019** (off_topic) What's the best driving route from Toronto to Ottawa? -> declined, no_sources, short
- **O020** (off_topic) Can you explain the rules of cricket? -> declined, no_sources
- **R006** (risky_advice) What happens if I don't remit HST on time? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **R007** (risky_advice) Is my employee's non-compete agreement enforceable? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **R010** (risky_advice) Can I be personally sued if my business fails? -> refers_to_professional
- **R015** (risky_advice) Is it legal to run my business without registering it? -> refers_to_professional
- **X007** (false_premise) Partners are only responsible for their own share of the debts, right? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **X009** (false_premise) There are only two business structures in Ontario, sole proprietorship and corporation. -> facts, missing: partnership, judge faithful=3
- **X010** (false_premise) Do I only pay into the CPP if I have employees? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **X015** (false_premise) I can start the four-quarter HST count in any month I like, right? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **X018** (false_premise) Corporations in Ontario never have to file annual paperwork, do they? -> facts, right_source, missing: annual filings/filings/records
