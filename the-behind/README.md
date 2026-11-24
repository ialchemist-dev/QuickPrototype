# The Behind — Tracing the Milestones

This subproject builds a recursive pipeline that traces backwards from the modern AI agent, interrogating each predecessor breakthrough with 12 fixed questions to build a merged graph (a DAG) of what made the agent possible. The graph becomes an interactive page on AI Praxis Lab (The Behind) that readers can explore node by node.

**Status:** design v2 approved 2026-11-24; smoke test (depth 2) completed 2026-11-24 — see [SMOKE_TEST.md](SMOKE_TEST.md). Rendered smoke graph: `smoke/index.html`.

## Documents

- [DESIGN.md](DESIGN.md) — the design document, for humans
- [RUNBOOK.md](RUNBOOK.md) — execution instructions, for executing agents

The pipeline code lives in `pipeline/` and is run by following RUNBOOK.md.
