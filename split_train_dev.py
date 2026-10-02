"""Splits data/train/train_pilot.jsonl into a training set and a held-out dev set.

This is NOT the Phase 4 acceptance test - that's still data/eval/eval_set.jsonl, untouched,
used once after training via evaluate.py + compare_runs.py. The dev split here is just for
sanity-checking loss/behavior during the QLoRA run itself (e.g. eval_loss in the Unsloth/TRL
trainer), so we can catch obvious overfitting or a broken run before spending eval time.

Split is STRATIFIED BY CATEGORY (not a flat random split) so every category - including the
smaller ones like process (22 examples) - is represented in both train and dev, roughly in
proportion. ~15% held out per category, rounded, with a floor of 1 example per category so no
category vanishes entirely from dev even at 15 examples.

Deterministic: same seed -> same split every time, so re-running this after adding more
examples later doesn't silently reshuffle items that were already in dev (it will still
reshuffle within each category's pool, since we don't persist which specific ids were chosen -
if you need a stable split across dataset growth, freeze data/train/dev.jsonl's ids instead of
re-running this script from scratch).

Usage:
    python split_train_dev.py [--dev-frac 0.15] [--seed 13]

Reads:
    data/train/train_pilot.jsonl   (written by build_training_set.py)
Writes:
    data/train/train.jsonl   - the training split, ready for the QLoRA script
    data/train/dev.jsonl     - the held-out dev split
"""
import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data" / "train"
SRC = DATA_DIR / "train_pilot.jsonl"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dev-frac", type=float, default=0.15)
    ap.add_argument("--seed", type=int, default=13)
    args = ap.parse_args()

    if not SRC.exists():
        raise SystemExit(f"{SRC} not found - run build_training_set.py first.")

    rows = [json.loads(line) for line in SRC.open()]
    if not rows:
        raise SystemExit(f"{SRC} is empty.")

    by_cat = defaultdict(list)
    for r in rows:
        by_cat[r["category"]].append(r)

    rng = random.Random(args.seed)
    train_rows, dev_rows = [], []
    for cat, items in sorted(by_cat.items()):
        items = items[:]
        rng.shuffle(items)
        n_dev = max(1, round(len(items) * args.dev_frac))
        dev_rows.extend(items[:n_dev])
        train_rows.extend(items[n_dev:])

    rng.shuffle(train_rows)
    rng.shuffle(dev_rows)

    train_path = DATA_DIR / "train.jsonl"
    dev_path = DATA_DIR / "dev.jsonl"
    with train_path.open("w") as f:
        for r in train_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with dev_path.open("w") as f:
        for r in dev_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Total: {len(rows)}  ->  train: {len(train_rows)}  dev: {len(dev_rows)} "
          f"({len(dev_rows) / len(rows):.1%})")
    print(f"Wrote {train_path}")
    print(f"Wrote {dev_path}")
    print("\nPer-category split:")
    train_by_cat = defaultdict(int)
    dev_by_cat = defaultdict(int)
    for r in train_rows:
        train_by_cat[r["category"]] += 1
    for r in dev_rows:
        dev_by_cat[r["category"]] += 1
    for cat in sorted(by_cat):
        print(f"  {cat:14s} train={train_by_cat[cat]:3d}  dev={dev_by_cat[cat]:3d}")


if __name__ == "__main__":
    main()
