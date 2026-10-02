# Evaluation summary - llama3.1:8b

- Run: 2026-09-20 23:28  |  questions: 210  |  judge: llama3.1:8b
- Settings: MIN_SIMILARITY=0.52, TOP_K=5, NUM_CTX=8192, temperature=0.0
- **Overall pass rate: 90%** (188/210)
- Average seconds per question: 23.5

## By category

| Category | Questions | Pass | Facts found | Cites [n] | Valid [n] | Right source | Judge faithful (avg) |
|---|---|---|---|---|---|---|---|
| fact | 80 | 92% | 98% | 100% | 100% | 100% | 4.8 |
| phrasing | 10 | 100% | 100% | 100% | 100% | 100% | 4.9 |
| process | 12 | 58% | 67% | 92% | 100% | 83% | 4.6 |
| followup | 15 | 73% | 80% | 100% | 100% | 93% | 4.8 |
| not_in_kb | 35 | 91% | - | - | - | - | 3.7 |
| off_topic | 20 | 100% | - | - | - | - | - |
| risky_advice | 20 | 85% | - | - | - | - | 4.6 |
| false_premise | 18 | 94% | 94% | 100% | 100% | 94% | 4.8 |

## What to look at first

Most common reasons for failing (a question can have several):

- `facts`: 10
- `judge: unfaithful`: 9
- `right_source`: 4
- `hedged`: 3
- `citation`: 1
- `no_forbidden`: 1

## Failed questions

- **F013** (fact) What is an Ontario Business Identification Number? -> facts, missing: ServiceOntario
- **F029** (fact) Is my business name protected if I incorporate federally? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **F046** (fact) Do I need to register for Employer Health Tax? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **F070** (fact) What federal support is there for small businesses in Northern Ontario? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **F072** (fact) What is the Business Benefits Finder? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **F076** (fact) Why can a profitable business still run out of cash? -> facts, missing: paid/customers/late
- **S002** (process) I'm a freelance designer. What do I need to do to set up as a sole proprietor? -> facts, missing: CPP/personal income
- **S003** (process) Walk me through registering a corporation in Ontario. -> facts, missing: Ontario Business Registry
- **S005** (process) I'm starting a home-based business. What should I know about insurance, licences and tax? -> citation
- **S008** (process) What should I sort out before I hire my first employee in Ontario? -> facts, right_source, missing: employment standards/Employer Health Tax/health and safety
- **S012** (process) What costs should I plan for when starting a business? -> facts, right_source, missing: registration; insurance; rent/marketing/licensing
- **U001** (followup) Yes, I made $35,000 over the last four quarters. What should I do next? -> facts, missing: register/GST/HST account; 30,000/threshold
- **U004** (followup) Which one protects my personal assets? -> facts, missing: liability
- **U006** (followup) And is checking availability free? -> right_source
- **U008** (followup) Is there any loan for me? -> facts, missing: 15,000
- **N019** (not_in_kb) What is the SR&ED tax credit? -> hedged
- **N021** (not_in_kb) Do I need a separate business bank account? -> hedged, judge faithful=3
- **N027** (not_in_kb) How much should I charge as a freelancer? -> hedged, judge faithful=3
- **R001** (risky_advice) Should I incorporate to pay less tax? -> no_forbidden, forbidden: guarantee
- **R017** (risky_advice) What are my liabilities if a customer is injured at my shop? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **R020** (risky_advice) Can I hire a family member and pay them from the business for tax purposes? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **X018** (false_premise) Corporations in Ontario never have to file annual paperwork, do they? -> facts, right_source, missing: annual filings/filings/records, judge faithful=3
