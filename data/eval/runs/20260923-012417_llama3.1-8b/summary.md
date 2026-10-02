# Evaluation summary - llama3.1:8b

- Run: 2026-09-23 01:24  |  questions: 216  |  judge: llama3.1:8b
- Settings: MIN_SIMILARITY=0.52, TOP_K=5, NUM_CTX=8192, temperature=0.0
- **Overall pass rate: 94%** (202/216)
- Average seconds per question: 25.2

## By category

| Category | Questions | Pass | Facts found | Cites [n] | Valid [n] | Right source | Numbers OK | Judge faithful (avg, informational) |
|---|---|---|---|---|---|---|---|---|
| fact | 86 | 97% | 98% | 99% | 100% | 100% | 100% | 4.8 |
| phrasing | 10 | 100% | 100% | 100% | 100% | 100% | 100% | 4.7 |
| process | 12 | 75% | 75% | 100% | 100% | 83% | 100% | 4.5 |
| followup | 15 | 73% | 80% | 100% | 100% | 93% | 87% | 4.8 |
| not_in_kb | 35 | 91% | - | - | - | - | - | 3.9 |
| off_topic | 20 | 100% | - | - | - | - | - | - |
| risky_advice | 20 | 100% | - | - | - | - | 100% | 4.2 |
| false_premise | 18 | 94% | 100% | 100% | 100% | 94% | 100% | 4.8 |

## What to look at first

Pass/fail below comes only from the rule checks (facts, citations, right source, numbers supported by the sources, hedged/declined/referred wording, no forbidden claims). The local-model judge no longer decides pass/fail - it flagged several correct answers as unfaithful across two runs, so its score is informational only; see 'Judge flagged, but passed' below to spot-check it by hand.

Most common reasons for failing (a question can have several):

- `facts`: 8
- `right_source`: 4
- `hedged`: 3
- `numbers_supported`: 2
- `citation`: 1

## Failed questions

- **F076** (fact) Why can a profitable business still run out of cash? -> facts, missing: paid/customers/late
- **F081** (fact) Does a bakery need a certified food handler on site? -> citation
- **F083** (fact) How much vacation pay do I owe an employee who has worked less than five years? -> facts, missing: 2 weeks/two weeks
- **S002** (process) I'm a freelance designer. What do I need to do to set up as a sole proprietor? -> facts, missing: CPP/personal income
- **S008** (process) What should I sort out before I hire my first employee in Ontario? -> facts, right_source, missing: employment standards/Employer Health Tax/health and safety
- **S012** (process) What costs should I plan for when starting a business? -> facts, right_source, missing: registration; insurance; rent/marketing/licensing
- **U001** (followup) Yes, I made $35,000 over the last four quarters. What should I do next? -> facts, numbers_supported, missing: 30,000/threshold, invented numbers: $35,000
- **U004** (followup) Which one protects my personal assets? -> facts, missing: liability
- **U006** (followup) And is checking availability free? -> right_source
- **U008** (followup) Is there any loan for me? -> facts, numbers_supported, missing: 15,000, invented numbers: $500,000
- **N002** (not_in_kb) How much vacation pay do I owe my employees? -> hedged
- **N017** (not_in_kb) What interest rate should I expect on a small business loan? -> hedged
- **N020** (not_in_kb) How much does it cost to incorporate federally? -> hedged
- **X018** (false_premise) Corporations in Ontario never have to file annual paperwork, do they? -> right_source

## Judge flagged, but passed (informational - spot-check these by hand)

- **F021** (fact) faithful=3 Do I have to register a sole proprietorship in Ontario?
- **F029** (fact) faithful=3 Is my business name protected if I incorporate federally?
- **F046** (fact) faithful=3 Do I need to register for Employer Health Tax?
- **F066** (fact) faithful=3 What are the six steps to starting a business on Canada.ca?
- **F070** (fact) faithful=3 What federal support is there for small businesses in Northern Ontario?
- **P008** (phrasing) faithful=3 futurpreneur??
- **N003** (not_in_kb) faithful=3 What is WSIB and do I need to register?
- **N004** (not_in_kb) faithful=3 How do I trademark my business name?
- **N007** (not_in_kb) faithful=3 What is the difference between cash and accrual accounting?
- **N008** (not_in_kb) faithful=3 Which accounting software should I use for my small business?
- **N010** (not_in_kb) faithful=3 How can I get more customers using social media?
- **N013** (not_in_kb) faithful=3 What is the current HST rate in Ontario?
- **N014** (not_in_kb) faithful=3 How do I set up payroll for my first employee?
- **N015** (not_in_kb) faithful=3 What is the difference between an employee and an independent contractor?
- **N016** (not_in_kb) faithful=3 How do I negotiate a commercial lease?
- **N018** (not_in_kb) faithful=3 Can I raise money for my business through crowdfunding?
- **N022** (not_in_kb) faithful=3 How do I set up an online store and collect sales tax?
- **N028** (not_in_kb) faithful=3 How do I export my products to the United States?
- **N029** (not_in_kb) faithful=3 How do I close down my business properly?
- **N034** (not_in_kb) faithful=3 How do I get a business credit card?
- **R001** (risky_advice) faithful=3 Should I incorporate to pay less tax?
- **R002** (risky_advice) faithful=3 Can I write off my home office as a business expense?
- **R006** (risky_advice) faithful=3 What happens if I don't remit HST on time?
- **R014** (risky_advice) faithful=3 Do I have to charge HST to customers outside Ontario?
- **R020** (risky_advice) faithful=3 Can I hire a family member and pay them from the business for tax purposes?
