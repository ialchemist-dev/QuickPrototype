# RUNBOOK — The Behind 01: Recursive Milestone Pipeline

**Read only this file and you can execute the entire pipeline.** It is
self-contained: purpose, setup, configuration, the graph format, the
step-by-step loop, every prompt verbatim, exact commands, the
checkpoint/resume protocol, stop conditions, rendering, and
troubleshooting. Background and rationale live in `DESIGN.md`; you do
not need it to run.

---

## 0. Purpose (5 lines)

1. Trace the breakthroughs that made the modern AI agent possible, backwards through history, as a merged graph (DAG), not a tree.
2. Start from one root node; repeatedly expand the best unexpanded node: scout ≈100 earlier candidate advances, resolve their identities, interrogate each with 12 fixed questions, prune by fixed gates to a capped set of survivors.
3. Each survivor becomes a node with a "bottleneck sentence"; edges read "enabled by". The same advance reached from many children is one node — convergence is the point.
4. Survivors face an adversarial verifier (multiples test, date check) and are marked `verified` or stay `provisional`.
5. At any point, render the graph to a single interactive HTML page.

Your role as the executing agent: you do the judgment work (scouting,
evaluating, judging identity pairs, verifying). The CLI in `pipeline/`
does all bookkeeping deterministically. **Never edit `graph.json` by
hand** — every state change goes through the CLI, which checkpoints
after every mutation.

---

## 1. Prerequisites and setup

- Python 3.10+ (developed on 3.12). The pipeline is **stdlib-only** and
  runs with no installs.
- Optional: `pip install sentence-transformers` enables the semantic
  embedder (all-MiniLM-L6-v2) for identity resolution. Without it, a
  TF-IDF fallback is used automatically (recorded in every resolution
  output). The fallback is safe: it errs toward "different" (§4.5's
  precision-over-recall bias), and name-containment pairs are still
  routed to you as judge.
- Web search access (for the scout and verifier steps).
- Working directory for everything below: this folder, `the-behind/`.
- CLI entry point: `python3 pipeline/pipeline.py <command> --graph <path> ...`
  In all commands below, `G` means your graph path (see §2).

Sanity check before a run:

```sh
cd the-behind
python3 pipeline/pipeline.py init --graph /tmp/_check.json --profile smoke --force
python3 pipeline/pipeline.py status --graph /tmp/_check.json
```

---

## 2. Configuration

Two profiles ship with the code. `init` snapshots the chosen profile
into the graph file; the snapshot governs the whole run.

### FULL-RUN profile (the design values — DESIGN.md §7)

| Key | Value | Meaning |
|---|---|---|
| `raw_target` | 100 | raw candidates to scout per expansion |
| `survivor_cap` | 20 | max survivors admitted per expansion |
| `depth_cap` | 10 | maximum depth (root = 0) |
| `node_budget` | 2000 | global live-node budget for the run |
| `min_gate_survivors` | 5 | an expansion yielding fewer survivors does not stop the run, but a *node* whose own later expansion would start from a pool this thin is a stop signal (see §8) |
| `year_floor` | 1500 | do not expand nodes whose candidate pool falls before ~1500 |

Start a full run:

```sh
mkdir -p runs/full/work
python3 pipeline/pipeline.py init --graph runs/full/graph.json --profile full
# G = runs/full/graph.json ; root id is printed (the-modern-ai-agent-2023)
```

### SMOKE-RUN profile (pipeline validation only — NOT design values)

| Key | Value | Meaning |
|---|---|---|
| `raw_target` | 60 | scout target per expansion |
| `survivor_cap` | 8 | cap for the depth-1 expansion |
| `depth_cap` | 2 | root + two levels |
| `node_budget` | 60 | plenty for a smoke graph |
| `min_gate_survivors` | 2 | — |
| `year_floor` | 1500 | — |

Smoke procedure (exact): init smoke → expand the root (cap 8) → expand
**two** of the survivors with `--cap 6` on `apply-verdicts` → verify
**all** survivors → render → write up counts in `SMOKE_TEST.md`.

```sh
mkdir -p smoke/work
python3 pipeline/pipeline.py init --graph smoke/graph.json --profile smoke
# G = smoke/graph.json
```

---

## 3. The graph file

One JSON file per run (path = `G`). Top-level keys:

- `config` — the profile snapshot (§2).
- `run_state` — `expansions_done`, `raw_candidates_seen`, and
  `rejected`: every rejected candidate with its parent and reason. This
  list is the `{already_rejected}` input for future scouts of the same
  parent, and `resolve` automatically drops exact repeats of it.
