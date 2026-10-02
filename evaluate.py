"""Run the Phase 2 evaluation: ask the assistant every question in data/eval/eval_set.jsonl,
score the answers (see scoring.py), and write a report.

Usage examples:
    python evaluate.py --rescore data/eval/runs/<folder>  # re-apply the current scoring rules, no model calls
    python evaluate.py --per-category 3              # balanced smoke test (about 24 questions)
    python evaluate.py --limit 20                    # first 20 questions only (all "fact")
    python evaluate.py                               # full run (about 200 questions)
    CHAT_MODEL=llama3.1:8b python evaluate.py        # choose the model being tested
    python evaluate.py --category off_topic          # one category only
    python evaluate.py --no-judge                    # rule-based checks only (much faster)
    python evaluate.py --resume data/eval/runs/<folder>   # continue an interrupted run

Output goes to data/eval/runs/<timestamp>_<model>/ :
    results.jsonl   one record per question (answer, sources, checks, judge scores)
    results.csv     the same, for a spreadsheet, with blank columns for your own grade
    summary.md      pass rates by category and a list of failures
"""
import argparse
import csv
import datetime as dt
import json
import random
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

import config
import scoring

EVAL_SET = config.DATA_DIR / "eval" / "eval_set.jsonl"
RUNS_DIR = config.DATA_DIR / "eval" / "runs"


def load_items(path: Path = EVAL_SET) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def ask(item: dict) -> tuple[str, list[dict]]:
    """Play the conversation turn by turn (the assistant sees its own earlier answers)
    and return the final answer and the sources it showed for that answer."""
    import rag

    history: list[dict] = []  # answers are cleaned exactly as the chat page cleans them
    answer, sources = "", []
    for turn in item["turns"]:
        sources, tokens = rag.answer_stream(turn, history)
        answer = rag.strip_invalid_citations("".join(tokens).strip(), len(sources))
        history += [{"role": "user", "content": turn}, {"role": "assistant", "content": answer}]
    return answer, sources


def judge(item: dict, answer: str, sources: list[dict], model: str) -> dict:
    import ollama

    client = ollama.Client(host=config.OLLAMA_HOST, timeout=config.REQUEST_TIMEOUT)
    try:
        resp = client.chat(
            model=model,
            messages=[
                {"role": "system", "content": scoring.JUDGE_SYSTEM},
                {"role": "user", "content": scoring.build_judge_prompt(item["question"], sources, answer)},
            ],
            format="json",
            options={"temperature": 0, "num_ctx": config.NUM_CTX, "num_predict": 300},
        )
        return scoring.parse_judge(resp["message"]["content"])
    except Exception as e:  # a judge failure must never stop the run
        return {"faithful": None, "helpful": None, "unsupported": [f"judge error: {e}"]}


def evaluate_item(item: dict, use_judge: bool, judge_model: str) -> dict:
    t0 = time.time()
    try:
        answer, sources = ask(item)
        error = ""
    except Exception as e:
        answer, sources, error = "", [], str(e)
    urls = [s["url"] or s["title"] for s in sources]  # your own documents have no URL, only a title
    source_text = "\n".join(s["text"] for s in sources)  # for numbers_supported(); not saved to disk
    scored = scoring.score_item(item, answer, urls, source_text)
    verdict = None
    if use_judge and answer and item["expect"] != "decline":
        verdict = judge(item, answer, sources, judge_model)
    rec = {
        "id": item["id"],
        "category": item["category"],
        "expect": item["expect"],
        "question": item["question"],
        "turns": item["turns"],
        "answer": answer,
        "sources": [{"title": s["title"], "url": s["url"], "similarity": s["similarity"]} for s in sources],
        "checks": scored["checks"],
        "auto_pass": scored["auto_pass"] and not error,
        "facts_recall": scored["facts_recall"],
        "missing_facts": scored["missing"],
        "forbidden_found": scored["forbidden_found"],
        "bad_numbers": scored["bad_numbers"],
        "judge": verdict,
        "error": error,
        "seconds": round(time.time() - t0, 1),
    }
    rec["pass"] = bool(not error and scoring.final_pass(item, scored, verdict))
    return rec


# ---------------------------------------------------------------- reporting
def pct(n: int, d: int) -> str:
    return f"{100 * n / d:.0f}%" if d else "-"


