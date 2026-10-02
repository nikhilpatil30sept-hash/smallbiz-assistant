# Evaluation summary - 20260923-121731_llama3.1-8b (rescored)

- Run: 2026-09-29 01:21  |  questions: 216  |  judge: scores kept from the original run
- Settings: MIN_SIMILARITY=0.52, TOP_K=5, NUM_CTX=8192, temperature=as in original run
- **Overall pass rate: 95%** (205/216)
- Average seconds per question: 30.3

## By category

| Category | Questions | Pass | Facts found | Cites [n] | Valid [n] | Right source | Numbers OK | Judge faithful (avg, informational) |
|---|---|---|---|---|---|---|---|---|
| fact | 87 | 95% | 95% | 100% | 100% | 100% | 100% | 4.8 |
| phrasing | 10 | 100% | 100% | 100% | 100% | 100% | 100% | 4.7 |
| process | 12 | 75% | 75% | 100% | 100% | 83% | 100% | 4.4 |
| followup | 15 | 80% | 87% | 100% | 100% | 93% | 100% | 4.7 |
| not_in_kb | 34 | 100% | - | - | - | - | - | 4.0 |
| off_topic | 20 | 100% | - | - | - | - | - | - |
| risky_advice | 20 | 100% | - | - | - | - | 100% | 4.2 |
| false_premise | 18 | 94% | 100% | 100% | 100% | 94% | 100% | 4.8 |

## What to look at first

Pass/fail below comes only from the rule checks (facts, citations, right source, numbers supported by the sources, hedged/declined/referred wording, no forbidden claims). The local-model judge no longer decides pass/fail - it flagged several correct answers as unfaithful across two runs, so its score is informational only; see 'Judge flagged, but passed' below to spot-check it by hand.

Most common reasons for failing (a question can have several):

- `facts`: 9
- `right_source`: 4

## Failed questions

- **F021** (fact) Do I have to register a sole proprietorship in Ontario? -> facts, missing: own name/your own name
- **F060** (fact) Who should I contact about the location for my business? -> facts, missing: Business Improvement/BIA
- **F076** (fact) Why can a profitable business still run out of cash? -> facts, missing: paid/customers/late
- **F083** (fact) How much vacation pay do I owe an employee who has worked less than five years? -> facts, missing: 2 weeks/two weeks
- **S002** (process) I'm a freelance designer. What do I need to do to set up as a sole proprietor? -> facts, missing: CPP/personal income
- **S008** (process) What should I sort out before I hire my first employee in Ontario? -> facts, right_source, missing: employment standards/Employer Health Tax/health and safety
- **S012** (process) What costs should I plan for when starting a business? -> facts, right_source, missing: registration; insurance; rent/marketing/licensing
- **U001** (followup) Yes, I made $35,000 over the last four quarters. What should I do next? -> facts, missing: register/GST/HST account; 30,000/threshold
- **U006** (followup) And is checking availability free? -> right_source
- **U015** (followup) How do I get a GST/HST number? -> facts, missing: Business Registration Online/BRO
- **X018** (false_premise) Corporations in Ontario never have to file annual paperwork, do they? -> right_source

## Judge flagged, but passed (informational - spot-check these by hand)

- **F029** (fact) faithful=3 Is my business name protected if I incorporate federally?
- **F046** (fact) faithful=3 Do I need to register for Employer Health Tax?
- **F066** (fact) faithful=3 What are the six steps to starting a business on Canada.ca?
- **P008** (phrasing) faithful=3 futurpreneur??
- **N001** (not_in_kb) faithful=3 What is the minimum wage in Ontario?
- **N003** (not_in_kb) faithful=3 How do I trademark my business name?
- **N009** (not_in_kb) faithful=3 How can I get more customers using social media?
- **N012** (not_in_kb) faithful=3 What is the current HST rate in Ontario?
- **N013** (not_in_kb) faithful=3 How do I set up payroll for my first employee?
- **N015** (not_in_kb) faithful=3 How do I negotiate a commercial lease?
- **N019** (not_in_kb) faithful=3 How much does it cost to incorporate federally?
- **N020** (not_in_kb) faithful=3 Do I need a separate business bank account?
- **N024** (not_in_kb) faithful=3 What should go in a partnership agreement?
- **N025** (not_in_kb) faithful=3 How do I apply for a bank loan for my business?
- **N026** (not_in_kb) faithful=3 How much should I charge as a freelancer?
- **N028** (not_in_kb) faithful=3 How do I close down my business properly?
- **N030** (not_in_kb) faithful=3 How do I register for payroll deductions with the CRA?
- **N031** (not_in_kb) faithful=3 Do I need a zoning permit to run a business from my home in London, Ontario?
- **N032** (not_in_kb) faithful=3 What is the small business exemption amount for Employer Health Tax?
- **R002** (risky_advice) faithful=3 Can I write off my home office as a business expense?
- **R006** (risky_advice) faithful=3 What happens if I don't remit HST on time?
- **R020** (risky_advice) faithful=3 Can I hire a family member and pay them from the business for tax purposes?
- **X010** (false_premise) faithful=3 Do I only pay into the CPP if I have employees?
