# Prepp1




Agent Eval Engine — AI-Assisted Coding Interview
Problem Statement
Design and implement an Agent Eval Engine — a library that scores how well an AI agent handles a new question by comparing the agent's execution path to previously observed reference paths.

Think of this as the scoring layer behind any system that needs to answer: "Did the agent take a good path to answer this question?"

Context
An AI agent processes user questions by making a series of tool calls (e.g., search, lookup, calculate, summarize). For any given question, there may be multiple valid paths — some better than others. Your engine stores reference paths (known-good executions) and scores new executions by how closely they resemble those references.

Constraints
This is a library, not a web service — no HTTP, no database, no persistence needed
All state is in-memory
Focus on clean API design, correct logic, and testability

 
