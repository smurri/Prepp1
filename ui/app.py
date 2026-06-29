"""Streamlit UI for the Agent Eval Engine.

Run with::

    uv sync --extra ui
    uv run streamlit run ui/app.py

Pick a mock backend (SQL / NoSQL), a comparator and aggregation, a question, and
a candidate path — then see the score and an explainable per-reference breakdown.
This is a thin presentation layer; all logic lives in the ``agent_eval`` package.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from agent_eval import (
    CompositeComparator,
    EvalEngine,
    JaccardComparator,
    LCSComparator,
    SequenceComparator,
    Trace,
    tool_and_args,
)
from agent_eval.aggregation import MAX, MEAN, TopKMean
from agent_eval.mockdata import NoSqlBackend, SqlBackend, hydrate

st.set_page_config(page_title="Agent Eval Engine", page_icon="🧭", layout="wide")

BACKENDS = {"SQL (SQLite, in-memory)": SqlBackend, "NoSQL (document store)": NoSqlBackend}


def build_comparator(key: str, credit_args: bool):
    step_sim = tool_and_args(0.5) if credit_args else None
    if key == "Sequence (edit distance)":
        return SequenceComparator(step_sim) if step_sim else SequenceComparator()
    if key == "Jaccard (set overlap)":
        return JaccardComparator()
    if key == "LCS (subsequence)":
        return LCSComparator()
    # Composite blends sequence + jaccard
    seq = SequenceComparator(step_sim) if step_sim else SequenceComparator()
    return CompositeComparator([(seq, 0.7), (JaccardComparator(), 0.3)])


def build_aggregation(key: str, k: int):
    return {"max": MAX, "mean": MEAN, "top-k mean": TopKMean(k)}[key]


def path_chips(tools: list[str]) -> str:
    return " → ".join(f"`{t}`" for t in tools) if tools else "_(empty path)_"


@st.cache_resource
def get_backend(name: str):
    return BACKENDS[name]()


# --- sidebar: configuration ------------------------------------------------
st.sidebar.header("⚙️ Configuration")
backend_name = st.sidebar.selectbox("Backend (mock DB)", list(BACKENDS))
comparator_key = st.sidebar.selectbox(
    "Comparator",
    ["Sequence (edit distance)", "Jaccard (set overlap)", "LCS (subsequence)",
     "Composite (seq+jaccard)"],
)
credit_args = st.sidebar.checkbox("Credit matching args (tool_and_args)", value=False)
agg_key = st.sidebar.selectbox("Aggregation", ["max", "mean", "top-k mean"])
k = st.sidebar.number_input("k (for top-k mean)", min_value=1, max_value=10, value=2)

backend = get_backend(backend_name)
comparator = build_comparator(comparator_key, credit_args)
aggregation = build_aggregation(agg_key, int(k))

engine = EvalEngine(comparator=comparator, aggregation=aggregation)
ref_ids = hydrate(engine, backend)

# --- header ----------------------------------------------------------------
st.title("🧭 Agent Eval Engine")
st.caption("Score an AI agent's tool-call path against known-good reference paths. "
           f"Data source: **{backend.name}**")

# --- question picker -------------------------------------------------------
questions = backend.questions()
labels = {f"[{q.domain}] {q.text}": q for q in questions}
chosen = st.selectbox("Question", list(labels))
question = labels[chosen]

left, right = st.columns(2)

with left:
    st.subheader("📚 Reference paths (known-good)")
    refs = backend.reference_paths(question.question_id)
    for rid, ref in zip(ref_ids[question.question_id], refs, strict=True):
        st.markdown(f"**ref#{rid}** · _{ref.quality}_ · by `{ref.author}`")
        st.markdown(path_chips(list(ref.trace.tool_names)))

with right:
    st.subheader("🤖 Candidate path to score")
    candidates = backend.candidates(question.question_id)
    cand_labels = {f"{c.label} — {c.note}": c for c in candidates}
    mode = st.radio("Source", ["Pick a sample run", "Build my own"], horizontal=True)

    if mode == "Pick a sample run":
        cand = cand_labels[st.selectbox("Sample candidate", list(cand_labels))]
        candidate_tools = list(cand.trace.tool_names)
    else:
        all_tools = sorted({t for q in questions
                            for ref in backend.reference_paths(q.question_id)
                            for t in ref.trace.tool_names}
                           | {"search", "calculate"})
        candidate_tools = st.multiselect(
            "Build an ordered path (selection order = call order)", all_tools)

    st.markdown("**Your path:** " + path_chips(candidate_tools))

# --- score -----------------------------------------------------------------
if st.button("Score this path", type="primary", use_container_width=True):
    result = engine.score(question.question_id, Trace.from_tools(candidate_tools))
    c1, c2, c3 = st.columns(3)
    c1.metric("Score", f"{result.score:.2f}")
    c2.metric("Best match", f"ref#{result.best.reference_id}" if result.best else "—")
    c3.metric("Comparator / agg", f"{result.comparator} / {result.aggregation}")
    st.progress(result.score)

    rows = [
        {"reference": f"ref#{rs.reference_id}", "similarity": round(rs.similarity, 3),
         "reference_steps": rs.reference_steps}
        for rs in result.breakdown
    ]
    st.subheader("🔎 Per-reference breakdown")
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
