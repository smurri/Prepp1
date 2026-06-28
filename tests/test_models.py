import pytest

from agent_eval import InvalidTraceError, Step, Trace


def test_step_requires_non_empty_tool():
    with pytest.raises(InvalidTraceError):
        Step(tool="")
    with pytest.raises(InvalidTraceError):
        Step(tool="   ")


def test_step_is_frozen_and_args_immutable():
    s = Step(tool="search", args={"q": "x"})
    with pytest.raises(AttributeError):  # frozen dataclass → FrozenInstanceError
        s.tool = "other"  # type: ignore[misc]
    with pytest.raises(TypeError):
        s.args["q"] = "y"  # MappingProxyType blocks mutation


def test_trace_from_tools_builds_steps_in_order():
    t = Trace.from_tools(["search", "lookup", "summarize"])
    assert t.tool_names == ("search", "lookup", "summarize")
    assert len(t) == 3
    assert all(isinstance(s, Step) for s in t.steps)


def test_trace_from_tools_rejects_bare_string():
    with pytest.raises(InvalidTraceError):
        Trace.from_tools("search")  # a string is a sequence of chars — reject it


def test_trace_rejects_non_step_elements():
    with pytest.raises(InvalidTraceError):
        Trace(steps=("search",))  # type: ignore[arg-type]


def test_trace_is_hashable_and_equal_by_value():
    a = Trace.from_tools(["search", "lookup"])
    b = Trace.from_tools(["search", "lookup"])
    assert a == b
    assert hash(a) == hash(b)
    assert len({a, b}) == 1


def test_empty_trace_is_valid():
    t = Trace()
    assert len(t) == 0
    assert t.tool_names == ()
