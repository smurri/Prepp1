"""Typed exception hierarchy for the agent-eval engine.

All library errors derive from :class:`AgentEvalError`, so callers can catch the
whole family with a single ``except``. Selected errors also subclass a builtin
(``KeyError`` / ``ValueError``) so they behave intuitively in existing code.
"""

from __future__ import annotations


class AgentEvalError(Exception):
    """Base class for every error raised by this library."""


class UnknownQuestionError(AgentEvalError, KeyError):
    """Raised when scoring a ``question_id`` that has no registered references.

    Distinct from a *low* score: an unknown question is a programming error
    (nothing to compare against), not "the agent took a bad path".
    """


class NoReferencesError(AgentEvalError):
    """Raised when a question exists but has zero references to score against.

    Defensive: under normal use a question only exists once it has ≥1 reference.
    """


class InvalidTraceError(AgentEvalError, ValueError):
    """Raised when a value passed where a :class:`~agent_eval.models.Trace` /
    :class:`~agent_eval.models.Step` is expected is malformed."""
