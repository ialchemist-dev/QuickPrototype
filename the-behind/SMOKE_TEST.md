# Smoke Test Log — The Behind pipeline

Run date: 2026-11-24. Profile: **SMOKE** (raw_target 60, survivor_cap 8 at depth 1, cap 6 per depth-2 expansion, depth_cap 2, node_budget 60, year_floor 1500). Executed by an agent following RUNBOOK.md end-to-end: scout → resolve → judge → evaluate → gates → verify → render. Embedder used: `tfidf-fallback` (no sentence-transformers on this machine; see "Known limitations").

## Counts at each stage

### Depth 1 — expand the root (The modern AI agent, 2023)

| Stage | Count |
|---|---|
| Raw candidates scouted (10 lenses, real web searches) | 107 |
| Dropped by hard year bound (Toolformer, 2023 = parent year) | 1 |
| Distinct after identity resolution | 95 |
| Judge pairs adjudicated (8 SAME, 1 DIFFERENT) | 9 |
| Distinct after judgments | 87 |
| Evaluated against the 12 questions (all with full verdict sets) | 87 |
| Gate survivors (smoke cap 8) | **8** |
| Rejected (gate fail or below cap) | 79 |

### Depth 2a — expand Transformer architecture (2017)

| Stage | Count |
|---|---|
| Raw candidates | 50 |
| Distinct after resolution (9 auto-merges) | 41 |
| Judge pairs (13 SAME — incl. 11 candidate-vs-existing-node pairs) | 13 |
| Distinct after judgments | 39 |
| Evaluated | 39 |
| Gate survivors (cap 6) | **6** = 5 new nodes + **1 linked to an existing node** |
| Rejected | 33 |

### Depth 2b — expand Cross-entropy loss (1948)

| Stage | Count |
|---|---|
| Raw candidates (all pre-1948, back to 1564) | 50 |
| Distinct after resolution (4 auto-merges, post-patch — see Bug 4) | 46 |
| Judge pairs (4 SAME) | 4 |
| Distinct after judgments | 42 |
| Evaluated | 42 |
| Gate survivors (cap 6) | **6** (all new nodes) |
| Rejected | 36 |

### Totals

- Raw candidates seen: **207**; evaluated: **168**; rejected overall: **148**; merges logged: **29**.
- Final graph: **20 nodes, 20 edges** (depth 0: 1, depth 1: 8, depth 2: 11). Node budget used: 20 / 60.

### Verifier pass (§6, all 19 non-root survivors)

- **Verified: 2** — Neural probabilistic language model (2003); Gibbs's statistical mechanics and Gibbs entropy (1902).
- **Provisional: 17** — survive, each with a documented weakness. The multiples test did most of the damage, exactly as designed: Napier's logarithms (Bürgi multiple), ResNet (Highway Networks, same year), sequence-to-sequence (Cho et al. simultaneous with Sutskever et al.), backpropagation (a textbook priority case: Linnainmaa 1970, Werbos 1974), stored-program architecture (priority dispute), CUDA (Q1 overstated — GPGPU predated it), gradient descent (independent rediscoveries), cross-entropy (dating/naming: Shannon 1948 introduced entropy; the loss form crystallized later).
- **Killed: 0.**

## Node list

**Depth 0:** The modern AI agent (2023).

**Depth 1 (predecessors of the agent):** Transformer architecture (2017) · Stored-program architecture (1945) · Cross-entropy loss (1948) · Word2vec embeddings (2013) · CUDA (2007) · Gradient descent (1847) · Linnainmaa's automatic differentiation (1970) · Attention mechanism (Bahdanau) (2014).

**Depth 2 (predecessors of the Transformer):** Deep Residual Learning (ResNet) (2015) · Backpropagation (1986) · Sequence-to-sequence learning (2014) · Layer Normalization (2016) · Neural probabilistic language model (2003) · + Attention mechanism (Bahdanau) (2014) — **linked to the existing depth-1 node, not duplicated**.

