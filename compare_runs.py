"""Compare two evaluation runs (for example 3B vs 8B, or before vs after a prompt change).

    python compare_runs.py data/eval/runs/<older_run> data/eval/runs/<newer_run>

Prints pass rates by category side by side, then lists the questions that got worse or better.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path


def load(run: str) -> dict[str, dict]:
    path = Path(run) / "results.jsonl"
    return {r["id"]: r for r in map(json.loads, path.read_text().splitlines()) if r}


def rate(rs: list[dict]) -> str:
    return f"{100 * sum(r['pass'] for r in rs) / len(rs):.0f}% ({sum(r['pass'] for r in rs)}/{len(rs)})" if rs else "-"


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 1
    a, b = load(sys.argv[1]), load(sys.argv[2])
    common = sorted(set(a) & set(b))
    print(f"A = {sys.argv[1]}\nB = {sys.argv[2]}\n{len(common)} questions in both\n")
    cats: dict[str, list[str]] = defaultdict(list)
    for i in common:
        cats[a[i]["category"]].append(i)
    print(f"{'category':<15}{'A':>16}{'B':>16}")
    for cat, ids in cats.items():
        print(f"{cat:<15}{rate([a[i] for i in ids]):>16}{rate([b[i] for i in ids]):>16}")
    print(f"{'ALL':<15}{rate([a[i] for i in common]):>16}{rate([b[i] for i in common]):>16}\n")
    # Describes B relative to A (A = first arg/older run, B = second arg/newer run).
    improved = [i for i in common if not a[i]["pass"] and b[i]["pass"]]
    regressed = [i for i in common if a[i]["pass"] and not b[i]["pass"]]
    print(f"Improved in B ({len(improved)}):")
    for i in improved:
        print(f"  {i} {b[i]['question'][:80]}")
    print(f"\nRegressed in B ({len(regressed)}):")
    for i in regressed:
        print(f"  {i} {b[i]['question'][:80]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
