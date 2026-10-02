# Evaluation summary - smallbiz-assistant-lora

- Run: 2026-09-28 22:49  |  questions: 216  |  judge: smallbiz-assistant-lora
- Settings: MIN_SIMILARITY=0.52, TOP_K=5, NUM_CTX=8192, temperature=0.0
- **Overall pass rate: 95%** (206/216)
- Average seconds per question: 27.7

## By category

| Category | Questions | Pass | Facts found | Cites [n] | Valid [n] | Right source | Numbers OK | Judge faithful (avg, informational) |
|---|---|---|---|---|---|---|---|---|
| fact | 87 | 98% | 98% | 100% | 100% | 100% | 100% | 4.7 |
| phrasing | 10 | 100% | 100% | 100% | 100% | 100% | 100% | 4.6 |
| process | 12 | 67% | 67% | 100% | 100% | 83% | 100% | 4.2 |
| followup | 15 | 80% | 87% | 100% | 100% | 93% | 93% | 4.4 |
| not_in_kb | 34 | 100% | - | - | - | - | - | 3.4 |
| off_topic | 20 | 100% | - | - | - | - | - | - |
| risky_advice | 20 | 100% | - | - | - | - | 100% | 3.6 |
| false_premise | 18 | 94% | 94% | 100% | 100% | 94% | 100% | 4.6 |

## What to look at first

Pass/fail below comes only from the rule checks (facts, citations, right source, numbers supported by the sources, hedged/declined/referred wording, no forbidden claims). The local-model judge no longer decides pass/fail - it flagged several correct answers as unfaithful across two runs, so its score is informational only; see 'Judge flagged, but passed' below to spot-check it by hand.

Most common reasons for failing (a question can have several):

- `facts`: 9
- `right_source`: 4
- `numbers_supported`: 1

## Failed questions

- **F080** (fact) What can I do to improve my cash flow? -> facts, missing: invoice
- **F083** (fact) How much vacation pay do I owe an employee who has worked less than five years? -> facts, missing: 2 weeks/two weeks
- **S001** (process) I want to start a small bakery in Ontario. What are the first steps? -> facts, missing: register
- **S002** (process) I'm a freelance designer. What do I need to do to set up as a sole proprietor? -> facts, missing: CPP/personal income
- **S008** (process) What should I sort out before I hire my first employee in Ontario? -> facts, right_source, missing: employment standards/Employer Health Tax/health and safety
- **S012** (process) What costs should I plan for when starting a business? -> facts, right_source, missing: registration; insurance; rent/marketing/licensing
- **U001** (followup) Yes, I made $35,000 over the last four quarters. What should I do next? -> facts, numbers_supported, missing: register/GST/HST account; 30,000/threshold, invented numbers: $35,000
- **U006** (followup) And is checking availability free? -> right_source
- **U015** (followup) How do I get a GST/HST number? -> facts, missing: Business Registration Online/BRO
- **X018** (false_premise) Corporations in Ontario never have to file annual paperwork, do they? -> facts, right_source, missing: annual filings/filings/records

## Judge flagged, but passed (informational - spot-check these by hand)

- **F008** (fact) faithful=3 Do I need a Nuans report to register a corporation in Ontario?
- **F029** (fact) faithful=3 Is my business name protected if I incorporate federally?
- **F046** (fact) faithful=3 Do I need to register for Employer Health Tax?
- **F048** (fact) faithful=3 What is Starter Company Plus?
- **F051** (fact) faithful=3 What is the Summer Company program?
- **F061** (fact) faithful=3 What start-up costs should I research?
- **F066** (fact) faithful=3 What are the six steps to starting a business on Canada.ca?
- **F071** (fact) faithful=3 What federal support is there for small businesses in Southern Ontario?
- **P008** (phrasing) faithful=3 futurpreneur??
- **U004** (followup) faithful=3 Which one protects my personal assets?
- **N001** (not_in_kb) faithful=3 What is the minimum wage in Ontario?
- **N006** (not_in_kb) faithful=3 What is the difference between cash and accrual accounting?
- **N008** (not_in_kb) faithful=3 How do I write a marketing plan?
- **N009** (not_in_kb) faithful=3 How can I get more customers using social media?
- **N010** (not_in_kb) faithful=1 When is my corporate tax return due?
- **N011** (not_in_kb) faithful=3 How often do I have to file my HST return?
- **N012** (not_in_kb) faithful=3 What is the current HST rate in Ontario?
- **N013** (not_in_kb) faithful=3 How do I set up payroll for my first employee?
- **N014** (not_in_kb) faithful=1 What is the difference between an employee and an independent contractor?
- **N015** (not_in_kb) faithful=3 How do I negotiate a commercial lease?
- **N017** (not_in_kb) faithful=3 Can I raise money for my business through crowdfunding?
- **N019** (not_in_kb) faithful=3 How much does it cost to incorporate federally?
- **N020** (not_in_kb) faithful=3 Do I need a separate business bank account?
- **N021** (not_in_kb) faithful=3 How do I set up an online store and collect sales tax?
- **N024** (not_in_kb) faithful=3 What should go in a partnership agreement?
- **N025** (not_in_kb) faithful=3 How do I apply for a bank loan for my business?
- **N026** (not_in_kb) faithful=3 How much should I charge as a freelancer?
- **N027** (not_in_kb) faithful=3 How do I export my products to the United States?
- **N028** (not_in_kb) faithful=3 How do I close down my business properly?
- **N029** (not_in_kb) faithful=3 What are good ways to advertise a new local business?
- ... and 19 more (see results.csv, judge_faithful column)
