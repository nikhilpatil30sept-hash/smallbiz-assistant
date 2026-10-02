"""Builds Phase 3 fine-tuning data from training_pairs.py.

For every item this calls the REAL retrieval (rag.retrieve + rag.group_by_page) against
the actual knowledge base, so the "sources" half of each training example is exactly what
production would show the model for that question - never hand-written. {{CITE:NAME}}
placeholders in the answer text are replaced with the real [n] once we know where that
source landed; if a named source didn't come back at all, the item is flagged instead of
silently guessing, so a human can fix the question or drop the item.

Usage (on the machine with the real venv + Ollama + built chroma_db):
    python build_training_set.py

Writes:
    data/train/train_pilot.jsonl   - one {"messages": [...]} per line, ready for SFT
    data/train/train_pilot.csv     - the same data, readable, for a quick human review pass
    (warnings, if any, are printed to the terminal - fix before trusting the jsonl)
"""
import csv
import json
from pathlib import Path

import rag
from prompts import SYSTEM_PROMPT, build_user_prompt
from training_pairs import PILOT, FRAGMENTS

OUT_DIR = Path(__file__).resolve().parent / "data" / "train"
EVAL_SET = Path(__file__).resolve().parent / "data" / "eval" / "eval_set.jsonl"


def _matches(fragment: str, url: str) -> bool:
    if fragment.startswith("http"):
        return url == fragment
    return fragment.lower() in url.lower()


def _source_key(s: dict) -> str:
    """Same fallback evaluate.py/scoring.py use: a source's URL, or its title when it has
    no URL (a local doc like the cash-flow guide)."""
    return s["url"] or s["title"]


def _resolve_citations(answer: str, cite_keys: list[str], sources: list[dict], warnings: list[str], qid: str) -> str:
    out = answer
    for key in cite_keys:
        frags = FRAGMENTS[key]
        idx = None
        for i, s in enumerate(sources, 1):
            if any(_matches(f, _source_key(s)) for f in frags):
                idx = i
                break
        placeholder = "{{CITE:%s}}" % key
        if idx is None:
            warnings.append(f"{qid}: source '{key}' ({frags}) not found in retrieval - left placeholder in place")
        else:
            out = out.replace(placeholder, f"[{idx}]")
    if "{{CITE:" in out:
        warnings.append(f"{qid}: unresolved placeholder(s) remain: {out}")
    return out


def _check_disjoint(all_questions: list[str]) -> None:
    if not EVAL_SET.exists():
        print(f"NOTE: {EVAL_SET} not found, skipping the eval-set overlap check.")
        return
    eval_qs = set()
    with EVAL_SET.open() as f:
        for line in f:
            eval_qs.add(json.loads(line)["question"].strip().lower())
    overlap = [q for q in all_questions if q.strip().lower() in eval_qs]
    if overlap:
        raise SystemExit(
            "REFUSING to write training data: these training questions exactly match a question "
            f"already in data/eval/eval_set.jsonl (must stay unseen for Phase 4):\n  - " + "\n  - ".join(overlap)
        )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    warnings: list[str] = []
    rows = []
    all_last_questions = [item["turns"][-1] for item in PILOT]
    _check_disjoint(all_last_questions)

    for i, item in enumerate(PILOT, 1):
        qid = f"T{i:03d}"
        turns = item["turns"]
        question = turns[-1]
        history = [{"role": "user", "content": t} for t in turns[:-1]] if len(turns) > 1 else None

        # Real retrieval for every category, not_in_kb included: production shows the
        # model whatever retrieval actually returns for these questions - sometimes
        # nothing, sometimes a couple of weakly-related chunks - and training must cover
        # both, or the model never practices declining when given real-but-irrelevant
        # source text (only the empty-retrieval shortcut).
        sources = rag.group_by_page(rag.retrieve(question, history=history))

        answer = _resolve_citations(item["answer"], item["cite"], sources, warnings, qid)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for m in (history or [])[-4:]:
            messages.append(m)
        messages.append({"role": "user", "content": build_user_prompt(question, sources)})
        messages.append({"role": "assistant", "content": answer})

        rows.append({
            "id": qid,
            "category": item["category"],
            "question": question,
            "n_sources": len(sources),
            "sources": [s["url"] or s["title"] for s in sources],
            "answer": answer,
            "messages": messages,
        })

    jsonl_path = OUT_DIR / "train_pilot.jsonl"
    with jsonl_path.open("w") as f:
        for r in rows:
            f.write(json.dumps({"id": r["id"], "category": r["category"], "messages": r["messages"]},
                                ensure_ascii=False) + "\n")

    csv_path = OUT_DIR / "train_pilot.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "category", "question", "n_sources", "sources", "answer"])
        for r in rows:
            w.writerow([r["id"], r["category"], r["question"], r["n_sources"], "; ".join(r["sources"]), r["answer"]])

    print(f"Wrote {len(rows)} training examples to {jsonl_path}")
    print(f"Human-readable copy: {csv_path}")
    by_cat: dict[str, int] = {}
    for r in rows:
        by_cat[r["category"]] = by_cat.get(r["category"], 0) + 1
    for cat, n in by_cat.items():
        print(f"  {cat:14s} {n}")
    if warnings:
        print(f"\n{len(warnings)} WARNING(S) - review before trusting this data:")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("\nNo warnings - every {{CITE:...}} placeholder resolved against a real retrieved source.")


if __name__ == "__main__":
    main()
