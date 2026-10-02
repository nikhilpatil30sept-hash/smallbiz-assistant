# Evaluation summary - smallbiz-assistant-lora

- Run: 2026-10-01 19:48  |  questions: 27  |  judge: off
- Settings: MIN_SIMILARITY=0.52, TOP_K=8, NUM_CTX=8192, temperature=0.0
- **Overall pass rate: 78%** (21/27)
- Average seconds per question: 31.8

## By category

| Category | Questions | Pass | Facts found | Cites [n] | Valid [n] | Right source | Numbers OK | Judge faithful (avg, informational) |
|---|---|---|---|---|---|---|---|---|
| process | 12 | 67% | 75% | 100% | 100% | 83% | 100% | - |
| followup | 15 | 87% | 87% | 100% | 100% | 100% | 93% | - |

## What to look at first

Pass/fail below comes only from the rule checks (facts, citations, right source, numbers supported by the sources, hedged/declined/referred wording, no forbidden claims). The local-model judge no longer decides pass/fail - it flagged several correct answers as unfaithful across two runs, so its score is informational only; see 'Judge flagged, but passed' below to spot-check it by hand.

Most common reasons for failing (a question can have several):

- `facts`: 5
- `right_source`: 2
- `numbers_supported`: 1

## Failed questions

- **S002** (process) I'm a freelance designer. What do I need to do to set up as a sole proprietor? -> facts, missing: CPP/personal income
- **S005** (process) I'm starting a home-based business. What should I know about insurance, licences and tax? -> facts, missing: BizPaL/licences
- **S008** (process) What should I sort out before I hire my first employee in Ontario? -> right_source
- **S012** (process) What costs should I plan for when starting a business? -> facts, right_source, missing: registration; insurance; rent/marketing/licensing
- **U001** (followup) Yes, I made $35,000 over the last four quarters. What should I do next? -> facts, numbers_supported, missing: register/GST/HST account; 30,000/threshold, invented numbers: $35,000
- **U015** (followup) How do I get a GST/HST number? -> facts, missing: Business Registration Online/BRO

## Judge flagged, but passed (informational - spot-check these by hand)

None.
