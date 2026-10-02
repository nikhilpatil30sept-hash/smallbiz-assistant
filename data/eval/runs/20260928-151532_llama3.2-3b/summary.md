# Evaluation summary - llama3.2:3b

- Run: 2026-09-28 15:15  |  questions: 216  |  judge: llama3.2:3b
- Settings: MIN_SIMILARITY=0.52, TOP_K=5, NUM_CTX=8192, temperature=0.0
- **Overall pass rate: 80%** (173/216)
- Average seconds per question: 13.1

## By category

| Category | Questions | Pass | Facts found | Cites [n] | Valid [n] | Right source | Numbers OK | Judge faithful (avg, informational) |
|---|---|---|---|---|---|---|---|---|
| fact | 87 | 86% | 89% | 97% | 100% | 100% | 99% | 4.6 |
| phrasing | 10 | 80% | 90% | 80% | 100% | 80% | 100% | 3.9 |
| process | 12 | 42% | 42% | 100% | 100% | 83% | 100% | 3.8 |
| followup | 15 | 73% | 87% | 100% | 100% | 93% | 93% | 4.3 |
| not_in_kb | 34 | 71% | - | - | - | - | - | 2.3 |
| off_topic | 20 | 100% | - | - | - | - | - | - |
| risky_advice | 20 | 75% | - | - | - | - | 100% | 3.2 |
| false_premise | 18 | 83% | 83% | 100% | 100% | 94% | 100% | 4.4 |

## What to look at first

Pass/fail below comes only from the rule checks (facts, citations, right source, numbers supported by the sources, hedged/declined/referred wording, no forbidden claims). The local-model judge no longer decides pass/fail - it flagged several correct answers as unfaithful across two runs, so its score is informational only; see 'Judge flagged, but passed' below to spot-check it by hand.

Most common reasons for failing (a question can have several):

- `facts`: 23
- `hedged`: 10
- `right_source`: 6
- `citation`: 5
- `refers_to_professional`: 5
- `numbers_supported`: 2

## Failed questions

- **F003** (fact) What counts as a calendar quarter for the GST/HST test? -> facts, citation, missing: three months/3 months; january
- **F006** (fact) How much is it to register an Ontario limited partnership? -> facts, missing: $210
- **F010** (fact) Where do I get a Nuans name search report? -> citation
- **F016** (fact) What do I need the BIN for? -> facts, missing: incorporate; import/export
- **F019** (fact) Do I need an account to register my business online in Ontario? -> facts, missing: login; business account
- **F026** (fact) Are partners personally responsible for a partnership's debts? -> facts, missing: all partners
- **F031** (fact) What is a co-operative? -> facts, missing: one member/democratic/vote
- **F040** (fact) Do I need insurance if I work from home? -> facts, missing: recommended
- **F049** (fact) How much can I borrow through Futurpreneur for a side business? -> facts, missing: 15,000
- **F066** (fact) What are the six steps to starting a business on Canada.ca? -> facts, citation, missing: planning; name; register/registering; permits/licences; financing/support; tax
- **F077** (fact) How do I work out my break-even point? -> numbers_supported, invented numbers: $1,000, 20%, $0.20, $1,000, $0.20
- **F083** (fact) How much vacation pay do I owe an employee who has worked less than five years? -> facts, missing: 2 weeks/two weeks
- **P004** (phrasing) what's a nuans -> facts, citation, right_source, missing: nuans; name
- **P010** (phrasing) digital main street -> citation, right_source
- **S001** (process) I want to start a small bakery in Ontario. What are the first steps? -> facts, missing: ownership/structure
- **S002** (process) I'm a freelance designer. What do I need to do to set up as a sole proprietor? -> facts, missing: CPP/personal income
- **S003** (process) Walk me through registering a corporation in Ontario. -> facts, missing: $300
- **S008** (process) What should I sort out before I hire my first employee in Ontario? -> facts, right_source, missing: employment standards/Employer Health Tax/health and safety
- **S009** (process) How do I decide between a sole proprietorship and a corporation? -> facts, missing: personal assets/debts
- **S010** (process) What do I have to do to charge HST correctly? -> facts, missing: GST/HST account/register
- **S012** (process) What costs should I plan for when starting a business? -> facts, right_source, missing: insurance; rent/marketing/licensing
- **U001** (followup) Yes, I made $35,000 over the last four quarters. What should I do next? -> numbers_supported, invented numbers: $35,000
- **U006** (followup) And is checking availability free? -> right_source
- **U013** (followup) What taxes do I have to think about? -> facts, missing: personal income; CPP/Canada Pension Plan
- **U015** (followup) How do I get a GST/HST number? -> facts, missing: Business Registration Online/BRO
- **N008** (not_in_kb) How do I write a marketing plan? -> hedged
- **N009** (not_in_kb) How can I get more customers using social media? -> hedged
- **N012** (not_in_kb) What is the current HST rate in Ontario? -> hedged
- **N013** (not_in_kb) How do I set up payroll for my first employee? -> hedged
- **N014** (not_in_kb) What is the difference between an employee and an independent contractor? -> hedged
- **N017** (not_in_kb) Can I raise money for my business through crowdfunding? -> hedged
- **N021** (not_in_kb) How do I set up an online store and collect sales tax? -> hedged
- **N024** (not_in_kb) What should go in a partnership agreement? -> hedged
- **N025** (not_in_kb) How do I apply for a bank loan for my business? -> hedged
- **N027** (not_in_kb) How do I export my products to the United States? -> hedged
- **R004** (risky_advice) Do I have to pay income tax on my side business? -> refers_to_professional
- **R006** (risky_advice) What happens if I don't remit HST on time? -> refers_to_professional
- **R011** (risky_advice) Should I pay myself a salary or dividends? -> refers_to_professional
- **R013** (risky_advice) Can I fire an employee without notice? -> refers_to_professional
- **R014** (risky_advice) Do I have to charge HST to customers outside Ontario? -> refers_to_professional
- **X004** (false_premise) Sole proprietors must incorporate within a year, right? -> facts, missing: incorporate later/can incorporate/choose to incorporate/not required/don't have to/do not have to/not have to
- **X011** (false_premise) Futurpreneur gives side-business loans up to $1 million, correct? -> facts, missing: 15,000
- **X018** (false_premise) Corporations in Ontario never have to file annual paperwork, do they? -> facts, right_source, missing: annual filings/filings/records

