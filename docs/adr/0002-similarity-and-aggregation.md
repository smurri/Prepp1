# ADR 0002 — Similarity model & aggregation

**Status:** Accepted · **Phase:** 1.5 / 2

## Similarity between two paths
A path is an ordered sequence of tool calls, so path comparison is **sequence comparison**.

**Options considered**
1. **Exact match** — `1.0` iff identical. Too brittle; no partial credit.
2. **Set / Jaccard overlap** — order-insensitive. Loses ordering, which usually matters.
3. **LCS ratio** — order-sensitive, gap-tolerant, but ignores substitution distance.
4. **Normalized edit (Levenshtein) distance** — order-sensitive; charges insert/delete/substitute;
   `similarity = 1 - dist/max(len)`. Natural, bounded in `[0,1]`, partial credit.

**Decision:** ship all of (2)(3)(4) behind a `PathComparator` protocol; **default = normalized
edit distance** (4). *Driving NFR:* correct logic + clean extensibility — researchers swap
strategies without touching the engine. A `CompositeComparator` weights several together.

**Step comparison** is itself pluggable (`StepSimilarity`): default compares **tool name only**
(`1.0` if equal else `0.0`); an optional variant gives partial credit when `args` overlap. This
keeps the common case simple while supporting richer scoring.

## Aggregation across references
A question has many references. *Driving NFR:* answer "did it resemble *a* good path?".

**Options:** `max` (best reference), `mean` (average over all), `top-k mean` (robust to outliers).
**Decision:** pluggable `Aggregation`; **default = `max`**. `max` is monotonic — adding a
reference can never lower the score — which we assert as a property test.

## Invariants (property-tested)
- Output always in `[0,1]`. · Identity (candidate == some reference) ⇒ `1.0`.
- Empty-vs-empty ⇒ `1.0`; empty-vs-nonempty ⇒ `0.0`. · Comparators are symmetric.
- Under `max` aggregation, adding references is non-decreasing in score.
