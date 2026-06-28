# Design — Agent Eval Engine (Phases 2–4, frozen)

## Module responsibilities
| Module | Responsibility |
|---|---|
| `models` | Immutable value objects `Step`, `Trace`. Validation at construction. |
| `comparators` | `PathComparator` protocol + `SequenceComparator` (default), `JaccardComparator`, `LCSComparator`, `CompositeComparator`; `StepSimilarity` callables. |
| `aggregation` | `Aggregation` strategies: `MAX` (default), `MEAN`, `TopKMean(k)`. |
| `results` | `ReferenceScore`, `ScoreResult` (explainable, frozen). |
| `store` | `ReferenceStore`: thread-safe in-memory `question_id → {ref_id: Trace}`. |
| `engine` | `EvalEngine` facade: validate, store, score, aggregate. |
| `errors` | `AgentEvalError` hierarchy. |

## Public interfaces (signatures — contracts)
```python
# models.py
@dataclass(frozen=True)
class Step:
    tool: str
    args: Mapping[str, Any] = {}            # validated non-empty tool

@dataclass(frozen=True)
class Trace:
    steps: tuple[Step, ...]
    metadata: Mapping[str, Any] = {}
    @classmethod
    def from_tools(cls, tools: Sequence[str], **metadata: Any) -> "Trace": ...
    @property
    def tool_names(self) -> tuple[str, ...]: ...
    def __len__(self) -> int: ...

# comparators.py
StepSimilarity = Callable[[Step, Step], float]          # -> [0,1]
def tool_match(a: Step, b: Step) -> float: ...           # default: 1.0/0.0
def tool_and_args(tool_weight: float = 0.5) -> StepSimilarity: ...

class PathComparator(Protocol):
    name: str
    def compare(self, candidate: Trace, reference: Trace) -> float: ...   # -> [0,1]

class SequenceComparator:   # normalized weighted edit distance (DEFAULT)
    def __init__(self, step_similarity: StepSimilarity = tool_match) -> None: ...
class JaccardComparator: ...     # set overlap of tool names
class LCSComparator: ...         # longest-common-subsequence ratio
class CompositeComparator:       # weighted blend
    def __init__(self, parts: Sequence[tuple[PathComparator, float]]) -> None: ...

# aggregation.py
class Aggregation(Protocol):
    name: str
    def __call__(self, scores: Sequence[float]) -> float: ...
MAX: Aggregation; MEAN: Aggregation
class TopKMean: 
    def __init__(self, k: int) -> None: ...

# results.py
@dataclass(frozen=True)
class ReferenceScore:
    reference_id: int
    similarity: float
    reference_steps: int

@dataclass(frozen=True)
class ScoreResult:
    score: float
    question_id: str
    comparator: str
    aggregation: str
    candidate_steps: int
    breakdown: tuple[ReferenceScore, ...]     # sorted by similarity desc
    @property
    def best(self) -> ReferenceScore | None: ...
    def __float__(self) -> float: ...

# engine.py
class EvalEngine:
    def __init__(self, comparator: PathComparator | None = None,
                 aggregation: Aggregation | None = None) -> None: ...
    def add_reference(self, question_id: str, trace: Trace) -> int: ...
    def add_references(self, question_id: str, traces: Iterable[Trace]) -> list[int]: ...
    def references(self, question_id: str) -> list[Trace]: ...
    def remove_reference(self, question_id: str, reference_id: int) -> bool: ...
    def clear(self, question_id: str | None = None) -> None: ...
    def score(self, question_id: str, candidate: Trace, *,
              comparator: PathComparator | None = None,
              aggregation: Aggregation | None = None) -> ScoreResult: ...
```

## Control & data flow
`add_reference` → validate → `ReferenceStore` assigns monotonic int id under a lock → returns id.
`score` → validate question exists (else `UnknownQuestionError`) and candidate is a `Trace` →
snapshot references under lock → for each ref compute `comparator.compare(candidate, ref)` →
sort into `breakdown` → `aggregation(similarities)` → assemble frozen `ScoreResult`.
**Source of truth:** the `ReferenceStore` dict. `score()` never mutates it.

## Error & boundary strategy
- `EvalEngine` is the trust boundary: validates types, non-empty tool names, known question.
- Errors: `UnknownQuestionError(KeyError)`, `NoReferencesError`, `InvalidTraceError(ValueError)`,
  all under `AgentEvalError`.
- Failure isolation: a comparator that raises on one reference aborts that `score()` call with a
  clear error rather than silently scoring 0 (corrupt input should be loud).

## Edge cases (handled)
empty candidate, empty reference, both empty, single-step paths, duplicate references,
unknown question, removing a missing id (returns `False`), `TopKMean(k > n)` (uses all),
non-`Trace` candidate, `Step` with empty tool name.

## Decomposition — vertical slices (build order)
1. **Skeleton:** `models` + `errors` + `SequenceComparator` + `EvalEngine.add_reference/score`
   with `MAX` → end-to-end "register one ref, score one candidate". *(walking skeleton)*
2. **Breadth of comparators:** `Jaccard`, `LCS`, `Composite` + step-similarity variants.
3. **Aggregation:** `MEAN`, `TopKMean`, per-call overrides.
4. **Lifecycle:** `add_references`, `references`, `remove_reference`, `clear`, thread-safety.
5. **Explainability + packaging:** `ScoreResult.breakdown/best`, README, full test suite.

## Validation (Phase 3) — issues found & resolved
- *Float drift could push score to 1.0000001* → clamp every comparator output to `[0,1]`.
- *Edit-distance normalization divide-by-zero on empty/empty* → special-case → `1.0`.
- *`max([])` raises on a question with zero refs* → can't happen (question exists ⇒ ≥1 ref);
  guarded by `NoReferencesError` defensively.
- *Mutable `args`/`metadata` dicts break frozen immutability/hash* → wrap in `MappingProxyType`.
- *Concurrent `add` + `score` race* → snapshot references under a lock before scoring.
- *Adversarial huge paths* → documented `O(R·m·n)`; acceptable at stated scale (no DoS surface,
  it's an in-process library).