def summarize(records: list[dict], meta: dict) -> str:
    by_cat: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_cat[r["category"]].append(r)

    lines = [
        f"# Evaluation summary - {meta['model']}",
        "",
        f"- Run: {meta['started']}  |  questions: {len(records)}  |  judge: {meta['judge']}",
        f"- Settings: MIN_SIMILARITY={config.MIN_SIMILARITY}, TOP_K={config.TOP_K}, "
        f"NUM_CTX={config.NUM_CTX}, temperature={meta['temperature']}",
        f"- **Overall pass rate: {pct(sum(r['pass'] for r in records), len(records))}** "
        f"({sum(r['pass'] for r in records)}/{len(records)})",
        f"- Average seconds per question: {sum(r['seconds'] for r in records) / max(1, len(records)):.1f}",
        "",
        "## By category",
        "",
        "| Category | Questions | Pass | Facts found | Cites [n] | Valid [n] | Right source | Numbers OK | Judge faithful (avg, informational) |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for cat, rs in by_cat.items():
        n = len(rs)
        ans = [r for r in rs if "citation" in r["checks"]]
        num_checked = [r for r in rs if "numbers_supported" in r["checks"]]
        faithful = [r["judge"]["faithful"] for r in rs if r.get("judge") and r["judge"].get("faithful") is not None]
        cells = [
            cat,
            str(n),
            pct(sum(r["pass"] for r in rs), n),
            pct(sum(1 for r in ans if r["checks"]["facts"]), len(ans)) if ans else "-",
            pct(sum(r["checks"]["citation"] for r in ans), len(ans)) if ans else "-",
            pct(sum(r["checks"].get("citations_valid", True) for r in ans), len(ans)) if ans else "-",
            pct(sum(r["checks"]["right_source"] for r in ans), len(ans)) if ans else "-",
            pct(sum(r["checks"]["numbers_supported"] for r in num_checked), len(num_checked)) if num_checked else "-",
            f"{sum(faithful) / len(faithful):.1f}" if faithful else "-",
        ]
        lines.append("| " + " | ".join(cells) + " |")

    lines += ["", "## What to look at first", ""]
    lines.append(
        "Pass/fail below comes only from the rule checks (facts, citations, right source, numbers "
        "supported by the sources, hedged/declined/referred wording, no forbidden claims). The local-model "
        "judge no longer decides pass/fail - it flagged several correct answers as unfaithful across two "
        "runs, so its score is informational only; see 'Judge flagged, but passed' below to spot-check it "
        "by hand."
    )
    fails = [r for r in records if not r["pass"]]
    reason_count: dict[str, int] = defaultdict(int)
    for r in fails:
        for name, ok in r["checks"].items():
            if not ok:
                reason_count[name] += 1
        if r["error"]:
            reason_count["error while answering"] += 1
    if reason_count:
        lines.append("")
        lines.append("Most common reasons for failing (a question can have several):")
        lines.append("")
        for name, c in sorted(reason_count.items(), key=lambda kv: -kv[1]):
            lines.append(f"- `{name}`: {c}")
    else:
        lines.append("")
        lines.append("No failures.")

    lines += ["", "## Failed questions", ""]
    for r in fails[:60]:
        why = [k for k, v in r["checks"].items() if not v]
        if r["missing_facts"]:
            why.append("missing: " + "; ".join("/".join(g) for g in r["missing_facts"]))
        if r["forbidden_found"]:
            why.append("forbidden: " + ", ".join(r["forbidden_found"]))
        if r.get("bad_numbers"):
            why.append("invented numbers: " + ", ".join(r["bad_numbers"]))
        if r["error"]:
            why.append("error: " + r["error"][:80])
        lines.append(f"- **{r['id']}** ({r['category']}) {r['question'][:90]} -> {', '.join(why)}")
    if len(fails) > 60:
        lines.append(f"- ... and {len(fails) - 60} more (see results.csv)")

    flagged = [r for r in records if r["pass"] and r.get("judge")
               and (r["judge"].get("faithful") or 5) < scoring.FAITHFUL_PASS]
    lines += ["", "## Judge flagged, but passed (informational - spot-check these by hand)", ""]
    if flagged:
        for r in flagged[:30]:
            lines.append(f"- **{r['id']}** ({r['category']}) faithful={r['judge']['faithful']} "
                         f"{r['question'][:80]}")
        if len(flagged) > 30:
            lines.append(f"- ... and {len(flagged) - 30} more (see results.csv, judge_faithful column)")
    else:
        lines.append("None.")
    return "\n".join(lines) + "\n"


def write_csv(records: list[dict], path: Path) -> None:
    cols = [
        "id", "category", "expect", "question", "answer", "sources", "pass", "failed_checks",
        "missing_facts", "invented_numbers", "judge_faithful", "judge_helpful", "judge_unsupported",
        "MY_GRADE_1to5", "MY_NOTES",
    ]
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in records:
            j = r.get("judge") or {}
            w.writerow([
                r["id"], r["category"], r["expect"], " / ".join(r["turns"]), r["answer"],
                "; ".join(s["url"] for s in r["sources"]),
                "PASS" if r["pass"] else "FAIL",
                ", ".join(k for k, v in r["checks"].items() if not v),
                "; ".join("/".join(g) for g in r["missing_facts"]),
                ", ".join(r.get("bad_numbers", [])),
                j.get("faithful", ""), j.get("helpful", ""), "; ".join(j.get("unsupported", [])),
                "", "",
            ])


def rescore(run_dir: Path, eval_set: Path) -> int:
    """Re-apply the CURRENT scoring rules to an earlier run's saved answers, without asking
    the model anything again. Judge scores are kept as they were (and no longer affect
    pass/fail either way). Use it after fixing scoring.py or the question set, so the
    baseline is not distorted by scorer mistakes.

    Caveat: results.jsonl only stores each source's title/url/similarity, not its text, so
    numbers_supported() cannot be re-checked here - it passes automatically on a rescore.
    Only a fresh `python evaluate.py` run checks invented numbers."""
    items = {i["id"]: i for i in load_items(eval_set)}
    out_dir = run_dir.parent / (run_dir.name.rstrip("/") + "_rescored")
    out_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for line in (run_dir / "results.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        item = items.get(rec["id"])
        if item is None:
            continue
        urls = [s["url"] or s["title"] for s in rec["sources"]]
        scored = scoring.score_item(item, rec["answer"], urls)  # no source_text: numbers_supported skipped
        rec.update(
            checks=scored["checks"], auto_pass=bool(scored["auto_pass"] and not rec["error"]),
            facts_recall=scored["facts_recall"], missing_facts=scored["missing"],
            forbidden_found=scored["forbidden_found"], bad_numbers=scored["bad_numbers"],
            question=item["question"], turns=item["turns"],
        )
        rec["pass"] = bool(not rec["error"] and scoring.final_pass(item, scored, rec.get("judge")))
        records.append(rec)
    (out_dir / "results.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records))
    meta = {"model": run_dir.name + " (rescored)", "started": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "temperature": "as in original run", "judge": "scores kept from the original run"}
    (out_dir / "summary.md").write_text(summarize(records, meta))
    write_csv(records, out_dir / "results.csv")
    print((out_dir / "summary.md").read_text())
    print(f"Files: {out_dir}/summary.md, results.csv, results.jsonl")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, help="only the first N questions (after any category filter)")
    ap.add_argument("--sample", type=int, help="random sample of N questions (seeded, so repeatable)")
    ap.add_argument("--per-category", type=int, help="first N questions of EACH category (a balanced smoke test)")
    ap.add_argument("--category", action="append", help="only this category (repeatable)")
    ap.add_argument("--no-judge", action="store_true", help="skip the local-model judge")
    ap.add_argument("--judge-model", default=None, help="model used as judge (default: same as CHAT_MODEL)")
    ap.add_argument("--temperature", type=float, default=0.0, help="generation temperature (default 0 = repeatable)")
    ap.add_argument("--resume", type=Path, help="continue an earlier run folder")
    ap.add_argument("--eval-set", type=Path, default=EVAL_SET)
    ap.add_argument("--rescore", type=Path, help="re-score an earlier run folder with the current rules (no model calls)")
    args = ap.parse_args(argv)
    if args.rescore:
        return rescore(args.rescore, args.eval_set)

    config.TEMPERATURE = args.temperature
    judge_model = args.judge_model or config.CHAT_MODEL
    items = load_items(args.eval_set)
    if args.category:
        items = [i for i in items if i["category"] in args.category]
    if args.per_category:
        seen: dict[str, int] = defaultdict(int)
        picked = []
        for i in items:
            if seen[i["category"]] < args.per_category:
                seen[i["category"]] += 1
                picked.append(i)
        items = picked
    if args.sample:
        items = random.Random(7).sample(items, min(args.sample, len(items)))
    if args.limit:
        items = items[: args.limit]

    started = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    if args.resume:
        run_dir = args.resume
    else:
        safe_model = re.sub(r"[^a-zA-Z0-9.]+", "-", config.CHAT_MODEL)
        run_dir = RUNS_DIR / f"{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}_{safe_model}"
    run_dir.mkdir(parents=True, exist_ok=True)
    results_path = run_dir / "results.jsonl"

    done: dict[str, dict] = {}
    if results_path.exists():
        for line in results_path.read_text().splitlines():
            if line.strip():
                rec = json.loads(line)
                done[rec["id"]] = rec
    todo = [i for i in items if i["id"] not in done]
    print(f"Model: {config.CHAT_MODEL} | judge: {'off' if args.no_judge else judge_model} | "
          f"{len(items)} questions ({len(done)} already done) -> {run_dir}")

    with results_path.open("a") as out:
        for n, item in enumerate(todo, 1):
            rec = evaluate_item(item, not args.no_judge, judge_model)
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            out.flush()
            done[rec["id"]] = rec
            j = rec["judge"]["faithful"] if rec.get("judge") else "-"
            print(f"[{n}/{len(todo)}] {rec['id']} {rec['category']:<13} "
                  f"{'PASS' if rec['pass'] else 'FAIL'}  faithful={j}  {rec['seconds']}s  {item['question'][:55]}",
                  flush=True)

    records = [done[i["id"]] for i in items if i["id"] in done]
    meta = {"model": config.CHAT_MODEL, "started": started, "temperature": args.temperature,
            "judge": "off" if args.no_judge else judge_model}
    (run_dir / "summary.md").write_text(summarize(records, meta))
    write_csv(records, run_dir / "results.csv")
    print("\n" + (run_dir / "summary.md").read_text())
    print(f"Files: {run_dir}/summary.md, results.csv, results.jsonl")
    return 0


if __name__ == "__main__":
    sys.exit(main())
