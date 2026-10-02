"""Offline tests for split_train_dev.py - no Ollama, no internet, no chromadb."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import split_train_dev as sp


def _write_pilot(path: Path, rows: list[dict]) -> None:
    with path.open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def test_split_is_stratified_and_covers_every_category(tmp_path, monkeypatch):
    rows = []
    for cat, n in [("fact", 20), ("process", 7), ("not_in_kb", 15)]:
        for i in range(n):
            rows.append({"id": f"{cat}{i}", "category": cat, "messages": []})

    data_dir = tmp_path / "data" / "train"
    data_dir.mkdir(parents=True)
    _write_pilot(data_dir / "train_pilot.jsonl", rows)
    monkeypatch.setattr(sp, "DATA_DIR", data_dir)
    monkeypatch.setattr(sp, "SRC", data_dir / "train_pilot.jsonl")

    import argparse
    monkeypatch.setattr(sp, "argparse", argparse)
    monkeypatch.setattr(sys, "argv", ["split_train_dev.py"])
    sp.main()

    train = [json.loads(l) for l in (data_dir / "train.jsonl").open()]
    dev = [json.loads(l) for l in (data_dir / "dev.jsonl").open()]

    assert len(train) + len(dev) == len(rows)
    train_cats = {r["category"] for r in train}
    dev_cats = {r["category"] for r in dev}
    assert train_cats == {"fact", "process", "not_in_kb"}
    assert dev_cats == {"fact", "process", "not_in_kb"}, "every category must appear in dev"

    # every id ends up in exactly one split
    train_ids = {r["id"] for r in train}
    dev_ids = {r["id"] for r in dev}
    assert not (train_ids & dev_ids)
    assert train_ids | dev_ids == {r["id"] for r in rows}

    # the small category (process, 7 items) still got at least 1 dev example
    process_dev = [r for r in dev if r["category"] == "process"]
    assert len(process_dev) >= 1


def test_split_is_deterministic_given_same_seed(tmp_path, monkeypatch):
    rows = [{"id": f"x{i}", "category": "fact", "messages": []} for i in range(30)]
    data_dir = tmp_path / "data" / "train"
    data_dir.mkdir(parents=True)
    _write_pilot(data_dir / "train_pilot.jsonl", rows)
    monkeypatch.setattr(sp, "DATA_DIR", data_dir)
    monkeypatch.setattr(sp, "SRC", data_dir / "train_pilot.jsonl")

    import sys as _sys
    monkeypatch.setattr(_sys, "argv", ["split_train_dev.py", "--seed", "42"])
    sp.main()
    dev_ids_1 = {json.loads(l)["id"] for l in (data_dir / "dev.jsonl").open()}

    monkeypatch.setattr(_sys, "argv", ["split_train_dev.py", "--seed", "42"])
    sp.main()
    dev_ids_2 = {json.loads(l)["id"] for l in (data_dir / "dev.jsonl").open()}

    assert dev_ids_1 == dev_ids_2