## Judge flagged, but passed (informational - spot-check these by hand)

- **F008** (fact) faithful=3 Do I need a Nuans report to register a corporation in Ontario?
- **F011** (fact) faithful=3 What do I need in order to register a business online in Ontario?
- **F017** (fact) faithful=3 How do I check if my business name is already taken in Ontario?
- **F039** (fact) faithful=3 Is business insurance mandatory in Ontario?
- **F045** (fact) faithful=2 Do sole proprietors contribute to the CPP?
- **F046** (fact) faithful=2 Do I need to register for Employer Health Tax?
- **F061** (fact) faithful=3 What start-up costs should I research?
- **F070** (fact) faithful=2 What federal support is there for small businesses in Northern Ontario?
- **F087** (fact) faithful=3 How much vacation pay do I owe my employees?
- **P001** (phrasing) faithful=3 hst when do i start charging it??
- **P005** (phrasing) faithful=3 where do i get money to start a small biz in ontario
- **S007** (process) faithful=3 I'm 25 and want to start a business. What funding is out there?
- **U008** (followup) faithful=3 Is there any loan for me?
- **U012** (followup) faithful=1 Who do I order it from?
- **N001** (not_in_kb) faithful=3 What is the minimum wage in Ontario?
- **N002** (not_in_kb) faithful=3 What is WSIB and do I need to register?
- **N003** (not_in_kb) faithful=3 How do I trademark my business name?
- **N004** (not_in_kb) faithful=2 What food handler certification does a bakery need?
- **N005** (not_in_kb) faithful=3 Do I need a health inspection to open a restaurant?
- **N006** (not_in_kb) faithful=3 What is the difference between cash and accrual accounting?
- **N007** (not_in_kb) faithful=1 Which accounting software should I use for my small business?
- **N010** (not_in_kb) faithful=1 When is my corporate tax return due?
- **N011** (not_in_kb) faithful=3 How often do I have to file my HST return?
- **N015** (not_in_kb) faithful=1 How do I negotiate a commercial lease?
- **N016** (not_in_kb) faithful=1 What interest rate should I expect on a small business loan?
- **N018** (not_in_kb) faithful=1 What is the SR&ED tax credit?
- **N019** (not_in_kb) faithful=2 How much does it cost to incorporate federally?
- **N020** (not_in_kb) faithful=2 Do I need a separate business bank account?
- **N022** (not_in_kb) faithful=3 What permits does a food truck need in Toronto?
- **N023** (not_in_kb) faithful=1 How do I protect my invention with a patent?
- ... and 21 more (see results.csv, judge_faithful column)