**Depth 2 (predecessors of cross-entropy loss):** Napier's logarithms (1614) · Huygens's expectation (1657) · Boltzmann's entropy formula (1877) · Gibbs's statistical mechanics and Gibbs entropy (1902) · Fisher's maximum likelihood estimation (1922) · Hartley's logarithmic measure of information (1928).

## Example chains

1. **The diamond (DAG convergence):** The modern AI agent → Transformer architecture (2017) → Attention mechanism (Bahdanau) (2014), where Bahdanau attention is *also* a direct predecessor of the agent — one node, two edges (in-degree 2, direct Q11 evidence).
2. **The architecture line:** The modern AI agent → Transformer architecture (2017) → Sequence-to-sequence learning (2014), and → Layer Normalization (2016), → Deep Residual Learning (ResNet) (2015), → Backpropagation (1986), → Neural probabilistic language model (2003).
3. **The information line:** The modern AI agent → Cross-entropy loss (1948) → Hartley's logarithmic measure of information (1928) → (and in parallel) → Gibbs entropy (1902), → Boltzmann's entropy formula (1877), → Fisher's maximum likelihood (1922), → Napier's logarithms (1614), → Huygens's expectation (1657). The chain reaches 1614/1657 in two hops — the recursion escapes the AI era immediately, as intended.

## Bugs found and fixed

1. **Name-containment pairs never reached the judge (dev phase).** "Transformer" vs "Transformer architecture" scored TF-IDF cosine 0.7677 — below the 0.80 gray band — although SAME-vs-SUBTYPE is precisely the judge's question. Fix: a containment rule in `identity.py` forces name-containment pairs into the gray zone.
2. **Missing CLI command.** The evaluator needs the final distinct cand_ids after judgments; added `show-distinct` to `pipeline.py` and aligned RUNBOOK.md.
3. **Frontier included verifier-killed nodes.** `graph.frontier()` now excludes nodes marked dead by verification.
4. **cand_id collision via the type veto (found in this smoke run).** "Halley's Breslau life table (1693)" was scouted twice with different type labels (`material` vs `method`). The signal-4 type-mismatch veto blocked the signal-2 alias match, leaving two clusters that then received the *same* cand_id (slugify had no uniqueness guard) — downstream lookups would have silently aliased them. Fixes in `identity.py`: (a) per §4.5's signal ordering, an exact normalized-name match **with the same year** settles identity at the alias tier and is not blocked by the type veto (the year-gap veto still applies); (b) cand_id disambiguation guard in the distinct-list build. Re-ran resolution for the cross-entropy expansion: 47 → 46 distinct, zero duplicate ids; unit-checked with the Halley pattern.
5. **Process bug (not code):** long JSON replies from worker agents were truncated in delivery. All scout/evaluator/verifier deliverables were switched to file writes with count-only replies; coverage was then machine-validated (87/87, 39/39, 42/42 cand_ids, complete 12-question sets).

## Known limitations observed

- **TF-IDF fallback cosine scale runs low** (observed range ~0.22–0.70 on true matches). The strong band (≥0.92) effectively never fires; the gray zone + judge carried identity resolution (26 judge pairs across the run). This errs toward "different" — safe under the design's precision-over-recall rule — but a MiniLM embedder should be installed for the full run so the bands behave as calibrated in §4.5.
- **Acceptable false splits remain** (precision bias, cheap to fix later, per design): in the root pool, Bahdanau attention and ReAct each appeared under two cand_ids; in the cross-entropy pool, Gibbs entropy, Bayes, Graunt, and de Moivre each appeared twice under different names (in each case at most one twin survived the gate).
- Scout-assigned `type` labels are lens-dependent (the same milestone arrived as both `material` and `method`); Bug 4's fix covers the exact-name case, but type should be treated as soft evidence in future calibration.
- Render QA: the page is a single self-contained HTML file; its embedded JS passes `node --check`; all 20 node names are present in the output; trace view, timeline view, search, and the detail panel (bottleneck, per-edge 12-question verdict tables with evidence and falsification, sources, status, verifier notes) are all in the generated file. No browser screenshot check was run.

## Rendered page

`smoke/index.html` (in this folder) — generated from `smoke/graph.json` by `pipeline.py render`. Open the file directly in a browser; no server or external assets needed.
