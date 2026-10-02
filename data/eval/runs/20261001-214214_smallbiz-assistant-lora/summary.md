# Evaluation summary - smallbiz-assistant-lora

- Run: 2026-10-01 21:42  |  questions: 216  |  judge: off
- Settings: MIN_SIMILARITY=0.52, TOP_K=5, NUM_CTX=8192, temperature=0.0
- **Overall pass rate: 94%** (204/216)
- Average seconds per question: 14.2

## By category

| Category | Questions | Pass | Facts found | Cites [n] | Valid [n] | Right source | Numbers OK | Judge faithful (avg, informational) |
|---|---|---|---|---|---|---|---|---|
| fact | 87 | 95% | 97% | 100% | 100% | 100% | 99% | - |
| phrasing | 10 | 90% | 100% | 90% | 100% | 100% | 100% | - |
| process | 12 | 75% | 83% | 100% | 100% | 92% | 92% | - |
| followup | 15 | 80% | 87% | 100% | 100% | 93% | 93% | - |
| not_in_kb | 34 | 100% | - | - | - | - | - | - |
| off_topic | 20 | 100% | - | - | - | - | - | - |
| risky_advice | 20 | 100% | - | - | - | - | 100% | - |
| false_premise | 18 | 94% | 94% | 100% | 100% | 94% | 100% | - |

## What to look at first

Pass/fail below comes only from the rule checks (facts, citations, right source, numbers supported by the sources, hedged/declined/referred wording, no forbidden claims). The local-model judge no longer decides pass/fail - it flagged several correct answers as unfaithful across two runs, so its score is informational only; see 'Judge flagged, but passed' below to spot-check it by hand.

Most common reasons for failing (a question can have several):

- `facts`: 8
- `numbers_supported`: 3
- `right_source`: 3
- `citation`: 1

## Failed questions

- **F060** (fact) Who should I contact about the location for my business? -> facts, missing: Business Improvement/BIA
- **F077** (fact) How do I work out my break-even point? -> numbers_supported, invented numbers: $10,000, $50, $10,000, $50
- **F080** (fact) What can I do to improve my cash flow? -> facts, missing: invoice
- **F083** (fact) How much vacation pay do I owe an employee who has worked less than five years? -> facts, missing: 2 weeks/two weeks
- **P003** (phrasing) do i need insurance for my home business -> citation
- **S002** (process) I'm a freelance designer. What do I need to do to set up as a sole proprietor? -> facts, numbers_supported, missing: CPP/personal income, invented numbers: $30,000
- **S008** (process) What should I sort out before I hire my first employee in Ontario? -> facts, missing: employment standards/Employer Health Tax/health and safety
- **S012** (process) What costs should I plan for when starting a business? -> right_source
- **U001** (followup) Yes, I made $35,000 over the last four quarters. What should I do next? -> facts, numbers_supported, missing: register/GST/HST account; 30,000/threshold, invented numbers: $35,000
- **U006** (followup) And is checking availability free? -> right_source
- **U015** (followup) How do I get a GST/HST number? -> facts, missing: Business Registration Online/BRO
- **X018** (false_premise) Corporations in Ontario never have to file annual paperwork, do they? -> facts, right_source, missing: annual filings/filings/records

## Judge flagged, but passed (informational - spot-check these by hand)

None.
