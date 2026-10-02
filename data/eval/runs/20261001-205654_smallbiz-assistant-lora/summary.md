# Evaluation summary - smallbiz-assistant-lora

- Run: 2026-10-01 20:56  |  questions: 27  |  judge: off
- Settings: MIN_SIMILARITY=0.52, TOP_K=5, NUM_CTX=8192, temperature=0.0
- **Overall pass rate: 78%** (21/27)
- Average seconds per question: 26.8

## By category

| Category | Questions | Pass | Facts found | Cites [n] | Valid [n] | Right source | Numbers OK | Judge faithful (avg, informational) |
|---|---|---|---|---|---|---|---|---|
| process | 12 | 75% | 83% | 100% | 100% | 92% | 92% | - |
| followup | 15 | 80% | 93% | 100% | 100% | 93% | 93% | - |

## What to look at first

Pass/fail below comes only from the rule checks (facts, citations, right source, numbers supported by the sources, hedged/declined/referred wording, no forbidden claims). The local-model judge no longer decides pass/fail - it flagged several correct answers as unfaithful across two runs, so its score is informational only; see 'Judge flagged, but passed' below to spot-check it by hand.

Most common reasons for failing (a question can have several):

- `facts`: 3
- `numbers_supported`: 2
- `right_source`: 2

## Failed questions

- **S002** (process) I'm a freelance designer. What do I need to do to set up as a sole proprietor? -> facts, numbers_supported, missing: CPP/personal income, invented numbers: $30,000
- **S008** (process) What should I sort out before I hire my first employee in Ontario? -> facts, missing: employment standards/Employer Health Tax/health and safety
- **S012** (process) What costs should I plan for when starting a business? -> right_source
- **U001** (followup) Yes, I made $35,000 over the last four quarters. What should I do next? -> numbers_supported, invented numbers: $35,000
- **U006** (followup) And is checking availability free? -> right_source
- **U015** (followup) How do I get a GST/HST number? -> facts, missing: Business Registration Online/BRO

## Judge flagged, but passed (informational - spot-check these by hand)

None.
