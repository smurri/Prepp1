"""Step-level explanation: align a candidate path to a reference path.

Answers *why* a path scored as it did by computing an optimal alignment (a
Needleman–Wunsch / edit-distance traceback over tool names) and labelling each
position as match / substitute / extra / missing — from the candidate's point of
view. Pure stdlib; consistent with :class:`SequenceComparator`'s unit-cost model.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import Trace

#: Operation kinds, described from the CANDIDATE's perspective.
MATCH = "match"          # candidate step equals the reference step
SUBSTITUTE = "substitute"  # candidate used a different tool than the reference
EXTRA = "extra"          # candidate made a step the reference does not have
MISSING = "missing"      # reference has a step the candidate skipped


@dataclass(frozen=True)
class AlignOp:
    """One aligned position. ``candidate``/``reference`` are tool names or None."""

    op: str
    candidate: str | None
    reference: str | None


def align(candidate: Trace, reference: Trace) -> list[AlignOp]:
    """Return the optimal step alignment between two paths (by tool name).

    Unit costs: match=0, substitute/extra/missing=1 — matching the default
    :class:`SequenceComparator`, so the alignment explains that comparator's score.
    """
    a = candidate.tool_names
    b = reference.tool_names
    m, n = len(a), len(b)

    # dp[i][j] = min edit cost aligning a[:i] with b[:j].
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        dp[i][0] = i
    for j in range(1, n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            sub = dp[i - 1][j - 1] + (0 if a[i - 1] == b[j - 1] else 1)
            dp[i][j] = min(sub, dp[i - 1][j] + 1, dp[i][j - 1] + 1)

    # Traceback (prefer diagonal, then deletion of an extra candidate step).
    ops: list[AlignOp] = []
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + (0 if a[i - 1] == b[j - 1] else 1):
            op = MATCH if a[i - 1] == b[j - 1] else SUBSTITUTE
            ops.append(AlignOp(op, a[i - 1], b[j - 1]))
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i - 1][j] + 1:
            ops.append(AlignOp(EXTRA, a[i - 1], None))
            i -= 1
        else:
            ops.append(AlignOp(MISSING, None, b[j - 1]))
            j -= 1
    ops.reverse()
    return ops


def alignment_summary(ops: list[AlignOp]) -> dict[str, int]:
    """Count each op kind — e.g. ``{'match': 3, 'extra': 1, 'missing': 0, ...}``."""
    counts = {MATCH: 0, SUBSTITUTE: 0, EXTRA: 0, MISSING: 0}
    for o in ops:
        counts[o.op] += 1
    return counts
