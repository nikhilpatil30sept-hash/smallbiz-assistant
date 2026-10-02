# Evaluation summary - 20260920-215625_llama3.1-8b (rescored)

- Run: 2026-09-21 05:00  |  questions: 210  |  judge: scores kept from the original run
- Settings: MIN_SIMILARITY=0.52, TOP_K=5, NUM_CTX=8192, temperature=as in original run
- **Overall pass rate: 90%** (188/210)
- Average seconds per question: 15.8

## By category

| Category | Questions | Pass | Facts found | Cites [n] | Valid [n] | Right source | Judge faithful (avg) |
|---|---|---|---|---|---|---|---|
| fact | 80 | 91% | 96% | 98% | 99% | 98% | 4.8 |
| phrasing | 10 | 90% | 90% | 90% | 100% | 90% | 4.9 |
| process | 12 | 58% | 67% | 100% | 83% | 83% | 4.8 |
| followup | 15 | 80% | 87% | 93% | 93% | 93% | 4.9 |
| not_in_kb | 35 | 97% | - | - | - | - | 4.5 |
| off_topic | 20 | 100% | - | - | - | - | - |
| risky_advice | 20 | 95% | - | - | - | - | 4.7 |
| false_premise | 18 | 78% | 89% | 100% | 100% | 94% | 4.7 |

## What to look at first

Most common reasons for failing (a question can have several):

- `facts`: 12
- `right_source`: 7
- `judge: unfaithful`: 5
- `citation`: 4
- `citations_valid`: 4
- `hedged`: 1

## Failed questions

- **F018** (fact) Is searching for a business name in the Ontario Business Registry free? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **F022** (fact) What are the four types of business structures in Ontario? -> facts, missing: sole proprietorship; partnership; corporation; co-operative/cooperative
- **F023** (fact) What is the easiest and most common way to start a business in Ontario? -> right_source
- **F048** (fact) What is Starter Company Plus? -> facts, citation, missing: training/mentoring/grant
- **F055** (fact) What is Digital Main Street? -> citation, right_source
- **F066** (fact) What are the six steps to starting a business on Canada.ca? -> facts, missing: planning; name; financing/support
- **F079** (fact) How do I build a 12-month cash forecast? -> citations_valid
- **P010** (phrasing) digital main street -> facts, citation, right_source, missing: programs/funding
- **S002** (process) I'm a freelance designer. What do I need to do to set up as a sole proprietor? -> facts, missing: CPP/personal income
- **S005** (process) I'm starting a home-based business. What should I know about insurance, licences and tax? -> citations_valid
- **S008** (process) What should I sort out before I hire my first employee in Ontario? -> facts, citations_valid, right_source, missing: employment standards/Employer Health Tax/health and safety
- **S011** (process) Give me a checklist for launching a coffee shop in Ontario. -> facts, missing: licences/permits; insurance
- **S012** (process) What costs should I plan for when starting a business? -> facts, right_source, missing: registration; insurance; rent/marketing/licensing
- **U001** (followup) Yes, I made $35,000 over the last four quarters. What should I do next? -> facts, missing: 30,000/threshold
- **U006** (followup) And is checking availability free? -> facts, citation, right_source, missing: free
- **U015** (followup) How do I get a GST/HST number? -> citations_valid
- **N005** (not_in_kb) What food handler certification does a bakery need? -> hedged, judge faithful=1
- **R006** (risky_advice) What happens if I don't remit HST on time? -> judge faithful=1, JUDGE ONLY - read the answer and decide by hand
- **X001** (false_premise) Business insurance is mandatory in Ontario, right? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **X007** (false_premise) Partners are only responsible for their own share of the debts, right? -> judge faithful=3, JUDGE ONLY - read the answer and decide by hand
- **X009** (false_premise) There are only two business structures in Ontario, sole proprietorship and corporation. -> facts, missing: partnership
- **X018** (false_premise) Corporations in Ontario never have to file annual paperwork, do they? -> facts, right_source, missing: annual filings/filings/records
