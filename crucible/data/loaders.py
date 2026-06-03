from __future__ import annotations

import random
from pathlib import Path

from crucible.adapters.base import Task

# deepset/prompt-injections columns: text (str), label (int 0/1)
# No attack_type metadata — Phase 4 will augment with a labelled source.
_DEEPSET_DATASET = "deepset/prompt-injections"

# PINT benchmark (lakeraai/pint-benchmark) is held out for final evaluation only.
# Download instructions: https://github.com/lakeraai/pint-benchmark
# Place the exported CSV at data/pint/pint_test.csv before running test_tasks().
_PINT_DEFAULT_PATH = Path(__file__).parent.parent.parent / "data" / "pint" / "pint_test.csv"


def load_deepset(
    train_fraction: float = 0.8,
    seed: int = 42,
) -> tuple[list[Task], list[Task]]:
    """Return (train_tasks, selection_tasks) from deepset/prompt-injections.

    Uses the dataset's built-in train split, then divides it 80/20 for
    train vs. selection. The test split is intentionally unused here —
    PINT is the held-out test set.
    """
    from datasets import load_dataset  # deferred: not needed at import time

    ds = load_dataset(_DEEPSET_DATASET, split="train")
    tasks = [
        Task(id=f"deepset_train_{i}", text=row["text"], label=row["label"])
        for i, row in enumerate(ds)
    ]

    rng = random.Random(seed)
    rng.shuffle(tasks)
    cutoff = int(len(tasks) * train_fraction)
    return tasks[:cutoff], tasks[cutoff:]


def load_pint(path: Path = _PINT_DEFAULT_PATH) -> list[Task]:
    """Load PINT benchmark from a local CSV.

    Columns expected: text (str), label (int 0/1).
    Raises FileNotFoundError with download instructions if the file is missing.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"PINT benchmark not found at {path}.\n"
            "Download from https://github.com/lakeraai/pint-benchmark and place "
            f"the exported CSV at {path}."
        )

    import csv

    tasks = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            tasks.append(Task(
                id=f"pint_{i}",
                text=row["text"],
                label=int(row["label"]),
            ))
    return tasks
