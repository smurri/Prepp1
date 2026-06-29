"""Headless end-to-end demo: load a mock backend, score every candidate run.

Run with::

    uv run python -m agent_eval.demo
    uv run python -m agent_eval.demo --backend nosql --comparator lcs

Exercises the full path: mock DB -> hydrate engine -> score candidates ->
explainable breakdown. No UI, no network — safe to run in CI.
"""

from __future__ import annotations

import argparse

from . import EvalEngine, JaccardComparator, LCSComparator, SequenceComparator
from .aggregation import MAX, MEAN
from .mockdata import NoSqlBackend, SqlBackend, hydrate

_BACKENDS = {"sql": SqlBackend, "nosql": NoSqlBackend}
_COMPARATORS = {
    "sequence": SequenceComparator,
    "jaccard": JaccardComparator,
    "lcs": LCSComparator,
}
_AGGREGATIONS = {"max": MAX, "mean": MEAN}


def run(backend_key: str = "sql", comparator_key: str = "sequence",
        aggregation_key: str = "max") -> None:
    backend = _BACKENDS[backend_key]()
    engine = EvalEngine(
        comparator=_COMPARATORS[comparator_key](),
        aggregation=_AGGREGATIONS[aggregation_key],
    )
    hydrate(engine, backend)

    print("\n=== Agent Eval Engine demo ===")
    print(f"backend={backend.name} | comparator={comparator_key} | aggregation={aggregation_key}\n")

    for q in backend.questions():
        refs = backend.reference_paths(q.question_id)
        print(f"[{q.domain}] {q.question_id}: {q.text}")
        print(f"  references: {len(refs)} "
              f"({', '.join(r.quality for r in refs)})")
        for cand in backend.candidates(q.question_id):
            result = engine.score(q.question_id, cand.trace)
            best = result.best
            bar = "#" * round(result.score * 20)
            print(f"    {cand.label:14s} {result.score:5.2f} |{bar:<20s}| "
                  f"best=ref#{best.reference_id} - {cand.note}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Agent Eval Engine demo")
    parser.add_argument("--backend", choices=_BACKENDS, default="sql")
    parser.add_argument("--comparator", choices=_COMPARATORS, default="sequence")
    parser.add_argument("--aggregation", choices=_AGGREGATIONS, default="max")
    args = parser.parse_args()
    run(args.backend, args.comparator, args.aggregation)


if __name__ == "__main__":
    main()
