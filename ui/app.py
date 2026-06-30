"""Streamlit dashboard for the Agent Eval Engine.

Run with::

    uv sync --extra ui
    uv run streamlit run ui/app.py

Two views: a single-path eval (score, PASS/FAIL, per-reference breakdown, and a
step-by-step alignment explaining *why*) and a batch eval report across every
sample candidate. Thin presentation layer — all logic lives in ``agent_eval``.
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
    align,
    alignment_summary,
    tool_and_args,
)
from agent_eval.aggregation import MAX, MEAN, TopKMean
from agent_eval.explain import EXTRA, MATCH, MISSING, SUBSTITUTE
from agent_eval.mockdata import NoSqlBackend, SqlBackend, hydrate

st.set_page_config(page_title="Agent Eval Engine", page_icon="🧭", layout="wide")

BACKENDS = {"SQL (SQLite, in-memory)": SqlBackend, "NoSQL (document store)": NoSqlBackend}
_OP_ICON = {MATCH: "✅ match", SUBSTITUTE: "🔁 substitute",
            EXTRA: "➕ extra (candidate)", MISSING: "➖ missing (reference)"}


def build_comparator(key: str, credit_args: bool):
    step_sim = tool_and_args(0.5) if credit_args else None
    if key == "Sequence (edit distance)":
        return SequenceComparator(step_sim) if step_sim else SequenceComparator()
    if key == "Jaccard (set overlap)":
        return JaccardComparator()
    if key == "LCS (subsequence)":
        return LCSComparator()
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
threshold = st.sidebar.slider("Pass threshold", 0.0, 1.0, 0.80, 0.05)

backend = get_backend(backend_name)
comparator = build_comparator(comparator_key, credit_args)
aggregation = build_aggregation(agg_key, int(k))

engine = EvalEngine(comparator=comparator, aggregation=aggregation)
ref_ids = hydrate(engine, backend)
questions = backend.questions()


def best_reference_trace(question_id: str, reference_id: int) -> Trace | None:
    for rid, trace in engine.reference_items(question_id):
        if rid == reference_id:
            return trace
    return None


st.title("🧭 Agent Eval Engine")
st.caption(f"Score agent tool-call paths against known-good references · "
           f"source: **{backend.name}** · comparator: **{comparator.name}** · "
           f"pass ≥ **{threshold:.2f}**")

single_tab, batch_tab = st.tabs(["🔬 Single eval", "📊 Batch report"])

# =========================================================================
# SINGLE EVAL
# =========================================================================
with single_tab:
    labels = {f"[{q.domain}] {q.text}": q for q in questions}
    question = labels[st.selectbox("Question", list(labels))]

    left, right = st.columns(2)
    with left:
        st.subheader("📚 Reference paths (known-good)")
        for rid, ref in zip(ref_ids[question.question_id],
                            backend.reference_paths(question.question_id), strict=True):
            st.markdown(f"**ref#{rid}** · _{ref.quality}_ · by `{ref.author}`")
            st.markdown(path_chips(list(ref.trace.tool_names)))

    with right:
        st.subheader("🤖 Candidate path")
        candidates = backend.candidates(question.question_id)
        cand_labels = {f"{c.label} — {c.note}": c for c in candidates}
        mode = st.radio("Source", ["Pick a sample run", "Build my own"], horizontal=True)
        if mode == "Pick a sample run":
            cand = cand_labels[st.selectbox("Sample candidate", list(cand_labels))]
            candidate_tools = list(cand.trace.tool_names)
        else:
            all_tools = sorted({t for q in questions
                                for ref in backend.reference_paths(q.question_id)
                                for t in ref.trace.tool_names} | {"search", "calculate"})
            candidate_tools = st.multiselect(
                "Build an ordered path (selection order = call order)", all_tools)
        st.markdown("**Your path:** " + path_chips(candidate_tools))

    if st.button("Score this path", type="primary", use_container_width=True):
        candidate = Trace.from_tools(candidate_tools)
        result = engine.score(question.question_id, candidate)
        passed = result.score >= threshold

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Score", f"{result.score:.2f}")
        c2.metric("Result", "✅ PASS" if passed else "❌ FAIL")
        c3.metric("Best match", f"ref#{result.best.reference_id}" if result.best else "—")
        c4.metric("Comparator / agg", f"{result.comparator} / {result.aggregation}")
        st.progress(result.score)

        st.subheader("🔎 Per-reference breakdown")
        st.dataframe(
            pd.DataFrame([
                {"reference": f"ref#{rs.reference_id}", "similarity": round(rs.similarity, 3),
                 "reference_steps": rs.reference_steps}
                for rs in result.breakdown
            ]),
            use_container_width=True, hide_index=True,
        )

        if result.best:
            ref_trace = best_reference_trace(question.question_id, result.best.reference_id)
            ops = align(candidate, ref_trace)
            summary = alignment_summary(ops)
            st.subheader(f"🧬 Step alignment vs ref#{result.best.reference_id} (why this score)")
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("✅ matched", summary[MATCH])
            s2.metric("🔁 substituted", summary[SUBSTITUTE])
            s3.metric("➕ extra", summary[EXTRA])
            s4.metric("➖ missing", summary[MISSING])
            st.dataframe(
                pd.DataFrame([
                    {"#": i + 1, "candidate": o.candidate or "—",
                     "reference": o.reference or "—", "op": _OP_ICON[o.op]}
                    for i, o in enumerate(ops)
                ]),
                use_container_width=True, hide_index=True,
            )

# =========================================================================
# BATCH REPORT
# =========================================================================
with batch_tab:
    st.subheader("📊 Batch evaluation — every sample candidate")
    rows = []
    for q in questions:
        for cand in backend.candidates(q.question_id):
            result = engine.score(q.question_id, cand.trace)
            edits = sum(1 for o in align(cand.trace,
                        best_reference_trace(q.question_id, result.best.reference_id)
                        or Trace()) if o.op != MATCH) if result.best else None
            rows.append({
                "question": q.question_id,
                "candidate": cand.label,
                "score": round(result.score, 3),
                "result": "✅ PASS" if result.score >= threshold else "❌ FAIL",
                "best_ref": f"ref#{result.best.reference_id}" if result.best else "—",
                "edits_vs_best": edits,
                "note": cand.note,
            })
    df = pd.DataFrame(rows)

    m1, m2, m3 = st.columns(3)
    pass_rate = (df["result"].str.contains("PASS")).mean() if len(df) else 0.0
    m1.metric("Candidates", len(df))
    m2.metric("Pass rate", f"{pass_rate:.0%}")
    m3.metric("Mean score", f"{df['score'].mean():.2f}" if len(df) else "—")

    st.dataframe(df, use_container_width=True, hide_index=True)
    if len(df):
        chart_df = df.assign(label=df["question"] + " / " + df["candidate"])
        st.bar_chart(chart_df.set_index("label")["score"])