- `nodes` — id → node record: `name`, `aliases`, `year`, `domain`,
  `type` (`device|theory|method|material|institution|other`),
  `definition` (one sentence), `bottleneck` (one sentence, form:
  "Before X, Y was impossible or impractical because Z."), `status`
  (`provisional|verified`), `depth`, `expanded`, `priority` (admission
  score; frontier is best-first), `sources` (list of `{title, url}`),
  `verification`, `merged_into` (union-find pointer; non-null nodes are
  merged away and invisible).
- `edges` — `{predecessor_id, successor_id, verdicts, score, gate}`.
  Reads: predecessor **enabled** successor (removed its bottleneck).
  `verdicts` holds the 12 answers for that predecessor *in relation to
  that successor*.
- `merge_log` — every identity merge with signals, scores, and the
  judge's one-sentence reason. Merges are reversible in the data model
  (`graph.py: unmerge`); there is no CLI for it — if you need one, stop
  and escalate rather than editing JSON.
- `expansions` — per-node working state: raw candidates, resolution,
  judge queue, stage (`scouted → resolved → judged → evaluated`). This
  is what makes an interrupted expansion resumable.

Checkpointing: the CLI rewrites `G` atomically after **every** command.
A crash loses at most the command in flight.

---

## 4. The loop (one expansion, step by step)

Repeat until a stop condition (§8) fires. Each iteration expands ONE
node: the first entry of the frontier.

### Step 0 — Pick the node

```sh
python3 pipeline/pipeline.py status --graph $G
```

`frontier_detail[0]` is your node (best-first by admission score).
Note its `id`, `name`, `year`, `domain`, `bottleneck`. Call it PARENT.

### Step 1 — Scout (you, with web search)

Fill the SCOUT PROMPT (§6.1) slots for PARENT:

- `{existing_nodes}`: the canonical names of all live nodes — get them
  from `status` output / the graph's node names you already know.
- `{already_rejected}`: names in `run_state.rejected` with
  `parent_id == PARENT.id` (empty on a first expansion).

Run the 10 lenses, ≥2 query variants each, and write the resulting
JSON array to `work/candidates_<PARENT_ID>.json`. Candidate objects
must carry the §4.3 fields **plus** the two identity-card fields §4.5
requires: `"type"` and `"definition"` (one sentence: what it is and
what it enabled). Then:

```sh
python3 pipeline/pipeline.py add-candidates --graph $G --parent <PARENT_ID> --file work/candidates_<PARENT_ID>.json
```

You may scout in several batches and call `add-candidates` repeatedly;
batches accumulate. Stop when you reach the profile's `raw_target`.

### Step 2 — Resolve identities (CLI)

```sh
python3 pipeline/pipeline.py resolve --graph $G --parent <PARENT_ID>
```

Deterministic resolution per §4.5: canonical-ID and alias matches and
strong-band embedding matches are applied; candidates dated on/after
the parent are dropped; exact repeats of this parent's rejections are
dropped. Ambiguous pairs are written to `judge_queue_<PARENT_ID>.json`
**next to the graph file**. The command prints `distinct`,
`matched_existing`, `auto_merges`, and `judge_queue` counts.

### Step 3 — Judge the gray zone (you) — skip if `judge_queue` is 0

Read the queue file. For every pair, decide using the IDENTITY JUDGE
instructions (§6.3): `SAME`, `DIFFERENT`, or `SUBTYPE`, with a
one-sentence reason. Write `work/judgments_<PARENT_ID>.json`:

```json
{"judgments": [{"pair_id": "cand-cand:3:7", "decision": "SAME", "reason": "…"}]}
```

```sh
python3 pipeline/pipeline.py apply-judgments --graph $G --parent <PARENT_ID> --file work/judgments_<PARENT_ID>.json
```

Every pair in the queue needs a decision; unjudged pairs stay separate
(the safe direction) but keep `pending_judge` flags in the output.

### Step 4 — Evaluate (you)

Get the final candidate list:

```sh
python3 pipeline/pipeline.py show-distinct --graph $G --parent <PARENT_ID>
```

For **every** distinct candidate, apply the EVALUATOR CONTRACT (§6.2):
answer Q1–Q12 in relation to PARENT, each verdict `pass|partial|fail`,
every pass carrying evidence + source + a falsification note. Also
write the candidate's `bottleneck` sentence (the bottleneck IT removed,
in the §3 form — this becomes its node text if admitted) and confirm
its `year`, `type`, `definition`. Write `work/verdicts_<PARENT_ID>.json`:

