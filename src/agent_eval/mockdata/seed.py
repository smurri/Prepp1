"""Realistic seed data: questions, known-good reference paths, and candidate runs.

This mimics what a real eval backend would hold — multiple questions across
domains, several human-curated reference executions per question (with author +
quality labels), and a spread of candidate agent runs (ideal / acceptable /
wasteful / wrong) so the engine has something meaningful to score.

Pure data (stdlib only). Both the SQL and NoSQL mock backends load from here, so
they return identical content through different storage shapes.
"""

from __future__ import annotations

from typing import Any

# A "path" is a list of {"tool": str, "args": {...}} dicts.
QUESTIONS: list[dict[str, Any]] = [
    {
        "question_id": "weather-paris",
        "text": "What will the weather be in Paris tomorrow?",
        "domain": "personal-assistant",
        "references": [
            {
                "author": "human-curated",
                "quality": "gold",
                "path": [
                    {"tool": "geocode", "args": {"city": "Paris"}},
                    {"tool": "weather_forecast", "args": {"day": "+1"}},
                    {"tool": "summarize", "args": {}},
                ],
            },
            {
                "author": "human-curated",
                "quality": "acceptable",
                "path": [
                    {"tool": "weather_forecast", "args": {"location": "Paris", "day": "+1"}},
                    {"tool": "summarize", "args": {}},
                ],
            },
        ],
        "candidates": [
            {"label": "ideal", "note": "exactly the gold path",
             "path": [
                 {"tool": "geocode", "args": {"city": "Paris"}},
                 {"tool": "weather_forecast", "args": {"day": "+1"}},
                 {"tool": "summarize", "args": {}},
             ]},
            {"label": "wasteful", "note": "redundant search before the forecast",
             "path": [
                 {"tool": "search", "args": {"q": "paris"}},
                 {"tool": "geocode", "args": {"city": "Paris"}},
                 {"tool": "weather_forecast", "args": {"day": "+1"}},
                 {"tool": "summarize", "args": {}},
             ]},
            {"label": "off-track", "note": "calculated instead of forecasting",
             "path": [
                 {"tool": "search", "args": {"q": "paris weather"}},
                 {"tool": "calculate", "args": {"expr": "1+1"}},
             ]},
        ],
    },
    {
        "question_id": "refund-order",
        "text": "Refund customer order #1234 if policy allows.",
        "domain": "customer-support",
        "references": [
            {
                "author": "ops-runbook",
                "quality": "gold",
                "path": [
                    {"tool": "lookup_order", "args": {"order_id": "1234"}},
                    {"tool": "check_refund_policy", "args": {}},
                    {"tool": "issue_refund", "args": {"order_id": "1234"}},
                    {"tool": "notify_customer", "args": {"channel": "email"}},
                ],
            },
        ],
        "candidates": [
            {"label": "ideal", "note": "follows the runbook",
             "path": [
                 {"tool": "lookup_order", "args": {"order_id": "1234"}},
                 {"tool": "check_refund_policy", "args": {}},
                 {"tool": "issue_refund", "args": {"order_id": "1234"}},
                 {"tool": "notify_customer", "args": {"channel": "email"}},
             ]},
            {"label": "skipped-policy", "note": "refunded without checking policy (risky)",
             "path": [
                 {"tool": "lookup_order", "args": {"order_id": "1234"}},
                 {"tool": "issue_refund", "args": {"order_id": "1234"}},
                 {"tool": "notify_customer", "args": {"channel": "email"}},
             ]},
            {"label": "no-notify", "note": "forgot to notify the customer",
             "path": [
                 {"tool": "lookup_order", "args": {"order_id": "1234"}},
                 {"tool": "check_refund_policy", "args": {}},
                 {"tool": "issue_refund", "args": {"order_id": "1234"}},
             ]},
        ],
    },
    {
        "question_id": "compare-gdp",
        "text": "Compare the GDP of France and Germany.",
        "domain": "research",
        "references": [
            {
                "author": "analyst-a",
                "quality": "gold",
                "path": [
                    {"tool": "search", "args": {"q": "France GDP"}},
                    {"tool": "fetch", "args": {"source": "worldbank"}},
                    {"tool": "search", "args": {"q": "Germany GDP"}},
                    {"tool": "fetch", "args": {"source": "worldbank"}},
                    {"tool": "calculate", "args": {"op": "ratio"}},
                    {"tool": "summarize", "args": {}},
                ],
            },
            {
                "author": "analyst-b",
                "quality": "acceptable",
                "path": [
                    {"tool": "search", "args": {"q": "France Germany GDP"}},
                    {"tool": "fetch", "args": {"source": "imf"}},
                    {"tool": "calculate", "args": {"op": "ratio"}},
                    {"tool": "summarize", "args": {}},
                ],
            },
        ],
        "candidates": [
            {"label": "thorough", "note": "matches analyst-a closely",
             "path": [
                 {"tool": "search", "args": {"q": "France GDP"}},
                 {"tool": "fetch", "args": {"source": "worldbank"}},
                 {"tool": "search", "args": {"q": "Germany GDP"}},
                 {"tool": "fetch", "args": {"source": "worldbank"}},
                 {"tool": "calculate", "args": {"op": "ratio"}},
                 {"tool": "summarize", "args": {}},
             ]},
            {"label": "concise", "note": "single combined search like analyst-b",
             "path": [
                 {"tool": "search", "args": {"q": "France Germany GDP"}},
                 {"tool": "fetch", "args": {"source": "imf"}},
                 {"tool": "calculate", "args": {"op": "ratio"}},
                 {"tool": "summarize", "args": {}},
             ]},
            {"label": "hallucinated", "note": "no fetch, summarized from nothing",
             "path": [
                 {"tool": "search", "args": {"q": "gdp"}},
                 {"tool": "summarize", "args": {}},
             ]},
        ],
    },
]
