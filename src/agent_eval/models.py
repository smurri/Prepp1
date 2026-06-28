"""Immutable value objects: :class:`Step` and :class:`Trace`.

A *Step* is a single tool call. A *Trace* (a.k.a. a *path*) is the ordered
sequence of tool calls an agent made to answer one question. Both are frozen and
hashable so they can be stored, compared, and deduplicated safely.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from .errors import InvalidTraceError


def _freeze_mapping(value: Mapping[str, Any]) -> Mapping[str, Any]:
    """Return an immutable, hashable view of a mapping (validates the type)."""
    if not isinstance(value, Mapping):
        raise InvalidTraceError(f"expected a mapping, got {type(value).__name__}")
    # MappingProxyType blocks mutation; tuple-of-items gives a stable hash.
    return MappingProxyType(dict(value))


@dataclass(frozen=True)
class Step:
    """A single tool call.

    Args:
        tool: Non-empty tool name (the primary similarity signal).
        args: Optional, opaque arguments (a secondary signal; off by default).
    """

    tool: str
    args: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.tool, str) or not self.tool.strip():
            raise InvalidTraceError("Step.tool must be a non-empty string")
        object.__setattr__(self, "args", _freeze_mapping(self.args))

    def __hash__(self) -> int:
        return hash((self.tool, tuple(sorted(self.args.items()))))


@dataclass(frozen=True)
class Trace:
    """An ordered path of tool calls.

    Construct directly from steps, or use :meth:`from_tools` for the common
    case of caring only about tool names.
    """

    steps: tuple[Step, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if isinstance(self.steps, Step):
            raise InvalidTraceError("Trace.steps must be a sequence of Step, not a single Step")
        if not isinstance(self.steps, Sequence) or isinstance(self.steps, str):
            raise InvalidTraceError("Trace.steps must be a sequence of Step")
        steps = tuple(self.steps)
        for s in steps:
            if not isinstance(s, Step):
                raise InvalidTraceError(f"every element must be a Step, got {type(s).__name__}")
        object.__setattr__(self, "steps", steps)
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))

    @classmethod
    def from_tools(cls, tools: Sequence[str], **metadata: Any) -> Trace:
        """Build a Trace from an ordered list of tool names.

        Example:
            >>> Trace.from_tools(["search", "lookup", "summarize"])
        """
        if isinstance(tools, str):
            raise InvalidTraceError("from_tools expects a sequence of names, not a single string")
        return cls(steps=tuple(Step(tool=t) for t in tools), metadata=metadata)

    @property
    def tool_names(self) -> tuple[str, ...]:
        """The ordered tuple of tool names — the primary comparison signal."""
        return tuple(s.tool for s in self.steps)

    def __len__(self) -> int:
        return len(self.steps)

    def __hash__(self) -> int:
        return hash((self.steps, tuple(sorted(self.metadata.items()))))