```json
{"evaluations": [
  {"cand_id": "<from show-distinct>", "bottleneck": "Before X, …",
   "verdicts": {"Q1": {"verdict": "pass", "evidence": "…", "source": "…", "falsification": "…"},
                "Q2": {"…": "…"}, "Q12": {"…": "…"}}}
]}
```

All 12 keys are required per evaluation (missing keys count as `fail`).

### Step 5 — Apply verdicts (CLI: gates, ranking, insertion)

```sh
python3 pipeline/pipeline.py apply-verdicts --graph $G --parent <PARENT_ID> --file work/verdicts_<PARENT_ID>.json
# smoke depth-2 expansions only: add --cap 6
```

The CLI applies the §5 gates ((Q1 or Q2 pass) and Q3 not a clear fail),
downgrades evidence-less passes to `partial`, ranks survivors by score
across the other nine questions, caps them, creates nodes (or links to
existing nodes the candidates matched — that is convergence), writes
edges with the verdicts, records every rejection with its reason, marks
PARENT expanded, and checkpoints. It prints survivor / created /
linked / rejected counts and the next frontier.

### Step 6 — Verify (you, then CLI)

For each survivor created or linked in Step 5, run the VERIFIER
instructions (§6.4): multiples test on Q3, attack on Q1, date and
causal-direction check. Write `work/verification_<PARENT_ID>.json`:

```json
{"verifications": [{"node_id": "…", "outcome": "verified|provisional|killed", "notes": "…"}]}
```

```sh
python3 pipeline/pipeline.py apply-verification --graph $G --file work/verification_<PARENT_ID>.json
```

`killed` keeps the node visible but removes it from the frontier
forever. When in doubt, use `provisional`, never `verified`.

### Step 7 — Render (CLI) and loop

```sh
python3 pipeline/pipeline.py render --graph $G --out runs/full/index.html
```

Render after every expansion (cheap) so the page is always current.
Then go back to Step 0.

---

## 5. Checkpoint / resume protocol

The graph file is the only state that matters. To resume after any
interruption (crash, restart, new agent):

1. `python3 pipeline/pipeline.py status --graph $G` — read counts,
   `expansions` stages, and the frontier.
2. If some node has an expansion in stage `scouted`, `resolved`, or
   `judged` but not `evaluated`, resume THAT expansion at the matching
   step in §4 (its raw candidates, resolution, and judge queue are all
   stored in the graph / queue file). Do not re-scout it.
3. Otherwise continue at Step 0 with `frontier_detail[0]`.
4. Never re-run `init` on an existing graph (it refuses without
   `--force`; `--force` destroys the run — do not use it mid-run).

---

## 6. Prompts (verbatim)

### 6.1 Scout prompt (DESIGN.md §4.3)

```
ROLE
You are the candidate scout for a recursive history-of-technology trace.
Your job is breadth, not judgment. A later stage will interrogate every
candidate with 12 fixed questions and prune hard. If you pre-filter by
importance, the trace loses exactly the candidates that matter most.
Over-propose.

PARENT NODE
Name: {parent_name}
Year: {parent_year}  (hard upper bound: every candidate must be earlier)
Domain: {parent_domain}
Bottleneck this node removed: {bottleneck_statement}
Read it as: "Before {parent_name}, {capability} was impossible or
impractical because {constraint}."

TASK
Find approximately 100 earlier advances that plausibly removed part of
that bottleneck, or were necessary preconditions for {parent_name}.
Work through all 10 search lenses (attached). Run real web searches for
each lens, at least 2 query variants per lens, and read the strongest
sources, preferring reference works, textbooks, and scholarly histories
over popular listicles.

RULES
- Dated and named. Every candidate is a specific advance with an
  approximate year. Era-words are banned: not "electricity" but
  "Gramme dynamo (1871)"; not "computers" but "stored-program
  architecture (1945)".
- Causal claim required. One sentence: "{candidate} made {parent_name}
  possible by ..." If you cannot write that sentence, drop the candidate.
- Reuse canonical names. If a candidate matches a node in EXISTING
  NODES (attached), use that exact name. This is what lets the graph merge.
- Never re-propose anything in ALREADY REJECTED (attached).
- Borderline is fine. Duplicates across lenses are fine; dedupe comes
  later. Importance filtering is NOT your job.

OUTPUT
A JSON array only, one object per candidate:
{"name": "...", "year": 1871, "domain": "...", "lens": "instruments",
 "causal_claim": "...", "source_title": "...", "source_url": "..."}
```

