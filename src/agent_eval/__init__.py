"""agent_eval — score an AI agent's tool-call path against reference paths.

Quick start::

    from agent_eval import EvalEngine, Trace

    engine = EvalEngine()
    engine.add_reference("q1", Trace.from_tools(["search", "lookup", "summarize"]))

    result = engine.score("q1", Trace.from_tools(["search", "lookup", "summarize"]))
    assert result.score == 1.0
"""

from __future__ import annotations

from . import aggregation
from .aggregation import MAX, MEAN, Aggregation, TopKMean
from .comparators import (
    CompositeComparator,
    JaccardComparator,
    LCSComparator,
    PathComparator,
    SequenceComparator,
    StepSimilarity,
    tool_and_args,
    tool_match,
)
from .engine import EvalEngine
from .errors import (
    AgentEvalError,
    InvalidTraceError,
    NoReferencesError,
    UnknownQuestionError,
)
from .models import Step, Trace
from .results import ReferenceScore, ScoreResult

__version__ = "0.1.0"

__all__ = [
    "MAX",
    "MEAN",
    "Aggregation",
    "AgentEvalError",
    "CompositeComparator",
    "EvalEngine",
    "InvalidTraceError",
    "JaccardComparator",
    "LCSComparator",
    "NoReferencesError",
    "PathComparator",
    "ReferenceScore",
    "ScoreResult",
    "SequenceComparator",
    "Step",
    "StepSimilarity",
    "TopKMean",
    "Trace",
    "UnknownQuestionError",
    "aggregation",
    "tool_and_args",
    "tool_match",
    "__version__",
]
