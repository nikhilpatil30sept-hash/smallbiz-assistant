# Evaluation summary - llama3.1:8b

- Run: 2026-09-20 03:07  |  questions: 206  |  judge: llama3.1:8b
- Settings: MIN_SIMILARITY=0.52, TOP_K=5, NUM_CTX=8192, temperature=0.0
- **Overall pass rate: 74%** (152/206)
- Average seconds per question: 16.0

## By category

| Category | Questions | Pass | Facts found | Cites [n] | Right source | Judge faithful (avg) |
|---|---|---|---|---|---|---|
| fact | 80 | 82% | 91% | 99% | 91% | 4.9 |
| phrasing | 6 | 83% | 100% | 100% | 100% | 4.5 |
| process | 12 | 67% | 67% | 92% | 83% | 4.7 |
| followup | 15 | 80% | 93% | 100% | 93% | 4.7 |
| not_in_kb | 35 | 60% | - | - | - | 4.1 |
| off_topic | 20 | 70% | - | - | - | - |
| risky_advice | 20 | 80% | - | - | - | 4.3 |
| false_premise | 18 | 56% | 89% | 100% | 94% | 4.5 |

## What to look at first

Most common reasons for failing (a question can have several):

- `judge: unfaithful`: 19
- `facts`: 14
- `right_source`: 11
- `hedged`: 6
- `declined`: 6
- `no_sources`: 6
- `no_forbidden`: 3
- `citation`: 2
- `short`: 2
- `refers_to_professional`: 2

## Failed questions

- **F002** (fact) How many consecutive calendar quarters does the HST revenue test look at? -> facts, missing: four
- **F018** (fact) Is searching for a business name in the Ontario Business Registry free? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **F022** (fact) What are the four types of business structures in Ontario? -> facts, missing: sole proprietorship; partnership; corporation; co-operative/cooperative
- **F023** (fact) What is the easiest and most common way to start a business in Ontario? -> right_source
- **F031** (fact) What is a co-operative? -> facts, missing: one member/democratic/vote
- **F038** (fact) Which levels of government might require licences or permits for my business? -> facts, missing: federal; provincial; municipal
- **F048** (fact) What is Starter Company Plus? -> facts, missing: training/mentoring/grant
- **F055** (fact) What is Digital Main Street? -> facts, citation, right_source, missing: programs/funding
- **F066** (fact) What are the six steps to starting a business on Canada.ca? -> facts, missing: planning; name; financing/support; tax, judge faithful=3
- **F076** (fact) Why can a profitable business still run out of cash? -> right_source
- **F077** (fact) How do I work out my break-even point? -> right_source
- **F078** (fact) How big a cash buffer should I keep? -> right_source
- **F079** (fact) How do I build a 12-month cash forecast? -> right_source
- **F080** (fact) What can I do to improve my cash flow? -> right_source
- **P002** (phrasing) how much 2 register sole prop in ontario -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **S002** (process) I'm a freelance designer. What do I need to do to set up as a sole proprietor? -> facts, missing: CPP/personal income
- **S008** (process) What should I sort out before I hire my first employee in Ontario? -> facts, right_source, missing: employment standards/Employer Health Tax/health and safety
- **S011** (process) Give me a checklist for launching a coffee shop in Ontario. -> facts, missing: licences/permits; insurance
- **S012** (process) What costs should I plan for when starting a business? -> facts, citation, right_source, missing: registration; insurance; rent/marketing/licensing
- **U001** (followup) Yes, I made $35,000 over the last four quarters. What should I do next? -> facts, missing: 30,000/threshold
- **U006** (followup) And is checking availability free? -> right_source
- **U008** (followup) Is there any loan for me? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **N003** (not_in_kb) What is WSIB and do I need to register? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **N004** (not_in_kb) How do I trademark my business name? -> hedged, judge faithful=3
- **N005** (not_in_kb) What food handler certification does a bakery need? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **N006** (not_in_kb) Do I need a health inspection to open a restaurant? -> hedged
- **N007** (not_in_kb) What is the difference between cash and accrual accounting? -> hedged
- **N011** (not_in_kb) When is my corporate tax return due? -> hedged
- **N013** (not_in_kb) What is the current HST rate in Ontario? -> hedged
- **N015** (not_in_kb) What is the difference between an employee and an independent contractor? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **N018** (not_in_kb) Can I raise money for my business through crowdfunding? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **N023** (not_in_kb) What permits does a food truck need in Toronto? -> hedged
- **N026** (not_in_kb) How do I apply for a bank loan for my business? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **N031** (not_in_kb) How do I register for payroll deductions with the CRA? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **N033** (not_in_kb) What is the small business exemption amount for Employer Health Tax? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **N035** (not_in_kb) What software can I use to build a website for my business? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
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
- **X004** (false_premise) Sole proprietors must incorporate within a year, right? -> no_forbidden, forbidden: must incorporate within
- **X007** (false_premise) Partners are only responsible for their own share of the debts, right? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **X009** (false_premise) There are only two business structures in Ontario, sole proprietorship and corporation. -> facts, missing: partnership, judge faithful=3
- **X010** (false_premise) Do I only pay into the CPP if I have employees? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **X011** (false_premise) Futurpreneur gives side-business loans up to $1 million, correct? -> no_forbidden, forbidden: 1 million
- **X012** (false_premise) There are 100 Small Business Enterprise Centres in Ontario, right? -> no_forbidden, forbidden: 100 Small Business
- **X015** (false_premise) I can start the four-quarter HST count in any month I like, right? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **X018** (false_premise) Corporations in Ontario never have to file annual paperwork, do they? -> facts, right_source, missing: annual filings/filings/records
