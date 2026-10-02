"""Module 15 diagnostic: WHY does each failing process/followup question fail?

For every question in a run that failed, report three things:
  1. RETRIEVAL - was each expected source page retrieved?
  2. FACTS     - is each missing fact present in the text the model was given?
  3. TRUNCATION- does the answer look cut off (hit the MAX_ANSWER_TOKENS cap)?

Verdict per question:
  retrieval  : the fact is not in the retrieved text  -> fix search / KB
  generation : the fact IS in the retrieved text but the answer omits it -> fix prompt
  truncation : the answer ends mid-sentence -> raise the token cap

Needs the venv and `ollama serve` (embeddings). Usage:
  python diagnose_failures.py data/eval/runs/20260928-224942_smallbiz-assistant-lora
  python diagnose_failures.py RUN_DIR --category process --category followup
"""
import argparse
import json
from pathlib import Path

import config
import rag

EVAL_SET = Path("data/eval/eval_set.jsonl")


def load(path):
    return [json.loads(l) for l in open(path) if l.strip()]


def contains(text, options):
    t = text.lower()
    return any(o.lower() in t for o in options)


def looks_truncated(answer):
    a = answer.rstrip()
    return bool(a) and a[-1] not in '.!?)"”*:' and not a.endswith("]")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--category", action="append", default=None)
    args = ap.parse_args()
    cats = args.category or ["process", "followup"]

    qs = {q["id"]: q for q in load(EVAL_SET)}
    rows = [r for r in load(args.run_dir / "results.jsonl")
            if r["category"] in cats and not r.get("pass")]
    print(f"{len(rows)} failing question(s) in {cats}  (cap={config.MAX_ANSWER_TOKENS} tokens, TOP_K={config.TOP_K})\n")

    summary = {}
    for r in rows:
        q = qs[r["id"]]
        turns = q["turns"]
        history = []
        for t in turns[:-1]:
            history += [{"role": "user", "content": t}, {"role": "assistant", "content": "(earlier answer)"}]
        sources = rag.group_by_page(rag.retrieve(turns[-1], history=history))
        urls = [s["url"] for s in sources]
        got = [slug for slug in q["expected_sources"] if any(slug in u for u in urls)]
        blob = "\n".join(s["text"] for s in sources)
        answer = r.get("answer", "")

        print(f"== {r['id']} [{r['category']}]  {turns[-1]}")
        print(f"   expected pages retrieved: {got or 'NONE'} of {q['expected_sources']}")
        print(f"   retrieved: {[u.rsplit('/', 1)[-1] for u in urls]}")
        verdicts = []
        for opts in r.get("missing_facts") or []:
            in_sources = contains(blob, opts)
            in_answer = contains(answer, opts)
            print(f"   fact {opts}: in retrieved text={in_sources}, in answer={in_answer}")
            verdicts.append("generation" if in_sources else "retrieval")
        trunc = looks_truncated(answer)
        print(f"   answer length={len(answer)} chars, looks cut off={trunc}")
        if trunc:
            verdicts.append("truncation")
        v = sorted(set(verdicts)) or ["unclear"]
        print(f"   VERDICT: {', '.join(v)}\n")
        for x in v:
            summary[x] = summary.get(x, 0) + 1
    print("SUMMARY (count of verdict tags):", summary)


if __name__ == "__main__":
    main()