Pipeline addendum to the OUTPUT schema (required by §4.5's identity
card; add these two fields to every object):
`"type": "device|theory|method|material|institution|other"` and
`"definition": "one sentence: what it is and what it enabled"`.
For a smoke run, "approximately 100" reads as the smoke `raw_target`.

The 10 lenses (attach to the prompt): 1 Bottleneck-direct ("what made
{capability} possible", "history of {domain}", "{parent} prerequisites",
"why was {parent} impossible before {parent_year}") · 2 Components
("history of {subsystem}", "{subsystem} invention", "first practical
{subsystem}") · 3 Underlying science ("{parent} scientific basis",
"discovery that enabled {domain}") · 4 Instruments ("instruments used
in early {domain}", "how was {quantity} first measured") · 5 Materials
("{material} production history", "history of {material} purification")
· 6 Mathematics ("mathematics behind {parent}", "history of
{formalism}") · 7 Infrastructure ("what infrastructure did {domain}
depend on") · 8 Cross-domain transfer ("{technique} applied to
{domain} history", "{parent} borrowed from which field") · 9 Methods
("process that made {parent} manufacturable", "history of {process}")
· 10 Timelines ("timeline of {domain}", encyclopedia / survey history
of {domain}).

### 6.2 Evaluator contract (DESIGN.md §5)

```
You receive ONE candidate, the PARENT node it claims to enable, and the
candidate's causal claim. Answer all 12 questions about the candidate
IN RELATION TO THE PARENT. Verdicts: pass / partial / fail.

Q1 Impossibility flip — Before this, was there a specific problem that
   could not be solved at all, and did this make it solvable?
Q2 Generativity — Did this unblock a whole space of previously
   impossible things, not just one problem?
Q3 Necessity — For the parent, was this the only path through, or could
   the parent have emerged another way?
Q4 Cost collapse — Did it drop the cost, time, or effort of something
   by orders of magnitude, making the impractical routine?
Q5 Measurability — Did it make something previously unobservable into
   something measurable?
Q6 Understanding — Did it supply a new explanatory model, so people
   could design deliberately instead of by trial and error?
Q7 Composability — Did it create a standard, interface, or abstraction
   others could build on without understanding its internals?
Q8 Cross-domain reach — Did it unlock progress in fields beyond the one
   it was created for?
Q9 Iteration speed — Did it collapse the experiment feedback loop,
   making the next try dramatically faster?
Q10 Displacement — Did it replace the incumbent default, so the old way
   stopped being the standard path?
Q11 Lineage centrality — In the history that actually happened, is this
   a trunk node or a side branch?
Q12 Irreversibility — Once it existed, could the field ever go back, or
   did it permanently reset the baseline?

Evidence discipline: every "pass" requires (a) a short evidence quote
or concrete factual claim, (b) a source, (c) a falsification note of
the form "this pass dies if …". A pass without evidence is recorded as
partial by the pipeline. Be strict: partial is the honest verdict for
"plausibly yes, thin evidence". Also return the candidate's bottleneck
sentence: "Before <candidate>, <capability> was impossible or
impractical because <constraint>."
```

Gates applied by the CLI (you do not apply them): survive iff
(Q1 pass OR Q2 pass) AND Q3 is not a clear fail; rank by score across
Q4–Q12 (pass 1.0, partial 0.5, fail 0); cap per profile.

### 6.3 Identity judge instructions (DESIGN.md §4.5)

```
You receive a pair of identity cards (name, aliases, year, domain,
type, one-sentence definition) that automated signals could not
separate: their embedding similarity fell in the 0.80–0.92 gray zone,
or their names stand in a containment relation. Decide:

SAME — both cards denote one and the same advance (same event /
  artifact / publication / formulation, allowing name variants,
  translations, and inventor-name prefixes).
DIFFERENT — two distinct advances, however related.
SUBTYPE — one card denotes a specific instance or variant of the other
  (e.g. "Gramme dynamo" vs "dynamo"): keep both; do NOT merge.

Rules: a year gap over ~25 years or a type clash (person vs device,
theory vs material) forces DIFFERENT. When genuinely unsure, choose
DIFFERENT — a false split is cheap, a false merge silently rewrites
history. Answer with the decision and ONE sentence of reason; the
reason is written to the merge log.
```

### 6.4 Verifier instructions (DESIGN.md §6)

```
You are the adversarial verifier. Your job is to KILL this node. For a
survivor node and the edge that admitted it, run three attacks:

1. Attack Q1: was the problem truly impossible before this advance, or
   merely hard, expensive, or unfashionable? Search for prior art.
2. Multiples test on Q3: search for independent, near-simultaneous
   discoverers or inventors of the same advance. If two others did it
   in the same decade, necessity is downgraded to "ripe" — record that
   in your notes (the node may still stand, but never as "verified"
   on necessity grounds).
3. Check the date and the causal direction: is the year defensible, and
   did the influence really run from this node toward the child?

Outcomes: "verified" only if all three attacks fail to land. "killed"
if the date is wrong, the causal direction is reversed, or the advance
did not exist as described. Otherwise "provisional", with the strongest
attack recorded in your notes.
```

---

## 7. Rendering

```sh
python3 pipeline/pipeline.py render --graph $G --out <path>.html
```

Produces ONE self-contained HTML file (no external assets; graph data
embedded). Open it in any browser. Features: Trace view (layered DAG by
depth, +/− collapse on nodes with predecessors), Timeline view (nodes
on a year axis), search by name/alias, and a detail panel per node:
bottleneck sentence, definition, status badge, sources, and the full
12-question verdict table with evidence and falsification notes for
every node it enables. Render after every expansion; rendering never
mutates the graph.

For the eventual AI Praxis Lab integration, this same file is the
artifact to embed (DESIGN.md §9).

---

## 8. Stop conditions

Stop the run (and render a final page) when ANY fires:

1. The frontier is empty (everything admitted has been expanded or hit
   the depth cap).
2. Live-node count reaches the profile `node_budget` (2000 full / 60
   smoke). The graph is still complete and publishable as-is.
3. An expansion yields fewer than `min_gate_survivors` survivors AND
   the frontier nodes behind it are all at or beyond the depth where
   their candidate pools fall before the `year_floor` (~1500) — the
   written record has thinned out.
4. Smoke profile only: root expanded + exactly two survivors expanded
   + all survivors verified + page rendered. Stop there by design.

Also stop a single node's expansion (mark it expanded via a verdicts
file with zero evaluations only if truly nothing passed — in practice,
record what happened in the run log instead) when its candidate pool is
exhausted: scouts return only already-rejected or post-dated items.

---

## 9. Troubleshooting

- **`graph file not found`** — run `init` first, and check `--graph`
  points at the run's graph (paths are relative to where you invoke).
- **`unknown cand_id in verdicts`** — verdicts must use the `cand_id`s
  from `show-distinct` for THIS parent, after judgments were applied.
  Re-run `show-distinct`; do not invent ids.
- **Judge queue file missing** — it is written next to the graph file
  (`judge_queue_<PARENT_ID>.json` in the graph's directory), not in
  `work/`. Re-run `resolve` to regenerate it.
- **A survivor links to an existing node instead of creating one** —
  that is convergence working as designed (§4.5), not a bug. It appears
  under `linked_existing` in the `apply-verdicts` output.
- **Everything is being rejected at the gate** — check evidence
  discipline first: passes without evidence text are downgraded to
  `partial`, and a `partial` Q1/Q2 does NOT satisfy the gate. Add real
  evidence quotes and re-apply verdicts for that parent (the expansion
  is still open until `apply-verdicts` succeeds once — after it has,
  re-applying is not supported; escalate instead).
- **Embedder shows `tfidf-fallback`** — expected without
  `sentence-transformers`. Consequences: fewer auto-merges, more pairs
  decided "different" by default, name-containment pairs still routed
  to the judge. Safe to run; note it in the run log.
- **Duplicate node names with different ids** — ids carry the year
  (`name-year`); two advances with the same name and year get `-2`
  suffixes. Check `aliases` before concluding a duplicate exists.
- **JSON errors in your work files** — validate before applying:
  `python3 -m json.tool work/<file>.json > /dev/null`.

---

## 10. File map

```
the-behind/
  README.md          what this is (humans)
  DESIGN.md          the approved design (humans)
  RUNBOOK.md         this file (executing agents)
  SMOKE_TEST.md      smoke-run log and results
  pipeline/
    pipeline.py      CLI (init/add-candidates/resolve/show-distinct/
                     apply-judgments/apply-verdicts/apply-verification/
                     status/render)
    graph.py         graph store: nodes, edges, union-find merges,
                     frontier, checkpointing
    identity.py      §4.5 identity resolution (signals, bands, vetoes)
    score.py         §5 gates + ranking (deterministic)
    render.py        graph.json -> single-file interactive HTML
  runs/full/         full-run graph + rendered page (created at runtime)
  smoke/             smoke-run graph + rendered page
```
